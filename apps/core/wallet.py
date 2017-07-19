from bitcoinrpc.authproxy import AuthServiceProxy
from ripple_api import ripple_api

from django.conf import settings


class DashWallet(object):
    rpcuser = settings.DASHD_RPCUSER
    rpcpassword = settings.DASHD_RPCPASSWORD
    account_name = settings.DASHD_ACCOUNT_NAME

    @property
    def _dashd_url(self):
        return 'http://{}:{}@127.0.0.1:9998'.format(
            self.rpcuser,
            self.rpcpassword,
        )

    @property
    def _rpc_connection(self):
        return AuthServiceProxy(self._dashd_url)

    def get_balance(self):
        return self._rpc_connection.getbalance(self.account_name)

    def get_new_address(self):
        return self._rpc_connection.getnewaddress(self.account_name)


class RippleWallet(object):
    account = settings.RIPPLE_ACCOUNT
    dash_currency_issuer = settings.RIPPLE_ACCOUNT
    dash_currency_code = 'DSH'

    def get_dash_balance(self):
        return ripple_api.balance(
            self.account,
            self.dash_currency_issuer,
            self.dash_currency_code,
        )
