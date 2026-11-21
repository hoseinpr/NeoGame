from django.contrib import admin
from .models import Game, Item, Profile, Order, BoostOrder, AccountListing, Review
admin.site.site_header = '⬡ مدیریت نئوگیم'
admin.site.register(Game)
admin.site.register(Item)
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(BoostOrder)
admin.site.register(AccountListing)
admin.site.register(Review)
