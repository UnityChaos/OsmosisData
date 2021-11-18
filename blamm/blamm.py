
class Blamm:
  
  #bank :: Bank (address -> denom -> balance)
  #leveragePools :: (x,y,t) -> LeveragePool
  #lendingPools :: x -> LendingPool
  #liquidityPools :: (x,y) -> LiquidityPool


  #Messages

  ## Lending
  def deposit(self, depositor, denom, amount):
    self.bank.transfer(depositor, "lendingPoolAccount", denom, amount)
    self.lendPools[denom].deposit(amount)
  def withdraw(self, denom, amount):
    pass

  ## Liquidity

  def Swap(self, din, dout, amountIn):
    pass
    #find LP, get EP and price after trade
    # loop iterate lev pools on LP to get rebalance trades0


  ## Leverage

  def lever(self, denom1, denom2, amount1, target):
    pass
  def deleverCollateral(self, denom1, denom2, amount2, ratio):
    pass
  




