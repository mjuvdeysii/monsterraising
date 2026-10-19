#!/usr/bin/env python3
"""Writes the results of one Android emulator QA run into the v2.8 ledgers.
Usage: python3 qa/fill_ledger.py <run_dir: qa/evidence/<version>/android> <version> <commit>
Emulator results are written as 「模拟器通过 / 模拟器失败」, never as 「通过」: the release gate keeps waiting for a phone.
iOS is paused, so every iOS column says so."""
import csv, json, os, sys, datetime
RUN, VER, SHA = sys.argv[1], sys.argv[2], sys.argv[3]
D = "docs/design/raising-monster-v2.8/"
res = json.load(open(os.path.join(RUN, "results.json"), encoding="utf-8"))
dev = res["device"]; DEV = "Android 模拟器 %s / Android %s (API %s, %s), %s；非真机" % (dev["model"], dev["android"], dev["sdk"], dev["abi"], dev.get("webview", "").replace("Current WebView package (name, version): ", "WebView "))
TODAY = datetime.date.today().isoformat()
R = {}
for r in res["results"]: R.setdefault(r["id"], r)
SHOT = lambda n: os.path.join(RUN, "shots", n + ".png")
IOS = "未执行（iOS 暂停，用户 2026-10-19 指示）"


def rw(path, rows, fields):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)


def rd(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f); return list(r), r.fieldnames


# ---------- 47 screens ----------
ROUTE = {
 "A1": "#today · app.js buildToday + focus.js HB_TODAY_WIRE（t-brand / t-pick / t-go / t-more）", "A2": "#today · nav.js t-mon2 + t-care2", "A3": "#today · app.js ticks() + nav.js tp-rings",
 "A4": "#today · nav.js t-bulk（HB_BULK，仅 c/a）", "A5": "#today · app.js buildToday 无出生日期分支", "A6": "首次启动 · app2.js 使用前须知",
 "B1": "#journal · journal.js render/dayPane + jr-week + jr-fab", "B2": "#journal · journal.js startSheet(nurse)", "B3": "#journal · journal.js jr-run-nurse（startTimer/pauseTimer/stopTimer）",
 "B4": "#journal · journal.js jr-run-sleep", "B5": "#journal · journal.js 节奏/每日事项/jr-tl（jr-saved）", "B6": "#journal · journal.js retroPick/open", "B7": "#journal · journal.js sheetForm(bottle)",
 "B8": "#journal · journal.js tap(diaper) + snack 撤销", "B9": "#journal · journal.js weekPane", "B10": "#journal · journal.js monthPane/compareCard", "B11": "#journal · journal.js growth pane（WHO 曲线）",
 "B12": "#journal · journal.js foodPane", "B13": "#journal · journal.js nightOpen/drawNight（jr-nt）", "B14": "#journal · journal.js visitOpen", "B15": "#journal · journal.js intro()",
 "C1": "#home · nav.js monthGrid（mg2）+ app.js monthPicker", "C2": "#home(map) · app.js HB_HOME_MAP + focus.js mapJump", "C3": "#home · nav.js 主题书架", "C4": "#home · nav.js 说明书架",
 "C5": "全书结构 · nav.js openMap", "C6": "#m6 · 月份页头 mh + focus.js monthStat + chainWin", "C7": "#m6-A…F · 六个领域与 CDC 观察", "C8": "#m6-acts · 活动 article.ac + focus.js tags/ac-bar/stepOpen",
 "C9": "#m6-care · 接种与儿保", "C10": "#m6 · journal.js monthCard（jr-mcard）", "C11": "#health 专题页", "C12": "#acts 活动库", "C13": "#search · app.js runQ/drawQ（筛选恢复 hb:q）",
 "D1": "#rec · focus.js recSum + app.js buildRec（贴纸在后）", "D2": "补看面板 · app3.js quickOpen/quickBody", "D3": "#rec 收藏 · app.js r-fav", "D4": "#rec 设置与帮助 · nav.js accordion",
 "D5": "#rec 设置展开 · app.js r-set（字号含跟随手机）", "D6": "#rec 形象切换 · ip.js r-ip", "D7": "版本说明 · app.js showNew（v/notes.json）",
 "E1": "#today · 深色主题", "E2": "#journal · 深色主题", "E3": "#m6 · 深色主题", "E4": "#today · 独眼款", "E5": "#home · 独眼款", "E6": "#rec · 独眼款贴纸",
}
rows, fields = rd(D + "reference_v2.7/04_47_Screen_Coverage.csv")
for r in rows:
    sid = r["Screen_ID"]; shot = SHOT(sid)
    r["2.6.52_状态依据"] = "代码核对（%s）" % SHA[:7]
    r["当前路由/组件（Claude填）"] = ROUTE.get(sid, "")
    r["Android验证"] = "模拟器截图" if os.path.isfile(shot) else "模拟器未出图"
    r["iOS验证"] = IOS
    r["实际证据路径"] = shot if os.path.isfile(shot) else ""
    r["最终状态"] = "未核验"
rw(D + "reference_v2.7/04_47_Screen_Coverage.csv", rows, fields)

# ---------- QA matrix ----------
MAP = {"T001": "T001", "T002": "T002", "T003": "T003", "T004": "T004", "T005": "T005", "T009": "T009", "T010": "T010", "T011": "T011", "T012": "T012", "T013": "T013",
       "T014": "T014", "T015": "T015", "T017": "T017", "T020": "T020", "T031": "T031", "T034": "T034", "T037": "T037", "T041": "T041", "T048": "T048", "T049": "T037",
       "T054": "T054", "T055": "T055", "T057": "T057", "T042": "PERF"}
SNAP = {"T001": "T001", "T002": "T002", "T004": "T004", "T010": "T010", "T012": "T012", "T014": "T014", "T031": "T031", "T048": "T048", "T054": "T054", "T055": "T055-after", "T037": "FONT-today", "T049": "FONT-m6", "T009": "A4-after"}
rows, fields = rd(D + "05_QA_ANDROID_IOS.csv")
for r in rows:
    if r["Platform"] == "iOS":
        r["Actual_Result"] = IOS; continue
    if r["Platform"] != "Android": continue
    tid = r["Test_ID"]; k = MAP.get(tid); x = R.get(k) if k else None
    if tid == "T050":
        shots = [SHOT("IP-%s-%s" % (a, b)) for a in ("round-light", "round-dark", "eye-light", "eye-dark") for b in ("today", "journal", "home", "rec")]
        ok = [s for s in shots if os.path.isfile(s)]
        x = {"pass": len(ok) == 16, "detail": "两套形象 × 浅/深 × 四个标签共 %d/16 张截图（需人工逐张核对可读性）" % len(ok)}; ev = ";".join(ok[:4])
    else:
        ev = SHOT(SNAP[tid]) if tid in SNAP and os.path.isfile(SHOT(SNAP[tid])) else ""
    if not x:
        if r["Actual_Result"] in ("", "未执行"): r["Actual_Result"] = "未执行（需真机或人工）"
        continue
    r["Actual_Result"] = ("模拟器通过：" if x["pass"] else "模拟器失败：") + x["detail"]
    r["Device_And_OS"] = DEV; r["Build_Hash"] = SHA; r["Evidence_Path"] = ev or os.path.join(RUN, "results.json")
    r["Tester"] = "Claude（自动化，qa/android_qa.py）"; r["Date"] = TODAY
    if not x["pass"]: r["Issue_ID"] = "QA-%s-%s" % (VER, tid)
rw(D + "05_QA_ANDROID_IOS.csv", rows, fields)
print("ledgers updated from", len(res["results"]), "results")
