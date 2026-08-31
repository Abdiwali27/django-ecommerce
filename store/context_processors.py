from .models import ContactMessage
from .models import ContactMessage, StoreSettings

def cart_count(request):

    cart = request.session.get("cart", {})

    total_items = sum(cart.values())

    return {
        "cart_count": total_items
    }


def customer_messages_count(request):

    count = ContactMessage.objects.filter(
        status="new"
    ).count()

    return {
        "unread_messages_count": count
    }

# =========================================================
# STORE SETTINGS CONTEXT PROCESSOR
# =========================================================

def store_settings(request):

    settings = StoreSettings.objects.first()

    if not settings:

        settings = StoreSettings.objects.create()

    return {
        "store_settings": settings
    }