# -*- coding: utf-8 -*-
# encoding: utf-8
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from mezzanine.utils.views import render
from mezzanine.conf import settings

from cartridge.shop.models import Product, ProductVariation, Order, OrderItem

import paypalrestsdk
from paypalrestsdk import Payment

import logging, urlparse

logger = logging.getLogger("integration.views")

from integration import paypal

@never_cache
def paypal_redirect(request, order_id):
    """
    Redireciona para a página de pagamento do paypal
    """
    logger.debug("integration.views.paypal_redirect(%s)" % order_id)
    lookup = {"id": order_id}
    if not request.user.is_authenticated():
        lookup["key"] = request.session.session_key
    elif not request.user.is_staff:
        lookup["user_id"] = request.user.id
    order = get_object_or_404(Order, **lookup)

    payment = paypalrestsdk.Payment.find(order.transaction_id)

    for link in payment.links:
        if link.method == "REDIRECT":
            redirect_url = link.href
            url = urlparse.urlparse(link.href)
            params = urlparse.parse_qs(url.query)
            redirect_token = params['token'][0]
            order.paypal_redirect_token = redirect_token
            order.save()

    logger.debug("redirect url : %s" % redirect_url)
    return redirect(redirect_url)

@never_cache
def paypal_execute(request, template="shop/payment_confirmation.html"):
    """
    Recebe a confirmação de pagamento do paypal
    """
    token = request.GET['token']
    payer_id = request.GET['PayerID']
    logger.debug("integration.views.paypal_execute(token=%s,payer_id=%s)" % (token,payer_id))

    order = get_object_or_404(Order, paypal_redirect_token=token)

    payment = Payment.find(order.transaction_id)
    payment.execute({ "payer_id": payer_id })

    # Pago, falta enviar
    order.status = 3
    order.save()

    context = { "order" : order }

    response = render(request, template, context)
    return response
