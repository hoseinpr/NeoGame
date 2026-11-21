# -*- coding: utf-8 -*-
# ⬡ نئوگیم — بوت‌استرپ جنگو
# این فایل را داخل پوشه neogame (کنار css/ و js/) بگذارید و اجرا کنید:  python bootstrap.py
import os, sys, shutil, subprocess, webbrowser, threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / '.venv'
PY = VENV / ('Scripts\\python.exe' if os.name == 'nt' else 'bin/python')

def banner(t): print('\n' + '═'*50 + f'\n  {t}\n' + '═'*50)

def W(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    print('  ✔', rel)

def run(*a): subprocess.run([str(PY), *a], cwd=ROOT, check=True)

# ───────────────────────── ۱) venv + نصب جنگو ─────────────────────────
banner('۱) ساخت محیط مجازی و نصب Django')
if not VENV.exists():
    subprocess.run([sys.executable, '-m', 'venv', str(VENV)], check=True)
run('-m', 'pip', 'install', '-q', '--upgrade', 'pip')
run('-m', 'pip', 'install', '-q', 'django')
print('  ✔ Django نصب شد')

# ───────────────────────── ۲) انتقال فرانت به static ─────────────────────────
banner('۲) انتقال CSS/JS به static')
for src, dst in [('css', 'static/css'), ('js', 'static/js')]:
    s = ROOT / src
    if not s.exists():
        sys.exit(f'  ✖ پوشه {src}/ پیدا نشد! این اسکریپت باید کنار پوشه‌های css/ و js/ اجرا بشه.')
    shutil.copytree(s, ROOT / dst, dirs_exist_ok=True)
    print('  ✔', dst)

# ───────────────────────── ۳) فایل‌های پروژه ─────────────────────────
banner('۳) ساخت پروژه Django')

W('manage.py', '''#!/usr/bin/env python
import os, django
from django.core.management import execute_from_command_line
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neogame.settings')
    execute_from_command_line()
''')

W('neogame/__init__.py', '')
W('neogame/wsgi.py', '''import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neogame.settings')
application = get_wsgi_application()
''')
W('neogame/asgi.py', '''import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neogame.settings')
application = get_asgi_application()
''')

W('neogame/settings.py', '''from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-neogame-neon-liquid-glass'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'core',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
ROOT_URLCONF = 'neogame.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'core.context_processors.cart_count',
    ]},
}]
WSGI_APPLICATION = 'neogame.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'fa'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
''')

W('neogame/urls.py', '''from django.contrib import admin
from django.urls import path
from core import views as v
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', v.home, name='home'),
    path('market/', v.market, name='market'),
    path('item/<int:id>/', v.product, name='product'),
    path('cart/add/<int:id>/', v.cart_add, name='cart_add'),
    path('cart/', v.cart, name='cart'),
    path('checkout/', v.checkout, name='checkout'),
    path('boost/', v.boost, name='boost'),
    path('trade/', v.trade, name='trade'),
    path('login/', v.login_v, name='login'),
    path('register/', v.register, name='register'),
    path('logout/', v.logout_v, name='logout'),
    path('dashboard/', v.dashboard, name='dashboard'),
]
''')

# ───────────────────────── ۴) اپ core ─────────────────────────
W('core/__init__.py', '')
W('core/apps.py', '''from django.apps import AppConfig
class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
''')

W('core/models.py', '''from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

RARITIES = [('gold', 'افسانه‌ای'), ('epic', 'اپیک'), ('rare', 'کمیاب')]
RANKS = [(0, '🥉 برنز'), (1, '🥈 سیلور'), (2, '🥇 گلد'), (3, '💎 پلاتین'), (4, '👑 الماس')]
BASE_PRICE = [29, 59, 99, 149, 199]
STATUS = [('pending', 'در انتظار'), ('processing', 'در حال انجام'), ('done', 'تکمیل')]

def boost_price(cur, tgt, priority=False, stream=False):
    if tgt <= cur: return 0
    p = BASE_PRICE[tgt] - BASE_PRICE[cur]
    if priority: p *= 1.25
    if stream: p *= 1.1
    return round(p, 2)

class Game(models.Model):
    name = models.CharField('نام', max_length=50)
    slug = models.SlugField(unique=True)
    icon = models.CharField('آیکون', max_length=10)
    color = models.CharField('رنگ', max_length=20)
    tagline = models.CharField('توضیح', max_length=100)
    def __str__(self): return self.name

class Item(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='items', verbose_name='بازی')
    name = models.CharField('نام آیتم', max_length=100)
    icon = models.CharField('آیکون', max_length=10)
    rarity = models.CharField('کمیابی', max_length=10, choices=RARITIES, default='rare')
    price = models.FloatField('قیمت')
    old_price = models.FloatField('قیمت قبلی', null=True, blank=True)
    description = models.TextField('توضیحات', blank=True)
    featured = models.BooleanField('ویژه', default=False)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    wallet = models.FloatField('کیف پول', default=25.0)

@receiver(post_save, sender=User)
def make_profile(s, i, **k): Profile.objects.get_or_create(user=i)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='کاربر')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='آیتم')
    qty = models.PositiveIntegerField(default=1)
    total = models.FloatField()
    status = models.CharField(max_length=15, choices=STATUS, default='pending')
    created = models.DateTimeField(auto_now_add=True)

class BoostOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boosts', verbose_name='کاربر')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name='بازی')
    cur = models.SmallIntegerField('رنک فعلی')
    tgt = models.SmallIntegerField('رنک مقصد')
    priority = models.BooleanField(default=False)
    stream = models.BooleanField(default=False)
    price = models.FloatField()
    status = models.CharField(max_length=15, choices=STATUS, default='pending')
    created = models.DateTimeField(auto_now_add=True)

class AccountListing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', null=True, blank=True, verbose_name='فروشنده')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name='بازی')
    title = models.CharField('عنوان', max_length=100)
    icon = models.CharField('آیکون', max_length=10)
    stats = models.CharField('مشخصات', max_length=100, blank=True)
    price = models.FloatField('قیمت')
    verified = models.BooleanField('وریفای', default=False)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews', verbose_name='آیتم')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    rating = models.SmallIntegerField(default=5)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
''')

W('core/context_processors.py', '''def cart_count(r):
    return {'cart_count': len(r.session.get('cart', {}))}
''')

W('core/admin.py', '''from django.contrib import admin
from .models import Game, Item, Profile, Order, BoostOrder, AccountListing, Review
admin.site.site_header = '⬡ مدیریت نئوگیم'
admin.site.register(Game)
admin.site.register(Item)
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(BoostOrder)
admin.site.register(AccountListing)
admin.site.register(Review)
''')

W('core/views.py', '''from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Game, Item, Order, BoostOrder, AccountListing, RANKS, boost_price

def home(r):
    return render(r, 'index.html', {'games': Game.objects.all(),
                                    'featured': Item.objects.filter(featured=True)[:4]})

def market(r):
    qs = Item.objects.all().select_related('game')
    q = r.GET.get('q')
    if q: qs = qs.filter(name__icontains=q)
    gm = r.GET.getlist('game')
    if gm: qs = qs.filter(game__slug__in=gm)
    rr = r.GET.getlist('rarity')
    if rr: qs = qs.filter(rarity__in=rr)
    maxp = r.GET.get('maxp')
    if maxp: qs = qs.filter(price__lte=float(maxp))
    sort = r.GET.get('sort', 'new')
    if sort == 'cheap': qs = qs.order_by('price')
    elif sort == 'exp': qs = qs.order_by('-price')
    else: qs = qs.order_by('-created')
    return render(r, 'market.html', {'items': qs, 'games': Game.objects.all(),
                                     'q': q or '', 'maxp': maxp or 200, 'sort': sort})

def product(r, id):
    it = get_object_or_404(Item, id=id)
    return render(r, 'product.html', {'item': it, 'reviews': it.reviews.all(),
                                      'related': Item.objects.filter(game=it.game).exclude(id=it.id)[:3]})

@login_required
def cart_add(r, id):
    cart = r.session.get('cart', {})
    cart[str(id)] = cart.get(str(id), 0) + 1
    r.session['cart'] = cart
    messages.success(r, 'به سبد خرید اضافه شد ✅')
    return redirect('cart' if 'buy' in r.GET else 'cart')

def cart(r):
    rows, total = [], 0
    for iid, qty in r.session.get('cart', {}).items():
        it = Item.objects.get(id=iid)
        rows.append({'item': it, 'qty': qty, 'sum': it.price * qty})
        total += it.price * qty
    return render(r, 'cart.html', {'rows': rows, 'total': total})

@login_required
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
    return redirect('dashboard')

def boost(r):
    if r.method == 'POST':
        if not r.user.is_authenticated:
            messages.error(r, 'اول وارد حساب شو 🔐')
            return redirect('login')
        g = get_object_or_404(Game, id=r.POST['game'])
        cur, tgt = int(r.POST['cur']), int(r.POST['tgt'])
        pr, st = 'priority' in r.POST, 'stream' in r.POST
        price = boost_price(cur, tgt, pr, st)
        if price <= 0:
            messages.error(r, 'رنک مقصد باید بالاتر از فعلی باشد')
        else:
            BoostOrder.objects.create(user=r.user, game=g, cur=cur, tgt=tgt,
                                      priority=pr, stream=st, price=price)
            messages.success(r, f'سفارش بوست با قیمت ${price} ثبت شد ⚡')
            return redirect('dashboard')
    return render(r, 'boost.html', {'games': Game.objects.all(), 'ranks': RANKS})

def trade(r):
    if r.method == 'POST':
        if not r.user.is_authenticated:
            messages.error(r, 'اول وارد حساب شو 🔐')
            return redirect('login')
        g = get_object_or_404(Game, id=r.POST['game'])
        AccountListing.objects.create(seller=r.user, game=g, title=r.POST['title'],
                                      icon=g.icon, stats=r.POST.get('stats', ''),
                                      price=float(r.POST['price']))
        messages.success(r, 'آگهی ثبت شد — پس از بررسی منتشر می‌شه ✅')
        return redirect('trade')
    return render(r, 'trade.html', {'listings': AccountListing.objects.all().select_related('game', 'seller')})

def login_v(r):
    if r.method == 'POST':
        u = authenticate(r, username=r.POST['username'], password=r.POST['password'])
        if u:
            dj_login(r, u)
            messages.success(r, 'ورود موفق 🎮')
            return redirect('dashboard')
        messages.error(r, 'نام کاربری یا رمز اشتباهه')
    return render(r, 'auth.html')

def register(r):
    if r.method == 'POST':
        u, p, p2 = r.POST['username'], r.POST['password'], r.POST.get('password2', '')
        if User.objects.filter(username=u).exists():
            messages.error(r, 'این نام کاربری قبلاً ثبت شده')
        elif len(p) < 4 or p != p2:
            messages.error(r, 'رمز حداقل ۴ کاراکتر و تکرارش یکسان باشه')
        else:
            user = User.objects.create_user(u, r.POST.get('email', ''), p)
            dj_login(r, user)
            messages.success(r, 'حساب ساخته شد — خوش اومدی 🎉')
            return redirect('dashboard')
    return render(r, 'auth.html')

def logout_v(r):
    dj_logout(r)
    messages.success(r, 'خروج موفق 👋')
    return redirect('home')

@login_required
def dashboard(r):
    return render(r, 'dashboard.html', {
        'orders': Order.objects.filter(user=r.user).select_related('item'),
        'boosts': BoostOrder.objects.filter(user=r.user).select_related('game'),
        'listings': AccountListing.objects.filter(seller=r.user),
        'wallet': r.user.profile.wallet})
''')

# ───────────────────────── ۵) تمپلیت‌ها ─────────────────────────
banner('۵) ساخت تمپلیت‌ها')

W('templates/base.html', '''{% load static %}<!DOCTYPE html>
<html lang="fa" dir="rtl"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{% block title %}نئوگیم | مارکت آیتم بازی{% endblock %}</title>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{% static 'css/style.css' %}">
</head><body>
<div class="bg"><span class="orb a"></span><span class="orb b"></span><span class="orb c"></span><span class="grid-floor"></span><span class="noise"></span></div>
<header class="nav-wrap"><div class="nav"><div class="nav-in">
  <a class="logo" href="{% url 'home' %}"><span class="logo-mark">⬡</span> نئوگیم</a>
  <ul class="links" id="navLinks">
    <li><a href="{% url 'home' %}">خانه</a></li>
    <li><a href="{% url 'market' %}">مارکت آیتم</a></li>
    <li><a href="{% url 'boost' %}">بوست اکانت</a></li>
    <li><a href="{% url 'trade' %}">خرید و فروش اکانت</a></li>
  </ul>
  <div class="nav-actions">
    <a class="icon-btn" href="{% url 'cart' %}">🛒<span class="dot">{{ cart_count }}</span></a>
    {% if user.is_authenticated %}
      <a href="{% url 'dashboard' %}" class="btn btn-glass sm">🥷 {{ user.username }}</a>
    {% else %}
      <a href="{% url 'login' %}" class="btn btn-glass sm">ورود | ثبت‌نام</a>
    {% endif %}
    <button class="menu-btn" id="menuBtn">☰</button>
  </div>
</div></div></header>
{% block content %}{% endblock %}
<footer class="footer"><div class="container">
  <div class="f-bottom"><span>نئوگیم © ۲۰۲۶ — Django + Neon/Liquid Glass ⬡</span><span>پرداخت امن · SSL · اسکرو تضمینی 💳</span></div>
</div></footer>
<div id="toast"></div>
<script src="{% static 'js/app.js' %}"></script>
{% for m in messages %}<script>toast("{{ m }}")</script>{% endfor %}
</body></html>
''')

W('templates/includes/item.html', '''<a href="{% url 'product' item.id %}" class="card item" style="--edge:{% if item.rarity == 'gold' %}#fbbf24{% elif item.rarity == 'epic' %}#c084fc{% else %}#22d3ee{% endif %}">
  <span class="badge b-{{ item.rarity }}">{{ item.get_rarity_display }}</span>
  <div class="art">{{ item.icon }}</div><h4>{{ item.name }}</h4><span class="tag">{{ item.game.name }}</span>
  <div class="item-foot">
    <div><span class="price">${{ item.price|floatformat:2 }}</span>{% if item.old_price %}<span class="old">${{ item.old_price|floatformat:2 }}</span>{% endif %}</div>
    <form method="post" action="{% url 'cart_add' item.id %}" onsubmit="event.stopPropagation()">{% csrf_token %}<button class="add-btn">+</button></form>
  </div>
</a>
''')

W('templates/index.html', '''{% extends 'base.html' %}{% block content %}
<section class="hero container"><div class="hero-grid">
  <div>
    <span class="eyebrow">آنلاین — ۱۲۴ کاربر فعال</span>
    <h1 class="hero-title">مارکت آیتم‌های بازی<br><span class="grad">سریع، امن، نئونی</span></h1>
    <p class="hero-sub">خرید و فروش آیتم‌های Warframe ،Dota 2 و Albion Online + بوست حرفه‌ای اکانت با تحویل آنی و اسکرو امن.</p>
    <form class="search" method="get" action="{% url 'market' %}"><input name="q" placeholder="جستجوی آیتم، بازی یا اکانت..."><button class="btn btn-primary sm">جستجو</button></form>
    <div class="hero-cta"><a href="{% url 'market' %}" class="btn btn-primary">🛒 خرید آیتم</a><a href="{% url 'trade' %}" class="btn btn-neon">💰 فروش اکانت</a></div>
    <div class="stats">
      <div class="stat"><b>+۱۲٬۵۰۰</b><span>کاربر فعال</span></div>
      <div class="stat"><b>+۴۸٬۰۰۰</b><span>سفارش تکمیل‌شده</span></div>
      <div class="stat"><b>۹۹٫۸٪</b><span>رضایت مشتری</span></div>
      <div class="stat"><b>۲۴/۷</b><span>پشتیبانی</span></div>
    </div>
  </div>
  <div class="hero-visual">
    <div class="ring"></div><div class="ring-core">🎮</div>
    <div class="float-card f1">🗡️ شمشیر آذرخش <b>$۲۴٫۹۹</b></div>
    <div class="float-card f2">🥇 ← 💎 بوست موفق ✅</div>
    <div class="float-card f3">⭐ <b>۴٫۹</b> از ۲٬۳۰۰ نظر</div>
  </div>
</div></section>

<section class="section container reveal">
  <div class="sec-head"><div><h2 class="sec-title">بازی‌های <i>محبوب</i></h2></div><a href="{% url 'market' %}" class="btn btn-glass sm">مشاهده همه ←</a></div>
  <div class="games-grid">
    {% for g in games %}
    <a href="{% url 'market' %}?game={{ g.slug }}" class="card game-card" style="--edge:{{ g.color }}">
      <div class="g-art">{{ g.icon }}</div>
      <div class="g-body"><h3>{{ g.name }}</h3><p>{{ g.tagline }}</p>
      <div class="g-meta"><span>{{ g.items.count }}+ آیتم</span><span style="color:var(--cyan)">ورود ←</span></div></div>
    </a>
    {% endfor %}
  </div>
</section>

<section class="section container reveal">
  <div class="sec-head"><div><h2 class="sec-title">آیتم‌های <i>ویژه</i></h2></div></div>
  <div class="items-grid">{% for item in featured %}{% include 'includes/item.html' %}{% endfor %}</div>
</section>

<section class="section container reveal">
  <div class="sec-head"><div><h2 class="sec-title">چطور <i>کار می‌کنه</i>؟</h2></div></div>
  <div class="steps">
    <div class="step"><div class="step-num">🔍</div><h4>انتخاب آیتم</h4><p>جستجو کن و فیلتر بذار</p></div>
    <div class="step"><div class="step-num">💳</div><h4>پرداخت امن</h4><p>پول وارد اسکرو می‌شه</p></div>
    <div class="step"><div class="step-num">📦</div><h4>تحویل آنی</h4><p>کمتر از ۵ دقیقه</p></div>
    <div class="step"><div class="step-num">⭐</div><h4>تأیید و نظر</h4><p>پول به فروشنده می‌رسه</p></div>
  </div>
</section>

<section class="container reveal"><div class="cta-banner">
  <h2>آماده‌ای شروع کنی؟ ⚡</h2>
  <p>همین حالا ثبت‌نام کن و <b style="color:var(--cyan)">۱۰٪ تخفیف</b> اولین سفارش رو بگیر</p>
  <a href="{% url 'register' %}" class="btn btn-primary">ثبت‌نام رایگان</a>
</div></section>
{% endblock %}
''')

W('templates/market.html', '''{% extends 'base.html' %}{% block title %}مارکت آیتم | نئوگیم{% endblock %}{% block content %}
<section class="page-head container">
  <div class="crumbs"><a href="{% url 'home' %}">خانه</a> / <span>مارکت آیتم</span></div>
  <h1 class="sec-title" style="font-size:2.2rem">مارکت <i>آیتم‌ها</i></h1>
  <p class="sec-sub">{{ items|length }} نتیجه پیدا شد</p>
</section>
<div class="container market">
  <aside class="card filters"><form method="get">
    <div class="f-group"><h5>جستجو</h5><div class="field" style="margin:0"><span class="f-icon">🔍</span><input name="q" value="{{ q }}" placeholder="نام آیتم..."></div></div>
    <div class="f-group"><h5>بازی</h5>{% for g in games %}<label class="f-check"><input type="checkbox" name="game" value="{{ g.slug }}"> {{ g.name }}</label>{% endfor %}</div>
    <div class="f-group"><h5>کمیابی</h5>
      <label class="f-check"><input type="checkbox" name="rarity" value="gold"> افسانه‌ای</label>
      <label class="f-check"><input type="checkbox" name="rarity" value="epic"> اپیک</label>
      <label class="f-check"><input type="checkbox" name="rarity" value="rare"> کمیاب</label></div>
    <div class="f-group"><h5>حداکثر قیمت — <span class="range-val">${{ maxp }}</span></h5>
      <input type="range" name="maxp" min="5" max="200" value="{{ maxp }}"></div>
    <div class="f-group"><h5>مرتب‌سازی</h5>
      <select name="sort" style="width:100%;padding:10px;border-radius:12px;background:var(--bg1);border:1px solid var(--stroke)">
        <option value="new" {% if sort == 'new' %}selected{% endif %}>جدیدترین</option>
        <option value="cheap" {% if sort == 'cheap' %}selected{% endif %}>ارزان‌ترین</option>
        <option value="exp" {% if sort == 'exp' %}selected{% endif %}>گران‌ترین</option>
      </select></div>
    <button class="btn btn-primary sm" style="width:100%">اعمال فیلتر ⚡</button>
  </form></aside>
  <div>
    <div class="items-grid">
      {% for item in items %}{% include 'includes/item.html' %}{% empty %}<p style="color:var(--muted)">چیزی پیدا نشد 😕</p>{% endfor %}
    </div>
  </div>
</div>
{% endblock %}
''')

W('templates/product.html', '''{% extends 'base.html' %}{% block title %}{{ item.name }} | نئوگیم{% endblock %}{% block content %}
<section class="page-head container" style="padding-bottom:10px;text-align:right">
  <div class="crumbs"><a href="{% url 'home' %}">خانه</a> / <a href="{% url 'market' %}">مارکت</a> / <span>{{ item.name }}</span></div>
</section>
<div class="container product">
  <div>
    <div class="g-main">{{ item.icon }}</div>
    <div class="g-thumbs"><button class="on">{{ item.icon }}</button><button>💠</button><button>⚔️</button></div>
  </div>
  <div class="p-info">
    <span class="badge b-{{ item.rarity }}">⭐ {{ item.get_rarity_display }}</span>
    <h1>{{ item.name }}</h1>
    <div class="rate">★★★★★ <small>({{ reviews|length }} نظر) · {{ item.game.name }}</small></div>
    <div class="seller"><span class="av">🥷</span><div><b>فروشگاه نئو</b><small>✓ فروشنده وریفای‌شده · ۹۸٪ رضایت</small></div></div>
    <div style="display:flex;align-items:center;gap:16px;margin:18px 0">
      <span class="p-price">${{ item.price|floatformat:2 }}</span>
      {% if item.old_price %}<span class="old" style="font-size:1rem">${{ item.old_price|floatformat:2 }}</span><span class="badge b-ok">تخفیف ویژه</span>{% endif %}
    </div>
    <div style="display:flex;gap:14px;flex-wrap:wrap">
      <form method="post" action="{% url 'cart_add' item.id %}?buy=1">{% csrf_token %}<button class="btn btn-primary">⚡ خرید فوری</button></form>
      <form method="post" action="{% url 'cart_add' item.id %}">{% csrf_token %}<button class="btn btn-glass">🛒 افزودن به سبد</button></form>
    </div>
    <div class="meta-list">
      <div>⚡ تحویل آنی — کمتر از ۵ دقیقه پس از پرداخت</div>
      <div>🔐 پرداخت از طریق اسکرو امن</div>
      <div>💠 گارانتی بازگشت وجه ۷ روزه</div>
    </div>
    {% if item.description %}<p style="color:var(--muted)">{{ item.description }}</p>{% endif %}
  </div>
</div>
{% if reviews %}
<div class="container"><h3 style="margin-bottom:16px">💬 نظرات</h3>
  {% for rv in reviews %}<div class="review"><div class="stars">{% for i in '★★★★★'|slice:':5' %}★{% endfor %}</div><p style="color:var(--muted);margin:8px 0">{{ rv.text }}</p><b>{{ rv.user.username }}</b></div>{% endfor %}
</div>{% endif %}
{% if related %}
<section class="section container"><div class="sec-head"><div><h2 class="sec-title">آیتم‌های <i>مرتبط</i></h2></div></div>
  <div class="items-grid">{% for item in related %}{% include 'includes/item.html' %}{% endfor %}</div>
</section>{% endif %}
{% endblock %}
''')

W('templates/boost.html', '''{% extends 'base.html' %}{% block title %}بوست اکانت | نئوگیم{% endblock %}{% block content %}
<section class="page-head container">
  <div class="crumbs"><a href="{% url 'home' %}">خانه</a> / <span>بوست اکانت</span></div>
  <h1 class="sec-title" style="font-size:2.2rem">بوست <i>حرفه‌ای اکانت</i></h1>
  <p class="sec-sub">رنک فعلی و مقصدت رو انتخاب کن — قیمت رو زنده ببین ⚡</p>
</section>
<div class="container boost-grid">
  <form method="post" class="card calc">{% csrf_token %}
    <label>🎮 بازی</label>
    <select id="bGame" name="game">{% for g in games %}<option value="{{ g.id }}">{{ g.name }}</option>{% endfor %}</select>
    <label>📍 رنک فعلی</label>
    <div class="seg">{% for v, t in ranks %}<label class="seg-item"><input type="radio" name="cur" value="{{ v }}" {% if forloop.first %}checked{% endif %}><span>{{ t }}</span></label>{% endfor %}</div>
    <label>🎯 رنک مقصد</label>
    <div class="seg">{% for v, t in ranks %}<label class="seg-item"><input type="radio" name="tgt" value="{{ v }}" {% if forloop.counter == 2 %}checked{% endif %}><span>{{ t }}</span></label>{% endfor %}</div>
    <label>✨ گزینه‌های اضافی</label>
    <label class="opt"><input type="checkbox" id="optPriority" name="priority"> ⚡ اولویت بالا (۲۵٪+)</label>
    <label class="opt"><input type="checkbox" id="optStream" name="stream"> 📺 استریم زنده (۱۰٪+)</label>
    <button class="btn btn-primary" style="width:100%;margin-top:16px">ثبت سفارش بوست ⚡</button>
  </form>
  <div class="card summary">
    <small style="color:var(--muted)">قیمت تقریبی</small>
    <div class="big" id="boostPrice">$۳۰</div>
    <div class="sum-row"><span>⏱ زمان تقریبی</span><span id="boostEta" style="color:var(--cyan)">۲ روز</span></div>
    <div class="sum-row"><span>🟢 بوستر آنلاین</span><span style="color:var(--green)">۱۴ نفر</span></div>
    <div class="sum-row"><span>🔐 امنیت اکانت</span><span style="color:var(--green)">تضمینی</span></div>
    <p style="color:var(--dim);font-size:.78rem;margin-top:12px">پرداخت امن · گارانتی بازگشت وجه</p>
  </div>
</div>
{% endblock %}
''')

W('templates/trade.html', '''{% extends 'base.html' %}{% block title %}ترید اکانت | نئوگیم{% endblock %}{% block content %}
<section class="page-head container">
  <div class="crumbs"><a href="{% url 'home' %}">خانه</a> / <span>خرید و فروش اکانت</span></div>
  <h1 class="sec-title" style="font-size:2.2rem">ترید <i>امن اکانت</i></h1>
  <p class="sec-sub">اکانت‌های وریفای‌شده با اسکرو تضمینی 🔐</p>
</section>
<div class="container" style="padding-bottom:80px">
  <div class="acc-grid" style="margin-bottom:50px">
    {% for l in listings %}
    <div class="card acc-card" style="--edge:{{ l.game.color }}">
      <div class="acc-top"><span class="av">{{ l.icon }}</span>
        <div><b>{{ l.title }}</b><small>فروشنده: {{ l.seller|default:'نئوگیم' }} {% if l.verified %}· <span class="badge b-ok" style="font-size:.65rem">✓ وریفای</span>{% endif %}</small></div></div>
      {% if l.stats %}<div class="acc-stats">{% for s in l.stats|slice:':12' %}{% endfor %}<div><b>{{ l.stats }}</b><small>مشخصات</small></div></div>{% endif %}
      <div class="item-foot"><span class="price" style="--edge:{{ l.game.color }}">${{ l.price|floatformat:2 }}</span>
      <button class="btn btn-primary sm" data-toast="درخواست خرید ثبت شد — منتظر اسکرو باش 🔐">خرید</button></div>
    </div>
    {% empty %}<p style="color:var(--muted)">هنوز آگهی‌ای ثبت نشده.</p>{% endfor %}
  </div>
  <div class="card sell-panel" style="max-width:640px;margin-inline:auto">
    <h3 style="margin-bottom:6px">اکانتت رو بفروش 💰</h3>
    <p style="color:var(--muted);font-size:.88rem;margin-bottom:20px">آگهی پس از بررسی تیم، با بج «وریفای» منتشر می‌شه.</p>
    <form method="post">{% csrf_token %}
      <div class="field"><span class="f-icon">🎮</span><select name="game" required>{% for g in games_all %}{% endfor %}<option value="">انتخاب بازی</option>{% for g in games %}<option value="{{ g.id }}">{{ g.name }}</option>{% endfor %}</select></div>
      <div class="field"><span class="f-icon">🏷️</span><input name="title" placeholder="عنوان آگهی (مثلاً Warframe رنک ۱۸)" required></div>
      <div class="field"><span class="f-icon">📊</span><input name="stats" placeholder="مشخصات خلاصه (رنک، آیتم‌ها...)"></div>
      <div class="field"><span class="f-icon">💲</span><input name="price" type="number" step="0.01" placeholder="قیمت (دلار)" required></div>
      <button class="btn btn-neon" style="width:100%">ثبت آگهی فروش</button>
    </form>
  </div>
</div>
{% endblock %}
''')

W('templates/cart.html', '''{% extends 'base.html' %}{% block title %}سبد خرید | نئوگیم{% endblock %}{% block content %}
<section class="page-head container">
  <div class="crumbs"><a href="{% url 'home' %}">خانه</a> / <span>سبد خرید</span></div>
  <h1 class="sec-title" style="font-size:2.2rem">سبد <i>خرید</i></h1>
</section>
<div class="container" style="padding-bottom:80px">
  {% if rows %}
  <div class="card table-wrap">
    <table><thead><tr><th>آیتم</th><th>تعداد</th><th>جمع</th></tr></thead><tbody>
      {% for row in rows %}<tr><td>{{ row.item.icon }} {{ row.item.name }}</td><td>{{ row.qty }}</td><td style="color:var(--cyan)">${{ row.sum|floatformat:2 }}</td></tr>{% endfor %}
      <tr><td colspan="2"><b>مجموع</b></td><td style="color:var(--gold);font-weight:900">${{ total|floatformat:2 }}</td></tr>
    </tbody></table>
  </div>
  <form method="post" action="{% url 'checkout' %}" style="margin-top:20px;text-align:center">{% csrf_token %}
    <button class="btn btn-primary">💳 پرداخت و ثبت سفارش</button>
  </form>
  {% else %}
  <div class="card" style="padding:60px;text-align:center;color:var(--muted)">
    <div style="font-size:4rem">🛒</div><p style="margin:14px 0 22px">سبد خریدت خالیه!</p>
    <a href="{% url 'market' %}" class="btn btn-primary">رفتن به مارکت</a>
  </div>
  {% endif %}
</div>
{% endblock %}
''')

W('templates/auth.html', '''{% extends 'base.html' %}{% block title %}ورود | نئوگیم{% endblock %}{% block content %}
<div class="auth">
  <div class="auth-side"><div class="big-logo">⬡</div>
    <blockquote>«به جامعه‌ی +۱۲٬۵۰۰ گیمر نئوگیم خوش اومدی — جایی که آیتم، بوست و ترید، سریع و امنه.»</blockquote></div>
  <div class="auth-form">
    <div class="card auth-card" data-tabs>
      <div class="tabs-bar" style="justify-content:center;border:0;margin-bottom:10px">
        <button type="button" class="tab-btn active" data-tab="f-login">ورود</button>
        <button type="button" class="tab-btn" data-tab="f-register">ثبت‌نام</button>
      </div>
      <form class="tab-pane active" id="f-login" method="post" action="{% url 'login' %}">{% csrf_token %}
        <p class="sub">خوش برگشتی! وارد حسابت شو.</p>
        <div class="field"><span class="f-icon">👤</span><input name="username" placeholder="نام کاربری" required></div>
        <div class="field"><span class="f-icon">🔒</span><input name="password" type="password" placeholder="رمز عبور" required></div>
        <button class="btn btn-primary" style="width:100%">ورود به حساب</button>
      </form>
      <form class="tab-pane" id="f-register" method="post" action="{% url 'register' %}">{% csrf_token %}
        <p class="sub">حسابت رو بساز و ۱۰٪ تخفیف اولین خرید رو بگیر.</p>
        <div class="field"><span class="f-icon">👤</span><input name="username" placeholder="نام کاربری" required></div>
        <div class="field"><span class="f-icon">📧</span><input name="email" type="email" placeholder="ایمیل"></div>
        <div class="field"><span class="f-icon">🔒</span><input name="password" type="password" placeholder="رمز عبور" required></div>
        <div class="field"><span class="f-icon">🔒</span><input name="password2" type="password" placeholder="تکرار رمز عبور" required></div>
        <button class="btn btn-primary" style="width:100%;margin-top:6px">ایجاد حساب</button>
      </form>
    </div>
  </div>
</div>
{% endblock %}
''')

W('templates/dashboard.html', '''{% extends 'base.html' %}{% block title %}داشبورد | نئوگیم{% endblock %}{% block content %}
<div class="container dash">
  <aside class="card side">
    <a href="#" class="active">📊 داشبورد</a>
    <a href="{% url 'market' %}">🛍️ مارکت</a>
    <a href="{% url 'boost' %}">⚡ سفارش بوست</a>
    <a href="{% url 'trade' %}">️ آگهی‌ها</a>
    <a href="{% url 'logout' %}" style="color:var(--red)">🚪 خروج</a>
  </aside>
  <main>
    <div class="topbar"><div><h2 style="font-weight:900">سلام {{ user.username }} 👋</h2><p style="color:var(--muted);font-size:.88rem">خلاصه‌ی فعالیتت اینجاست</p></div></div>
    <div class="stat-grid">
      <div class="card s-card"><small>💰 کیف پول</small><b>${{ wallet|floatformat:2 }}</b></div>
      <div class="card s-card"><small>📦 سفارش آیتم</small><b>{{ orders|length }}</b></div>
      <div class="card s-card"><small>⚡ سفارش بوست</<b>{{ boosts|length }}</b></div>
      <div class="card s-card"><small>🏷️ آگهی‌های من</small><b>{{ listings|length }}</b></div>
    </div>

    <div class="card table-wrap" style="margin-bottom:22px">
      <h3 style="padding:14px 0">📦 سفارش‌های آیتم</h3>
      <table><thead><tr><th>شناسه</th><th>آیتم</th><th>تعداد</th><th>وضعیت</th><th>مبلغ</th></tr></thead><tbody>
        {% for o in orders %}<tr><td>#{{ o.id }}</td><td>{{ o.item.icon }} {{ o.item.name }}</td><td>{{ o.qty }}</td>
        <td><span class="st {% if o.status == 'done' %}st-ok{% elif o.status == 'processing' %}st-run{% else %}st-wait{% endif %}">{{ o.get_status_display }}</span></td>
        <td style="color:var(--cyan)">${{ o.total|floatformat:2 }}</td></tr>{% empty %}<tr><td colspan="5" style="text-align:center">هنوز سفارشی نداری 😕</td></tr>{% endfor %}
      </tbody></table>
    </div>

    <div class="card table-wrap" style="margin-bottom:22px">
      <h3 style="padding:14px 0">⚡ سفارش‌های بوست</h3>
      <table><thead><tr><th>شناسه</th><th>بازی</th><th>مسیر رنک</th><th>وضعیت</th><th>مبلغ</th></tr></thead><tbody>
        {% for b in boosts %}<tr><td>#B{{ b.id }}</td><td>{{ b.game.icon }} {{ b.game.name }}</td><td>رنک {{ b.cur }} → {{ b.tgt }}</td>
        <td><span class="st {% if b.status == 'done' %}st-ok{% elif b.status == 'processing' %}st-run{% else %}st-wait{% endif %}">{{ b.get_status_display }}</span></td>
        <td style="color:var(--cyan)">${{ b.price|floatformat:2 }}</td></tr>{% empty %}<tr><td colspan="5" style="text-align:center">سفارش بوستی نداری ⚡</td></tr>{% endfor %}
      </tbody></table>
    </div>

    <div class="card act-list">
      <h3 style="margin-bottom:6px">🏷️ آگهی‌های من</h3>
      {% for l in listings %}<div class="act"><i>{{ l.icon }}</i><div>{{ l.title }} — ${{ l.price|floatformat:2 }}<small>{% if l.verified %}✓ وریفای شده{% else %}در انتظار بررسی{% endif %}</small></div></div>{% empty %}<p style="color:var(--muted)">آگهی‌ای ثبت نکردی.</p>{% endfor %}
    </div>
  </main>
</div>
{% endblock %}
''')

# ───────────────────────── ترمیم: پاس دادن بازی‌ها به trade ─────────────────────────
vp = ROOT / 'core' / 'views.py'
s = vp.read_text(encoding='utf-8')
s = s.replace(
    "return render(r, 'trade.html', {'listings': AccountListing.objects.all().select_related('game', 'seller')})",
    "return render(r, 'trade.html', {'listings': AccountListing.objects.all().select_related('game', 'seller'), 'games': Game.objects.all()})")
vp.write_text(s, encoding='utf-8')
print('  ✔ views به‌روزرسانی شد')

# ───────────────────────── ۶) داده‌های نمونه ─────────────────────────
W('seed_data.py', '''import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neogame.settings')
django.setup()
from django.contrib.auth.models import User
from core.models import Game, Item, AccountListing, Review, Order, BoostOrder

if Game.objects.exists():
    print('  ✔ داده‌ها قبلاً ساخته شده')
else:
    wf = Game.objects.create(name='Warframe', slug='warframe', icon='🤖', color='#22d3ee', tagline='پلاتینیوم، فریم و سلاح')
    dt = Game.objects.create(name='Dota 2', slug='dota2', icon='⚔️', color='#f87171', tagline='اسکین، Immortal و Arcana')
    al = Game.objects.create(name='Albion Online', slug='albion', icon='🛡️', color='#fbbf24', tagline='سیلور، آیتم و پرمیوم')
    cs = Game.objects.create(name='CS2', slug='cs2', icon='🎯', color='#a78bfa', tagline='اسکین و کیس')

    i1 = Item.objects.create(game=wf, name='شمشیر یخی آذرخش', icon='🗡️', rarity='gold', price=24.99, old_price=34.99, featured=True,
                             description='سلاح نزدیک‌برد کمیاب با آسیب یخی و الکتریکی، فورم‌شده و با کاتالیست.')
    Item.objects.create(game=dt, name='کمان خلأ', icon='🏹', rarity='epic', price=25.99, featured=True)
    Item.objects.create(game=al, name='زره نگهبان', icon='🛡️', rarity='rare', price=14.99, featured=True)
    Item.objects.create(game=wf, name='طلسم جنگجو', icon='💠', rarity='epic', price=9.99, featured=True)
    Item.objects.create(game=dt, name='نیزه امپراتور', icon='🔱', rarity='gold', price=49.0)
    Item.objects.create(game=wf, name='۱۰ پلاتینیوم', icon='🪙', rarity='rare', price=7.5)
    Item.objects.create(game=al, name='معجون قدرت', icon='🧪', rarity='epic', price=4.99)
    Item.objects.create(game=cs, name='ماسک Arcana', icon='🎭', rarity='gold', price=89.0, old_price=120.0)

    admin = User.objects.create_superuser('admin', 'admin@neo.gg', 'admin')
    demo = User.objects.create_user('demo', 'demo@neo.gg', 'demo123')

    Review.objects.create(item=i1, user=demo, rating=5, text='تحویل واقعاً زیر ۳ دقیقه بود! عالی.')
    Review.objects.create(item=i1, user=admin, rating=5, text='قیمت عالی نسبت به بازار رسمی.')

    AccountListing.objects.create(seller=demo, game=wf, title='Warframe — رنک ۱۸', icon='🤖', stats='رنک ۱۸ · ۴۲ فریم', price=349.99, verified=True)
    AccountListing.objects.create(game=dt, title='Dota 2 — Immortal', icon='⚔️', stats='Immortal · ۳۲۰ اسکین', price=520.0, verified=True)
    AccountListing.objects.create(game=al, title='Albion — Season 12', icon='🛡️', stats='S12 · ۲M سیلور', price=18.0, verified=True)
    AccountListing.objects.create(game=cs, title='CS2 — Global Elite', icon='🎯', stats='GE · ۸۵ اسکین', price=410.0, verified=True)

    Order.objects.create(user=demo, item=i1, qty=1, total=24.99, status='done')
    BoostOrder.objects.create(user=demo, game=dt, cur=2, tgt=4, price=100.0, status='processing')
    print('  ✔ داده‌های نمونه ساخته شد')
''')

# ───────────────────────── ۷) migrate + seed + سرور ─────────────────────────
banner('۷) ساخت دیتابیس، داده‌های نمونه و اجرای سرور')
run('manage.py', 'makemigrations', 'core')
run('manage.py', 'migrate')
run('seed_data.py')

banner('✅ همه‌چیز آماده‌ست!')
print('''
  🌐 سایت:          http://127.0.0.1:8000
  🛠️  پنل ادمین:     http://127.0.0.1:8000/admin      →  admin / admin
  🥷 کاربر دمو:     demo / demo123  (با سفارش و کیف پول پر)

  برای توقف سرور: Ctrl+C
''')
threading.Timer(2.0, lambda: webbrowser.open('http://127.0.0.1:8000')).start()
try:
    run('manage.py', 'runserver', '0.0.0.0:8000')
except KeyboardInterrupt:
    print('\nخداحافظ 👋')