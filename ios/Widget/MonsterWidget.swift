import WidgetKit
import SwiftUI

/// Home-screen widget: the baby's age, a live clock since the last feed (or of the running timer), and four
/// quick buttons that open the journal on the right record. Same pictures as the Android widget.
struct Entry: TimelineEntry {
    let date: Date
}

struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> Entry { Entry(date: Date()) }
    func getSnapshot(in context: Context, completion: @escaping (Entry) -> Void) { completion(Entry(date: Date())) }
    func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> Void) {
        // the clocks count by themselves; the timeline only needs to roll over for the age and the night picture
        let now = Date()
        let entries = (0..<12).map { Entry(date: now.addingTimeInterval(Double($0) * 3600)) }
        completion(Timeline(entries: entries, policy: .atEnd))
    }
}

struct MonsterWidgetView: View {
    @Environment(\.widgetFamily) var family
    let entry: Entry

    var look: String { Shared.look }
    var age: (text: String, months: Int)? { Shared.age(now: entry.date) }
    var journal: Shared.Journal? { Shared.journal }

    func picture() -> String {
        let st = Shared.stage(age?.months ?? 0), hr = Calendar.current.component(.hour, from: entry.date)
        let night = hr >= 21 || hr < 6
        return (look == "eye" ? (night ? "e_z" : "e_s") : (night ? "mascot_z" : "mascot_s")) + "\(st)"
    }

    @ViewBuilder func clock() -> some View {
        if let j = journal, j.on == true {
            if let k = j.runK, !k.isEmpty, let start = j.runStart, start > 0 {
                let label = k == "sleep" ? "已睡" : "亲喂" + (j.side == "l" ? "·左" : j.side == "r" ? "·右" : "")
                if let p = j.runPaused, p > 0 {
                    Text("\(label) 暂停中").font(.caption).foregroundColor(.secondary)
                } else {
                    let base = Date(timeIntervalSince1970: (start + (j.runPz ?? 0)) / 1000)
                    HStack(spacing: 4) { Text(label); Text(base, style: .timer).monospacedDigit() }.font(.caption.weight(.semibold))
                }
            } else if let t = j.lastT, t > 0 {
                HStack(spacing: 4) { Text("距上次喂奶"); Text(Date(timeIntervalSince1970: t / 1000), style: .timer).monospacedDigit() }.font(.caption)
            } else {
                Text(j.today ?? "").font(.caption).foregroundColor(.secondary)
            }
        }
    }

    func button(_ k: String, _ name: String) -> some View {
        Link(destination: URL(string: "monsterraising://log/\(k)")!) {
            VStack(spacing: 0) {
                Image((look == "eye" ? "ew_" : "w_") + k).resizable().scaledToFit().frame(height: 30)
                Text(name).font(.caption2).foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity, minHeight: 50)
            .background(RoundedRectangle(cornerRadius: 14).fill(Color("Tile" + k.capitalized)))
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 10) {
                Image(picture()).resizable().scaledToFit().frame(width: 44, height: 44)
                VStack(alignment: .leading, spacing: 2) {
                    Text(age?.text ?? "养小怪兽").font(.headline).lineLimit(1)
                    clock()
                }
                Spacer(minLength: 0)
                if family != .systemSmall, journal?.on == true {
                    Link(destination: URL(string: "monsterraising://night")!) {
                        Image(look == "eye" ? "ew_sleep" : "w_sleep").resizable().scaledToFit().frame(width: 30, height: 30)
                    }
                }
            }
            if family != .systemSmall, journal?.on == true {
                HStack(spacing: 6) {
                    button("nurse", journal?.runK == "nurse" ? "喂完" : "亲喂")
                    button("bottle", "瓶喂")
                    button("sleep", journal?.runK == "sleep" ? "醒了" : "睡眠")
                    button("diaper", "尿布")
                }
            }
        }
        .padding(2)
        .widgetURL(URL(string: "monsterraising://today"))
        .modifier(WidgetBackground())
    }
}

struct WidgetBackground: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 17.0, *) {
            content.containerBackground(Color("WidgetBackground"), for: .widget)
        } else {
            content.padding().background(Color("WidgetBackground"))
        }
    }
}

@main
struct MonsterWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "MonsterWidget", provider: Provider()) { entry in
            MonsterWidgetView(entry: entry)
        }
        .configurationDisplayName("养小怪兽")
        .description("宝宝今天满几个月，距上次喂奶多久，以及快捷记录按钮。")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
