from django.contrib.auth.models import User
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
def make_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)

DELIVERY_SLOTS = [
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
