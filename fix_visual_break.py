# -*- coding: utf-8 -*-
# فیکس فوری: آیکون‌های غول‌پیکر/سیاه = کش قدیمی CSS
# اجرا: python fix_visual_break.py
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
css_p = ROOT / 'static/css/style.css'
base_p = ROOT / 'templates/base.html'

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
.acc-body{max-height:0;overflow:hidden;transition:max-height .5s ease,padding .3s}
.acc-item.open .acc-body{max-height:600px;padding:0 22px 18px}
@media(max-width:900px){.f-grid{grid-template-columns:1fr 1fr}}
@media(max-width:640px){.f-grid{grid-template-columns:1fr}.support-banner{flex-direction:column;text-align:center}.fab-wrap{bottom:16px;right:16px}.f-bottom{justify-content:center;text-align:center}}
'''

INLINE = '''<style>/* critical icon css - cache-proof */
.ic{width:1.15em;height:1.15em;vertical-align:-.22em;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;display:inline-block}
.ic-big{width:54px;height:54px;stroke-width:1.4}.ic-xl{width:84px;height:84px;stroke-width:1.2}
.ic-cyan{color:#22d3ee}.ic-violet{color:#a78bfa}.ic-pink{color:#f472b6}.ic-gold{color:#fbbf24}.ic-green{color:#34d399}.ic-bronze{color:#cd7f32}.ic-silver{color:#c8c8d0}
.btn .ic,.fab-item .ic,.acc-head .ic{width:1.2em;height:1.2em}
</style>
'''

# ۱) بلوک CSS روی دیسک
css = css_p.read_text(encoding='utf-8')
if 'v3: آیکون‌های SVG' not in css:
    css_p.write_text(css + FIX, encoding='utf-8')
    print('  ✔ بلوک CSS v3 به style.css اضافه شد (روی دیسک نبود!)')
else:
    print('  ✔ بلوک CSS v3 روی دیسک موجوده → مشکل فقط کش مرورگره')

# ۲) CSS حیاتی inline داخل base.html (ضد کش)
base = base_p.read_text(encoding='utf-8')
if 'critical icon css' not in base:
    base = base.replace('</head>', INLINE + '</head>', 1)
    print('  ✔ CSS حیاتی inline به base.html اضافه شد')

# ۳) باطل‌کردن کش با ورژن کوئری
base = re.sub(r"(\{% static 'css/style\.css' %\})(\?v=\d+)?", r"\1?v=3", base)
base = re.sub(r"(\{% static 'js/app\.js' %\})(\?v=\d+)?", r"\1?v=3", base)
base_p.write_text(base, encoding='utf-8')
print('  ✔ ورژن ?v=3 به فایل‌های static اضافه شد')

print('''
  ✅ تمام! حالا:
  ۱. سرور رو ری‌استارت کن (Ctrl+C بعد:  .venv\\Scripts\\python manage.py runserver)
  ۲. در مرورگر:  Ctrl + Shift + R   (ریفresh سخت)
  ۳. اگه بازهم خراب بود: یک پنجره Incognito باز کن و تست کن
''')