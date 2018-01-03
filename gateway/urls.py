from django.conf.urls import url
from django.contrib import admin
from apps.core.views import (
    DepositSubmitApiView,
    DepositStatusApiView,
    GetPageDetailsView,
    IndexView,
    WithdrawalSubmitApiView,
    WithdrawalStatusApiView,
)


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^submit-deposit/$',
        DepositSubmitApiView.as_view(), name='submit-deposit'),
    url(r'^submit-withdrawal/$',
        WithdrawalSubmitApiView.as_view(), name='submit-withdrawal'),
    url(
            r'^deposit/'
            r'(?P<transaction_id>'
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/'
            r'status-api/$',
            DepositStatusApiView.as_view(),
            name='deposit-status-api',
    ),
    url(
        r'^deposit/'
        r'(?P<transaction_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-'
        r'[0-9a-f]{12})/$',
        GetPageDetailsView.as_view(),
        {'slug': 'status'},
        name='deposit-status',
    ),
    url(
        r'^withdraw/(?P<transaction_id>[0-9]+)/status-api/$',
        WithdrawalStatusApiView.as_view(),
        name='withdrawal-status-api',
    ),
    url(
        r'^withdraw/(?P<transaction_id>[0-9]+)/$',
        GetPageDetailsView.as_view(),
        {'slug': 'status'},
        name='withdrawal-status',
    ),
    url(r'^(?P<slug>[a-z0-9-]+?)/$',
        GetPageDetailsView.as_view(), name='page'),
    url(r'^(?P<slug>[a-z0-9-]+?)/how-to/$',
        GetPageDetailsView.as_view(), name='how-to'),
]
