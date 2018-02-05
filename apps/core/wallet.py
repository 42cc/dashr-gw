from bitcoinrpc.authproxy import AuthServiceProxy

from django.conf import settings


class DashWallet(object):
    rpcuser = settings.DASHD_RPCUSER
    rpcpassword = settings.DASHD_RPCPASSWORD
    account_name = settings.DASHD_ACCOUNT_NAME

    @property
    def _rpc_connection(self):
        return AuthServiceProxy(settings.DASHD_URL)

    def get_address_balance(self, address, min_confirmations):
        return self._rpc_connection.getreceivedbyaddress(
            address,
            min_confirmations,
        )

    def get_new_address(self):
        return self._rpc_connection.getnewaddress(self.account_name)

    def send_to_address(self, address, amount):
        return self._rpc_connection.sendtoaddress(address, amount)

    def check_address_valid(self, address):
        return self._rpc_connection.validateaddress(address)['isvalid']
