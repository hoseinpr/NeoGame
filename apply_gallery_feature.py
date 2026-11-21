# -*- coding: utf-8 -*-
# ⬡ نئوگیم — افزودن گالری تصاویر به آیتم‌ها (عکس اصلی + گالری اسکرولی)
# اجرا: python apply_gallery_feature.py
import sys, shutil, subprocess, webbrowser, threading
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
VENV = ROOT / '.venv'
PY = VENV / ('Scripts\\python.exe' if os.name == 'nt' else 'bin/python') if (os := __import__('os')).name == 'nt' else VENV / 'bin/python'
BACKUP_DIR = ROOT / '_backups' / ('gallery_' + datetime.now().strftime('%Y%m%d_%H%M%S'))

def banner(t): print('\n' + '═'*55 + f'\n  {t}\n' + '═'*55)
def ok(t): print(f'  ✔ {t}')
def fail(t): print(f'  ✖ {t}'); sys.exit(1)

# ───────────────────────── ۱) پیش‌نیازها ─────────────────────────
banner('۱) بررسی پیش‌نیازها')
for need in ['manage.py', 'core/models.py', 'core/admin.py',
             'templates/product.html', 'templates/includes/item.html',
             'static/css/style.css']:
    if not (ROOT / need).exists():
        fail(f'فایل {need} پیدا نشد! اسکریپت باید در پوشه اصلی پروژه اجرا شود.')
if not PY.exists():
    fail('محیط مجازی (.venv) پیدا نشد! اول bootstrap.py را اجرا کنید.')
ok('ساختار پروژه صحیح است')

# ───────────────────────── ۲) بکاپ ─────────────────────────
banner('۲) پشتیبان‌گیری')
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
for f in ['core/models.py', 'core/admin.py', 'core/views.py', 'neogame/settings.py',
          'neogame/urls.py', 'templates/product.html', 'templates/includes/item.html',
          'static/css/style.css']:
    src = ROOT / f
    if src.exists():
        dst = BACKUP_DIR / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
ok(f'بکاپ: {BACKUP_DIR}')

# ───────────────────────── ۳) نصب Pillow ─────────────────────────
banner('۳) نصب Pillow (برای ImageField)')
subprocess.run([str(PY), '-m', 'pip', 'install', '-q', 'pillow'], cwd=ROOT, check=True)
ok('Pillow نصب شد')

def replace_in(path, old, new, desc):
    p = ROOT / path
    txt = p.read_text(encoding='utf-8')
    if new in txt:
        print(f'  ⚠ تغییر قبلاً روی {path} اعمال شده — رد شد')
        return
    if old not in txt:
        print(f'  ⚠ الگو در {path} پیدا نشد — دستی بررسی کن')
        return
    p.write_text(txt.replace(old, new), encoding='utf-8')
    ok(f'{desc} → {path}')

# ───────────────────────── ۴) models.py ─────────────────────────
banner('۴) تغییر core/models.py')

replace_in('core/models.py',
    "    name = models.CharField('نام آیتم', max_length=100)\n    icon = models.CharField('آیکون', max_length=10)",
    "    name = models.CharField('نام آیتم', max_length=100)\n    icon = models.CharField('آیکون', max_length=10)\n    image = models.ImageField('عکس اصلی', upload_to='items/', blank=True, null=True)",
    'فیلد عکس اصلی به Item')

replace_in('core/models.py',
    "    featured = models.BooleanField('ویژه', default=False)\n    created = models.DateTimeField(auto_now_add=True)\n    def __str__(self): return self.name",
    """    featured = models.BooleanField('ویژه', default=False)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='gallery', verbose_name='آیتم')
    image = models.ImageField('عکس گالری', upload_to='items/gallery/')
    order = models.PositiveIntegerField('ترتیب نمایش', default=0)
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'عکس گالری'
        verbose_name_plural = 'عکس‌های گالری (اسکرولی)'
    def __str__(self): return f'{self.item.name} #{self.order}'""",
    'مدل ItemImage (گالری)')

# ───────────────────────── ۵) settings.py ─────────────────────────
banner('۵) تغییر neogame/settings.py')

replace_in('neogame/settings.py',
    "DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'",
    """DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'""",
    'تنظیمات MEDIA')

# ───────────────────────── ۶) urls.py ─────────────────────────
banner('۶) تغییر neogame/urls.py')

replace_in('neogame/urls.py',
    "    path('dashboard/', v.dashboard, name='dashboard'),\n]",
    """    path('dashboard/', v.dashboard, name='dashboard'),
]
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)""",
    'سرو فایل‌های media')

# ───────────────────────── ۷) admin.py ─────────────────────────
banner('۷) تغییر core/admin.py')

replace_in('core/admin.py',
    "from django.contrib import admin\nfrom .models import Game, Item, Profile, Order, BoostOrder, AccountListing, Review",
    "from django.contrib import admin\nfrom django.utils.html import format_html\nfrom .models import Game, Item, ItemImage, Profile, Order, BoostOrder, AccountListing, Review",
    'importهای ادمین')

replace_in('core/admin.py',
    "admin.site.register(Item)",
    """class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 3
    verbose_name = 'عکس گالری'
    verbose_name_plural = 'عکس‌های گالری (اسکرولی)'

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'admin_thumb', 'name', 'game', 'rarity', 'price', 'featured')
    list_filter = ('rarity', 'game', 'featured')
    search_fields = ('name',)
    list_editable = ('featured',)
    inlines = [ItemImageInline]

    @admin.display(description='عکس')
    def admin_thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:42px;height:42px;object-fit:cover;border-radius:10px;border:1px solid #444"/>', obj.image.url)
        return obj.icon""",
    'ItemAdmin + گالری inline')

# ───────────────────────── ۸) includes/item.html ─────────────────────────
banner('۸) تغییر templates/includes/item.html')

replace_in('templates/includes/item.html',
    '<div class="art">{{ item.icon }}</div>',
    '<div class="art">{% if item.image %}<img src="{{ item.image.url }}" alt="{{ item.name }}" loading="lazy">{% else %}{{ item.icon }}{% endif %}</div>',
    'نمایش عکس اصلی در کارت آیتم')

# ───────────────────────── ۹) product.html ─────────────────────────
banner('۹) تغییر templates/product.html')

replace_in('templates/product.html',
    """  <div>
    <div class="g-main">{{ item.icon }}</div>
    <div class="g-thumbs"><button class="on">{{ item.icon }}</button><button>💠</button><button>⚔️</button></div>
  </div>""",
    """  <div>
    <div class="g-main" id="gMain">
      {% if item.image %}<img src="{{ item.image.url }}" alt="{{ item.name }}">
      {% elif item.gallery.all %}<img src="{{ item.gallery.all.0.image.url }}" alt="{{ item.name }}">
      {% else %}{{ item.icon }}{% endif %}
    </div>
    <div class="g-thumbs" id="gThumbs">
      {% if item.image %}<button class="on" data-src="{{ item.image.url }}" title="عکس اصلی"><img src="{{ item.image.url }}"></button>{% endif %}
      {% for g in item.gallery.all %}<button {% if not item.image and forloop.first %}class="on"{% endif %} data-src="{{ g.image.url }}"><img src="{{ g.image.url }}"></button>{% endfor %}
      {% if not item.image and not item.gallery.all %}<button class="on">{{ item.icon }}</button><button>💠</button><button>⚔️</button>{% endif %}
    </div>
    {% if item.image or item.gallery.all %}<p style="color:var(--dim);font-size:.78rem;margin-top:8px">↔ روی عکس‌ها کلیک کن یا اسکرول کن</p>{% endif %}
  </div>""",
    'گالری صفحه محصول')

replace_in('templates/product.html',
    "</section>{% endif %}\n{% endblock %}",
    """</section>{% endif %}

<script>
(function(){
  const main = document.getElementById('gMain');
  if(!main) return;
  document.querySelectorAll('#gThumbs button[data-src]').forEach(b=>{
    b.addEventListener('click',()=>{
      document.querySelectorAll('#gThumbs button').forEach(x=>x.classList.remove('on'));
      b.classList.add('on');
      main.innerHTML = '<img src="'+b.dataset.src+'" alt="">';
    });
  });
})();
</script>
{% endblock %}""",
    'اسکریپت تعویض عکس گالری')

# ───────────────────────── ۱۰) CSS گالری ─────────────────────────
banner('۱۰) افزودن CSS گالری')

css_path = ROOT / 'static/css/style.css'
css = css_path.read_text(encoding='utf-8')
gallery_css = """
/* ========== گالری تصاویر آیتم ========== */
.g-main img{max-width:82%;max-height:82%;object-fit:contain;border-radius:18px;filter:drop-shadow(0 0 34px rgba(251,191,36,.35))}
.g-thumbs{overflow-x:auto;scrollbar-width:thin;padding-bottom:6px}
.g-thumbs button{flex:none;width:88px;height:74px}
.g-thumbs button img{width:100%;height:100%;object-fit:cover;border-radius:12px;transition:.3s}
.g-thumbs button:hover img{transform:scale(1.07)}
.item .art img{width:100%;height:100%;object-fit:cover;border-radius:var(--rs)}
"""
if 'گالری تصاویر آیتم' not in css:
    css_path.write_text(css + gallery_css, encoding='utf-8')
    ok('CSS گالری اضافه شد')
else:
    print('  ⚠ CSS گالری قبلاً اضافه شده')

# ───────────────────────── ۱۱) پوشه media ─────────────────────────
banner('۱۱) ساخت پوشه‌های media')
(ROOT / 'media/items/gallery').mkdir(parents=True, exist_ok=True)
ok('media/items/gallery ساخته شد')

# ───────────────────────── ۱۲) migrate ────────────────────────
banner('۲) مهاجرت دیتابیس')
subprocess.run([str(PY), 'manage.py', 'makemigrations', 'core'], cwd=ROOT, check=True)
subprocess.run([str(PY), 'manage.py', 'migrate'], cwd=ROOT, check=True)
ok('دیتابیس به‌روز شد')

# ───────────────────────── ۱۳) اجرا ─────────────────────────
banner('✅ گالری تصاویر فعال شد!')
print('''
  🖼️  حالا در پنل ادمین (/admin → Items → Add):

  ۱. عکس اصلی:  فیلد «عکس اصلی» (یک تصویر)
  ۲. گالری:      بخش «عکس‌های گالری (اسکرولی)» — هر چند تا بخوای
  ۳. ترتیب:      با فیلد «ترتیب نمایش» چینش رو مشخص کن

  🎮 در سایت:
  • کارت آیتم → عکس اصلی نشون داده می‌شه
  • صفحه محصول → عکس بزرگ + نوار اسکرولی thumbnails
  • کلیک روی هر thumbnail → عکس بزرگ عوض می‌شه
  • اگه عکس نذاشتی → همون ایموجی قبلی نمایش داده می‌شه (fallback)

  📁 بکاپ قبلی: {b}

  حالا سرور رو اجرا کن:  python manage.py runserver
'''.format(b=BACKUP_DIR))

ans = input('  سرور الان استارت بشه؟ (y/n): ').strip().lower()
if ans in ('y', 'yes', 'بله', 'آره', ''):
    threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:8000/admin/core/item/add/')).start()
    try:
        subprocess.run([str(PY), 'manage.py', 'runserver', '0.0.0.0:8000'], cwd=ROOT)
    except KeyboardInterrupt:
        print('\nخداحافظ 👋')
else:
    print('\n  برای اجرا:  python manage.py runserver')