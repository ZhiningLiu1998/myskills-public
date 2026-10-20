import AppKit
import ApplicationServices
import Foundation

func attribute(_ element: AXUIElement, _ name: String) -> CFTypeRef? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success else { return nil }
    return value
}
func string(_ element: AXUIElement, _ name: String) -> String {
    attribute(element, name) as? String ?? ""
}
func children(_ element: AXUIElement) -> [AXUIElement] {
    attribute(element, kAXChildrenAttribute) as? [AXUIElement] ?? []
}
func search(_ element: AXUIElement, _ predicate: (AXUIElement) -> Bool) -> AXUIElement? {
    if predicate(element) { return element }
    for child in children(element) {
        if let match = search(child, predicate) { return match }
    }
    return nil
}
func failure(_ message: String) -> NSError {
    NSError(domain: "chrome-ax", code: 1, userInfo: [NSLocalizedDescriptionKey: message])
}
func output(_ value: Any) throws {
    let data = try JSONSerialization.data(withJSONObject: value, options: [.prettyPrinted, .sortedKeys])
    print(String(decoding: data, as: UTF8.self))
}

func run() throws {
    let args = Array(CommandLine.arguments.dropFirst())
    let usage = """
    chrome-ax PID windows
    chrome-ax PID WINDOW-TITLE dump|text
    chrome-ax PID WINDOW-TITLE set LABEL UTF8-FILE
    chrome-ax PID WINDOW-TITLE click LABEL
    chrome-ax PID WINDOW-TITLE paste-image LABEL PNG [PNG...]
    """
    if args == ["--help"] { print(usage); return }
    guard args.count >= 2, let pid = Int32(args[0]) else { throw failure(usage) }
    guard let chrome = NSRunningApplication(processIdentifier: pid),
          chrome.bundleIdentifier == "com.google.Chrome" else {
        throw failure("PID is not a running Google Chrome instance.")
    }
    guard AXIsProcessTrusted() else {
        throw failure("macOS Accessibility access is unavailable for this runner.")
    }
    let app = AXUIElementCreateApplication(pid)
    AXUIElementSetMessagingTimeout(app, 5)
    AXUIElementSetAttributeValue(app, "AXEnhancedUserInterface" as CFString, kCFBooleanTrue)
    let windows = attribute(app, kAXWindowsAttribute) as? [AXUIElement] ?? []
    if args[1] == "windows" {
        try output(windows.map { ["title": string($0, kAXTitleAttribute)] })
        return
    }
    guard args.count >= 3 else { throw failure(usage) }
    let matches = windows.filter { string($0, kAXTitleAttribute) == args[1] }
    guard matches.count == 1, let window = matches.first else {
        throw failure("Expected one window with this exact title; found \(matches.count). Refresh windows.")
    }
    let action = args[2]
    let target = args.count > 3 ? args[3] : ""
    func labeled(_ element: AXUIElement) -> Bool {
        [kAXTitleAttribute, kAXDescriptionAttribute, kAXValueAttribute].contains {
            string(element, $0) == target
        }
    }
    let web = search(window, { string($0, kAXRoleAttribute) == "AXWebArea" }) ?? window
    if action == "dump" || action == "text" {
        var records: [[String: String]] = []
        func collect(_ element: AXUIElement) {
            let role = string(element, kAXRoleAttribute)
            let title = string(element, kAXTitleAttribute)
            let description = string(element, kAXDescriptionAttribute)
            let value = string(element, kAXValueAttribute)
            if (action == "text" && role == "AXStaticText") ||
                (action == "dump" && (!title.isEmpty || !description.isEmpty || !value.isEmpty)) {
                records.append(["role": role, "title": title, "description": description, "value": value])
            }
            for child in children(element) { collect(child) }
        }
        collect(web)
        try output(records)
        return
    }
    guard ["set", "click", "paste-image"].contains(action), !target.isEmpty else {
        throw failure(usage)
    }
    let roles = action == "click"
        ? ["AXButton", "AXPopUpButton", "AXMenuItem", "AXLink", "AXCheckBox"]
        : ["AXTextArea", "AXTextField", "AXComboBox"]
    guard let control = search(web, { labeled($0) && roles.contains(string($0, kAXRoleAttribute)) }) else {
        throw failure("Control not found: \(target). Refresh dump and use its current label.")
    }
    if action == "click" {
        let result = AXUIElementPerformAction(control, kAXPressAction as CFString)
        guard result == .success else { throw failure("Press failed: \(result.rawValue)") }
        print("Pressed \(target)")
    } else if action == "set" {
        guard args.count == 5 else { throw failure(usage) }
        let content = try String(contentsOfFile: args[4], encoding: .utf8)
        let result = AXUIElementSetAttributeValue(control, kAXValueAttribute as CFString, content as CFString)
        guard result == .success else { throw failure("Set value failed: \(result.rawValue)") }
        print("Entered \(content.count) characters")
    } else {
        guard args.count >= 5 else { throw failure(usage) }
        let images = try args.dropFirst(4).map { path -> Data in
            let data = try Data(contentsOf: URL(fileURLWithPath: path))
            guard data.starts(with: [137, 80, 78, 71, 13, 10, 26, 10]) else {
                throw failure("Expected a PNG: \(path)")
            }
            return data
        }
        let foreground = NSWorkspace.shared.frontmostApplication
        defer {
            if foreground?.processIdentifier != pid,
               NSWorkspace.shared.frontmostApplication?.processIdentifier == pid {
                foreground?.activate(options: [])
            }
        }
        chrome.activate(options: [])
        Thread.sleep(forTimeInterval: 0.5)
        AXUIElementSetAttributeValue(window, kAXMainAttribute as CFString, kCFBooleanTrue)
        let focused = AXUIElementSetAttributeValue(control, kAXFocusedAttribute as CFString, kCFBooleanTrue)
        guard focused == .success else { throw failure("Could not focus the composer.") }
        let pasteboard = NSPasteboard.general
        let saved = (pasteboard.pasteboardItems ?? []).map { item -> NSPasteboardItem in
            let copy = NSPasteboardItem()
            for type in item.types {
                if let data = item.data(forType: type) { copy.setData(data, forType: type) }
            }
            return copy
        }
        var change: Int?
        defer {
            if let change, pasteboard.changeCount == change {
                pasteboard.clearContents()
                pasteboard.writeObjects(saved)
            }
        }
        for image in images {
            if let change, pasteboard.changeCount != change {
                throw failure("Clipboard changed during upload; inspect the attachments before retrying.")
            }
            pasteboard.clearContents()
            pasteboard.setData(image, forType: .png)
            change = pasteboard.changeCount
            for pressed in [true, false] {
                guard let event = CGEvent(keyboardEventSource: nil, virtualKey: 9, keyDown: pressed) else {
                    throw failure("Could not create the paste key event.")
                }
                event.flags = .maskCommand
                event.postToPid(pid)
            }
            Thread.sleep(forTimeInterval: 3)
        }
        print("Pasted \(images.count) image(s); inspect attachment previews before sending.")
    }
}

do {
    try run()
} catch {
    FileHandle.standardError.write(Data((error.localizedDescription + "\n").utf8))
    exit(1)
}
