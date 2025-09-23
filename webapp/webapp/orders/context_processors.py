from .models import Cart

def cart_items(request):
    """Add cart information to all templates"""
    cart = None
    cart_count = 0
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    elif request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()
    
    if cart:
        cart_count = cart.total_items
    
    return {
        'cart': cart,
        'cart_count': cart_count,
    }