#!/usr/bin/env python3
"""Writes qa/plan.json: the 47 baseline screens (docs/design/raising-monster-v2.8/reference_v2.7/04_47_Screen_Coverage.csv
order), the two-look x light/dark matrix of the four tabs, and the path tests run by qa/runner.js."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
# Screen_ID, label, flags, hash, actions (joined by ||)
SCREENS = [
 ("A1", "今天首屏", "", "today", ""),
 ("A2", "本月要点与接种儿保", "", "today", "scrollTo(0,900)"),
 ("A3", "本月记录展开", "", "today", "document.querySelector('[data-ring=\"0\"]').click()||scrollTo(0,1700)"),
 ("A4", "首次补录", "nobulk", "today", "scrollTo(0,300)"),
 ("A5", "未填出生日期", "nobirth", "today", ""),
 ("A6", "首次须知", "first", "today", ""),
 ("B1", "手帐这一天", "", "journal", ""),
 ("B2", "亲喂开始", "", "journal", "HB_START('nurse')"),
 ("B3", "亲喂计时中", "", "journal", "HB_START('nurse')||document.querySelector('.sheet-m [data-ss=r]').click()"),
 ("B4", "睡眠计时中", "run", "journal", ""),
 ("B5", "本日节奏/事项/记录", "", "journal", "scrollTo(0,980)"),
 ("B6", "补录一条", "", "journal", "document.querySelector('[data-retro]').click()"),
 ("B7", "瓶喂表单", "", "journal", "document.querySelector('.jr-b[data-k=bottle]').click()"),
 ("B8", "尿布快记", "", "journal", "document.querySelector('.jr-b[data-k=diaper]').click()"),
 ("B9", "近7天", "", "journal", "document.querySelector('[data-pane=w]').click()"),
 ("B10", "按月龄回顾", "", "journal", "document.querySelector('[data-pane=m]').click()||scrollTo(0,520)"),
 ("B11", "生长曲线", "", "journal", "document.querySelector('[data-pane=g]').click()||scrollTo(0,300)"),
 ("B12", "辅食清单", "", "journal", "document.querySelector('[data-pane=f]').click()||scrollTo(0,300)"),
 ("B13", "夜间模式", "", "journal", "document.querySelector('[data-night]').click()"),
 ("B14", "给医生的小结", "", "journal", "document.querySelectorAll('.jacc').forEach(c=>c.classList.add('open'))||document.querySelector('[data-x=visit]').click()"),
 ("B15", "手帐未开启", "nojr", "journal", ""),
 ("C1", "月份格子", "grid", "home", ""),
 ("C2", "成长地图", "map", "home", ""),
 ("C3", "主题", "", "home", "document.querySelector('.shelf [data-s=t]').click()"),
 ("C4", "说明", "", "home", "document.querySelector('.shelf [data-s=i]').click()"),
 ("C5", "全书结构", "", "home", "HB_MAP()"),
 ("C6", "月龄页开头", "", "m6", ""),
 ("C7", "六个发展领域", "", "m6", "scrollTo(0,1500)"),
 ("C8", "本月活动", "", "m6", "var t=document.getElementById('m6-acts');t&&scrollTo(0,t.getBoundingClientRect().top+scrollY-110)"),
 ("C9", "接种与儿保", "", "m6", "var t=document.getElementById('m6-care');t&&scrollTo(0,t.getBoundingClientRect().top+scrollY-110)"),
 ("C10", "这个月的手帐", "", "m6", "var t=document.querySelector('#m6 .jr-mcard');t&&scrollTo(0,t.getBoundingClientRect().top+scrollY-200)"),
 ("C11", "每日健康与安全专题", "", "health", ""),
 ("C12", "活动库", "", "acts", ""),
 ("C13", "搜索", "", "search", "var q=document.getElementById('q');q.value='辅食';q.dispatchEvent(new Event('input'))"),
 ("D1", "进度与贴纸册", "", "rec", ""),
 ("D2", "过往月份补看", "", "rec", "HB_QUICK(3)"),
 ("D3", "收藏", "", "rec", "document.querySelector('.rp-seg [data-rp=f]').click()"),
 ("D4", "设置与帮助", "", "rec", "document.querySelector('.rp-seg [data-rp=s]').click()"),
 ("D5", "设置展开", "", "rec", "document.querySelector('.rp-seg [data-rp=s]').click()||document.querySelector('.r-set h2').click()"),
 ("D6", "形象切换", "", "rec", "document.querySelector('.rp-seg [data-rp=s]').click()||document.querySelector('.r-ip h2').click()"),
 ("D7", "版本更新记录", "", "rec", "HB_SHOWNEW()"),
 ("E1", "深色·今天", "dark", "today", ""),
 ("E2", "深色·手帐", "dark", "journal", ""),
 ("E3", "深色·月份", "dark", "m6", ""),
 ("E4", "独眼款·今天", "eye", "today", ""),
 ("E5", "独眼款·目录", "eye,grid", "home", ""),
 ("E6", "独眼款·贴纸", "eye", "rec", "scrollTo(0,900)"),
]
assert len(SCREENS) == 47

plan = []
for sid, label, flags, h, act in SCREENS:
    plan.append({"t": "frame", "id": sid, "label": label, "flags": flags, "hash": h, "act": act, "snap": sid})
# two looks x light/dark, the four tabs
for f, nm in [("", "round-light"), ("dark", "round-dark"), ("eye", "eye-light"), ("eye,dark", "eye-dark")]:
    for h in ["today", "journal", "home", "rec"]:
        plan.append({"t": "frame", "id": "T050", "label": nm + " " + h, "flags": f, "hash": h, "act": "", "snap": "IP-%s-%s" % (nm, h)})


def test(fn, flags="", h="today", snap=None, keep=False, only=None):
    s = {"t": "test", "fn": fn, "flags": flags, "hash": h}
    if snap: s["snap"] = snap
    if keep: s["keep"] = True
    if only: s["only"] = only
    plan.append(s)


test("today_focus", snap="T001")
test("pick_skip", snap="T004")
test("browsed", h="m6", snap="T010")
test("all_months", h="m6")
test("rapid", h="m6", snap="T012")
test("edges", h="m6")
test("map_jump", flags="map", h="home", snap="T014")
test("map_return", flags="map", h="home")
test("act_safety", h="m6")
test("rec_first", h="rec", snap="T031")
test("bulk", flags="nobulk", h="today", snap="A4-after")
test("did_semantics", h="m6", snap="T054")
test("search_restore", h="search", snap="T048")
test("hit", h="today")
test("perf_scroll", h="m6")
# a timer survives the process being killed, and ends once
test("timer_start", h="journal", snap="T055-before")
plan.append({"t": "native", "cmd": "kill", "wait": 60000})
test("timer_after_kill", h="journal", keep=True, snap="T055-after")
# a timer survives the app going to the background
test("bg_start", h="journal")
plan.append({"t": "native", "cmd": "background", "wait": 16000})
test("bg_back", h="today", keep=True, snap="T002")
# the system back key: first the sheet, then the page
test("back_a", h="home", only="android")
plan.append({"t": "native", "cmd": "back", "wait": 4000, "only": "android"})
test("back_b", h="", keep=True, only="android")
plan.append({"t": "native", "cmd": "back", "wait": 4000, "only": "android"})
test("back_c", h="", keep=True, only="android")
# large system font
plan.append({"t": "native", "cmd": "font_big", "wait": 60000})
for h in ["today", "journal", "m6", "rec"]:
    plan.append({"t": "frame", "id": "T037", "label": "大字体 " + h, "flags": "", "hash": h, "act": "", "snap": "FONT-" + h, "keep": True})
test("overflow", h="today", keep=True)
plan.append({"t": "native", "cmd": "font_normal", "wait": 60000})

json.dump(plan, open(os.path.join(HERE, "plan.json"), "w"), ensure_ascii=False, indent=0)
print(len(plan), "steps")
