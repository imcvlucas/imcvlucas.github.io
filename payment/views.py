import braintree, stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from orders.models import Order
from cart.cart import Cart

# Create your views here.
gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)

def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    total_cost = order.get_total_cost()
    if request.method == 'POST':
        # retrieve nonce
        nonce = request.POST.get('payment_method_nonce', None)
        # create and submit transaction
        result = gateway.transaction.sale({
            'amount': f'{total_cost:.2f}',
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        if result.is_success:
            # mark the order as paid
            order.paid = True
            # store the unique transaction id
            order.braintree_id = result.transaction.id
            order.save()
            return redirect('payment:checkout')
        else:
            return redirect('payment:cancelled')
    else:
        # generate token
        client_token = gateway.client_token.generate()
        context = {'order': order, 'client_token': client_token}
        return render(request, 'payment/process.html', context)

def payment_done(request):
    return render(request, 'payment/done.html')

def payment_cancelled(request):
    return render(request, 'payment/cancelled.html')

def payment_checkout(request):
    return render(request, 'payment/checkout.html')


# STRIPE
# This is your test secret API key.
stripe.api_key = 'sk_test_51LhNbNBGZyNiyiqHLHFvN0Eucgo7IWOQcT33pjpIQ4CQd14nOvqHCJVCsT0aOfRVWQnDV5fd7tGSTTksVADAarlj00GdR1hI4l'

DOMAIN = 'http://127.0.0.1:8000/'

def create_checkout_session(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    total_cost = order.get_total_cost()
    total_cost_to_int = int(total_cost) * 100

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'cad',
                    'product_data': {
                        'name': 'T-shirt',
                    },
                    'unit_amount': total_cost_to_int,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url= DOMAIN + 'payment/success/',
            cancel_url= DOMAIN + 'payment/cancelled/',
        )
        order.paid = True
        order.save()
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url)

def checkout_success(request):
    return render(request, 'payment/success.html')
