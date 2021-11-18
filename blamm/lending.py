import math

class LendingPool:
  def __init__(self, blamm, denom, deposits, borrowed, issued):
    self.blamm = blamm
    self.denom = denom
    self.deposits = deposits
    self.borrowed = borrowed
    self.issued = issued
    self.k = 1.33*pow(10,-8)
    #targeting 5% per year interest at 50% utilization, assuming 6second blocks

    self.moduleAccount = "lendingPoolAccount"
    self.depositDenom = "lending/"+self.denom

    assert(deposits > borrowed)
  
  #Views
  def utilization(self):
    return self.borrowed / self.deposits
  def available(self):
    return self.deposits - self.borrowed
  def accumulation(self):
    return self.deposits / self.issued
  def rate(self):
    self.k*math.ln(1/self.utilization)


  #Messages
  def deposit(self, address, amount):
    newlyIssued = amount / self.accumulation()

    self.blamm.bank.transfer(address, self.moduleAccount, self.denom, amount)
    self.blamm.bank.mint(address, self.depositDenom, newlyIssued)

    self.deposits += amount
    self.issued += newlyIssued

  def withdraw(self, address, amount):
    amountOut = amount * self.accumulation()

    assert(self.available() > amountOut)

    self.blamm.bank.burn(address, self.depositDenom, amount)
    self.blamm.bank.transfer(address, self.moduleAccount, self.denom, amountOut)

    self.blamm.deposits -= amountOut
    self.blamm.issued -= amount

  #Keeper
  def borrow(self, amount):
    assert(self.available() > amount)
    self.borrowed += amount
  def repay(self, amount):
    self.borrowed -= amount
  

  def step(self):
    rate = self.rate()
    util = self.utilization()
    self.deposits = self.deposits * (1 + rate * util)
    self.borrowed = self.borrowed * (1 + rate)
