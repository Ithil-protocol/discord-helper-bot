import logging
from ens import ENS
import web3
from web3 import Web3
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from web3.middleware import construct_sign_and_send_raw_middleware, geth_poa_middleware

from discord_bot.abi.ERC20 import ERC20_ABI

class TransactionManager:
    def __init__(
        self,
        rpc_url: str,
        private_key: str,
        amount: float,
        token_amount: float
    ):
        self.eth_balance = 0.0
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.amount_in_eth = amount
        self.token_amount = token_amount
        self._init_web_handle()
        self._init_account()
        logging.info("Created TransactionManager.")


    def _init_web_handle(self) -> None:
        self.web3Handle = Web3(
            Web3.HTTPProvider(self.rpc_url)
        )
        self.ens = ENS.fromWeb3(self.web3Handle)


    def _init_account(self) -> None:
        self.account = web3.eth.Account.privateKeyToAccount(self.private_key)
        self.web3Handle.middleware_onion.add(
            construct_sign_and_send_raw_middleware(self.account)
        )
        self.web3Handle.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.web3Handle.eth.set_gas_price_strategy(rpc_gas_price_strategy)


    def is_valid(self, wallet) -> bool:
        return Web3.isAddress(wallet)


    def balance(self) -> int:
        account_address = self.account.address
        return self.web3Handle.eth.get_balance(account_address)


    def token_balance(self, token_address: str) -> str:
        # Convert the amount to the token's decimal units
        token_contract = self.web3Handle.eth.contract(address=token_address, abi=ERC20_ABI)
        decimal_units = token_contract.functions.decimals().call()

        account_address = self.account.address
        balance = token_contract.functions.balanceOf(account_address).call()

        return balance/decimal_units


    def send_eth(self, to: str) -> str:
        maybe_gas_price = self.web3Handle.eth.generate_gas_price()
        gas_price = maybe_gas_price * 2 if maybe_gas_price is not None else None
        txn = {
            "to": to,
            "value": Web3.toWei(self.amount_in_eth, "ether"),
            "gas": 21000,
            "gasPrice": gas_price,
            "nonce": self.web3Handle.eth.getTransactionCount(self.account.address),
        }
        return self.sign_and_send(txn)


    def send_tokens(self, token_address: str, to: str) -> str:
        # Convert the amount to the token's decimal units
        token_contract = self.web3Handle.eth.contract(address=token_address, abi=ERC20_ABI)
        decimal_units = token_contract.functions.decimals().call()
        amount_in_token_units = int(self.token_amount * 10 ** decimal_units)

        # Prepare the token transfer transaction data
        maybe_gas_price = self.web3Handle.eth.generate_gas_price()
        gas_price = maybe_gas_price * 2 if maybe_gas_price is not None else None

        transfer_function = token_contract.functions.transfer(to, amount_in_token_units)
        txn_data = transfer_function.buildTransaction({
            "from": self.account.address,
            "gas": 100000,  # You may need to adjust the gas limit based on the token's requirements
            "gasPrice": gas_price,
            "nonce": self.web3Handle.eth.getTransactionCount(self.account.address),
        })

        # Sign and send the token transfer transaction
        return self.sign_and_send(txn_data)


    def sign_and_send(self, txn_dict) -> str:
        logging.info(f"Preparing to transact")

        try:
            account_address = self.account.address
            logging.info(
                f"Account balance in ETH before: {Web3.fromWei(self.web3Handle.eth.getBalance(account_address), 'ether')}"
            )

            assert self.web3Handle.eth.getBalance(account_address) > 0

            signed_txn = self.web3Handle.eth.account.signTransaction(
                txn_dict, private_key=self.private_key
            )
            tx_hash = self.web3Handle.eth.sendRawTransaction(signed_txn.rawTransaction)
            self.web3Handle.eth.wait_for_transaction_receipt(tx_hash.hex())
            eth_balance_after = Web3.fromWei(
                self.web3Handle.eth.getBalance(account_address), "ether"
            )
            logging.info(f"Account balance in ETH after: {eth_balance_after}")
            self.eth_balance = eth_balance_after

            return Web3.toHex(tx_hash)
        except Exception as e:
            logging.error(e)
            return None


    def resolve_address(self, address):
        if self.web3.isAddress(address):
            return address
        elif self.web3.isChecksumAddress(address):
            return self.web3.toChecksumAddress(address)
        else:
            try:
                return self.ens.address(address)
            except Exception:
                raise ValueError(f"Could not resolve address: {address}")
