from django.contrib import admin
from django.urls import path
from core import views as v
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', v.home, name='home'),
    path('market/', v.market, name='market'),
    path('item/<int:id>/', v.product, name='product'),
    path('cart/add/<int:id>/', v.cart_add, name='cart_add'),
    path('cart/', v.cart, name='cart'),
    path('checkout/', v.checkout, name='checkout'),
    path('boost/', v.boost, name='boost'),
    path('trade/', v.trade, name='trade'),
    path('login/', v.login_v, name='login'),
    path('register/', v.register, name='register'),
    path('logout/', v.logout_v, name='logout'),
    path('dashboard/', v.dashboard, name='dashboard'),
    path('faq/', v.faq, name='faq'),
]
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
