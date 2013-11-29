# -*- coding: utf-8 -*-
import unittest
from mock import Mock

from integration import checkout, paypal

class TestIntegration(unittest.TestCase):
    
	def setUp(self):
		self.request = Mock()
		self.order_form = Mock()
		self.order = Mock()

	def test_checkout_default_billship_handler(self):
        
		checkout.default_billship_handler(self.request,self.order_form)

	def test_paypal_process(self):
        
		paypal.process(self.request, self.order_form, self.order)
