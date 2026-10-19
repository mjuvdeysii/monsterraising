"""Builds ios/Generated/Assets.xcassets from the files the Android app already has, so both apps use the same
pictures: mascot images for the widget, the two app icons, and the widget colours (light and dark)."""
import json, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
IOS = os.path.dirname(HERE)
ROOT = os.path.dirname(IOS)
RES = os.path.join(ROOT, "app", "src", "main", "res", "drawable-nodpi")
OUT = os.path.join(IOS, "Generated", "Assets.xcassets")
INFO = {"author": "xcode", "version": 1}

def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

shutil.rmtree(OUT, ignore_errors=True)
write(os.path.join(OUT, "Contents.json"), {"info": INFO})

# mascot pictures, one image set each
for f in sorted(os.listdir(RES)):
    if not f.endswith(".png"):
        continue
    name = f[:-4]
    d = os.path.join(OUT, name + ".imageset")
    os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(RES, f), os.path.join(d, f))
    write(os.path.join(d, "Contents.json"), {"images": [{"idiom": "universal", "filename": f, "scale": "1x"}], "info": INFO})

# app icons: one 1024 px picture each (Xcode makes the other sizes)
for name, src in (("AppIcon", "AppIcon.png"), ("AppIconEye", "AppIconEye.png")):
    d = os.path.join(OUT, name + ".appiconset")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(IOS, "icons", src)
    images = [{"idiom": "universal", "platform": "ios", "size": "1024x1024"}]
    if os.path.exists(p):
        shutil.copy(p, os.path.join(d, src))
        images[0]["filename"] = src
    write(os.path.join(d, "Contents.json"), {"images": images, "info": INFO})

def rgb(h):
    h = h.lstrip("#")
    return {"red": "0x" + h[0:2], "green": "0x" + h[2:4], "blue": "0x" + h[4:6], "alpha": "1.000"}

def color(name, light, dark):
    write(os.path.join(OUT, name + ".colorset", "Contents.json"), {
        "colors": [
            {"idiom": "universal", "color": {"color-space": "srgb", "components": rgb(light)}},
            {"idiom": "universal", "appearances": [{"appearance": "luminosity", "value": "dark"}], "color": {"color-space": "srgb", "components": rgb(dark)}},
        ],
        "info": INFO,
    })

color("LaunchBackground", "#FCF9F4", "#1E1B19")
color("WidgetBackground", "#FFFDF8", "#211E1B")
color("TileNurse", "#FBE7E4", "#3A2726")
color("TileBottle", "#FCEFD9", "#3A3022")
color("TileSleep", "#E4EAF8", "#232A3A")
color("TileDiaper", "#DFF0F3", "#1F3236")
print("assets ready:", OUT)
