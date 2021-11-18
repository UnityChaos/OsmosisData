from blamm import Blamm
from bank import Bank
from random import random

from liquidity import LiquidityPool
from lending import LendingPool
from leverage import LeveragePool

randAmount = lambda: random.randrange(100) * pow(10, random.randrange(3,10))
fee = 0.0001

def Init():
  denoms = ["Osmo","Atom","Ust"]
  accounts = ["system", "user1","user2","user3"]
  targets = [0.2, 0.5, 0.75]


  blamm = Blamm()
  blamm.bank = InitBank(denoms, accounts)
  blamm.lendingPools = {denom : InitLendingPool(blamm, denom, randAmount()) for denom in denoms}
  blamm.liquidityPools = {(x,y) : InitLiquidityPool(blamm, x, y, randAmount(), randAmount()) for x in denoms for y in denoms if x < y}
  blamm.leveragePools = {(x,y,t) : InitLeveragePool(blamm,x,y,randAmount(),t) for x in denoms for y in denoms for t in targets}

  return blamm



def InitBank(denoms, accounts):
  return Bank({account : {denom : randAmount() for denom in denoms} for account in accounts})

def InitLendingPool(blamm, denom, amount):
  blamm.bank.mint("lendingPoolAccount", denom, amount)
  blamm.bank.mint("system", "lending/"+denom, amount)
  return LendingPool(blamm, amount, 0, amount)

def InitLiquidityPool(blamm, denom1, denom2, amount1, amount2):
  blamm.bank.mint("liquidityPoolAccount", denom1, amount1)
  blamm.bank.mint("liquidityPoolAccount", denom2, amount2)
  blamm.bank.mint("system", "liquidity/"+denom1+"/"+denom2+"/"+fee, 1000000)
  return LiquidityPool(blamm, amount1, amount2, fee, 1000000)
  

def InitLeveragePool(blamm, debtDenom, collateralDenom, collateralAmount, target):
  blamm.bank.mint("leveragePoolAccount", collateralDenom, collateralAmount)
  blamm.bank.mint("system", "leverage/"+debtDenom+"/"+collateralDenom+"/"+target, 1000000)
  return LeveragePool(blamm, debtDenom, 0, collateralDenom, collateralAmount, target)