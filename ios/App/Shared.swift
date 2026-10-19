import Foundation

/// What the app and the home-screen widget share: the birth date, the look, and the journal summary the
/// page sends after every change. Kept in the app group so the widget can read it without opening the app.
enum Shared {
    static let group = "group.cn.growthhandbook.app"
    static var defaults: UserDefaults { UserDefaults(suiteName: group) ?? .standard }

    static var birth: String {
        get { defaults.string(forKey: "birth") ?? "" }
        set { defaults.set(newValue, forKey: "birth") }
    }
    static var look: String {
        get { defaults.string(forKey: "ip") ?? "mint" }
        set { defaults.set(newValue, forKey: "ip") }
    }
    static var journalJSON: String {
        get { defaults.string(forKey: "journal") ?? "{}" }
        set { defaults.set(newValue, forKey: "journal") }
    }

    struct Journal: Decodable {
        var on: Bool?
        var last: String?
        var sleep: String?
        var today: String?
        var lastT: Double?
        var runK: String?
        var runStart: Double?
        var runPz: Double?
        var runPaused: Double?
        var side: String?
    }

    static var journal: Journal? {
        guard let d = journalJSON.data(using: .utf8) else { return nil }
        return try? JSONDecoder().decode(Journal.self, from: d)
    }

    /// Same rule as the handbook: the same day of the month, or the last day of a shorter month.
    static func addMonths(_ b: Date, _ m: Int) -> Date {
        let cal = Calendar(identifier: .gregorian)
        var c = cal.dateComponents([.year, .month, .day], from: b)
        let day = c.day ?? 1
        c.day = 1
        c.month = (c.month ?? 1) + m
        let first = cal.date(from: c) ?? b
        let range = cal.range(of: .day, in: .month, for: first) ?? 1..<29
        c.day = min(day, range.count)
        return cal.date(from: c) ?? b
    }

    /// "今天满 4 个月 8 天" and the growth stage (1–4) the mascot pictures use.
    static func age(now: Date = Date()) -> (text: String, months: Int)? {
        let p = birth.split(separator: "-").compactMap { Int($0) }
        guard p.count == 3 else { return nil }
        let cal = Calendar(identifier: .gregorian)
        guard let b = cal.date(from: DateComponents(year: p[0], month: p[1], day: p[2])) else { return nil }
        let today = cal.startOfDay(for: now)
        let yc = cal.dateComponents([.year, .month], from: b, to: today)
        var m = (yc.year ?? 0) * 12 + (yc.month ?? 0)
        if addMonths(b, m) > today { m -= 1 }
        if m < 0 { return nil }
        let d = cal.dateComponents([.day], from: addMonths(b, m), to: today).day ?? 0
        return ("今天满 \(m) 个月" + (d > 0 ? " \(d) 天" : ""), m)
    }

    static func stage(_ m: Int) -> Int { m < 12 ? 1 : m < 24 ? 2 : m <= 36 ? 3 : 4 }
}
