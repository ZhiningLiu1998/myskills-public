---
name: chatgpt-ui-review
description: Ask ChatGPT in an already signed-in browser to review text, UI screenshots, or both. Use when the user requests a web ChatGPT writing review, UI/UX review, or combined review.
---

# ChatGPT text and UI review

Obtain an actual review from the user's authenticated ChatGPT web session.
This skill works from Codex or Claude Code; the helper uses macOS native APIs.

## Review scope

Follow the user's requested scope. Otherwise infer it from their goal and supplied
materials, and state the choice. Text visible in a screenshot alone does not imply
a combined review.

- **Text only:** provide the text and relevant audience, purpose, and constraints.
  Ask for clarity, structure, tone, concision, and concrete edits. No screenshots
  or UI redesign are needed.
- **UI only:** provide real screenshots and enough context to explain the flow.
  Ask about layout, hierarchy, navigation, interaction, and missing states.
  Discuss labels where they affect usability; avoid unrelated prose rewrites.
- **Combined:** pair screenshots with their corresponding copy. Ask for UI/flow
  improvements and revised text that work together.

For copy under review, include this standard in the brief: clear, concise text
fit for mature commercial software. Cut filler, repetition, obvious explanations,
and overly defensive caveats or assurances.

## Workflow

1. Put the selected scope's materials, user feedback, and constraints in a local
   review folder. For UI review, capture real states as PNGs, including relevant
   content below the fold. Use fixture data when available; exclude unrelated
   private data.
2. Reuse the signed-in browser and any ChatGPT project the user specified. Create
   a dedicated review tab/window and record its IDs and URL. A newly launched
   debugging browser does not inherit the user's login.
3. Enter one brief stating the review scope and requested output. Include the
   source text for text review. When images are included, attach them, explain
   their order and context, and request review of the screenshots themselves.
   Keep proposed changes within the user's goals and the product's capabilities.
4. Space review message send attempts at least two minutes apart, including
   retries. Follow any longer cooldown shown by the website. Before sending,
   check the composer text and any attachment previews. Wait for any uploads to
   finish. Send once; if the result is uncertain, inspect the conversation before
   retrying so the same request is not submitted twice.
5. Wait for the response to finish, then save the actual answer and conversation
   URL beside the inputs. Report partial or inaccessible responses accurately.
   Apply recommendations only when implementation is part of the user's request.
6. Close only browser tabs/windows this task created. Keep the review artifacts.

## Chrome on macOS

Choose the browser control method from what the environment allows:

1. Use an existing authenticated browser connection if it supports the needed
   operations.
2. If Chrome's **Allow JavaScript from Apple Events** is enabled, DOM scripting
   through AppleScript (`execute javascript`) is available.
3. Otherwise, for example when an organization's policy keeps that setting off,
   normal AppleScript/ScriptingBridge window and tab operations still work, but
   DOM scripting does not. Use Accessibility (AX) for text, and PNG clipboard
   paste only when images are part of the review.

Do not ask the user to change a browser setting that their organization
manages; use the next available method.

The included [helper](scripts/chrome-ax.swift) takes the current Chrome **PID**
and exact window title. Discover both afresh, particularly when another task has
started a second Chrome. Use normal AppleScript/ScriptingBridge to create or
close the review tab; target the PID with ScriptingBridge when instances overlap.

```sh
# SKILL_DIR is this skill's directory; REVIEW_DIR holds this review's artifacts.
swiftc "$SKILL_DIR/scripts/chrome-ax.swift" -o "$REVIEW_DIR/chrome-ax"
"$REVIEW_DIR/chrome-ax" "$CHROME_PID" windows
"$REVIEW_DIR/chrome-ax" "$CHROME_PID" "$WINDOW_TITLE" dump > "$REVIEW_DIR/controls.json"
# Read current labels from controls.json; do not assume English button names.
"$REVIEW_DIR/chrome-ax" "$CHROME_PID" "$WINDOW_TITLE" set "$COMPOSER_LABEL" "$REVIEW_DIR/prompt.txt"
# UI / combined only: paste each screenshot. Skip this for text-only review.
"$REVIEW_DIR/chrome-ax" "$CHROME_PID" "$WINDOW_TITLE" paste-image "$COMPOSER_LABEL" "$REVIEW_DIR/01.png"
# When images are present, inspect thumbnails and upload completion.
"$REVIEW_DIR/chrome-ax" "$CHROME_PID" "$WINDOW_TITLE" click "$SEND_LABEL"
# ChatGPT may rename the window after sending: refresh `windows` first.
"$REVIEW_DIR/chrome-ax" "$CHROME_PID" "$WINDOW_TITLE" text > "$REVIEW_DIR/reply.json"
```

`set` enters UTF-8 text through AX. `paste-image` briefly activates Chrome and
posts Command-V to that PID; it restores the prior app and clipboard unless the
user changed them. Mention the brief focus change before pasting. Other commands
do not activate Chrome. `text` includes visible conversation text: identify the
assistant's answer rather than mistaking the submitted prompt for the review.

If a background Chrome window disappears from AX, reorder only the task's window
while Chrome is behind the current app, then refresh the window list. If native
Accessibility access or browser login is unavailable, report that specific
blocker. Do not restart the user's browser, copy its profile, change enterprise
policy, or substitute an API response for the requested web review.
