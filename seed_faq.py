import os, django
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
