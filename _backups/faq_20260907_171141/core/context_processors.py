def cart_count(r):
    return {'cart_count': len(r.session.get('cart', {}))}
