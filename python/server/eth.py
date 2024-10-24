from eth_account import messages
from web3.auto import w3
from fastapi import HTTPException

def verify_signature(address: str, message: messages.SignableMessage, signature: str):
    recovered = w3.eth.account.recover_message(message, signature=signature)
    return recovered.lower() == address.lower()
  
def verify_owner_blockchain(address: str, character_id: str):
		# TODO: read from blockchain
		if True:
				return True
		else:
			raise HTTPException(status_code=403, detail="You don't own this character")


address_regex = "^0x[a-fA-F0-9]{40}$"
