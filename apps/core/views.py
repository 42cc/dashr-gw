# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView, View
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import BaseFormView
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.vary import vary_on_headers

from .utils import get_received_amount
from .forms import DepositTransactionModelForm, WithdrawalTransactionModelForm
from .models import (
    DepositTransaction,
    GatewaySettings,
    Page,
    RippleWalletCredentials,
    WithdrawalTransaction,
)
from .tasks import (
    monitor_dash_to_ripple_transaction,
    monitor_ripple_to_dash_transaction,
)


class IndexView(TemplateView):
    """
    Index page view
    """
    template_name = 'base.html'


class GetPageDetailsView(BaseDetailView):
    """
    View returns given by url serialized page instance
    """
    model = Page

    def get(self, request, slug):
        if request.is_ajax():
            page = self.get_object()
            gateway_ripple_address = RippleWalletCredentials.get_solo().address
            expiration_minutes = (
                GatewaySettings.get_solo().transaction_expiration_minutes
            )
            response = {
                'page': {
                    'title': page.title,
                    'description': page.description.format(
                        gateway_ripple_address=gateway_ripple_address,
                        transaction_expiration_minutes=expiration_minutes,
                    ),
                },
            }
            return JsonResponse(response, safe=False)
        return render(request, 'base.html')

    @method_decorator(ensure_csrf_cookie)
    @method_decorator(vary_on_headers('X-Requested-With'))
    def dispatch(self, *args, **kwargs):
        return super(GetPageDetailsView, self).dispatch(*args, **kwargs)


class BaseSubmitApiView(BaseFormView):
    http_method_names = ('post', 'put')

    def form_valid(self, form):
        transaction = form.save()
        self.monitor_task.apply_async((transaction.id,), countdown=30)
        return JsonResponse(
            {
                'status_url': reverse(
                    self.status_urlpattern_name,
                    args=(transaction.id,),
                ),
            },
        )

    def form_invalid(self, form):
        return JsonResponse({'form_errors': form.errors}, status=400)


class DepositSubmitApiView(BaseSubmitApiView):
    form_class = DepositTransactionModelForm
    monitor_task = monitor_dash_to_ripple_transaction
    status_urlpattern_name = 'deposit-status'


class WithdrawalSubmitApiView(BaseSubmitApiView):
    form_class = WithdrawalTransactionModelForm
    monitor_task = monitor_ripple_to_dash_transaction
    status_urlpattern_name = 'withdrawal-status'


class BaseStatusApiView(View):
    def get(self, request, transaction_id):
        transaction = get_object_or_404(self.model, id=transaction_id)
        return JsonResponse(
            {
                'transactionId': transaction.id,
                'state': transaction.get_current_state(),
                'stateHistory': transaction.get_state_history(),
            }
        )


class DepositStatusApiView(BaseStatusApiView):
    model = DepositTransaction


class WithdrawalStatusApiView(BaseStatusApiView):
    model = WithdrawalTransaction


class GetReceivedAmountApiView(View):
    @staticmethod
    def get(request):
        if (
            'amount' not in request.GET or
            'transaction_type' not in request.GET or
            request.GET['transaction_type'] not in ('deposit', 'withdrawal')
        ):
            return HttpResponseBadRequest()

        try:
            received_amount = get_received_amount(
                request.GET['amount'],
                request.GET['transaction_type'],
            )
        except ArithmeticError:
            return HttpResponseBadRequest()

        return JsonResponse({'received_amount': received_amount})
