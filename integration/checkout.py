# encoding: utf-8
# -*- coding: utf-8 -*-
"""
Checkout process customization.
"""

import logging, locale

logger = logging.getLogger("integration.checkout")

from django.utils.translation import ugettext as _

from mezzanine.conf import settings

from cartridge.shop.models import Order
from cartridge.shop.utils import set_shipping

from suds.client import Client
from decimal import Decimal
from cartridge.shop.checkout import CheckoutError

import paypalrestsdk
from paypalrestsdk import Payment

def correios_billship_handler(request, order_form):
	"""
	Default billing/shipping handler - called when the first step in
	the checkout process with billing/shipping address fields is
	submitted. Implement your own and specify the path to import it
	from via the setting ``SHOP_HANDLER_BILLING_SHIPPING``.
	This function will typically contain any shipping calculation
	where the shipping amount can then be set using the function
	``cartridge.shop.utils.set_shipping``. The Cart object is also
	accessible via ``request.cart``
	"""
	logger.debug("integration.checkout.correios_billship_handler()")
	if not request.session.get("free_shipping"):
        	settings.use_editable()
        
		# http://www.correios.com.br/webservices/default.cfm
		# http://www.correios.com.br/webServices/PDF/SCPP_manual_implementacao_calculo_remoto_de_precos_e_prazos.pdf

		client = Client("http://ws.correios.com.br/calculador/CalcPrecoPrazo.asmx?wsdl")
	
		"""
			40010 = SEDEX
		"""
		origin_cep = settings.CEP_ORIGIN
		data = order_form.cleaned_data
		dest_cep = data["billing_detail_postcode"]

		logger.debug("cep de %s para %s" % (origin_cep,dest_cep) )
		# Propriedades fixas apenas para testar por enquanto
		result = client.service.CalcPreco("","",40010, origin_cep, dest_cep , "1.0",1, 50.0, 50.0, 50.0, 50.0, "N", 0 , "N")

		price = Decimal(result.Servicos[0][0].Valor.replace(",","."))
		logger.debug("preço %10.2d" % price)

		set_shipping(request, _("SEDEX"), price)

def paypal_payment_handler(request, order_form, order):
	"""
	Default payment handler - called when the final step of the
	checkout process with payment information is submitted. Implement
	your own and specify the path to import it from via the setting
	``SHOP_HANDLER_PAYMENT``. This function will typically contain
	integration with a payment gateway. Raise
	cartridge.shop.checkout.CheckoutError("error message") if payment
	is unsuccessful.
	"""

	logger.debug("integration.checkout.paypal_payment_handler()")
   
	logger.debug("request %s \n order_form %s \n order %s" % (request, order_form, order) )
 
	try:
		PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
		PAYPAL_SECRET = settings.PAYPAL_SECRET
	except AttributeError:
		raise ImproperlyConfigured(_("Credenciais de acesso ao paypal estão faltando, "
				"isso inclui PAYPAL_CLIENT_ID e PAYPAL_SECRET "
				"basta incluí-las no settings.py para serem utilizadas "
				"no processador de pagamentos do paypal."))

	if settings.DEBUG:
		mode = "sandbox"
	else:
		mode = "live"

	api = paypalrestsdk.set_config(
		mode = mode, # sandbox or live
		client_id = PAYPAL_CLIENT_ID,
		client_secret = PAYPAL_SECRET
	)
	# autenticação
	access_token = api.get_token()

	logger.debug("Paypal Access Token %s" % access_token)

	data = order_form.cleaned_data
	locale.setlocale(locale.LC_ALL, settings.SHOP_CURRENCY_LOCALE)
	currency = locale.localeconv()
	currency_code = currency['int_curr_symbol'][0:3] 
	logger.debug("Currency Code %s" % currency_code)

	payment = Payment({
		"intent": "sale",
		"payer": {
			"payment_method": "paypal",
		},
		"redirect_urls" : {
			"return_url" : "http://localhost:5000/payment/execute",
			"cancel_url" : "http://localhost:5000"
		},
		"transactions": [{
			"amount": {
				"total": str(order.total),
				"currency": currency_code
			},
			"description": "Compra de Produtos na loja." 
    		}]
	})

	if payment.create():
		logger.debug("Payment[%s] created successfully"%(payment.id))
		return payment.id
	else:
		# Display Error message
		logger.error("Payment error \n %s" % payment)
		raise CheckoutError(payment.error)

