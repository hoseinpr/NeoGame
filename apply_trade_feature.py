# -*- coding: utf-8 -*-
# ⬡ نئوگیم — اعمال قابلیت ترید با آیدی بازی و زمان‌بندی
# این فایل را در پوشه اصلی پروژه (کنار manage.py) بگذارید و اجرا کنید: python apply_trade_feature.py
import os, sys, shutil, subprocess, webbrowser, threading
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
VENV = ROOT / '.venv'
PY = VENV / ('Scripts\\python.exe' if os.name == 'nt' else 'bin/python')
BACKUP_DIR = ROOT / '_backups' / datetime.now().strftime('%Y%m%d_%H%M%S')

def banner(t): print('\n' + '═'*55 + f'\n  {t}\n' + '═'*55)
def ok(t): print(f'  ✔ {t}')
def fail(t): print(f'  ✖ {t}'); sys.exit(1)

# ───────────────────────── بررسی پیش‌نیازها ─────────────────────────
banner('۱) بررسی پیش‌نیازها')
for need in ['manage.py', 'core/models.py', 'core/views.py', 'core/admin.py',
             'templates/cart.html', 'templates/dashboard.html']:
    if not (ROOT / need).exists():
        fail(f'فایل {need} پیدا نشد! اسکریپت باید در پوشه اصلی پروژه اجرا شود.')
if not PY.exists():
    fail('محیط مجازی (.venv) پیدا نشد! اول bootstrap.py را اجرا کنید.')
ok('ساختار پروژه صحیح است')

# ───────────────────────── پشتیبان‌گیری ─────────────────────────
banner('۲) پشتیبان‌گیری از فایل‌ها')
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
backup_files = ['core/models.py', 'core/views.py', 'core/admin.py',
                'templates/cart.html', 'templates/dashboard.html']
for f in backup_files:
    src = ROOT / f
    dst = BACKUP_DIR / f
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
ok(f'بکاپ در: {BACKUP_DIR}')

# ───────────────────────── ابزارهای تغییر فایل ─────────────────────────
def replace_in(path, old, new, desc):
    p = ROOT / path
    txt = p.read_text(encoding='utf-8')
    if old not in txt:
        print(f'  ⚠ الگوی قبلی در {path} پیدا نشد (ممکن است قبلاً اعمال شده باشد)')
        return False
    if new in txt:
        print(f'  ⚠ تغییر قبلاً روی {path} اعمال شده')
        return False
    p.write_text(txt.replace(old, new), encoding='utf-8')
    ok(f'{desc} → {path}')
    return True

# ───────────────────────── ۳) تغییر models.py ─────────────────────────
banner('۳) تغییر core/models.py')

# اضافه کردن DELIVERY_SLOTS قبل از کلاس Order و افزودن فیلدها
old_order_model = '''class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='کاربر')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='آیتم')
    qty = models.PositiveIntegerField(default=1)
    total = models.FloatField()
    status = models.CharField(max_length=15, choices=STATUS, default='pending')
    created = models.DateTimeField(auto_now_add=True)'''

new_order_model = '''DELIVERY_SLOTS = [
    ('10:00-12:00', '۱۰:۰۰ تا ۱۲:۰۰'),
    ('12:00-14:00', '۱۲:۰۰ تا ۱۴:۰۰'),
    ('14:00-16:00', '۱۴:۰۰ تا ۱۶:۰۰'),
    ('16:00-18:00', '۱۶:۰۰ تا ۱۸:۰۰'),
    ('18:00-20:00', '۱۸:۰۰ تا ۲۰:۰۰'),
    ('20:00-22:00', '۲۰:۰۰ تا ۲۲:۰۰'),
    ('22:00-00:00', '۲۲:۰۰ تا ۲۴:۰۰'),
    ('00:00-02:00', '۰۰:۰۰ تا ۰۲:۰۰'),
]

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='کاربر')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='آیتم')
    qty = models.PositiveIntegerField(default=1)
    total = models.FloatField()
    status = models.CharField(max_length=15, choices=STATUS, default='pending')
    game_username = models.CharField('آیدی درون بازی', max_length=100, blank=True)
    delivery_slot = models.CharField('زمان ترید', max_length=20, choices=DELIVERY_SLOTS, blank=True)
    delivery_notes = models.TextField('توضیحات تحویل', blank=True)
    created = models.DateTimeField(auto_now_add=True)'''

replace_in('core/models.py', old_order_model, new_order_model, 'افزودن DELIVERY_SLOTS و فیلدهای جدید')

# ───────────────────────── ۴) تغییر views.py ─────────────────────────
banner('۴) تغییر core/views.py')

old_checkout = '''@login_required
def checkout(r):
    cart = r.session.get('cart', {})
    if not cart:
        messages.error(r, 'سبد خرید خالی است')
        return redirect('cart')
    for iid, qty in cart.items():
        it = Item.objects.get(id=iid)
        Order.objects.create(user=r.user, item=it, qty=qty, total=round(it.price * qty, 2))
    r.session['cart'] = {}
    messages.success(r, 'پرداخت موفق — سفارش‌ها ثبت شد 🎉')
    return redirect('dashboard')'''

new_checkout = '''def checkout(r):
    cart = r.session.get('cart', {})
    if not cart:
        messages.error(r, 'سبد خرید خالی است')
        return redirect('cart')

    rows, total = [], 0
    for iid, qty in cart.items():
        it = Item.objects.get(id=iid)
        rows.append({'item': it, 'qty': qty, 'sum': it.price * qty})
        total += it.price * qty

    if r.method == 'POST':
        if not r.user.is_authenticated:
            messages.error(r, 'اول وارد حساب شو 🔐')
            return redirect('login')
        game_username = r.POST.get('game_username', '').strip()
        delivery_slot = r.POST.get('delivery_slot', '').strip()
        notes = r.POST.get('delivery_notes', '').strip()

        if not game_username:
            messages.error(r, 'لطفاً آیدی درون بازی رو وارد کن')
        elif not delivery_slot:
            messages.error(r, 'لطفاً زمان ترید رو انتخاب کن')
        else:
            for iid, qty in cart.items():
                it = Item.objects.get(id=iid)
                Order.objects.create(
                    user=r.user, item=it, qty=qty,
                    total=round(it.price * qty, 2),
                    game_username=game_username,
                    delivery_slot=delivery_slot,
                    delivery_notes=notes)
            r.session['cart'] = {}
            messages.success(r, f'سفارش ثبت شد — ادمین در زمان {delivery_slot} با آیدی {game_username} ترید می‌کنه 🎮')
            return redirect('dashboard')

    from .models import DELIVERY_SLOTS
    return render(r, 'checkout.html', {'rows': rows, 'total': total, 'slots': DELIVERY_SLOTS})'''

replace_in('core/views.py', old_checkout, new_checkout, 'تابع checkout جدید')

# ───────────────────────── ۵) تغییر admin.py ─────────────────────────
banner('۵) تغییر core/admin.py')

old_admin = 'admin.site.register(Order)'

new_admin = '''@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item', 'qty', 'game_username', 'delivery_slot', 'status', 'total', 'created')
    list_filter = ('status', 'delivery_slot', 'item__game')
    search_fields = ('user__username', 'game_username', 'item__name')
    list_editable = ('status',)
    readonly_fields = ('created',)

    fieldsets = (
        ('اطلاعات کاربر', {'fields': ('user', 'item', 'qty', 'total')}),
        ('اطلاعات ترید', {'fields': ('game_username', 'delivery_slot', 'delivery_notes')}),
        ('وضعیت', {'fields': ('status', 'created')}),
    )'''

replace_in('core/admin.py', old_admin, new_admin, 'OrderAdmin پیشرفته')

# ───────────────────────── ۶) تغییر cart.html ─────────────────────────
banner('۶) تغییر templates/cart.html')

old_cart_btn = '''<form method="post" action="{% url 'checkout' %}" style="margin-top:20px;text-align:center">{% csrf_token %}
    <button class="btn btn-primary">💳 پرداخت و ثبت سفارش</button>
  </form>'''

new_cart_btn = '''<div style="margin-top:20px;text-align:center">
    <a href="{% url 'checkout' %}" class="btn btn-primary">💳 ادامه به اطلاعات تحویل</a>
  </div>'''

replace_in('templates/cart.html', old_cart_btn, new_cart_btn, 'دکمه سبد خرید')

# ───────────────────────── ۷) تغییر dashboard.html ─────────────────────────
banner('۷) تغییر templates/dashboard.html')

old_dash_table = '''<table><thead><tr><th>شناسه</th><th>آیتم</th><th>تعداد</th><th>وضعیت</th><th>مبلغ</th></tr></thead><tbody>
        {% for o in orders %}<tr><td>#{{ o.id }}</td><td>{{ o.item.icon }} {{ o.item.name }}</td><td>{{ o.qty }}</td>
        <td><span class="st {% if o.status == 'done' %}st-ok{% elif o.status == 'processing' %}st-run{% else %}st-wait{% endif %}">{{ o.get_status_display }}</span></td>
        <td style="color:var(--cyan)">${{ o.total|floatformat:2 }}</td></tr>{% empty %}<tr><td colspan="5" style="text-align:center">هنوز سفارشی نداری 😕</td></tr>{% endfor %}
      </tbody></table>'''

new_dash_table = '''<table><thead><tr><th>شناسه</th><th>آیتم</th><th>آیدی بازی</th><th>زمان ترید</th><th>وضعیت</th><th>مبلغ</th></tr></thead><tbody>
        {% for o in orders %}<tr><td>#{{ o.id }}</td><td>{{ o.item.icon }} {{ o.item.name }}</td>
        <td style="color:var(--cyan)">{{ o.game_username|default:'-' }}</td>
        <td style="color:var(--violet)">{{ o.get_delivery_slot_display|default:'-' }}</td>
        <td><span class="st {% if o.status == 'done' %}st-ok{% elif o.status == 'processing' %}st-run{% else %}st-wait{% endif %}">{{ o.get_status_display }}</span></td>
        <td style="color:var(--cyan)">${{ o.total|floatformat:2 }}</td></tr>{% empty %}<tr><td colspan="6" style="text-align:center">هنوز سفارشی نداری 😕</td></tr>{% endfor %}
      </tbody></table>'''

replace_in('templates/dashboard.html', old_dash_table, new_dash_table, 'جدول داشبورد')

# ───────────────────────── ۸) ساخت checkout.html ─────────────────────────
banner('۸) ساخت templates/checkout.html')

checkout_html = '''{% extends 'base.html' %}
{% block title %}تکمیل سفارش | نئوگیم{% endblock %}
{% block content %}
<section class="page-head container">
  <div class="crumbs"><a href="{% url 'home' %}">خانه</a> / <a href="{% url 'cart' %}">سبد</a> / <span>تکمیل سفارش</span></div>
  <h1 class="sec-title" style="font-size:2.2rem">اطلاعات <i>تحویل</i></h1>
  <p class="sec-sub">آیدی بازی و زمان ترید رو وارد کن تا ادمین در اون ساعت آنلاین باشه</p>
</section>

<div class="container boost-grid" style="padding-bottom:80px">
  <form method="post" class="card calc">{% csrf_token %}
    <h3 style="margin-bottom:18px">📝 اطلاعات ترید</h3>

    <label>🎮 آیدی درون بازی (دقیق وارد کن)</label>
    <div class="field" style="margin:0">
      <span class="f-icon">👤</span>
      <input name="game_username" placeholder="مثلاً: NeoGamer#1234" required>
    </div>

    <label>⏰ زمان ترید (ادمین توی این ساعت آنلاین می‌شه)</label>
    <select name="delivery_slot" required>
      <option value="">یک بازه‌ی زمانی انتخاب کن</option>
      {% for val, label in slots %}
        <option value="{{ val }}">{{ label }}</option>
      {% endfor %}
    </select>

    <label>📌 توضیحات اضافی (اختیاری)</label>
    <div class="field" style="margin:0">
      <textarea name="delivery_notes" placeholder="مثلاً: در سرور اروپا بازی می‌کنم، یا: فقط از طریق Trade Window ترید می‌کنم..."></textarea>
    </div>

    <div style="padding:18px;border-radius:14px;background:rgba(34,211,238,.08);border:1px dashed var(--cyan);margin-top:20px">
      <div style="color:var(--muted);font-size:.88rem">
        ✅ ادمین در بازه‌ی انتخابی شما آنلاین می‌شه<br>
        ✅ ترید فقط از طریق سیستم رسمی بازی انجام می‌شه<br>
        ✅ تا قبل از تحویل، پول شما در اسکرو امانت است<br>
        ✅ در صورت عدم تحویل، ۱۰۰٪ بازگشت وجه
      </div>
    </div>

    <button class="btn btn-primary" style="width:100%;margin-top:20px">💳 تأیید و پرداخت</button>
  </form>

  <div class="card summary">
    <small style="color:var(--muted)">خلاصه سفارش</small>
    <div class="big">${{ total|floatformat:2 }}</div>

    <div style="margin-top:20px;text-align:right">
      {% for row in rows %}
      <div class="sum-row">
        <span>{{ row.item.icon }} {{ row.item.name }} × {{ row.qty }}</span>
        <span style="color:var(--cyan)">${{ row.sum|floatformat:2 }}</span>
      </div>
      {% endfor %}
    </div>

    <div style="margin-top:20px;padding:14px;border-radius:12px;background:rgba(0,0,0,.3);border:1px solid var(--stroke)">
      <small style="color:var(--muted);display:block;margin-bottom:8px">🔐 پرداخت امن</small>
      <p style="color:var(--muted);font-size:.82rem">پول تا زمان تأیید تحویل توسط شما، نزد نئوگیم امانت می‌مونه.</p>
    </div>
  </div>
</div>
{% endblock %}
'''

chk_path = ROOT / 'templates/checkout.html'
chk_path.write_text(checkout_html, encoding='utf-8')
ok('templates/checkout.html ساخته شد')

# ───────────────────────── ۹) migrate دیتابیس ─────────────────────────
banner('۹) مهاجرت دیتابیس')

def run_manage(*args):
    subprocess.run([str(PY), 'manage.py', *args], cwd=ROOT, check=True)

run_manage('makemigrations', 'core')
run_manage('migrate')
ok('دیتابیس به‌روز شد')

# ───────────────────────── ۱۰) ری‌استارت سرور ─────────────────────────
banner('✅ همه‌چیز اعمال شد!')
print('''
  🎮 قابلیت جدید فعال شد:

  ✨ کاربر موقع checkout:
     • آیدی بازی رو وارد می‌کنه
     • زمان دلخواه ترید رو انتخاب می‌کنه

  🛠️ ادمین در پنل /admin می‌بینه:
     • آیدی بازی هر کاربر
     • زمان ترید (فیلتر و جستجو داره)
     • می‌تونه وضعیت رو سریع عوض کنه

  📊 کاربر در داشبورد می‌بینه:
     • آیدی بازی خودش
     • زمان ترید انتخابی
     • وضعیت سفارش

  ⏰ زمان‌های ترید:
     • ۱۰-۱۲، ۱۲-۱۴، ۱۴-۱۶، ۱۶-۱۸
     • ۱۸-۲۰، ۲۰-۲۲، ۲۲-۲۴، ۰۰-۰۲

  📁 بکاپ فایل‌های قبلی:
     • {backup}

  حالا سرور رو دوباره اجرا کن:
     python manage.py runserver
'''.format(backup=BACKUP_DIR))

ans = input('  می‌خوای سرور الان استارت بشه؟ (y/n): ').strip().lower()
if ans in ('y', 'yes', 'آره', 'بله', ''):
    threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:8000/cart/')).start()
    try:
        run_manage('runserver', '0.0.0.0:8000')
    except KeyboardInterrupt:
        print('\nخداحافظ 👋')
else:
    print('\n  برای اجرا:  python manage.py runserver')