# -*- coding: utf-8 -*-
import paypalrestsdk
from mezzanine.conf import settings
import logging
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger("integration.paypal")

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

