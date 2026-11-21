from django.contrib import admin
from django.utils.html import format_html
from .models import Game, Item, ItemImage, Profile, Order, BoostOrder, AccountListing, Review
admin.site.site_header = '⬡ مدیریت نئوگیم'
admin.site.register(Game)
class ItemImageInline(admin.TabularInline):
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
        return obj.icon
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
