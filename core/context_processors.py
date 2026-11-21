from django.conf import settings

def cart_count(r):
    return {'cart_count': len(r.session.get('cart', {})),
            'TELEGRAM_URL': getattr(settings, 'TELEGRAM_SUPPORT_URL', 'https://t.me/neogame_support')}
