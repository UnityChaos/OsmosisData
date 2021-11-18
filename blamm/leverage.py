
class LeveragePool:
  def __init__(self, blamm, debtDenom, debtAmount, collateralDenom, collateralAmount, target):
    self.blamm = blamm
    self.debtDenom = debtDenom
    self.debtAmount = debtAmount
    self.collateralDenom = collateralDenom
    self.collateralAmount = collateralAmount
    self.target = target

  #Views
  def Spot(self):
    if self.debtDenom < self.collateralDenom:
      self.blamm.LiquidityPools[(self.debtDenom, self.collateralDenom)].Spot()
    else:
      self.blamm.LiquidityPools[(self.collateralDenom, self.debtDenom)].Spot()    
  def Equity(self):
    self.Spot()*self.collateral - self.debt
  def LTV(self):
    self.debt / (self.Spot() * self.collateral)
  
  #Messages
  def Enter(self, amount):#Enter : (N1 : x) -> (N2 : leverage/x/y/t)
    self.collateralAmount += amount
    #calculate number of LP tokens to mint based on share of equity added
  
  def ExitCollateral(self, amount):#ExitCollateral : (N1 : leverage/x/y/t) -> (N2 : x)
    self.collateralAmount -= amount
  #both these should have input units of the pool token, and convert to collateral/debt
  #and update the pool token outstanding, which effects conversion
  def ExitDebt(self, amount):    #ExitDebt : (N1 : leverage/x/y/t) -> (N2 : y)
    self.debtAmount += amount

    
    




  #Keeper
  def step(self):
    pass

