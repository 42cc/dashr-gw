from django.conf.urls import url
from django.contrib import admin
from apps.core.views import (
    DepositSubmitApiView,
    GetPageDetailsView,
    IndexView,
)


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^submit-deposit/$',
        DepositSubmitApiView.as_view(), name='submit-deposit'),
    url(r'^(?P<slug>[a-z0-9-]+?)/$',
        GetPageDetailsView.as_view(), name='page'),
    url(r'^(?P<slug>[a-z0-9-]+?)/how-to/$',
        GetPageDetailsView.as_view(), name='how-to'),
]
