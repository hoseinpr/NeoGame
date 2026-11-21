from django.contrib import admin
from .models import Game, Item, Profile, Order, BoostOrder, AccountListing, Review
admin.site.site_header = '⬡ مدیریت نئوگیم'
admin.site.register(Game)
admin.site.register(Item)
admin.site.register(Profile)
@admin.register(Order)
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
    )
admin.site.register(BoostOrder)
admin.site.register(AccountListing)
admin.site.register(Review)
