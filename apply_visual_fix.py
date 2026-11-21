# -*- coding: utf-8 -*-
# ⬡ نئوگیم — فیکس ظاهری: اسپرایت SVG رنگی + فوتر کامل + فیکس آکاردئون/ریسپانسیو
# اجرا: python apply_visual_fix.py
import os, re, sys, shutil, subprocess, webbrowser, threading
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
VENV = ROOT / '.venv'
PY = VENV / ('Scripts\\python.exe' if os.name == 'nt' else 'bin/python')
BACKUP_DIR = ROOT / '_backups' / ('visual_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
TPL = ROOT / 'templates'

def banner(t): print('\n' + '═'*55 + f'\n  {t}\n' + '═'*55)
def ok(t): print(f'  ✔ {t}')

banner('۱) بکاپ')
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
for f in list(TPL.rglob('*.html')) + [ROOT/'static/css/style.css', ROOT/'core/models.py']:
    dst = BACKUP_DIR / f.relative_to(ROOT); dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, dst)
ok(f'بکاپ: {BACKUP_DIR}')

# ─────────── ۲) اسپرایت SVG ───────────
banner('۲) اسپرایت آیکون‌های SVG')
SPRITE = '''<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true"><defs>
<linearGradient id="gL" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient>
</defs>
<symbol id="i-logo" viewBox="0 0 24 24"><path d="M12 2l8.5 5v10L12 22 3.5 17V7z" fill="url(#gL)"/><path d="M9 15V9l3 3 3-3v6" stroke="#041018" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-cart" viewBox="0 0 24 24"><circle cx="9" cy="20" r="1.6"/><circle cx="17" cy="20" r="1.6"/><path d="M3 4h2l2.6 11h10L20 8H6"/></symbol>
<symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13 2L5 13h5l-1 9 8-11h-5z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-tag" viewBox="0 0 24 24"><path d="M20 12l-8 8-9-9V4h7z"/><circle cx="7.5" cy="7.5" r="1.5"/></symbol>
<symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.3-4.3"/></symbol>
<symbol id="i-lock" viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></symbol>
<symbol id="i-headset" viewBox="0 0 24 24"><path d="M4 13a8 8 0 0 1 16 0"/><rect x="3" y="13" width="4" height="6" rx="2"/><rect x="17" y="13" width="4" height="6" rx="2"/></symbol>
<symbol id="i-send" viewBox="0 0 24 24"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4z"/></symbol>
<symbol id="i-help" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 0 1 5 .2c0 1.8-2.5 2-2.5 3.8"/><circle cx="12" cy="17" r=".9" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-star" viewBox="0 0 24 24"><path d="M12 3l2.7 5.8 6.3.8-4.6 4.3 1.2 6.1-5.6-3-5.6 3 1.2-6.1L3 9.6l6.3-.8z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-package" viewBox="0 0 24 24"><path d="M12 3l8 4v10l-8 4-8-4V7z"/><path d="M4 7l8 4 8-4M12 11v10"/></symbol>
<symbol id="i-wallet" viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="13" rx="3"/><path d="M16 12h5v4h-5a2 2 0 0 1 0-4z"/></symbol>
<symbol id="i-user" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 20a8 8 0 0 1 16 0"/></symbol>
<symbol id="i-gear" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3.2"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9L17 7M7 17l-2.1 2.1"/></symbol>
<symbol id="i-logout" viewBox="0 0 24 24"><path d="M14 4H6v16h8"/><path d="M10 12h11M18 8l3 4-3 4"/></symbol>
<symbol id="i-chart" viewBox="0 0 24 24"><path d="M5 20v-6M10 20V8M15 20v-10M20 20V6"/></symbol>
<symbol id="i-home" viewBox="0 0 24 24"><path d="M4 11l8-7 8 7"/><path d="M6 10v10h12V10"/></symbol>
<symbol id="i-check" viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 6.5"/></symbol>
<symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></symbol>
<symbol id="i-sword" viewBox="0 0 24 24"><path d="M20 4L9 15l-3 5 5-3L20 4z"/><path d="M5 15l4 4"/></symbol>
<symbol id="i-bow" viewBox="0 0 24 24"><path d="M5 3c9 1 15 7 16 16"/><path d="M5 3l16 16"/><path d="M13 11l5-1-1 5"/></symbol>
<symbol id="i-shieldcheck" viewBox="0 0 24 24"><path d="M12 3l7 3v6c0 5-3.5 8-7 9-3.5-1-7-4-7-9V6z"/><path d="M9 12l2 2 4-4"/></symbol>
<symbol id="i-gem" viewBox="0 0 24 24"><path d="M7 3h10l4 6-9 12L3 9z"/><path d="M3 9h18M12 21L8 9l3-6M12 21l4-12-3-6"/></symbol>
<symbol id="i-trident" viewBox="0 0 24 24"><path d="M12 22V3M9 6l3-3 3 3M7 12a5 5 0 0 0 10 0M7 12V9M17 12V9"/></symbol>
<symbol id="i-coin" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/></symbol>
<symbol id="i-potion" viewBox="0 0 24 24"><path d="M10 3h4M11 3v4l-4.5 8a4.5 4.5 0 0 0 4 6.5h3a4.5 4.5 0 0 0 4-6.5L13 7V3"/><path d="M8 15h8"/></symbol>
<symbol id="i-mask" viewBox="0 0 24 24"><path d="M4 6c4 2 12 2 16 0v6c0 5-4 8-8 8s-8-3-8-8z"/><circle cx="9" cy="11" r=".9" fill="currentColor" stroke="none"/><circle cx="15" cy="11" r=".9" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-helmet" viewBox="0 0 24 24"><path d="M12 2l7 4v7c0 5-3 8-7 9-4-1-7-4-7-9V6z"/><path d="M8.5 10h7M12 12v6"/></symbol>
<symbol id="i-crosshair" viewBox="0 0 24 24"><circle cx="12" cy="12" r="7"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-medal" viewBox="0 0 24 24"><circle cx="12" cy="14" r="5"/><path d="M8 3l4 6 4-6M6 3h3M15 3h3"/></symbol>
<symbol id="i-crown" viewBox="0 0 24 24"><path d="M4 18h16M4 18l-1-9 5 4 4-7 4 7 5-4-1 9z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-fire" viewBox="0 0 24 24"><path d="M12 22c4 0 7-2.7 7-6.5 0-4-3-6-4.5-9C13 9 10 9.5 10 7c-2.5 2-4 5-4 8.5C6 19.3 8 22 12 22z"/></symbol>
<symbol id="i-chat" viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z"/></symbol>
<symbol id="i-screen" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M9 20h6M12 16v4"/></symbol>
<symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s-6-5.2-6-10a6 6 0 1 1 12 0c0 4.8-6 10-6 10z"/><circle cx="12" cy="11" r="2"/></symbol>
<symbol id="i-mail" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></symbol>
<symbol id="i-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14 0 18-3-4-3-14.5 0-18z"/></symbol>
<symbol id="i-gamepad" viewBox="0 0 24 24"><rect x="3" y="8" width="18" height="9" rx="4"/><path d="M8 11v3M6.5 12.5h3"/><circle cx="16" cy="11.5" r=".9" fill="currentColor" stroke="none"/><circle cx="18" cy="13.5" r=".9" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-bell" viewBox="0 0 24 24"><path d="M6 16v-5a6 6 0 0 1 12 0v5l2 3H4z"/><path d="M10 19a2 2 0 0 0 4 0"/></symbol>
<symbol id="i-wave" viewBox="0 0 24 24"><path d="M7 11V6a1.5 1.5 0 0 1 3 0v4M10 10V4.5a1.5 1.5 0 0 1 3 0V10M13 10V6a1.5 1.5 0 0 1 3 0v6c0 4-2.5 7-6 7s-5-2-6-5l-1.5-4a1.4 1.4 0 0 1 2.6-1L7 11"/></symbol>
<symbol id="i-instagram" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="4"/><circle cx="12" cy="12" r="3.5"/><circle cx="16.5" cy="7.5" r=".9" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-youtube" viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="12" rx="3"/><path d="M10 9.5l5 2.5-5 2.5z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>
</svg>'''

base = (TPL / 'base.html').read_text(encoding='utf-8')
if 'i-logo' not in base:
    base = base.replace('</head><body>', '</head><body>\n' + SPRITE, 1)
    ok('اسپرایت به base.html اضافه شد')

# ─────────── ۳) فوتر کامل ───────────
banner('۳) بازگردانی فوتر ۴ستونه')
FOOTER = '''<footer class="footer"><div class="container">
  <div class="f-grid">
    <div class="f-col">
      <a class="logo" href="{% url 'home' %}"><span class="logo-mark"><svg class="ic" style="width:22px;height:22px;color:#041018"><use href="#i-logo"/></svg></span> نئوگیم</a>
      <p>بزرگ‌ترین مارکت آیتم، بوست و ترید اکانت بازی‌های آنلاین؛ با اسکرو امن و تحویل آنی.</p>
      <div class="socials">
        <a class="icon-btn" href="{{ TELEGRAM_URL }}" target="_blank" aria-label="تلگرام"><svg class="ic ic-cyan"><use href="#i-send"/></svg></a>
        <a class="icon-btn" href="#" aria-label="دیسکورد"><svg class="ic ic-violet"><use href="#i-gamepad"/></svg></a>
        <a class="icon-btn" href="#" aria-label="اینستاگرام"><svg class="ic ic-pink"><use href="#i-instagram"/></svg></a>
        <a class="icon-btn" href="#" aria-label="یوتیوب"><svg class="ic ic-gold"><use href="#i-youtube"/></svg></a>
      </div>
    </div>
    <div class="f-col"><h4>خدمات</h4>
      <a href="{% url 'market' %}">مارکت آیتم</a><a href="{% url 'boost' %}">بوست اکانت</a>
      <a href="{% url 'trade' %}">خرید و فروش اکانت</a><a href="{% url 'faq' %}">سوالات متداول</a></div>
    <div class="f-col"><h4>پشتیبانی ۲۴/۷</h4>
      <a href="{{ TELEGRAM_URL }}" target="_blank">تلگرام پشتیبانی</a><a href="{% url 'faq' %}?cat=pay">امنیت و اسکرو</a>
      <a href="{% url 'faq' %}?cat=sup">راهنمای تماس</a><a href="{% url 'dashboard' %}">پیگیری سفارش</a></div>
    <div class="f-col"><h4>خبرنامه</h4>
      <p style="margin-top:0">تخفیف‌ها و آیتم‌های جدید رو اول از همه بگیر.</p>
      <form class="news" data-fake="عضو خبرنامه شدی"><input placeholder="ایمیل شما..."><button class="btn btn-primary sm">عضویت</button></form></div>
  </div>
  <div class="f-bottom"><span>نئوگیم © ۲۰۲۶ — طراحی نئون / لیکویید گلس</span>
  <span>پرداخت امن · SSL · اسکرو تضمینی <svg class="ic ic-green"><use href="#i-lock"/></svg></span></div>
</div></footer>'''
base = re.sub(r'<footer class="footer">.*?</footer>', FOOTER, base, count=1, flags=re.S)
(TPL / 'base.html').write_text(base, encoding='utf-8')
ok('فوتر کامل جایگزین شد')

# ─────────── ۴) نقشه ایموجی → SVG ───────────
banner('۴) جایگزینی ایموجی‌ها با SVG رنگی')
COLOR = {'cart':'ic-cyan','bolt':'ic-gold','coin':'ic-gold','search':'ic-cyan','lock':'ic-green','headset':'ic-cyan',
 'send':'ic-cyan','help':'ic-violet','star':'ic-gold','package':'ic-violet','wallet':'ic-green','user':'ic-violet',
 'gear':'ic-violet','logout':'ic-pink','chart':'ic-cyan','home':'ic-cyan','check':'ic-green','clock':'ic-violet',
 'sword':'ic-gold','bow':'ic-violet','shieldcheck':'ic-cyan','gem':'ic-cyan','trident':'ic-gold','potion':'ic-green',
 'mask':'ic-pink','helmet':'ic-cyan','crosshair':'ic-violet','fire':'ic-pink','chat':'ic-cyan','screen':'ic-violet',
 'tag':'ic-pink','pin':'ic-pink','mail':'ic-cyan','globe':'ic-cyan','gamepad':'ic-violet','bell':'ic-gold','wave':'ic-gold'}
EMO = {'🛒':'cart','⚡':'bolt','💰':'coin','🔍':'search','🔐':'lock','🔒':'lock','🎧':'headset','✈️':'send','❓':'help',
 '⭐':'star','📦':'package','💳':'wallet','👤':'user','🥷':'user','⚙️':'gear','🚪':'logout','📊':'chart','📈':'chart',
 '🏠':'home','✅':'check','⏰':'clock','🕒':'clock','🗡️':'sword','🏹':'bow','🛡️':'shieldcheck','💠':'gem','🔱':'trident',
 '🪙':'coin','🧪':'potion','🎭':'mask','🤖':'helmet','🎯':'crosshair','🔥':'fire','💬':'chat','📺':'screen','🏷️':'tag',
 '🛍️':'tag','📌':'pin','📧':'mail','🌐':'globe','🎮':'gamepad','🔔':'bell','👋':'wave','😕':'help'}
SPECIAL = {'🥉':'<svg class="ic ic-bronze"><use href="#i-medal"/></svg>', '🥈':'<svg class="ic ic-silver"><use href="#i-medal"/></svg>',
 '🥇':'<svg class="ic ic-gold"><use href="#i-medal"/></svg>', '💎':'<svg class="ic ic-cyan"><use href="#i-gem"/></svg>',
 '👑':'<svg class="ic ic-cyan"><use href="#i-crown"/></svg>'}
def svg_for(k): return f'<svg class="ic {COLOR[k]}"><use href="#i-{k}"/></svg>'

for f in list(TPL.rglob('*.html')):
    txt = f.read_text(encoding='utf-8')
    stash = {}
    txt = re.sub(r'data-toast="[^"]*"', lambda m: stash.setdefault(m.group(0), m.group(0)) and f'@@T{len(stash)}@@' or f'@@T{list(stash).index(m.group(0))+1}@@', txt)
    for e, s in SPECIAL.items(): txt = txt.replace(e, s)
    for e, k in EMO.items(): txt = txt.replace(e, svg_for(k))
    txt = txt.replace('\uFE0F', '')
    for tok, val in stash.items():
        idx = list(stash).index(tok) + 1
        txt = txt.replace(f'@@T{idx}@@', val)
    f.write_text(txt, encoding='utf-8')
ok('همه‌ی تمپلیت‌ها به SVG مجهز شدن')

# ─────────── ۵) آیکون‌های دیتابیسی (بازی/آیتم) ───────────
banner('۵) آیکون‌های حاصل از دیتابیس')
def rep(path, old, new):
    p = TPL / path; t = p.read_text(encoding='utf-8')
    if old in t: p.write_text(t.replace(old, new), encoding='utf-8'); ok(path)
rep('includes/item.html', '<div class="art">{{ item.icon }}</div>',
    '<div class="art"><svg class="ic ic-big"><use href="#i-{{ item.icon }}"/></svg></div>')
rep('index.html', '<div class="g-art">{{ g.icon }}</div>',
    '<div class="g-art"><svg class="ic ic-xl"><use href="#i-{{ g.icon }}"/></svg></div>')
rep('product.html', '{% else %}{{ item.icon }}{% endif %}',
    '{% else %}<svg class="ic ic-xl"><use href="#i-{{ item.icon }}"/></svg>{% endif %}')
rep('trade.html', '<div class="acc-top"><span class="av">{{ l.icon }}</span>',
    '<div class="acc-top"><span class="av"><svg class="ic ic-big" style="width:30px;height:30px"><use href="#i-{{ l.icon }}"/></svg></span>')
rep('cart.html', '<td>{{ row.item.icon }} {{ row.item.name }}</td>',
    '<td><svg class="ic ic-cyan"><use href="#i-{{ row.item.icon }}"/></svg> {{ row.item.name }}</td>')
rep('dashboard.html', '<td>{{ o.item.icon }} {{ o.item.name }}</td>',
    '<td><svg class="ic ic-cyan"><use href="#i-{{ o.item.icon }}"/></svg> {{ o.item.name }}</td>')
rep('dashboard.html', '<td>{{ b.game.icon }} {{ b.game.name }}</td>',
    '<td><svg class="ic ic-violet"><use href="#i-{{ b.game.icon }}"/></svg> {{ b.game.name }}</td>')
rep('dashboard.html', '<div class="act"><i>{{ l.icon }}</i>',
    '<div class="act"><i><svg class="ic ic-cyan"><use href="#i-{{ l.icon }}"/></svg></i>')

# ─────────── ۶) رنک‌ها: SVG به‌جای ایموجی ───────────
banner('۶) رنک‌های بوست')
rep2 = lambda p, o, n: rep(p, o, n)
rep2('../core/models.py', "RANKS = [(0, '🥉 برنز'), (1, '🥈 سیلور'), (2, '🥇 گلد'), (3, '💎 پلاتین'), (4, '👑 الماس')]",
     "RANKS = [(0, 'medal', 'ic-bronze', 'برنز'), (1, 'medal', 'ic-silver', 'سیلور'), (2, 'medal', 'ic-gold', 'گلد'), (3, 'gem', 'ic-violet', 'پلاتین'), (4, 'crown', 'ic-cyan', 'الماس')]")
for name, chk in [('cur', '{% if forloop.first %}checked{% endif %}'), ('tgt', '{% if forloop.counter == 2 %}checked{% endif %}')]:
    rep2('boost.html',
      '{% for v, t in ranks %}<label class="seg-item"><input type="radio" name="' + name + '" value="{{ v }}" ' + chk + '><span>{{ t }}</span></label>{% endfor %}',
      '{% for v, sym, col, label in ranks %}<label class="seg-item"><input type="radio" name="' + name + '" value="{{ v }}" ' + chk + '><span><svg class="ic {{ col }}"><use href="#i-{{ sym }}"/></svg> {{ label }}</span></label>{% endfor %}')

# ─────────── ۷) فیکس‌های CSS ───────────
banner('۷) فیکس‌های CSS')
css_p = ROOT / 'static/css/style.css'; css = css_p.read_text(encoding='utf-8')
FIX = '''
/* ========== v3: آیکون‌های SVG + فیکس‌ها ========== */
.ic{width:1.15em;height:1.15em;vertical-align:-.22em;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;display:inline-block}
.ic-big{width:54px;height:54px;stroke-width:1.4;filter:drop-shadow(0 0 16px currentColor)}
.ic-xl{width:84px;height:84px;stroke-width:1.2;filter:drop-shadow(0 0 26px currentColor)}
.ic-cyan{color:var(--cyan)}.ic-violet{color:var(--violet)}.ic-pink{color:var(--pink)}
.ic-gold{color:var(--gold)}.ic-green{color:var(--green)}
.ic-bronze{color:#cd7f32}.ic-silver{color:#c8c8d0}
.g-art .ic-xl{width:70px;height:70px}
.l-item i .ic{width:30px;height:30px}
.step-num .ic{width:26px;height:26px}
a.icon-btn{display:grid;place-items:center;text-decoration:none}
.logo-mark .ic{filter:none}
/* فیکس آکاردئون: جواب کامل نمایش داده بشه */
.acc-body{max-height:0;overflow:hidden;transition:max-height .5s ease,padding .3s}
.acc-item.open .acc-body{max-height:600px;padding:0 22px 18px}
/* فیکس ریسپانسیو فوتر و بنر */
@media(max-width:900px){.f-grid{grid-template-columns:1fr 1fr}}
@media(max-width:640px){.f-grid{grid-template-columns:1fr}.support-banner{flex-direction:column;text-align:center}.fab-wrap{bottom:16px;right:16px}.f-bottom{justify-content:center;text-align:center}}
'''
if 'v3: آیکون‌های SVG' not in css:
    css_p.write_text(css + FIX, encoding='utf-8'); ok('CSS فیکس شد')

# ─────────── ۸) آپدیت آیکون‌های دیتابیس ───────────
banner('۸) تبدیل ایموجی‌های دیتابیس به کلید SVG')
(ROOT / 'update_icons.py').write_text('''import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neogame.settings')
django.setup()
from core.models import Game, Item, AccountListing
M = {'🤖':'helmet','⚔️':'sword','🛡️':'shieldcheck','🎯':'crosshair','🗡️':'sword','🏹':'bow',
     '💠':'gem','🔱':'trident','🪙':'coin','🧪':'potion','🎭':'mask'}
n = 0
for model in (Game, Item, AccountListing):
    for obj in model.objects.all():
        if obj.icon in M:
            obj.icon = M[obj.icon]; obj.save(); n += 1
print(f'  ✔ {n} آیکون دیتابیس به کلید SVG تبدیل شد')
''', encoding='utf-8')
subprocess.run([str(PY), 'update_icons.py'], cwd=ROOT, check=True)

banner('✅ فیکس ظاهری کامل شد!')
print('''
   تغییرات:
  • همه‌ی ایموجی‌ها → آیکون SVG رنگی با درخشش نئونی (یکدست روی همه‌ی دستگاه‌ها)
  • فوتر ۴ستونه‌ی کامل برگشت (لوگو، خدمات، پشتیبانی، خبرنامه، شبکه‌های اجتماعی)
  • آکاردئون FAQ دیگه جواب‌ها رو قطع نمی‌کنه
  • رنک‌های بوست (برنز..الماس) با مدال/الماس/تاج SVG رنگی
  • فیکس ریسپانسیو فوتر و بنر پشتیبانی در موبایل

  📁 بکاپ: {b}
'''.format(b=BACKUP_DIR))
ans = input('  سرور الان استارت بشه؟ (y/n): ').strip().lower()
if ans in ('y', 'yes', 'بله', 'آره', ''):
    threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:8000/')).start()
    try: subprocess.run([str(PY), 'manage.py', 'runserver', '0.0.0.0:8000'], cwd=ROOT)
    except KeyboardInterrupt: print('\nخداحافظ 👋')
else: print('\n  برای اجرا:  .venv\\Scripts\\python manage.py runserver')