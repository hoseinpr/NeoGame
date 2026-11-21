from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Game, Item, Order, BoostOrder, AccountListing, Review, FAQ, RANKS, boost_price

def home(r):
    return render(r, 'index.html', {'games': Game.objects.all(),
                                    'featured': Item.objects.filter(featured=True)[:4],
                                    'home_faqs': FAQ.objects.filter(show_home=True)[:4]})

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

def checkout(r):
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
    return render(r, 'checkout.html', {'rows': rows, 'total': total, 'slots': DELIVERY_SLOTS})

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
    return render(r, 'trade.html', {'listings': AccountListing.objects.all().select_related('game', 'seller'), 'games': Game.objects.all()})

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

def faq(r):
    cat = r.GET.get('cat')
    qs = FAQ.objects.all()
    if cat: qs = qs.filter(category=cat)
    return render(r, 'faq.html', {'faqs': qs, 'cat': cat or '', 'cats': FAQ.CATEGORY})
