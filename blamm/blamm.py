import math 

fee = 0.001 # assume 0.1% swap fee everywhere for simplicity

class Blamm:
  def __init__(self, circulation, lendPools, liqPools, levPools):
    self.circulation = circulation
    self.lendPools = lendPools
    self.liqPools = liqPools
    self.levPools = levPools
    assert(all([self.circulation[x] >= 0 for x in self.circulation]))
  
  def deposit(self, denom, amount):
    self.lendPools[denom].deposit(amount)
    self.circulation[denom] -= amount
  def withdraw(self, denom, amount):
    pass


  def trade(self,din, dout, amount):
    pass
    #find LP, get EP and price after trade
    # loop iterate lev pools on LP to get rebalance trades


  def lever(self, denom1, denom2, amount, ratio):
    pass
  def delever(self, denom1, denom2, amount, ratio):
    pass
  
  def arb(self):
    pass
    


class LiquidityPool:
  def __init__(self, X, Y):
    self.X = X
    self.Y = Y
  def K(self):
    return self.X * self.Y
  def Spot(self):
    return self.X / self.Y
  def long(self,xIn):
    yOut = self.Y * (1 - xIn/(self.X + xIn*(1-fee)))
    X_ = self.X + xIn
    Y_ = self.Y - yOut
    return (yOut, LiquidityPool(X_, Y_))
  def short(self,yIn):
    xOut = self.X * (1 - yIn/(self.Y + yIn*(1-fee)))
    X_ = self.X - xOut
    Y_ = self.Y + yIn
    return (xOut, LiquidityPool(X_, Y_))
  def EffectivePriceLong(self, xIn):
    return (self.X + xIn*(1 - fee))/(self.Y * (1 - fee))
  def EffectivePriceShort(self, yIn):
    return (self.Y + yIn*(1 - fee))/(self.X * (1 - fee))

class LendingPool:
  def __init__(self, deposits, borrowed):
    self.deposits = deposits
    self.borrowed = borrowed
    self.k = 1.33*pow(10,-8)
    #targeting 5% per year interest at 50% utilization, assuming 6second blocks
    assert(deposits >= borrowed)
  def utilization(self):
    return self.borrowed / self.deposits
  def rate(self):
    self.k*math.ln(1/self.utilization)
  def deposit(self, amount):
    return LendingPool(self.deposits + amount, self.borrowed)
  def withdraw(self, amount):
    return LendingPool(self.deposits - amount, self.borrowed)
  def borrow(self, amount):
    return LendingPool(self.deposits, self.borrowed + amount)
  def repay(self, amount):
    return LendingPool(self.deposits, self.borrowed - amount)
  def step(self):
    return LendingPool(self.deposits, self.borrowed * (1+self.rate()))

class LeveragePool:
  def __init__(self, LiqPool, LendPool, isLong, debt, collateral, target):
    self.LiqPool = LiqPool
    self.LendPool = LendPool
    self.isLong = isLong # LP.X is debt, LP.Y is collateral
    self.debt = debt
    self.collateral = collateral
    self.target = target
  def Price(self):
    if self.isLong:
      self.LP.Spot()
    else:
      1/self.LP.Spot()
  def Equity(self):
    self.Price()*self.collateral - self.debt
  def LTV(self):
    self.debt / (self.Price() * self.collateral)
  
  def RebalanceLong(self, xIn):
    if self.islong:
      
    else:

