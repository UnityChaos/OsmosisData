
class Bank:
  def __init__(self, balances):
    self.balances = balances # map from address to (map from denom to int)

  #helpers
  def account_exists(self, address):
    if self.balances.get(address) == None:
      self.balances[address] = {}
  def denom_exists(self, address, denom):
    self.account_exists(address)
    if self.balances[address].get(denom) == None:
      self.balances[address][denom] = 0
  
  #Messages
  def transfer(self, sender, receiver, denom, amount):
    assert(self.balances[sender][denom] >= amount)
    self.balances[sender][denom] -= amount
    self.denom_exists(receiver, denom)
    self.balances[receiver][denom] += amount
  
  #Keeper
  def mint(self, address, denom, amount):
    self.denom_exists(address, denom)
    self.balances[address][denom] += amount
  def burn(self, address, denom, amount):
    assert(self.balances[address][denom] >= amount)
    self.balances[address][denom] -= amount
