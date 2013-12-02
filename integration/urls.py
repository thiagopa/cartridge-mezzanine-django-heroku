
from django.conf.urls import patterns, url

urlpatterns = patterns("integration.views",
    url("^pay/(?P<order_id>\d+)/$", "paypal_redirect", name="paypal_redirect"),
    url("^execute", "paypal_execute" , name="paypal_execute"),
)
