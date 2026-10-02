from django.conf import settings


def calculate_totals(lines, discount=None):
    """lines: [(product, quantity)]. Always computed from DB prices, never from the client."""
    subtotal = sum(p.price * q for p, q in lines)
    off = subtotal * discount.percent // 100 if discount else 0
    after = subtotal - off
    shipping = 0 if after >= settings.FREE_SHIPPING_THRESHOLD else settings.SHIPPING_COST
    return {"subtotal": subtotal, "discount": off, "shipping": shipping, "total": after + shipping}
