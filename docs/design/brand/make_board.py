"""Brand naming board: three candidate name sets on the real touchpoints, rendered with the app's own fonts and monsters."""
import base64, json, sys
from playwright.sync_api import sync_playwright
R = '/home/claude/monsterraising/app/src/main/res/mipmap-xxxhdpi/'
ICON = 'data:image/png;base64,' + base64.b64encode(open(R + 'ic_launcher.png', 'rb').read()).decode()
ICONE = 'data:image/png;base64,' + base64.b64encode(open(R + 'ic_launcher_eye.png', 'rb').read()).decode()
OPTS = [
    {"k": "A", "tag": "推荐候选", "zh": "小怪兽成长簿", "en": "Monster Milestones", "short": "小怪兽", "sub": "0–3 岁育儿记录与成长陪伴",
     "note": "怪兽 IP + 月龄里程碑 + 记录。Milestones 易被理解为“达标”，页面需写明“只用于记录和回顾，不是发展评估”。"},
    {"k": "B", "tag": "叙事型", "zh": "怪兽成长记", "en": "Monster Journey", "short": "怪兽成长记", "sub": "0–3 岁育儿记录与成长陪伴",
     "note": "贴合成长地图与故事感；手帐、计时等工具属性弱一些。"},
    {"k": "C", "tag": "保留现名", "zh": "养小怪兽", "en": "Little Monster Journal", "short": "养小怪兽", "sub": "0–3 岁育儿记录与成长陪伴",
     "note": "沿用已上线中文名，用户认知不变；英文从 Monster Raising 换为更易懂的说法，中英文不逐词对应。"},
]
CUR = {"zh": "养小怪兽", "en": "Monster Raising"}
JS = r"""
(o)=>{const M=(ip,mood,st,hold,flat)=>HB_MONSTER.svg({ip:ip,color:'mint',stage:st||2,mood:mood||'happy',hold:hold||'',flat:flat!==false?true:false});
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const css=`
*{box-sizing:border-box}body{margin:0;background:#EFE9DD;font-family:"Nunito","Noto Sans SC","PingFang SC",sans-serif;color:#292D27;-webkit-font-smoothing:antialiased}
.board{width:1560px;padding:40px 44px 48px}
.hd{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:22px}
.hd h1{font-family:var(--f-title);font-size:34px;margin:0;letter-spacing:.04em}
.hd p{margin:6px 0 0;font-size:15px;color:#5F6159}
.cur{font-size:14px;color:#5F6159;text-align:right;line-height:1.6}
.cur b{color:#1F7A59}
.row{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.opt{background:#FFFEFA;border-radius:22px;padding:22px;box-shadow:0 1px 0 rgba(70,48,24,.06),0 14px 30px -18px rgba(70,48,24,.35)}
.oh{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.ok{width:36px;height:36px;border-radius:12px;background:#1F7A59;color:#fff;font-weight:800;font-size:18px;display:grid;place-items:center}
.ot{font-size:13px;font-weight:800;color:#1F7A59;background:#E3F1EA;border-radius:8px;padding:3px 10px}
.on{font-family:var(--f-title);font-size:28px;font-weight:800;margin:10px 0 0;letter-spacing:.04em}
.oe{font-family:"Nunito",sans-serif;font-size:16px;font-weight:700;color:#5F6159;margin-top:2px}
.note{font-size:13px;line-height:1.65;color:#5F6159;margin:10px 0 16px;min-height:64px}
.lab{font-size:12px;font-weight:800;color:#8A8C84;letter-spacing:.06em;margin:16px 0 8px}
.icons{display:flex;gap:18px;align-items:flex-start;background:linear-gradient(160deg,#6E8FB8,#9DB8D6);border-radius:18px;padding:16px 18px}
.ic{width:74px;text-align:center}.ic img{width:62px;height:62px;border-radius:16px;display:block;margin:0 auto;box-shadow:0 4px 10px rgba(0,0,0,.2)}
.ic span{display:block;margin-top:6px;font-size:12px;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-shadow:0 1px 2px rgba(0,0,0,.35)}
.welcome{border-radius:18px;background:#FBF6EC;padding:22px 18px 18px;text-align:center}
.welcome .wm{display:flex;justify-content:center;align-items:flex-end;gap:2px;height:96px}.welcome .wm>span{display:block}
.welcome .wm .a{width:96px}.welcome .wm .b{width:64px;transform:rotate(-6deg)}
.welcome h2{font-family:var(--f-title);font-size:26px;margin:10px 0 0;letter-spacing:.06em}
.welcome .we{font-size:14px;font-weight:700;color:#6B6D64;margin-top:2px}
.welcome .ws{font-size:13px;color:#6B6D64;margin-top:8px}
.welcome .wt{font-size:12px;color:#9A8F7C;margin-top:10px}
.bars{display:grid;gap:8px}
.bar{display:flex;align-items:center;gap:10px;border-radius:16px;padding:8px 10px;width:100%}
.bar .pair{position:relative;width:54px;height:40px;flex:none}.bar .pair>span{position:absolute;bottom:0;display:block}.bar .pair .b{left:0;width:28px;transform:rotate(-8deg)}.bar .pair .a{right:0;width:38px}
.bar .nm{flex:1;min-width:0;line-height:1.1}.bar .nm b{display:block;font-family:var(--f-title);font-size:20px;letter-spacing:.04em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.bar .nm small{display:block;font-size:11.5px;font-weight:700;opacity:.7;margin-top:2px;white-space:nowrap}
.bar .sr{width:22px;height:22px;border:2.4px solid currentColor;border-radius:50%;position:relative;flex:none;margin-right:6px}.bar .sr::after{content:"";position:absolute;width:8px;height:2.4px;background:currentColor;right:-7px;bottom:-3px;transform:rotate(45deg)}
.L{background:#FBF6EC;color:#292D27}.D{background:#1E211D;color:#ECE7DC}
.w360{width:300px}.big .nm b{font-size:25px}.big .nm small{font-size:14px}
.cap{font-size:11px;color:#8A8C84;margin:-2px 0 4px 2px}
.about{border-radius:16px;background:#FBF6EC;padding:14px 16px;display:flex;gap:12px;align-items:center}
.about img{width:52px;height:52px;border-radius:14px}.about b{display:block;font-size:17px}.about small{display:block;font-size:12px;color:#6B6D64;margin-top:2px}
.store{border-radius:16px;border:1px solid #E4DCCB;padding:14px 16px;display:flex;gap:14px;align-items:center}
.store img{width:68px;height:68px;border-radius:16px}.store b{display:block;font-size:17px}.store small{display:block;font-size:13px;color:#6B6D64;margin-top:3px}.store i{display:inline-block;margin-top:6px;font-style:normal;font-size:12px;font-weight:800;color:#fff;background:#1F7A59;border-radius:999px;padding:4px 14px}
.foot{margin-top:22px;display:grid;grid-template-columns:1.2fr 1fr;gap:22px}
.box{background:#FFFEFA;border-radius:18px;padding:18px 20px;font-size:13.5px;line-height:1.75;color:#3E4139}
.box h3{margin:0 0 6px;font-size:15px}
.box ul{margin:0;padding-left:18px}
`;
const bar=(x,cls,ip,w)=>`<div class="bar ${cls} ${w||''}"><span class="pair"><span class="b">${M(ip==='eye'?'mint':'eye')}</span><span class="a">${M(ip,'happy',2,'',false)}</span></span><span class="nm"><b>${esc(x.zh)}</b><small>${esc(x.en)}</small></span><span class="sr"></span></div>`;
let h=`<style>${css}</style><div class="board"><div class="hd"><div><h1>品牌命名 · 三套方案触点对照</h1><p>只做比较，未改名。名称、图标、商店名都保持现状，等您确认三项：中文主名、英文主名、图标下短名。</p></div><div class="cur">当前上线：<b>${o.cur.zh}</b> / ${o.cur.en}<br>未做商标、域名、应用商店重名检索</div></div><div class="row">`;
o.opts.forEach(x=>{
 h+=`<section class="opt"><div class="oh"><span class="ok">${x.k}</span><span class="ot">${esc(x.tag)}</span></div><p class="on">${esc(x.zh)}</p><p class="oe">${esc(x.en)}</p><p class="note">${esc(x.note)}</p>`;
 h+=`<p class="lab">桌面图标下的短名</p><div class="icons"><div class="ic"><img src="${o.icon}"><span>${esc(x.short)}</span></div><div class="ic"><img src="${o.icone}"><span>${esc(x.short)}</span></div><div class="ic"><img src="${o.icon}" style="filter:grayscale(1);opacity:.55"><span>相册</span></div></div>`;
 h+=`<p class="lab">欢迎页</p><div class="welcome"><div class="wm"><span class="b">${M('eye','happy',2)}</span><span class="a">${M('mint','happy',2,'book',false)}</span></div><h2>${esc(x.zh)}</h2><p class="we">${esc(x.en)}</p><p class="ws">${esc(x.sub)}</p><p class="wt">陪孩子慢慢长大</p></div>`;
 h+=`<p class="lab">今天页顶部 · 两套形象 × 浅色 / 深色（360 宽）</p><div class="bars">${bar(x,'L','mint','w360')}${bar(x,'D','mint','w360')}${bar(x,'L','eye','w360')}${bar(x,'D','eye','w360')}<p class="cap">系统大字体（约 130%）</p>${bar(x,'L big','mint','w360')}</div>`;
 h+=`<p class="lab">设置 › 关于</p><div class="about"><img src="${o.icon}"><div><b>${esc(x.zh)}</b><small>${esc(x.en)} · 版本 0.7</small><small>${esc(x.sub)}</small></div></div>`;
 h+=`<p class="lab">应用商店列表</p><div class="store"><img src="${o.icon}"><div><b>${esc(x.zh)}：${esc(x.en)}</b><small>${esc(x.sub)}</small><i>获取</i></div></div></section>`;
});
h+=`</div><div class="foot"><div class="box"><h3>改名时会涉及的地方（确认后单独一版处理）</h3><ul><li>直接显示：启动与欢迎页、今天页顶部、设置关于、通知标题、分享卡片与导出文件名、隐私说明、版本说明</li><li>系统层：安卓应用名称与桌面短名、小组件标题、通知渠道名称；应用商店名称、副标题与截图</li><li>外部：发布页标题、图标说明、支持邮件签名</li></ul></div><div class="box"><h3>不会因为改名而改动</h3><ul><li>安卓包名 cn.growthhandbook.app 与签名</li><li>本机存储键（hb: 开头）、勾选与手帐记录、备份文件格式</li><li>两只小怪兽的形象、颜色和已有贴纸</li></ul></div></div></div>`;
document.body.innerHTML=h;document.body.className='';document.documentElement.className='';return document.querySelector('.board').offsetHeight}
"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1560, 'height': 1200}, device_scale_factor=1.5)
    pg.add_init_script("localStorage.setItem('hb:ok','1');window.HBApp={platform(){return 'android'},getTextZoom(){return 100},versionName(){return '0.7'},version(){return 1},setReminders(){},setDark(){},haptic(){},setIp(){},setJournal(){},setJournalReminders(){},checkUpdate(){}}")
    pg.goto('http://localhost:8766/index.html#home'); pg.wait_for_timeout(2000)
    hgt = pg.evaluate(JS, {"opts": OPTS, "icon": ICON, "icone": ICONE, "cur": CUR})
    pg.set_viewport_size({'width': 1560, 'height': hgt}); pg.wait_for_timeout(600)
    pg.screenshot(path=sys.argv[1], full_page=True); b.close()
print('ok', hgt)
