def helper_cmd():
    return "Summary of available commands:\n- `/help` shows this help message\n- `/resource [langing, app, docs, blog, twitter]` shows the relevant resource\n- `/fund 0xabc...` sends 0.02 gETH (Goerli test ETH) to the specified wallet **only once per wallet!**"


def resource_cmd(resource: str):
        if resource == "landing":
            return "Here you have:\nhttps://ithil.fi"
        elif resource == "app":
            return "Here you have:\nhttps://app.ithil.fi"
        elif resource == "dex":
            return "Here you have:\nhttps://dex.ithil.fi"
        elif resource == "docs":
            return "Here you have:\nhttps://docs.ithil.fi"
        elif resource == "blog":
            return "Here you have:\nhttps://ithil-protocol.medium.com"
        elif resource == "twitter":
            return "Here you have:\nhttps://twitter.com/ithil_protocol"
        else:
            return "Invalid resource selected"


def send_eth_cmd(wallet: str, user_manager: any, transaction_manager: any):
    if (
        wallet == "0x000000000000000000000000000000000000dEaD"
        or wallet == "0x0000000000000000000000000000000000000000"
    ):
        return "Cannot send to null address"
    elif not transaction_manager.is_valid(wallet):
        return "Invalid address provided"
    elif transaction_manager.balance() <= 100000000000000000:
        return "Not enough ETH, retry in a while"
    else:
        address = wallet.lower()
        if user_manager.check_interaction(address, "ETH"):
            txid = transaction_manager.send_eth(wallet)
            if txid != None:
                return "Funded!"
            else:
                return "An error occurred"
        else:
            return "Claimed already, retry in a day"

  
def send_tokens_cmd(wallet: str, token_address: str, user_manager: any, transaction_manager: any):
    if (
        wallet == "0x000000000000000000000000000000000000dEaD"
        or wallet == "0x0000000000000000000000000000000000000000"
    ):
        return "Cannot send to null address"
    elif not transaction_manager.is_valid(wallet):
        return "Invalid address provided"
    elif transaction_manager.balance() <= 100000000000000000:
        return "Not enough ETH, retry in a while"
    elif transaction_manager.token_balance(token_address) == 0:
        return "Not enough tokens, retry in a while"
    else:
        address = wallet.lower()
        if user_manager.check_interaction(address, token_address):
            txid = transaction_manager.send_tokens(token_address, wallet)
            if txid != None:
                return "Funded!"
            else:
                return "An error occurred"
        else:
            return "Claimed already, retry in a day"
