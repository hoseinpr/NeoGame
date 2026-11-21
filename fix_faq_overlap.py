# -*- coding: utf-8 -*-
# فیکس تداخل کلاس .acc-item (بج آنلاین vs آکاردئون سوالات)
# اجرا: python fix_faq_overlap.py
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
css_p = ROOT / 'static/css/style.css'
boost_p = ROOT / 'templates/boost.html'
base_p = ROOT / 'templates/base.html'

css = css_p.read_text(encoding='utf-8')
old_rule = '.acc-item{position:absolute;top:14px;left:14px}'
if old_rule in css:
    css = css.replace(old_rule, '.b-card2 .badge{position:absolute;top:14px;left:14px}')
    print('  ✔ قانون position:absolute از .acc-item حذف و فقط به بج کارت بوستر محدود شد')
else:
    print('  ⚠ قانون قبلاً حذف شده')

if '.card.acc-item{position:relative}' not in css:
    css += '\n/* فیکس تداخل acc-item */\n.card.acc-item{position:relative;overflow:hidden}\n'
    print('  ✔ قانون ایمن برای کارت‌های آکاردئون اضافه شد')
css_p.write_text(css, encoding='utf-8')

b = boost_p.read_text(encoding='utf-8')
n = b.count('badge b-ok acc-item')
if n:
    b = b.replace('badge b-ok acc-item', 'badge b-ok')
    boost_p.write_text(b, encoding='utf-8')
    print(f'  ✔ کلاس اضافی از {n} بج «آنلاین» حذف شد')

base = base_p.read_text(encoding='utf-8')
base = re.sub(r"(\{% static 'css/style\.css' %\})\?v=\d+", r'\1?v=4', base)
base = re.sub(r"(\{% static 'js/app\.js' %\})\?v=\d+", r'\1?v=4', base)
if '?v=' not in base:
    base = base.replace("{% static 'css/style.css' %}", "{% static 'css/style.css' %}?v=4")
    base = base.replace("{% static 'js/app.js' %}", "{% static 'js/app.js' %}?v=4")
base_p.write_text(base, encoding='utf-8')
print('  ✔ کش با ?v=4 باطل شد')

print('''
  ✅ تمام! ری‌استارت سرور + Ctrl+Shift+R
  حالا بخش «سوالات پرتکرار» به‌صورت لیست مرتب آکاردئونی نمایش داده می‌شه
  و صفحه /faq/ هم درست شده. بج‌های «آنلاین» بوسترها هم سر جاشون می‌مونن.
''')