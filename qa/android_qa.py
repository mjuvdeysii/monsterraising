#!/usr/bin/env python3
"""Android QA on an emulator: installs the debug APK, drives the app's own WebView through Chrome DevTools Protocol,
lets qa/runner.js walk qa/plan.json, takes a real device screenshot (adb screencap) at every "QA:SNAP", and performs
device actions on "QA:NATIVE" (kill and relaunch, background and resume, back key, system font size).
Usage: python3 qa/android_qa.py <apk> <out_dir>"""
import json, os, subprocess, sys, time, urllib.request

PKG = "cn.growthhandbook.app"
ACT = PKG + "/.MainActivity"
APK, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(OUT, "shots"), exist_ok=True)
import websocket  # websocket-client


def adb(*a, check=False, text=True):
    r = subprocess.run(["adb"] + list(a), capture_output=True, text=text)
    if check and r.returncode: raise SystemExit("adb %s failed: %s" % (a, r.stderr))
    return r.stdout.strip() if text else r.stdout


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def launch(fresh=False):
    if fresh: adb("shell", "am", "force-stop", PKG); time.sleep(1.5)
    adb("shell", "am", "start", "-W", "-n", ACT)
    time.sleep(3)


class Page:
    def __init__(self):
        self.ws = None; self.n = 0

    def connect(self, script):
        deadline = time.time() + 90
        while time.time() < deadline:
            pid = adb("shell", "pidof", PKG)
            if pid:
                adb("forward", "--remove-all")
                adb("forward", "tcp:9222", "localabstract:webview_devtools_remote_" + pid.split()[0])
                try:
                    pages = json.load(urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=5))
                    pages = [p for p in pages if p.get("type") == "page" and "index.html" in p.get("url", "")]
                    if pages:
                        self.ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=5, suppress_origin=True)
                        self.send("Runtime.enable"); self.send("Page.enable")
                        self.send("Page.addScriptToEvaluateOnNewDocument", source=script)
                        self.send("Runtime.evaluate", expression=script)
                        log("connected to WebView, pid", pid)
                        return True
                except Exception as e:
                    log("waiting for WebView:", e)
            time.sleep(2)
        return False

    def send(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        return self.n

    def lines(self):
        try:
            m = json.loads(self.ws.recv())
        except websocket.WebSocketTimeoutException:
            return []
        except Exception:
            raise
        if m.get("method") == "Runtime.consoleAPICalled":
            return [a.get("value") for a in m["params"].get("args", []) if isinstance(a.get("value"), str)]
        return []


def device():
    wv = adb("shell", "dumpsys", "webviewupdate")
    wvl = [l.strip() for l in wv.splitlines() if "Current WebView package" in l]
    return {"model": adb("shell", "getprop", "ro.product.model"), "android": adb("shell", "getprop", "ro.build.version.release"),
            "sdk": adb("shell", "getprop", "ro.build.version.sdk"), "abi": adb("shell", "getprop", "ro.product.cpu.abi"),
            "density": adb("shell", "wm", "density"), "size": adb("shell", "wm", "size"), "webview": wvl[0] if wvl else "",
            "app": [l.strip() for l in adb("shell", "dumpsys", "package", PKG).splitlines() if "versionName" in l][:1]}


def main():
    adb("wait-for-device")
    adb("install", "-r", "-g", APK, check=True)
    adb("shell", "pm", "grant", PKG, "android.permission.POST_NOTIFICATIONS")
    adb("shell", "settings", "put", "system", "font_scale", "1.0")
    adb("shell", "settings", "put", "global", "window_animation_scale", "1")
    info = device(); log("device", info)
    plan = json.load(open(os.path.join(HERE, "plan.json"), encoding="utf-8"))
    runner = open(os.path.join(HERE, "runner.js"), encoding="utf-8").read()
    script = "window.QA_BOOT=" + json.dumps(plan, ensure_ascii=False) + ";" + runner
    launch(fresh=True)
    pg = Page()
    if not pg.connect(script): raise SystemExit("could not attach to the WebView")
    results, done, t0, last = [], False, time.time(), time.time()
    while not done and time.time() - t0 < 70 * 60:
        try:
            ls = pg.lines()
        except Exception as e:
            log("connection lost:", e); time.sleep(2); pg.connect(script); continue
        if not ls and time.time() - last > 150:
            log("no progress for 150 s; screenshot and stop")
            open(os.path.join(OUT, "shots", "STALL.png"), "wb").write(adb("exec-out", "screencap", "-p", text=False)); break
        for t in ls:
            if not t.startswith("QA:"): continue
            last = time.time(); typ, _, js = t[3:].partition(":")
            o = json.loads(js)
            if typ == "SNAP":
                png = adb("exec-out", "screencap", "-p", text=False)
                open(os.path.join(OUT, "shots", o["name"] + ".png"), "wb").write(png); log("snap", o["name"])
                pg.send("Runtime.evaluate", expression="window.__qaAck=1")
            elif typ == "RES":
                o["device"] = info["model"] + " / Android " + info["android"]; results.append(o)
                log("PASS" if o["pass"] else "FAIL", o["id"], o["detail"][:160])
            elif typ == "NATIVE":
                c = o["cmd"]; log("native", c)
                if c == "kill":
                    adb("shell", "am", "force-stop", PKG); time.sleep(2); launch(); pg.connect(script)
                elif c == "background":
                    adb("shell", "input", "keyevent", "3"); time.sleep(7); launch();
                elif c == "back":
                    adb("shell", "input", "keyevent", "4")
                elif c in ("font_big", "font_normal"):
                    adb("shell", "settings", "put", "system", "font_scale", "1.3" if c == "font_big" else "1.0")
                    adb("shell", "am", "force-stop", PKG); time.sleep(2); launch(); pg.connect(script)
            elif typ == "DONE":
                done = True; log("plan finished")
            elif typ == "LOG":
                log("page:", o)
    json.dump({"device": info, "done": done, "results": results}, open(os.path.join(OUT, "results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    p = sum(1 for r in results if r["pass"]); log("results", p, "/", len(results), "passed; finished=", done)


if __name__ == "__main__":
    main()
