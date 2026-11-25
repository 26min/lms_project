import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, description):
    """Создаёт продукт в Stripe и возвращает его ID"""
    try:
        product = stripe.Product.create(
            name=name,
            description=description,
        )
        return product.id
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None


def create_stripe_price(product_id, amount, currency="rub"):
    """Создаёт цену в Stripe и возвращает её ID"""
    try:
        price = stripe.Price.create(
            product=product_id,
            unit_amount=int(amount * 100),  # в копейках!
            currency=currency,
        )
        return price.id
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None


def create_stripe_checkout_session(price_id, success_url, cancel_url):
    """Создаёт сессию оплаты и возвращает ссылку"""
    try:
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.url
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None
