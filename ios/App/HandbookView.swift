import SwiftUI
import UIKit
import WebKit
import UniformTypeIdentifiers
import UserNotifications
import WidgetKit

struct HandbookView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> HandbookController { HandbookController() }
    func updateUIViewController(_ vc: HandbookController, context: Context) {}
}

/// The handbook pages run offline from the app bundle, the same files the Android app ships.
final class HandbookController: UIViewController, WKNavigationDelegate, UIDocumentPickerDelegate {
    var web: WKWebView!
    var bridge: Bridge!

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor(red: 0.988, green: 0.976, blue: 0.957, alpha: 1)
        bridge = Bridge(controller: self)
        let cfg = WKWebViewConfiguration()
        cfg.userContentController.addUserScript(WKUserScript(source: bridge.shim(), injectionTime: .atDocumentStart, forMainFrameOnly: true))
        cfg.userContentController.add(bridge, name: "hb")
        cfg.websiteDataStore = .default()
        web = WKWebView(frame: view.bounds, configuration: cfg)
        web.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        web.navigationDelegate = self
        web.allowsBackForwardNavigationGestures = true
        web.scrollView.contentInsetAdjustmentBehavior = .automatic
        web.isOpaque = false
        web.backgroundColor = view.backgroundColor
        if #available(iOS 14.0, *) { web.pageZoom = CGFloat(UserDefaults.standard.integer(forKey: "zoom").clamped(100, 130)) / 100 }
        view.addSubview(web)
        Router.shared.bridge = bridge
        if let site = Bundle.main.url(forResource: "site", withExtension: nil) {
            web.loadFileURL(site.appendingPathComponent("index.html"), allowingReadAccessTo: site)
        }
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        bridge.loaded = true
        if let h = Router.shared.pendingHash { Router.shared.pendingHash = nil; bridge.run("location.hash='\(h)'") }
        // a widget tap that arrived before the page was ready
        let lg = Router.shared.pendingLog
        if !lg.isEmpty { Router.shared.pendingLog = ""; DispatchQueue.main.asyncAfter(deadline: .now() + 0.7) { self.bridge.run("window.HB_LOG&&HB_LOG('\(lg)')") } }
    }

    // links that leave the handbook open in Safari
    func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if let u = action.request.url, let s = u.scheme, s == "http" || s == "https" {
            UIApplication.shared.open(u); decisionHandler(.cancel); return
        }
        decisionHandler(.allow)
    }

    // MARK: files
    func present(_ vc: UIViewController) {
        if let pop = vc.popoverPresentationController { pop.sourceView = view; pop.sourceRect = CGRect(x: view.bounds.midX, y: view.bounds.maxY - 80, width: 1, height: 1) }
        present(vc, animated: true)
    }

    func pickFile() {
        let picker = UIDocumentPickerViewController(forOpeningContentTypes: [.json, .plainText, .data], asCopy: true)
        picker.delegate = self
        present(picker)
    }

    func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
        guard let u = urls.first, let text = try? String(contentsOf: u, encoding: .utf8) else { bridge.run("HB_FILE_DONE&&HB_FILE_DONE('open',false)"); return }
        bridge.run("HB_IMPORT(\(Bridge.jsString(text)))")
    }

    func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) { bridge.run("HB_FILE_DONE&&HB_FILE_DONE('open',null)") }
}

/// window.HBApp for the pages: the same method names as the Android bridge. Calls that return a value are
/// answered from values injected at start; the rest are posted to native code.
final class Bridge: NSObject, WKScriptMessageHandler {
    weak var controller: HandbookController?
    var loaded = false

    init(controller: HandbookController) { self.controller = controller }

    static func jsString(_ s: String) -> String {
        let d = (try? JSONSerialization.data(withJSONObject: [s])) ?? Data("[\"\"]".utf8)
        let a = String(data: d, encoding: .utf8) ?? "[\"\"]"
        return String(a.dropFirst().dropLast())
    }

    func run(_ js: String) { DispatchQueue.main.async { self.controller?.web.evaluateJavaScript(js, completionHandler: nil) } }

    func shim() -> String {
        let info = Bundle.main.infoDictionary ?? [:]
        let short = info["CFBundleShortVersionString"] as? String ?? "2.2.0"
        let build = Int(info["CFBundleVersion"] as? String ?? "1") ?? 1
        let parts = short.split(separator: ".")
        let name = parts.count >= 2 ? "\(parts[0]).\(parts[1]).\(build)" : short
        let zoom = UserDefaults.standard.integer(forKey: "zoom").clamped(100, 130)
        let pending = Bridge.jsString(Router.shared.pendingLog)
        Router.shared.pendingLog = ""
        return """
        (function(){
          function post(a,o){ try{ o=o||{}; o.a=a; window.webkit.messageHandlers.hb.postMessage(o); }catch(e){} }
          var zoom=\(zoom), pend=\(pending);
          window.HBApp={
            platform:function(){return "ios";},
            version:function(){return \(build);},
            versionName:function(){return "\(name)";},
            getTextZoom:function(){return zoom;},
            setTextZoom:function(z){zoom=+z||100;post("zoom",{z:zoom});},
            haptic:function(){post("haptic");},
            share:function(t,x){post("share",{t:String(t||""),x:String(x||"")});},
            saveFile:function(n,t){post("save",{n:String(n||"file.txt"),t:String(t||"")});},
            shareFile:function(n,t){post("save",{n:String(n||"file.txt"),t:String(t||"")});},
            openFile:function(){post("open");},
            openUrl:function(u){post("url",{u:String(u||"")});},
            setDark:function(d){post("dark",{d:!!d});},
            setBirth:function(b){post("birth",{b:String(b||"")});},
            setName:function(n){},
            setReminders:function(j){post("care",{j:String(j||"[]")});},
            setJournalReminders:function(j){post("jrem",{j:String(j||"[]")});},
            setJournal:function(j){post("journal",{j:String(j||"{}")});},
            setIp:function(i,c){post("ip",{i:String(i||"mint"),c:!!c});},
            pendingLog:function(){var p=pend;pend="";return p;}
          };
        })();
        """
    }

    func userContentController(_ uc: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let o = message.body as? [String: Any], let a = o["a"] as? String, let vc = controller else { return }
        switch a {
        case "haptic":
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
        case "share":
            let text = (o["x"] as? String) ?? ""
            vc.present(UIActivityViewController(activityItems: [text], applicationActivities: nil))
        case "save":
            let name = ((o["n"] as? String) ?? "file.txt").replacingOccurrences(of: "/", with: "-")
            let url = FileManager.default.temporaryDirectory.appendingPathComponent(name)
            do { try ((o["t"] as? String) ?? "").write(to: url, atomically: true, encoding: .utf8) } catch { run("HB_FILE_DONE&&HB_FILE_DONE('save',false)"); return }
            let share = UIActivityViewController(activityItems: [url], applicationActivities: nil)
            share.completionWithItemsHandler = { [weak self] _, done, _, err in self?.run("HB_FILE_DONE&&HB_FILE_DONE('save',\(done && err == nil ? "true" : "null"))") }
            vc.present(share)
        case "open":
            vc.pickFile()
        case "url":
            if let s = o["u"] as? String, let u = URL(string: s) { UIApplication.shared.open(u) }
        case "dark":
            vc.overrideUserInterfaceStyle = (o["d"] as? Bool ?? false) ? .dark : .light
        case "zoom":
            let z = (o["z"] as? Int ?? 100).clamped(100, 130)
            UserDefaults.standard.set(z, forKey: "zoom")
            if #available(iOS 14.0, *) { vc.web.pageZoom = CGFloat(z) / 100 }
        case "birth":
            Shared.birth = (o["b"] as? String) ?? ""
            WidgetCenter.shared.reloadAllTimelines()
        case "journal":
            Shared.journalJSON = (o["j"] as? String) ?? "{}"
            WidgetCenter.shared.reloadAllTimelines()
        case "care":
            Notifications.replace(prefix: "care-", json: (o["j"] as? String) ?? "[]", page: nil)
        case "jrem":
            Notifications.replace(prefix: "jr-", json: (o["j"] as? String) ?? "[]", page: "journal")
        case "ip":
            let ip = (o["i"] as? String) == "eye" ? "eye" : "mint"
            Shared.look = ip
            WidgetCenter.shared.reloadAllTimelines()
            let want: String? = ((o["c"] as? Bool) ?? false) && ip == "eye" ? "AppIconEye" : nil
            if UIApplication.shared.supportsAlternateIcons && UIApplication.shared.alternateIconName != want {
                UIApplication.shared.setAlternateIconName(want, completionHandler: nil)
            }
        default:
            break
        }
    }
}

/// Reminders the page computes (vaccines and check-ups, vitamin D, time since the last feed) become local
/// notifications. iOS keeps at most 64 pending, so only the nearest ones are scheduled.
enum Notifications {
    static func replace(prefix: String, json: String, page: String?) {
        let c = UNUserNotificationCenter.current()
        c.getPendingNotificationRequests { reqs in
            c.removePendingNotificationRequests(withIdentifiers: reqs.map { $0.identifier }.filter { $0.hasPrefix(prefix) })
            guard let d = json.data(using: .utf8), let list = (try? JSONSerialization.jsonObject(with: d)) as? [[String: Any]], !list.isEmpty else { return }
            c.requestAuthorization(options: [.alert, .sound, .badge]) { ok, _ in
                guard ok else { return }
                let now = Date().timeIntervalSince1970
                let items = list.compactMap { e -> (Double, [String: Any])? in
                    guard let t = (e["t"] as? Double) ?? (e["t"] as? Int).map(Double.init) else { return nil }
                    return t / 1000 > now ? (t / 1000, e) : nil
                }.sorted { $0.0 < $1.0 }.prefix(30)
                for (i, item) in items.enumerated() {
                    let content = UNMutableNotificationContent()
                    content.title = (item.1["title"] as? String) ?? "养小怪兽"
                    content.body = (item.1["text"] as? String) ?? ""
                    content.sound = .default
                    var info: [String: Any] = [:]
                    if let p = page { info["page"] = p }
                    if let m = item.1["m"] as? Int { info["m"] = m }
                    content.userInfo = info
                    let comps = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: Date(timeIntervalSince1970: item.0))
                    c.add(UNNotificationRequest(identifier: "\(prefix)\(i)", content: content, trigger: UNCalendarNotificationTrigger(dateMatching: comps, repeats: false)))
                }
            }
        }
    }
}

extension Int {
    func clamped(_ lo: Int, _ hi: Int) -> Int { self == 0 ? lo : Swift.min(Swift.max(self, lo), hi) }
}
