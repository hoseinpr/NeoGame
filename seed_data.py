import os, django
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
