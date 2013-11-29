# encoding: utf-8
# -*- coding: utf-8 -*-
"""
Checkout process customization.
"""

from django.utils.translation import ugettext as _

from mezzanine.conf import settings

from cartridge.shop.models import Order
from cartridge.shop.utils import set_shipping

from suds.client import Client
from decimal import Decimal

def default_billship_handler(request, order_form):
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

	result = client.service.CalcPreco("","",40010, origin_cep, dest_cep , "1.0",1, 50.0, 50.0, 50.0, 50.0, "N", 0 , "N")

	price = Decimal(result.Servicos[0][0].Valor.replace(",","."))

	set_shipping(request, _("SEDEX"), price)

