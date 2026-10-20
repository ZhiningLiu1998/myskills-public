#!/usr/bin/env python3
"""Observe a GitHub collaboration inbox; never execute or publish its contents."""
from __future__ import annotations

import argparse
import base64
import contextlib
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import sqlite3
import subprocess
import sys
import threading
import time
from typing import Any, Iterator
from urllib.parse import quote, urlsplit

import fcntl

if sys.version_info < (3, 10):
    print("Python 3.10+ is required; use an installed compatible interpreter.", file=sys.stderr)
    raise SystemExit(2)

MAX_DOCUMENT_BYTES = 512 * 1024
STATES = (
    "baseline", "pending", "ignored", "needs_input", "accepted", "queued",
    "running", "validated", "reported", "failed", "superseded", "cancelled",
)
REPO_SOURCE = "@repository"


def require(condition: Any, message: str) -> None:
    """Reject an invalid configuration or operation with an actionable error."""
    if not condition:
        raise ValueError(message)


def encoded(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def positive_int(value: Any) -> bool:
    return type(value) is int and value > 0


def relative_path(value: Any) -> bool:
    return (isinstance(value, str) and bool(value) and not value.startswith("/")
            and "\\" not in value and ".." not in value.split("/")
            and not any(ord(char) < 32 for char in value))


def validate_config(config: dict, state_dir: Path) -> None:
    """Check source bindings and local-state placement without granting authority."""
    require(isinstance(config, dict) and config.get("version") == 1,
            "config.json must have version 1")
    repository = config.get("repository", {})
    require(isinstance(repository, dict), "repository must be an object")
    require(re.fullmatch(r"[A-Za-z0-9.-]+", repository.get("host", "")),
            "repository.host must be a GitHub hostname")
    require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",
                         repository.get("name", "")), "repository.name must be OWNER/REPO")
    require(positive_int(repository.get("id")), "repository.id must be a verified numeric ID")
    project = Path(config.get("project_dir", ""))
    require(project.is_absolute() and project.is_dir(),
            "project_dir must name an existing absolute directory")
    require(not state_dir.resolve().is_relative_to(project.resolve()),
            "Keep the state directory outside the collaborator-controlled project")
    require(type(config.get("interval_seconds")) is int and config["interval_seconds"] >= 30,
            "interval_seconds must be an integer of at least 30")
    prefix = config.get("command_prefix")
    require(isinstance(prefix, str) and prefix and not any(c.isspace() for c in prefix),
            "command_prefix must be a nonempty token, for example @coopa")
    for key in ("trusted_comment_author_ids", "ignored_comment_author_ids"):
        require(isinstance(config.get(key), list) and all(positive_int(x) for x in config[key]),
                f"{key} must contain numeric GitHub user IDs")
    require(type(config.get("auto_execute")) is bool, "auto_execute must be true or false")
    sources = config.get("sources")
    require(isinstance(sources, list) and sources, "Configure at least one source")
    seen = set()
    for source in sources:
        require(isinstance(source, dict), "Each source must be an object")
        identity = source.get("id", "")
        require(isinstance(identity, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", identity),
                "source.id must use letters, digits, underscores or hyphens")
        require(identity not in seen, f"Duplicate source ID: {identity}")
        seen.add(identity)
        kind = source.get("kind")
        require(kind in {"files", "issue", "pull_review", "commit"},
                f"Unsupported source kind for {identity}")
        if kind == "files":
            require(isinstance(source.get("ref"), str) and source["ref"]
                    and not any(ord(c) < 32 for c in source["ref"]),
                    f"{identity}: ref must be a branch or commit")
            require(isinstance(source.get("paths"), list) and source["paths"]
                    and all(relative_path(p) for p in source["paths"]),
                    f"{identity}: paths must be nonempty repository-relative patterns")
            require(type(source.get("trusted")) is bool, f"{identity}: set trusted explicitly")
        elif kind == "commit":
            require(re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", source.get("sha", "")),
                    f"{identity}: use a full commit SHA")
        else:
            require(positive_int(source.get("number")), f"{identity}: number must be positive")


def load_config(state_dir: Path) -> dict:
    config = json.loads((state_dir / "config.json").read_text(encoding="utf-8"))
    validate_config(config, state_dir)
    return config


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        stream.write(encoded(value) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


class BusyError(ValueError):
    """Another local collector currently owns this operation."""


@contextlib.contextmanager
def lock(path: Path) -> Iterator[None]:
    """Hold a local advisory lock; a second collector must wait for its owner."""
    with path.open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise BusyError(f"Busy: original process holds {path}; do not start a duplicate") from error
        yield


class ApiError(Exception):
    def __init__(self, message: str, *, halted: bool = False, retry_at: float = 0):
        super().__init__(message)
        self.halted = halted
        self.retry_at = retry_at


class GitHub:
    """Read GitHub using gh's existing credentials, without interactive login."""

    def __init__(self, host: str):
        self.host = host

    def request(self, endpoint: str) -> tuple[Any, dict[str, str]]:
        environment = {**os.environ, "GH_PROMPT_DISABLED": "1", "GIT_TERMINAL_PROMPT": "0",
                       "GH_PAGER": "cat", "GH_DEBUG": ""}
        try:
            result = subprocess.run(
                ["gh", "api", "--hostname", self.host, "--method", "GET", "--include", endpoint],
                stdin=subprocess.DEVNULL, capture_output=True, text=True, env=environment, timeout=45)
        except subprocess.TimeoutExpired as error:
            raise ApiError("GitHub read timed out; the previous snapshot is retained") from error
        header_text, separator, body = result.stdout.partition("\n\n")
        match = re.match(r"HTTP/\S+\s+(\d+)", header_text)
        headers = {}
        if match and separator:
            for line in header_text.splitlines()[1:]:
                key, colon, value = line.partition(":")
                if colon:
                    headers[key.lower().strip()] = value.strip()
            status = int(match.group(1))
        else:
            match = re.search(r"HTTP (\d{3})", result.stderr)
            status = int(match.group(1)) if match else 0
        if result.returncode or not 200 <= status < 300:
            diagnostic = (body + result.stderr).lower()
            limited = (status == 429 or "retry-after" in headers
                       or headers.get("x-ratelimit-remaining") == "0"
                       or "rate limit" in diagnostic)
            retry_at = 0.0
            if limited:
                try:
                    if "retry-after" in headers:
                        retry_at = time.time() + float(headers["retry-after"])
                    else:
                        retry_at = float(headers.get("x-ratelimit-reset", 0))
                except ValueError:
                    pass
            denied = status in {401, 403, 404} and not limited
            denied = denied or (status == 0 and any(x in diagnostic for x in (
                "authentication failed", "not logged into", "gh auth login", "bad credentials")))
            reason = "rate limited" if limited else "access denied or source unavailable" if denied else "read failed"
            raise ApiError(f"GitHub HTTP {status or 'unknown'}: {reason}",
                           halted=denied, retry_at=retry_at)
        try:
            return json.loads(body), headers
        except json.JSONDecodeError as error:
            raise ApiError("GitHub returned invalid JSON; snapshot not advanced") from error

    def get(self, endpoint: str) -> Any:
        return self.request(endpoint)[0]

    def pages(self, endpoint: str) -> list[dict]:
        """Read all pages before returning; validate server-supplied next URLs."""
        result, visited = [], set()
        initial_path = urlsplit(endpoint).path.lstrip("/")
        while endpoint:
            if endpoint in visited:
                raise ApiError("Pagination repeated a page; snapshot not advanced")
            visited.add(endpoint)
            data, headers = self.request(endpoint)
            if not isinstance(data, list):
                raise ApiError("Expected a paginated array; snapshot not advanced")
            result.extend(data)
            next_link = re.search(r'<([^>]+)>\s*;\s*rel="next"', headers.get("link", ""))
            endpoint = ""
            if next_link:
                parsed = urlsplit(next_link.group(1))
                expected_host = "api.github.com" if self.host == "github.com" else self.host
                prefix = "" if self.host == "github.com" else "/api/v3"
                if (parsed.scheme != "https" or parsed.netloc != expected_host
                        or parsed.path != prefix + "/" + initial_path or parsed.fragment):
                    raise ApiError("Unexpected pagination destination; snapshot not advanced", halted=True)
                endpoint = initial_path + ("?" + parsed.query if parsed.query else "")
        return result


def candidate(config: dict, payload: dict) -> tuple[bool, str]:
    """Apply source identity/address filters; task authorization remains with the agent."""
    source = next((s for s in config["sources"] if s["id"] == payload["source"]), None)
    if source is None:
        return False, "source no longer configured"
    if payload["kind"] == "files":
        return source["trusted"], "designated file source" if source["trusted"] else "file source not delegated"
    author = payload["author"]
    if author.get("id") in config["ignored_comment_author_ids"] or author.get("type") == "Bot":
        return False, "operator or bot output"
    if author.get("id") not in config["trusted_comment_author_ids"]:
        return False, "author not delegated"
    text = payload["body"].lstrip()
    if text.startswith("<!-- coopa-result"):
        return False, "result marker"
    prefix = config["command_prefix"]
    if not re.match(re.escape(prefix) + r"(?=$|\s|:)", text):
        return False, "not addressed to the agent"
    return True, "addressed comment from a delegated author"


def snapshot(api: GitHub, config: dict, source: dict) -> tuple[list[dict], str]:
    """Collect one complete source snapshot before any cursor or event is changed."""
    base = "repos/" + config["repository"]["name"]
    kind = source["kind"]
    items = []
    if kind == "files":
        commit = api.get(f"{base}/commits/{quote(source['ref'], safe='')}")
        version = commit["sha"]
        tree = api.get(f"{base}/git/trees/{commit['commit']['tree']['sha']}?recursive=1")
        if tree.get("truncated") is not False:
            raise ApiError("Repository tree is incomplete; narrow the source or add subtree traversal")
        for entry in tree["tree"]:
            path = entry["path"]
            if entry.get("type") == "tree" or not any(fnmatch.fnmatchcase(path, p) for p in source["paths"]):
                continue
            if entry.get("mode") not in {"100644", "100755"} or entry.get("type") != "blob":
                raise ApiError(f"Watched path is not a regular file: {path}")
            if entry.get("size", MAX_DOCUMENT_BYTES + 1) > MAX_DOCUMENT_BYTES:
                raise ApiError(f"Watched file exceeds 512 KiB: {path}")
            blob = api.get(f"{base}/git/blobs/{entry['sha']}")
            if blob.get("encoding") != "base64":
                raise ApiError(f"Unsupported blob encoding: {path}")
            try:
                raw = base64.b64decode("".join(blob["content"].split()), validate=True)
                if len(raw) > MAX_DOCUMENT_BYTES:
                    raise ValueError("oversized")
                text = raw.decode("utf-8")
            except (ValueError, UnicodeError) as error:
                raise ApiError(f"Invalid or oversized UTF-8 document: {path}") from error
            items.append({"key": path, "body": text, "version": version, "blob": entry["sha"],
                          "url": f"https://{config['repository']['host']}/{config['repository']['name']}/blob/{version}/{quote(path, safe='/')}"})
    else:
        if kind == "issue":
            issue = api.get(f"{base}/issues/{source['number']}")
            objects = [("body", issue)] + [
                ("comment", item) for item in api.pages(
                    f"{base}/issues/{source['number']}/comments?per_page=100")]
        else:
            suffix = (f"pulls/{source['number']}/comments" if kind == "pull_review"
                      else f"commits/{source['sha']}/comments")
            objects = [("comment", item) for item in api.pages(f"{base}/{suffix}?per_page=100")]
        version = str(time.time_ns())
        for object_kind, item in objects:
            text = item.get("body") or ""
            if len(text.encode("utf-8")) > MAX_DOCUMENT_BYTES:
                raise ApiError("Comment exceeds 512 KiB; snapshot not advanced")
            user = item.get("user") or {}
            items.append({"key": f"{object_kind}:{item['id']}", "body": text,
                          "title": item.get("title"), "version": item["updated_at"],
                          "url": item["html_url"],
                          "author": {k: user.get(k) for k in ("id", "login", "type")}})
    for item in items:
        item.update(source=source["id"], kind=kind, repository=config["repository"], change="content")
        item["candidate"], item["reason"] = candidate(config, item)
        # Content hashes detect revisions; metadata-only updates do not resubmit requests.
        item["fingerprint"] = hashlib.sha256(encoded({
            "body": item["body"], "title": item.get("title"),
            "author_id": item.get("author", {}).get("id"),
        }).encode("utf-8")).hexdigest()
    keys = [item["key"] for item in items]
    if len(keys) != len(set(keys)):
        raise ApiError("Snapshot repeated an object; retry a complete snapshot")
    return items, version


class Store:
    """Persist source snapshots and receipts in atomic SQLite transactions."""

    def __init__(self, state_dir: Path, config: dict):
        self.config = config
        self.db = sqlite3.connect(state_dir / "inbox.sqlite3", timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            PRAGMA foreign_keys=ON;
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY, spec TEXT NOT NULL, initialized INTEGER DEFAULT 0,
                last_success REAL, failures INTEGER DEFAULT 0, error TEXT,
                retry_at REAL DEFAULT 0, halted INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY, source TEXT NOT NULL REFERENCES sources(id),
                object_key TEXT NOT NULL, observed_at REAL NOT NULL,
                status TEXT NOT NULL, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS objects (
                source TEXT NOT NULL REFERENCES sources(id), object_key TEXT NOT NULL,
                fingerprint TEXT NOT NULL, present INTEGER NOT NULL, event_id INTEGER NOT NULL,
                PRIMARY KEY (source, object_key));
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY, event_id INTEGER NOT NULL REFERENCES events(id),
                recorded_at REAL NOT NULL, status TEXT NOT NULL, note TEXT NOT NULL,
                evidence TEXT NOT NULL);
        """)
        identity = encoded(config["repository"])
        old = self.db.execute("SELECT value FROM meta WHERE key='repository'").fetchone()
        if old and old["value"] != identity:
            self.db.close()
            raise ValueError("State belongs to another repository; use its original config")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO meta VALUES ('repository', ?)", (identity,))

    def close(self) -> None:
        self.db.close()

    def bind(self, source: dict) -> None:
        specification = encoded({k: v for k, v in source.items() if k != "trusted"})
        old = self.db.execute("SELECT spec FROM sources WHERE id=?", (source["id"],)).fetchone()
        require(not old or old["spec"] == specification,
                f"Source {source['id']} changed identity; use a new source ID and review its baseline")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO sources(id,spec) VALUES (?,?)",
                            (source["id"], specification))

    def source_status(self, identity: str) -> dict:
        row = self.db.execute("SELECT * FROM sources WHERE id=?", (identity,)).fetchone()
        require(row is not None, f"Unknown source: {identity}")
        return dict(row)

    def deferred(self, identity: str) -> bool:
        row = self.source_status(identity)
        return bool(row["halted"] or row["retry_at"] > time.time())

    def failure(self, identity: str, error: ApiError) -> None:
        failures = self.source_status(identity)["failures"] + 1
        retry_at = max(error.retry_at, time.time() + min(1800, 60 * 2 ** min(failures - 1, 5)))
        with self.db:
            self.db.execute("UPDATE sources SET failures=?,error=?,retry_at=?,halted=? WHERE id=?",
                            (failures, str(error), retry_at, int(error.halted), identity))

    def success(self, identity: str) -> None:
        self.db.execute("""UPDATE sources SET initialized=1,last_success=?,failures=0,
                           error=NULL,retry_at=0,halted=0 WHERE id=?""", (time.time(), identity))

    def ingest(self, identity: str, items: list[dict], version: str) -> int:
        baseline = not self.source_status(identity)["initialized"]
        previous = {row["object_key"]: dict(row) for row in self.db.execute(
            "SELECT * FROM objects WHERE source=?", (identity,))}
        count = 0
        with self.db:
            for payload in items:
                old = previous.pop(payload["key"], None)
                if old and old["present"] and old["fingerprint"] == payload["fingerprint"]:
                    continue
                status = ("baseline" if baseline else "pending") if payload["candidate"] else "ignored"
                event_id = self.db.execute(
                    "INSERT INTO events(source,object_key,observed_at,status,payload) VALUES (?,?,?,?,?)",
                    (identity, payload["key"], time.time(), status, encoded(payload))).lastrowid
                self.db.execute("INSERT OR REPLACE INTO objects VALUES (?,?,?,?,?)",
                                (identity, payload["key"], payload["fingerprint"], 1, event_id))
                count += 1
            for key, old in previous.items():
                if not old["present"]:
                    continue
                payload = self.event(old["event_id"])["payload"]
                payload.update(change="missing", snapshot_version=version,
                               previous_event_id=old["event_id"],
                               reason="Absence requires review; it does not cancel a job")
                status = "needs_input" if payload["candidate"] else "ignored"
                event_id = self.db.execute(
                    "INSERT INTO events(source,object_key,observed_at,status,payload) VALUES (?,?,?,?,?)",
                    (identity, key, time.time(), status, encoded(payload))).lastrowid
                self.db.execute("UPDATE objects SET present=0,event_id=? WHERE source=? AND object_key=?",
                                (event_id, identity, key))
                count += 1
            self.success(identity)
        return count

    def events(self, status: str | None = None) -> list[dict]:
        query = "SELECT id,source,object_key,observed_at,status FROM events"
        rows = self.db.execute(query + (" WHERE status=?" if status else "") + " ORDER BY id",
                               (status,) if status else ())
        return [dict(row) for row in rows]

    def event(self, event_id: int) -> dict:
        row = self.db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        require(row is not None, f"Unknown event ID: {event_id}")
        result = dict(row)
        result["payload"] = json.loads(result["payload"])
        result["receipts"] = [
            {**dict(receipt), "evidence": json.loads(receipt["evidence"])}
            for receipt in self.db.execute(
                "SELECT * FROM receipts WHERE event_id=? ORDER BY id", (event_id,))]
        return result

    def record(self, event_id: int, status: str, note: str, evidence: list[str]) -> dict:
        require(status in STATES and status not in {"baseline", "pending"}, "Unsupported receipt status")
        require(bool(note.strip()), "A receipt needs a concrete note")
        require(status not in {"validated", "reported"} or any(x.strip() for x in evidence),
                "Validated/reported receipts need an evidence path or delivery reference")
        event = self.event(event_id)
        if status in {"accepted", "queued", "running"}:
            require(event["payload"]["candidate"] and event["payload"]["change"] == "content",
                    "Filtered or missing content cannot be accepted for execution")
            require(event["status"] not in {"validated", "reported", "ignored", "superseded", "cancelled"},
                    "Do not reopen finished or discarded work; use an explicit new request")
        if status == "accepted":
            eligible, reason = candidate(self.config, event["payload"])
            require(eligible, f"Request is no longer eligible: {reason}")
            current_source = next(s for s in self.config["sources"] if s["id"] == event["source"])
            require(self.source_status(event["source"])["spec"]
                    == encoded({k: v for k, v in current_source.items() if k != "trusted"}),
                    "Source binding changed; review the new source baseline")
            latest = self.db.execute("SELECT event_id FROM objects WHERE source=? AND object_key=?",
                                     (event["source"], event["object_key"])).fetchone()
            require(latest["event_id"] == event_id, "Read the latest revision before accepting this request")
        with self.db:
            self.db.execute("INSERT INTO receipts(event_id,recorded_at,status,note,evidence) VALUES (?,?,?,?,?)",
                            (event_id, time.time(), status, note, encoded(evidence)))
            self.db.execute("UPDATE events SET status=? WHERE id=?", (status, event_id))
        return self.event(event_id)

    def status(self) -> dict:
        return {
            "sources": [{k: row[k] for k in row.keys() if k != "spec"}
                        for row in self.db.execute("SELECT * FROM sources ORDER BY id")],
            "event_counts": {row["status"]: row["n"] for row in self.db.execute(
                "SELECT status,COUNT(*) n FROM events GROUP BY status")},
        }


def poll(state_dir: Path, config: dict, store: Store, api: GitHub) -> dict:
    """Acquire complete snapshots independently; failures never advance their sources."""
    with lock(state_dir / "poll.lock"):
        store.bind({"id": REPO_SOURCE, "repository": config["repository"]})
        for source in config["sources"]:
            store.bind(source)
        changes, errors = 0, []
        if store.deferred(REPO_SOURCE):
            errors.append(store.source_status(REPO_SOURCE))
        else:
            try:
                repository = api.get("repos/" + config["repository"]["name"])
                if repository["id"] != config["repository"]["id"]:
                    raise ApiError("Repository ID changed; refusing this source", halted=True)
                with store.db:
                    store.success(REPO_SOURCE)
            except (KeyError, TypeError) as error:
                store.failure(REPO_SOURCE, ApiError("Malformed repository metadata"))
                errors.append(store.source_status(REPO_SOURCE))
            except ApiError as error:
                store.failure(REPO_SOURCE, error)
                errors.append(store.source_status(REPO_SOURCE))
        if not errors:
            for source in config["sources"]:
                identity = source["id"]
                if store.deferred(identity):
                    errors.append(store.source_status(identity))
                    continue
                try:
                    items, version = snapshot(api, config, source)
                    changes += store.ingest(identity, items, version)
                except (KeyError, TypeError) as error:
                    store.failure(identity, ApiError("Malformed source response; snapshot not advanced"))
                    errors.append(store.source_status(identity))
                except ApiError as error:
                    store.failure(identity, error)
                    errors.append(store.source_status(identity))
        receipt = {"observed_at": time.time(), "ok": not errors, "new_events": changes,
                   "errors": [{k: e[k] for k in ("id", "error", "last_success", "retry_at", "halted")}
                              for e in errors], "experiments_executed": False}
        atomic_json(state_dir / "latest.json", receipt)
        return receipt


def readiness(config: dict, store: Store) -> list[str]:
    """Find missing setup fields; this is not a security or scientific validator."""
    missing = []
    repository = store.db.execute("SELECT * FROM sources WHERE id=?", (REPO_SOURCE,)).fetchone()
    if not repository or not repository["initialized"] or repository["error"]:
        missing.append("successful repository identity check")
    for key in ("conversation_id", "auto_execute"):
        if not config.get(key):
            missing.append(key)
    authority = config.get("authorization", {})
    for key in ("recorded_from", "objective", "allowed_write_paths", "runner", "resources"):
        if not authority.get(key):
            missing.append("authorization." + key)
    publication = authority.get("publication", {})
    if publication.get("mode") not in {"local", "repo_files"}:
        missing.append("authorization.publication.mode (local or repo_files)")
    elif publication["mode"] == "repo_files" and not (
            publication.get("paths") and publication.get("branch")):
        missing.append("authorized publication paths and existing branch")
    for source in config["sources"]:
        row = store.db.execute("SELECT * FROM sources WHERE id=?", (source["id"],)).fetchone()
        if not row or not row["initialized"] or row["error"]:
            missing.append(source["id"] + ": successful baseline poll")
        elif time.time() - row["last_success"] > 2 * config["interval_seconds"]:
            missing.append(source["id"] + ": fresh poll")
        elif row["spec"] != encoded({k: v for k, v in source.items() if k != "trusted"}):
            missing.append(source["id"] + ": changed binding needs a new source ID")
        if source["kind"] == "files":
            if not source["trusted"]:
                missing.append(source["id"] + ": local file-source delegation")
            count = store.db.execute("SELECT COUNT(*) FROM objects WHERE source=? AND present=1",
                                     (source["id"],)).fetchone()[0]
            if not count:
                missing.append(source["id"] + ": a matching instruction file")
        elif not (set(config["trusted_comment_author_ids"]) - set(config["ignored_comment_author_ids"])):
            missing.append(source["id"] + ": a delegated comment author")
    return missing


def initialize(state_dir: Path, repo: str, host: str, project: Path) -> dict:
    """Create a disabled local contract using read-only repository/account metadata."""
    require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo), "--repo must be OWNER/REPO")
    require(re.fullmatch(r"[A-Za-z0-9.-]+", host), "--host must be a GitHub hostname")
    require(not state_dir.exists() or not any(state_dir.iterdir()),
            "State already exists; inspect and resume it instead of overwriting")
    require(project.is_absolute() and project.is_dir(), "--project-dir must be an existing absolute directory")
    require(not state_dir.resolve().is_relative_to(project.resolve()),
            "State must be outside the shared checkout")
    api = GitHub(host)
    metadata, viewer = api.get("repos/" + repo), api.get("user")
    config = json.loads((Path(__file__).resolve().parents[1] / "assets/config.example.json").read_text())
    config["repository"] = {"host": host, "name": metadata["full_name"], "id": metadata["id"]}
    config["project_dir"] = str(project.resolve())
    config["ignored_comment_author_ids"] = [viewer["id"]]
    config["sources"][0]["ref"] = metadata["default_branch"]
    validate_config(config, state_dir)
    state_dir.mkdir(parents=True, mode=0o700, exist_ok=True)
    with (state_dir / "config.json").open("x", encoding="utf-8") as stream:
        stream.write(encoded(config) + "\n")
    return {"state_dir": str(state_dir), "repository": config["repository"],
            "auto_execute": False, "next": "Configure authority and sources, then review the first poll"}


def watch(state_dir: Path) -> None:
    """Collect with one live process; an active agent must separately consume events."""
    stop = threading.Event()
    original = {}
    with lock(state_dir / "watch.lock"):
        for signum in (signal.SIGINT, signal.SIGTERM):
            original[signum] = signal.signal(signum, lambda *_: stop.set())
        identity = {"pid": os.getpid(), "started_at": time.time(), "consumer": "not managed by this helper"}
        try:
            while not stop.is_set():
                config = load_config(state_dir)
                try:
                    with contextlib.closing(Store(state_dir, config)) as store:
                        receipt = poll(state_dir, config, store, GitHub(config["repository"]["host"]))
                except BusyError:
                    atomic_json(state_dir / "watcher.json", {
                        **identity, "state": "waiting_for_poll", "heartbeat_at": time.time()})
                    stop.wait(1)
                    continue
                print(encoded(receipt), flush=True)
                deadline = time.monotonic() + config["interval_seconds"]
                while not stop.is_set():
                    atomic_json(state_dir / "watcher.json", {
                        **identity, "state": "collecting", "heartbeat_at": time.time(),
                        "last_poll_ok": receipt["ok"]})
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    stop.wait(min(30, remaining))
        finally:
            atomic_json(state_dir / "watcher.json", {**identity, "state": "stopped", "heartbeat_at": time.time()})
            for signum, handler in original.items():
                signal.signal(signum, handler)


def main() -> int:
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--repo", required=True)
    init.add_argument("--host", default="github.com")
    init.add_argument("--project-dir", type=Path, required=True)
    for command in ("poll", "status", "ready", "watch"):
        commands.add_parser(command)
    events = commands.add_parser("events")
    events.add_argument("--status", choices=STATES)
    show = commands.add_parser("show")
    show.add_argument("event_id", type=int)
    record = commands.add_parser("record")
    record.add_argument("event_id", type=int)
    record.add_argument("status", choices=STATES)
    record.add_argument("--note", required=True)
    record.add_argument("--evidence", action="append", default=[])
    retry = commands.add_parser("retry-source")
    retry.add_argument("source_id")
    args = parser.parse_args()
    state_dir = args.state_dir.expanduser().resolve()
    try:
        if args.command == "init":
            output = initialize(state_dir, args.repo, args.host, args.project_dir)
        elif args.command == "watch":
            load_config(state_dir)
            watch(state_dir)
            return 0
        else:
            config = load_config(state_dir)
            with contextlib.closing(Store(state_dir, config)) as store:
                if args.command == "poll":
                    output = poll(state_dir, config, store, GitHub(config["repository"]["host"]))
                    print(encoded(output))
                    return 0 if output["ok"] else 3
                if args.command == "events":
                    output = store.events(args.status)
                elif args.command == "show":
                    output = store.event(args.event_id)
                elif args.command == "record":
                    output = store.record(args.event_id, args.status, args.note, args.evidence)
                elif args.command == "retry-source":
                    with lock(state_dir / "poll.lock"), store.db:
                        store.source_status(args.source_id)
                        store.db.execute("UPDATE sources SET retry_at=0,halted=0 WHERE id=?", (args.source_id,))
                    output = {"source": args.source_id, "next_read_enabled": True}
                elif args.command == "ready":
                    missing = readiness(config, store)
                    print(encoded({"ready": not missing, "missing": missing, "execution_started": False}))
                    return 2 if missing else 0
                else:
                    output = store.status()
                    for filename in ("latest.json", "watcher.json"):
                        if (state_dir / filename).exists():
                            output[filename] = json.loads((state_dir / filename).read_text())
        print(encoded(output))
        return 0
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error, ApiError) as error:
        print(encoded({"ok": False, "error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
