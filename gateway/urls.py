from django.conf.urls import url
from django.contrib import admin

from apps.core.views import IndexView, GetPageDetailsView


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^(?P<slug>[a-z0-9-]+?)/$',
        GetPageDetailsView.as_view(), name='page'),
    url(r'^(?P<slug>[a-z0-9-]+?)/how-to/$',
        GetPageDetailsView.as_view(), name='how-to'),
]
