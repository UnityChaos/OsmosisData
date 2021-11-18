

class LiquidityPool:
  def __init__(self, blamm, xDenom, xAmount, yDenom, yAmount, fee, issued):
    self.blamm = blamm
    self.xDenom = xDenom
    self.xAmount = xAmount
    self.yDenom = yDenom
    self.yAmount = yAmount
    self.fee = fee
    self.issued = issued
    self.lpDenom = "liquidity/" + self.xDenom + "/" + self.yDenom + "/" +self.fee
    self.moduleName = "liquidityPoolAccount"

  #Views
  def K(self):
    return self.xAmount * self.yAmount
  def Spot(self): #price of Y in units of X
    return self.xAmount / self.yAmount

  def EffectivePriceLong(self, xIn):
    return (self.xAmount + xIn*(1 - self.fee))/(self.yAmount * (1 - self.fee))
  def EffectivePriceShort(self, yIn):
    return (self.yAmount + yIn*(1 - self.fee))/(self.xAmount * (1 - self.fee))

  #Messages
  def JoinPool(self, address, xIn, yIn):
    xMin = min(xIn, self.Spot() * yIn)
    yMin = xMin / self.Spot()
    newlyIssued = xMin * self.Issued / self.xAmount

    self.blamm.bank.transfer(address, self.moduleName, self.xDenom, xMin)
    self.blamm.bank.transfer(address, self.moduleName, self.yDenom, yMin)
    self.blamm.bank.mint(address, self.lpDenom, newlyIssued)

    self.xAmount += xMin
    self.yAmount += yMin
    self.issued += newlyIssued
  
  def ExitPool(self, address, lpAmount):
    xOut = self.xAmount * lpAmount / self.issued
    yOut = self.yAmount * lpAmount / self.issued

    self.blamm.bank.transfer(self.moduleName, address, self.xDenom, xOut)
    self.blamm.bank.transfer(self.moduleName, address, self.yDenom, yOut)
    self.blamm.bank.burn(address, self.lpDenom, lpAmount)

    self.xAmount -= xOut
    self.yAmount -= yOut
    self.issued -= lpAmount
  
  def SwapLong(self, address, xIn):
    yOut = self.Y * (1 - xIn/(self.X + xIn*(1-self.fee)))

    self.blamm.bank.transfer(address, self.moduleName, self.xDenom, xIn)
    self.blamm.bank.transfer(self.moduleName, self.yDenom, yOut)

    self.xAmount += xIn
    self.yAmount -= yOut

  def SwapShort(self, address, yIn):
    xOut = self.X * (1 - yIn/(self.Y + yIn*(1-self.fee)))

    self.blamm.bank.transfer(address, self.moduleName, self.yDenom, yIn)
    self.blamm.bank.transfer(self.moduleName, address, self.xDenom, xOut)

    self.yAmount += yIn
    self.xAmount -= xOut