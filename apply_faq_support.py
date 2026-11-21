# -*- coding: utf-8 -*-
# ⬡ نئوگیم — افزودن سوالات متداول (مدل + صفحه + مینی‌FAQ) و پشتیبانی ۲۴/۷ تلگرام (ویجت شناور + بنر)
# اجرا: python apply_faq_support.py
import os, sys, shutil, subprocess, webbrowser, threading
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
VENV = ROOT / '.venv'
PY = VENV / ('Scripts\\python.exe' if os.name == 'nt' else 'bin/python')
BACKUP_DIR = ROOT / '_backups' / ('faq_' + datetime.now().strftime('%Y%m%d_%H%M%S'))

def banner(t): print('\n' + '═'*55 + f'\n  {t}\n' + '═'*55)
def ok(t): print(f'  ✔ {t}')
def fail(t): print(f'  ✖ {t}'); sys.exit(1)

banner('۱) بررسی پیش‌نیازها')
for need in ['manage.py', 'core/models.py', 'core/views.py', 'core/admin.py',
             'core/context_processors.py', 'neogame/settings.py', 'neogame/urls.py',
             'templates/base.html', 'templates/index.html', 'static/css/style.css', 'static/js/app.js']:
    if not (ROOT / need).exists(): fail(f'فایل {need} پیدا نشد!')
if not PY.exists(): fail('.venv پیدا نشد! اول bootstrap.py را اجرا کنید.')
ok('ساختار صحیح است')

banner('۲) پشتیبان‌گیری')
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
for f in ['core/models.py','core/views.py','core/admin.py','core/context_processors.py',
          'neogame/settings.py','neogame/urls.py','templates/base.html','templates/index.html',
          'static/css/style.css','static/js/app.js']:
    dst = BACKUP_DIR / f; dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / f, dst)
ok(f'بکاپ: {BACKUP_DIR}')

def replace_in(path, old, new, desc):
    p = ROOT / path; txt = p.read_text(encoding='utf-8')
    if new in txt: print(f'  ⚠ {path}: قبلاً اعمال شده'); return
    if old not in txt: print(f'  ⚠ {path}: الگو پیدا نشد — دستی بررسی کن'); return
    p.write_text(txt.replace(old, new), encoding='utf-8'); ok(f'{desc} → {path}')

def append_if(path, marker, content, desc):
    p = ROOT / path; txt = p.read_text(encoding='utf-8')
    if marker in txt: print(f'  ⚠ {path}: قبلاً اضافه شده'); return
    p.write_text(txt + content, encoding='utf-8'); ok(f'{desc} → {path}')

# ─────────── ۳) مدل FAQ ───────────
banner('۳) مدل FAQ در core/models.py')
replace_in('core/models.py',
    "    def __str__(self): return f'{self.item.name} #{self.order}'",
    """    def __str__(self): return f'{self.item.name} #{self.order}'

class FAQ(models.Model):
    CATEGORY = [('buy', 'خرید آیتم'), ('boost', 'بوست اکانت'), ('trade', 'ترید اکانت'),
                ('pay', 'پرداخت و امنیت'), ('sup', 'پشتیبانی')]
    category = models.CharField('دسته', max_length=10, choices=CATEGORY, default='buy')
    question = models.CharField('سوال', max_length=200)
    answer = models.TextField('جواب')
    order = models.PositiveIntegerField('ترتیب', default=0)
    show_home = models.BooleanField('نمایش در صفحه اصلی', default=False)
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'
    def __str__(self): return self.question""",
    'مدل FAQ')

# ─────────── ۴) settings + context processor ───────────
banner('۴) تنظیم آیدی تلگرام')
replace_in('neogame/settings.py',
    "MEDIA_ROOT = BASE_DIR / 'media'",
    "MEDIA_ROOT = BASE_DIR / 'media'\nTELEGRAM_SUPPORT_URL = 'https://t.me/neogame_support'  # ← آیدی تلگرام خودت رو اینجا بذار",
    'TELEGRAM_SUPPORT_URL')
replace_in('core/context_processors.py',
    "def cart_count(r):\n    return {'cart_count': len(r.session.get('cart', {}))}",
    "from django.conf import settings\n\ndef cart_count(r):\n    return {'cart_count': len(r.session.get('cart', {})),\n            'TELEGRAM_URL': getattr(settings, 'TELEGRAM_SUPPORT_URL', 'https://t.me/neogame_support')}",
    'context processor تلگرام')

# ─────────── ۵) views + urls ───────────
banner('۵) ویوها و URLها')
replace_in('core/views.py',
    "from .models import Game, Item, Order, BoostOrder, AccountListing, RANKS, boost_price",
    "from .models import Game, Item, Order, BoostOrder, AccountListing, Review, FAQ, RANKS, boost_price",
    'import FAQ')
replace_in('core/views.py',
    "    return render(r, 'index.html', {'games': Game.objects.all(),\n                                    'featured': Item.objects.filter(featured=True)[:4]})",
    "    return render(r, 'index.html', {'games': Game.objects.all(),\n                                    'featured': Item.objects.filter(featured=True)[:4],\n                                    'home_faqs': FAQ.objects.filter(show_home=True)[:4]})",
    'مینی‌FAQ در خانه')
replace_in('core/views.py',
    "        'wallet': r.user.profile.wallet})",
    """        'wallet': r.user.profile.wallet})

def faq(r):
    cat = r.GET.get('cat')
    qs = FAQ.objects.all()
    if cat: qs = qs.filter(category=cat)
    return render(r, 'faq.html', {'faqs': qs, 'cat': cat or '', 'cats': FAQ.CATEGORY})""",
    'ویوی faq')
replace_in('neogame/urls.py',
    "    path('dashboard/', v.dashboard, name='dashboard'),",
    "    path('dashboard/', v.dashboard, name='dashboard'),\n    path('faq/', v.faq, name='faq'),",
    'URL /faq/')

# ─────────── ۶) admin ───────────
banner('۶) پنل ادمین FAQ')
replace_in('core/admin.py',
    "from .models import Game, Item, ItemImage, Profile, Order, BoostOrder, AccountListing, Review",
    "from .models import Game, Item, ItemImage, Profile, Order, BoostOrder, AccountListing, Review, FAQ",
    'import FAQ')
replace_in('core/admin.py',
    "admin.site.register(Review)",
    """admin.site.register(Review)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'category', 'order', 'show_home')
    list_filter = ('category', 'show_home')
    list_editable = ('order', 'show_home')
    search_fields = ('question',)""",
    'FAQAdmin')

# ─────────── ۷) base.html: ویجت شناور + لینک فوتر ───────────
banner('۷) ویجت پشتیبانی شناور در base.html')
replace_in('templates/base.html',
    "</div></footer>\n<div id=\"toast\"></div>",
    """</div></footer>

<div class="fab-wrap" id="fabWrap">
  <div class="fab-panel">
    <div class="fab-head"><span>🎧 پشتیبانی ۲۴/۷</span><span class="badge b-ok">آنلاین</span></div>
    <a class="fab-item" href="{{ TELEGRAM_URL }}" target="_blank" rel="noopener">✈️ <div>تلگرام پشتیبانی<small>میانگین پاسخ: زیر ۵ دقیقه</small></div></a>
    <a class="fab-item" href="{% url 'faq' %}">❓ <div>سوالات متداول<small>جواب‌های سریع</small></div></a>
    <a class="fab-item" href="{% url 'faq' %}?cat=pay">🔐 <div>امنیت و پرداخت<small>اسکرو و گارانتی</small></div></a>
  </div>
  <button class="fab" id="fabBtn" aria-label="پشتیبانی">🎧<span class="fab-dot"></span></button>
</div>
<div id="toast"></div>""",
    'ویجت FAB')
replace_in('templates/base.html',
    "<span>پرداخت امن · SSL · اسکرو تضمینی 💳</span>",
    "<span>پرداخت امن · SSL · اسکرو تضمینی 💳 · <a href=\"{{ TELEGRAM_URL }}\" target=\"_blank\" style=\"color:var(--cyan)\">پشتیبانی تلگرام ✈️</a> · <a href=\"{% url 'faq' %}\" style=\"color:var(--cyan)\">سوالات متداول ❓</a></span>",
    'لینک‌های فوتر')

# ─────────── ۸) index.html: مینی‌FAQ + بنر پشتیبانی ───────────
banner('۸) بخش FAQ و پشتیبانی در صفحه اصلی')
replace_in('templates/index.html',
    "<section class=\"container reveal\"><div class=\"cta-banner\">",
    """<section class="section container reveal">
  <div class="sec-head"><div><h2 class="sec-title">سوالات <i>پرتکرار</i></h2><p class="sec-sub">جواب سریع، بدون معطلی</p></div><a href="{% url 'faq' %}" class="btn btn-glass sm">همه سوالات ←</a></div>
  <div style="display:grid;gap:12px">
    {% for f in home_faqs %}
    <div class="card acc-item"><div class="acc-head">{{ f.question }}</div><div class="acc-body"><p style="padding-top:4px">{{ f.answer }}</p></div></div>
    {% empty %}<p style="color:var(--muted)">سوالی ثبت نشده — از پنل ادمین اضافه کن.</p>{% endfor %}
  </div>
</section>

<section class="container reveal" style="padding-bottom:60px">
  <div class="card support-banner">
    <div class="sup-ico">✈️</div>
    <div style="flex:1"><h3>پشتیبانی ۲۴/۷ در تلگرام</h3>
    <p>هر ساعت از شبانه‌روز تیم نئوگیم آنلاینه — میانگین زمان پاسخ: <b style="color:var(--cyan)">زیر ۵ دقیقه</b></p></div>
    <a class="btn btn-primary" href="{{ TELEGRAM_URL }}" target="_blank" rel="noopener">گفتگو در تلگرام</a>
  </div>
</section>

<section class="container reveal"><div class="cta-banner">""",
    'مینی‌FAQ + بنر پشتیبانی')

# ─────────── ۹) صفحه faq.html ───────────
banner('۹) ساخت templates/faq.html')
(ROOT / 'templates/faq.html').write_text('''{% extends 'base.html' %}
{% block title %}سوالات متداول | نئوگیم{% endblock %}
{% block content %}
<section class="page-head container">
  <div class="crumbs"><a href="{% url 'home' %}">خانه</a> / <span>سوالات متداول</span></div>
  <h1 class="sec-title" style="font-size:2.2rem">سوالات <i>متداول</i></h1>
  <p class="sec-sub">جواب هر چی تو ذهنته اینجاست — اگه نبود، تلگرام پیام بده</p>
</section>
<div class="container" style="padding-bottom:80px">
  <div class="f-chips" style="justify-content:center;margin-bottom:30px">
    <a class="chip {% if not cat %}active{% endif %}" href="{% url 'faq' %}">همه</a>
    {% for v, t in cats %}<a class="chip {% if cat == v %}active{% endif %}" href="?cat={{ v }}">{{ t }}</a>{% endfor %}
  </div>
  <div style="max-width:820px;margin-inline:auto;display:grid;gap:12px">
    {% for f in faqs %}
    <div class="card acc-item {% if forloop.first and not cat %}open{% endif %}">
      <div class="acc-head">{{ f.question }}</div>
      <div class="acc-body"><p style="padding-top:4px">{{ f.answer }}</p>
      <span class="badge b-rare" style="margin-top:10px">{{ f.get_category_display }}</span></div>
    </div>
    {% empty %}<p style="color:var(--muted);text-align:center">سوالی در این دسته ثبت نشده.</p>{% endfor %}
  </div>
  <div class="card support-banner" style="margin-top:40px">
    <div class="sup-ico">✈️</div>
    <div style="flex:1"><h3>جوابت رو پیدا نکردی؟</h3><p>پشتیبانی ۲۴/۷ تلگرام — میانگین پاسخ زیر ۵ دقیقه</p></div>
    <a class="btn btn-primary" href="{{ TELEGRAM_URL }}" target="_blank" rel="noopener">پیام در تلگرام</a>
  </div>
</div>
{% endblock %}
''', encoding='utf-8')
ok('templates/faq.html')

# ─────────── ۱۰) CSS + JS ───────────
banner('۱۰) استایل و اسکریپت ویجت')
append_if('static/css/style.css', 'ویجت پشتیبانی شناور', """
/* ========== ویجت پشتیبانی شناور + بنر پشتیبانی ========== */
.fab-wrap{position:fixed;bottom:24px;right:24px;z-index:150;display:flex;flex-direction:column;align-items:flex-end;gap:12px}
.fab{width:60px;height:60px;border-radius:50%;border:1px solid var(--stroke2);background:linear-gradient(135deg,var(--cyan),var(--purple));font-size:1.5rem;cursor:pointer;box-shadow:0 10px 34px rgba(34,211,238,.45);position:relative;transition:.3s}
.fab:hover{transform:scale(1.08) rotate(-8deg)}
.fab-dot{position:absolute;top:4px;left:6px;width:12px;height:12px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green);animation:pulseGlow 2s infinite}
.fab-panel{min-width:260px;padding:14px;border-radius:20px;background:rgba(10,13,31,.88);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid var(--stroke2);box-shadow:0 20px 60px rgba(0,0,0,.6);display:none;flex-direction:column;gap:8px}
.fab-wrap.open .fab-panel{display:flex;animation:fadeUp .35s}
.fab-head{font-weight:900;color:var(--cyan);padding:4px 8px;display:flex;justify-content:space-between;align-items:center}
.fab-item{display:flex;gap:10px;align-items:center;padding:10px 12px;border-radius:14px;background:var(--glass);border:1px solid var(--stroke);transition:.3s;font-size:.88rem}
.fab-item:hover{border-color:var(--cyan);transform:translateX(-4px)}
.fab-item small{display:block;color:var(--dim);font-size:.72rem}
.support-banner{display:flex;align-items:center;gap:22px;padding:30px 34px;flex-wrap:wrap;background:linear-gradient(120deg,rgba(34,211,238,.14),rgba(139,92,246,.14)),var(--glass);border:1px solid var(--stroke2)}
.support-banner p{color:var(--muted);font-size:.9rem}
.sup-ico{width:70px;height:70px;flex:none;border-radius:22px;display:grid;place-items:center;font-size:2rem;background:linear-gradient(135deg,var(--cyan),var(--purple));box-shadow:0 0 30px rgba(34,211,238,.5);animation:floaty 5s ease-in-out infinite}
""", 'CSS ویجت')

append_if('static/js/app.js', 'ویجت پشتیبانی', """
/* ===== ویجت پشتیبانی ===== */
const fabBtn=$('#fabBtn'),fabWrap=$('#fabWrap');
fabBtn&&fabBtn.addEventListener('click',e=>{e.stopPropagation();fabWrap.classList.toggle('open')});
document.addEventListener('click',e=>{if(fabWrap&&!fabWrap.contains(e.target))fabWrap.classList.remove('open')});
""", 'JS ویجت')

# ─────────── ۱۱) seed سوالات ───────────
banner('۱۱) داده‌های اولیه FAQ')
(ROOT / 'seed_faq.py').write_text('''import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neogame.settings')
django.setup()
from core.models import FAQ
if not FAQ.objects.exists():
    F = FAQ.objects.create
    F(category='buy',  order=1, show_home=True,  question='چطور یک آیتم بخرم؟',
      answer='کافیه آیتم رو به سبد اضافه کنی، در صفحه تکمیل سفارش آیدی بازی و زمان ترید رو وارد کنی و پرداخت کنی. بقیه‌ش با ما!')
    F(category='buy',  order=2, show_home=True,  question='تحویل آیتم چقدر طول می‌کشه؟',
      answer='ترید دقیقاً در بازه‌ی زمانی انتخابی خودت انجام می‌شه؛ ادمین همون ساعت آنلاین می‌شه و معمولاً کل فرآیند زیر ۳۰ دقیقه‌ست.')
    F(category='boost',order=3, show_home=True,  question='آیا بوست اکانت امنه؟',
      answer='بله. بوسترها با VPN اختصاصی و بدون هیچ چیتی وارد می‌شن. تا امروز حتی یک مورد بن هم گزارش نشده.')
    F(category='boost',order=4, question='بوست چقدر طول می‌کشه؟',
      answer='بسته به اختلاف رنک بین ۱ تا ۵ روز. با گزینه «اولویت بالا» تا ۳۰٪ سریع‌تر می‌شه.')
    F(category='trade',order=5, show_home=True,  question='اسکرو امن یعنی چی؟',
      answer='پول خریدار تا زمانی که تحویل رو تأیید نکنه نزد نئوگیم امانت می‌مونه؛ پس هیچ‌کس نمی‌تونه کلاهبرداری کنه.')
    F(category='trade',order=6, question='اگه فروشنده اکانت رو پس بگیره چی؟',
      answer='گارانتی ۳۰ روزه داریم؛ اگر اکانت پس گرفته شد، ۱۰۰٪ مبلغ رو برمی‌گردونیم.')
    F(category='pay',  order=7, question='چه روش‌های پرداختی دارید؟',
      answer='کارت‌به‌کارت، درگاه آنلاین و ارز دیجیتال — همه از طریق اسکرو امن.')
    F(category='pay',  order=8, question='اگه سفارش تحویل نشد پولم برمی‌گرده؟',
      answer='بله، ۱۰۰٪ بازگشت وجه بدون قید و شرط، معمولاً زیر ۲ ساعت.')
    F(category='sup',  order=9, show_home=True,  question='چطور با پشتیبانی تماس بگیرم؟',
      answer='دکمه شناور 🎧 گوشه صفحه رو بزن یا مستقیم در تلگرام پیام بده. ۲۴ ساعته، هر ۷ روز هفته، میانگین پاسخ زیر ۵ دقیقه.')
    print('  ✔ ۹ سوال متداول ساخته شد')
else:
    print('  ✔ سوالات قبلاً وجود داره')
''', encoding='utf-8')
subprocess.run([str(PY), 'seed_faq.py'], cwd=ROOT, check=True)

# ─────────── ۱۲) migrate + اجرا ───────────
banner('۱۲) مهاجرت دیتابیس')
subprocess.run([str(PY), 'manage.py', 'makemigrations', 'core'], cwd=ROOT, check=True)
subprocess.run([str(PY), 'manage.py', 'migrate'], cwd=ROOT, check=True)
ok('دیتابیس به‌روز شد')

banner('✅ FAQ و پشتیبانی ۲۴/۷ فعال شد!')
print('''
  ❓ سوالات متداول:
     • صفحه کامل:  http://127.0.0.1:8000/faq/  (با فیلتر دسته‌بندی)
     • مینی‌FAQ در صفحه اصلی (قبل از بنر CTA)
     • مدیریت از ادمین: /admin → سوالات متداول
       (ترتیب، دسته و «نمایش در صفحه اصلی» رو اونجا تنظیم کن)

  🎧 پشتیبانی تلگرام:
     • ویجت شناور گوشه‌ی همه‌ی صفحات (دکمه 🎧 با نقطه سبز «آنلاین»)
     • بنر پشتیبانی در صفحه اصلی + انتهای صفحه FAQ + فوتر
     • ✏️ تغییر آیدی تلگرام: neogame/settings.py → TELEGRAM_SUPPORT_URL

  📁 بکاپ: {b}
'''.format(b=BACKUP_DIR))

ans = input('  سرور الان استارت بشه؟ (y/n): ').strip().lower()
if ans in ('y', 'yes', 'بله', 'آره', ''):
    threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:8000/faq/')).start()
    try:
        subprocess.run([str(PY), 'manage.py', 'runserver', '0.0.0.0:8000'], cwd=ROOT)
    except KeyboardInterrupt:
        print('\nخداحافظ 👋')
else:
    print('\n  برای اجرا:  python manage.py runserver')