from .models import Cart

def get_base_context(request):
    if not request.session.exists(request.session.session_key):
        request.session.create()
    carts = Cart.objects.filter(session_key = request.session.session_key)
    carts_count = 0
    carts_final_price = 0
    carts_total_price = 0

    for cart in carts:
        carts_count += cart.quantity
        carts_final_price += cart.get_final_price()
    carts_total_price += carts_final_price

    context = {
        'carts': carts,
        'carts_count': carts_count,
        'carts_final_price': carts_final_price,
        'carts_total_price': carts_total_price
    }
    return context