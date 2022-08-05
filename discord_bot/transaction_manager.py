import logging
from typing import Dict

import web3
from eth_typing import ChecksumAddress
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware, geth_poa_middleware


class TransactionManager:
    def __init__(
        self,
        infura_key: str,
        network: str,
        private_key: str,
        amount: int
    ):
        self.eth_balance = 0.0
        self.infura_key = infura_key
        self.network = network
        self.private_key = private_key
        self.amount_in_eth = amount
        self._init_web_handle()
        self._init_account()
        logging.info("Created TransactionManager.")


    def _init_web_handle(self):
        self.web3Handle = Web3(
            Web3.HTTPProvider(
                f"https://{self.network}.infura.io/v3/{self.infura_key}"
            )
        )


    def _init_account(self) -> None:
        self.account = web3.eth.Account.privateKeyToAccount(self.private_key)
        self.web3Handle.middleware_onion.add(
            construct_sign_and_send_raw_middleware(self.account)
        )
        self.web3Handle.middleware_onion.inject(geth_poa_middleware, layer=0)


    def is_valid(self, wallet) -> bool:
        return Web3.isAddress(wallet)


    def balance(self) -> int:
        account_address = self.account.address
        return self.web3Handle.eth.get_balance(account_address)


    def send_eth(self, to) -> str:
        account_address = self.account.address
        nonce = self.web3Handle.eth.getTransactionCount(account_address)
        txn = {
            "to": to,
            "value": Web3.toWei(self.amount_in_eth, "ether"),
            "gas": 21000,
            "gasPrice": Web3.toWei("5", "gwei"),
            "nonce": nonce
        }
        return self.sign_and_send(txn)

    def sign_and_send(self, txn_dict) -> str:
        logging.info(
            f"Preparing to transact"
        )

        try:
            account_address = self.account.address
            logging.info(
                f"Account balance in ETH before: {Web3.fromWei(self.web3Handle.eth.getBalance(account_address), 'ether')}"
            )
            before = Web3.fromWei(
                self.web3Handle.eth.getBalance(account_address), 'ether'
            )
            assert self.web3Handle.eth.getBalance(account_address) > 0
            logging.info(
                f"Estimated gas in ETH for current transaction: {Web3.fromWei(self.web3Handle.eth.estimateGas(txn_dict)*10**9, 'ether')}"
            )
            signed_txn = self.web3Handle.eth.account.signTransaction(
                txn_dict, private_key=self.private_key
            )
            tx_hash = self.web3Handle.eth.sendRawTransaction(signed_txn.rawTransaction)
            self.web3Handle.eth.wait_for_transaction_receipt(tx_hash.hex())
            eth_balance_after = Web3.fromWei(self.web3Handle.eth.getBalance(account_address), 'ether')
            logging.info(
                f"Account balance in ETH after: {eth_balance_after}"
            )
            self.eth_balance = eth_balance_after

            return Web3.toHex(tx_hash)
        except Exception as e:
            logging.error(e)
