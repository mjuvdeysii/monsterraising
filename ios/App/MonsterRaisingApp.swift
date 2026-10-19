import SwiftUI
import UIKit
import UserNotifications

@main
struct MonsterRaisingApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var delegate

    var body: some Scene {
        WindowGroup {
            HandbookView()
                .ignoresSafeArea(.container, edges: .bottom)
                .onOpenURL { url in Router.shared.open(url) }
        }
    }
}

/// Tapping a reminder opens the right page: a month's vaccines and check-ups, or the journal.
final class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        UNUserNotificationCenter.current().delegate = self
        return true
    }

    func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification, withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([.banner, .sound])
    }

    func userNotificationCenter(_ center: UNUserNotificationCenter, didReceive response: UNNotificationResponse, withCompletionHandler completionHandler: @escaping () -> Void) {
        let info = response.notification.request.content.userInfo
        if let page = info["page"] as? String, page == "journal" {
            Router.shared.go(hash: "journal")
        } else if let m = info["m"] as? Int, m >= 0 {
            Router.shared.go(hash: "m\(m)-care")
        }
        completionHandler()
    }
}

/// Deep links from the widget (monsterraising://log/nurse, monsterraising://night) and from notifications.
final class Router {
    static let shared = Router()
    weak var bridge: Bridge?
    var pendingHash: String?
    var pendingLog: String = ""

    func open(_ url: URL) {
        guard url.scheme == "monsterraising" else { return }
        let host = url.host ?? ""
        if host == "log", let k = url.pathComponents.dropFirst().first, k.range(of: "^[a-z]+$", options: .regularExpression) != nil {
            log(k)
        } else if host == "night" {
            log("night")
        } else {
            go(hash: "today")
        }
    }

    func log(_ k: String) {
        if let b = bridge, b.loaded { b.run("window.HB_LOG&&HB_LOG('\(k)')") } else { pendingLog = k }
    }

    func go(hash: String) {
        if let b = bridge, b.loaded { b.run("location.hash='\(hash)'") } else { pendingHash = hash }
    }
}
