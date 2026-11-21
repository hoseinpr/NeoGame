import os, django
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
