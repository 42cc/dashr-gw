from bitcoinrpc.authproxy import AuthServiceProxy

from django.conf import settings


class DashWallet(object):
    rpcuser = settings.DASHD_RPCUSER
    rpcpassword = settings.DASHD_RPCPASSWORD
    account_name = settings.DASHD_ACCOUNT_NAME

    @property
    def _dashd_url(self):
        return 'http://{}:{}@127.0.0.1:19998'.format(
            self.rpcuser,
            self.rpcpassword,
        )

    @property
    def _rpc_connection(self):
        return AuthServiceProxy(self._dashd_url)

    def get_balance(self):
        return self._rpc_connection.getbalance(
            self.account_name,
            settings.DASHD_MINIMAL_CONFIRMATIONS,
        )

    def get_address_balance(self, address, min_confirmations=1):
        return self._rpc_connection.getreceivedbyaddress(
            address,
            min_confirmations,
        )

    def get_new_address(self):
        return self._rpc_connection.getnewaddress(self.account_name)

    def send_to_address(self, address, amount):
        self._rpc_connection.sendtoaddress(address, amount)
