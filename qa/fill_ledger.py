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

# ---------- requirements ----------
REQ = {
 "BR-01": ("待决策", "docs/design/brand/naming-options-0.7.png（三方案触点对照，未改名）", "", "BR"),
 "BR-02": ("已实现待测", "docs/design/brand/naming-options-0.7.png；proto/focus.js t-brand", "T050", ""),
 "BR-03": ("待决策", "未开始：等待名称批准；包名与 hb: 存储键不改", "", "BR"),
 "GX-01": ("已实现待测", "proto/nav.js bulkPast/t-bulk；proto/app.js HB_BULK/recT；kind c/a/v/k 分开存储于 hb:rec", "A4", ""),
 "GX-02": ("已实现待测", "proto/nav.js t-bulk（data-bk=v 默认不勾）；proto/nav.js .qb-mall 只含 c/a；proto/app3.js quickBody", "T009", ""),
 "GX-03": ("已实现待测", "proto/focus.js didify/pick（提示“不代表能力已达到”）；进度统计按 c/a/h 分开", "T054", ""),
 "GX-04": ("已实现待测", "proto/journal.js save()/saveMark()：写入后读回比对，失败显示“未能保存 · 点此重试”", "", ""),
 "GX-05": ("已实现待测", "proto/journal.js startTimer/stopTimer（RUN 持久化于 hb:jr:run、结束幂等）、visibilitychange 重新读取、时间早于开始时提示", "T055", ""),
 "GX-06": ("未核验", "proto/journal.js visitOpen/mergeOut；PRIVACY.md —— 本版未改，需人工对照隐私说明", "", ""),
 "NV-01": ("已实现待测", "proto/focus.js HB_TODAY_WIRE（t-pick/t-go/t-more/t-brand）", "T001", ""),
 "NV-02": ("已实现待测", "proto/nav.js tabsIP；proto/app3.js tabHold；四个 IP 标签保留", "T050", ""),
 "NV-03": ("已实现待测", "proto/focus.js monthStat/chainWin；proto/app.js show（单一 cur 视图）", "T012", ""),
 "NV-04": ("已实现待测", "proto/focus.js chainWin（±2 + 现在锚点）+ ch-all → app.js monthPicker（37 格分阶段）", "T011", ""),
 "NV-05": ("已实现待测", "proto/focus.js mapJump；返回位置由 app.js pos[] 恢复", "T015", ""),
 "NV-06": ("已实现待测", "proto/polish.css 0.7 段（月份页面包屑去掉月龄、mstat 放入标题下）；插画未裁切", "T010", ""),
 "NV-07": ("已实现待测", "proto/focus.js tags/stepOpen/watchActs（ac-bar 记为做过+收藏，带撤销）", "T020", ""),
 "NV-08": ("已实现待测", "proto/app.js show（pos/stack 返回恢复）；搜索 hb:q 恢复", "T034", ""),
 "NV-09": ("已实现待测", "proto/app.js kindOf（新增 观察 c 分类）+ sessionStorage hb:q", "T048", ""),
 "UI-01": ("已实现待测", "proto/polish.css token 段（--r-*/--sp*/--hit）；MainActivity.textZoom 跟随系统字体", "T037", ""),
 "UI-02": ("已实现待测", "proto/polish.css（热区 ≥48）", "T041", ""),
 "UI-03": ("已实现待测", "撤回了会裁头的封面限高；插画容器保持原比例", "", ""),
 "UI-04": ("开发中", "已有：按压、禁用、空状态（收藏空态入口）、保存失败态；未系统化：loading/offline 统一组件", "", ""),
 "UI-05": ("已实现待测", "proto/focus.js recSum（总进度、三类计数、最近记录 hb:recT、贴纸后置）", "T031", ""),
 "UI-06": ("已实现待测", "proto/polish.css --brand 浅/深；两形象", "T050", ""),
 "UX-01": ("未核验", "proto/polish.css 动效时长；减少动画已有 prefers-reduced-motion 分支，未在设备上验证", "", ""),
 "UX-02": ("已实现待测", "proto/journal.js jr-fab/jr-week/开始大圆按钮；夜间模式 jr-nt 保持独立", "", ""),
 "UX-03": ("已实现待测", "MainActivity.onBackPressed → WebView 历史；弹层 pushState 先关闭", "T057", ""),
 "UX-04": ("待决策", "iOS 暂停（用户 2026-10-19 指示）", "", ""),
 "UX-05": ("开发中", "字体：跟随系统已实现；TalkBack 未测", "T037", ""),
 "UX-06": ("开发中", "proto/perf.js、app.js sigOf、HB_LATER；本地 Chromium 4 倍降速测量 + 模拟器 rAF 间隔，均非真机", "PERF", ""),
 "UX-07": ("未核验", "未做网页版与 App 同任务对照", "", ""),
 "UX-08": ("已实现待测", "全部本地离线；后台恢复 visibilitychange", "T002", ""),
 "UX-09": ("未核验", "安全区/输入法/分享导出需真机", "", ""),
 "CT-01": ("已实现待测", "活动安全提示位于步骤之前（自动检查满 6 个月 4 个活动）；内容未改写", "T020", ""),
 "CT-02": ("已实现待测", "proto/app.js ageOf/getBirth 单一算法；未填生日显示中性状态（A5）", "", ""),
 "QA-01": ("开发中", "47 屏路由已映射，模拟器逐屏截图；人工逐屏复核未完成", "", ""),
 "QA-02": ("开发中", "Android 模拟器已执行；真机未执行；iOS 暂停", "", ""),
 "QA-03": ("已实现待测", "发布说明逐条对应代码；本台账", "", ""),
 "QA-04": ("已实现待测", "已读 frontend-design（/mnt/skills/public/frontend-design）；ui-ux-pro-max / effective-html / mobile-native 未安装", "", ""),
}
rows, fields = rd(D + "04_REQUIREMENTS.csv")
for r in rows:
    x = REQ.get(r["Req_ID"])
    if not x: continue
    st, path, tid, _ = x; t = R.get(tid) if tid else None
    r["Status"] = st; r["Current_Code_Path"] = path; r["Commit_Hash"] = SHA
    r["Baseline_Evidence"] = "代码核对（%s）" % SHA[:7]
    if tid == "T050":
        n = len([1 for a in ("round-light", "round-dark", "eye-light", "eye-dark") for b in ("today", "journal", "home", "rec") if os.path.isfile(SHOT("IP-%s-%s" % (a, b)))])
        r["Android_Result"] = "模拟器截图 %d/16，待人工核对" % n; r["Evidence_Paths"] = SHOT("IP-eye-dark-today") if n else ""
    elif t:
        r["Android_Result"] = ("模拟器通过" if t["pass"] else "模拟器失败") + "（" + t["id"] + "）"
        r["Evidence_Paths"] = os.path.join(RUN, "results.json")
    else:
        r["Android_Result"] = "未执行"
    r["iOS_Result"] = IOS
    r["Blocker_Or_Decision"] = "需用户批准名称" if r["Req_ID"].startswith("BR-0") and st == "待决策" else ("需真机" if st in ("已实现待测", "开发中", "未核验") else r["Blocker_Or_Decision"])
    r["Next_Action"] = "真机复测并人工核对截图" if st == "已实现待测" else ("等待决策" if st == "待决策" else "继续实现/测量")
rw(D + "04_REQUIREMENTS.csv", rows, fields)
print("requirements updated")
