from scipy.optimize import minimize_scalar
from scipy.optimize import minimize, Bounds

from matplotlib import pyplot as plt
import numpy as np
from math import sqrt, exp, log10


class Blamm:
  def __init__(self, Ds, Cs, Ls, X, Y, f):
    self.n = len(Ds) #assert ds,cs,ls same len
    self.Ds = Ds
    self.Cs = Cs 
    self.Ls = Ls
    self.X = X
    self.Y = Y
    self.W = 6 # equity scale minimum
    self.Ts = [self.Ls[i] / (1 + exp(self.W - log10(self.Cs[i]*self.P() - self.Ds[i]))) for i in range(self.n)]
    self.f = f

    L = max([1/(1-self.Ls[i]) for i in range(self.n)])
    F = 1-f
    self.XKMax = int((1 + F - sqrt(pow(F, 2) * L + 2*F*(L+2) + L)/sqrt(L))*X/(-2*F))
    self.YKMax = int((1 + F - sqrt(pow(F, 2) * L + 2*F*(L+2) + L)/sqrt(L))*Y/(-2*F))


    assert(len(self.Cs) == len(self.Ds) == len(self.Ls))
    assert(all([self.Ds[i] >= 0 for i in range(self.n)]))
    assert(all([self.Cs[i] >= 0 for i in range(self.n)]))
    assert(all([self.Equity(i)>0 for i in range(self.n)]))
    assert(all([int(self.EP_short(sum(self.Cs))*sum(self.Cs)) > sum(self.Ds)]))

    assert(all([int(self.EP_short(self.Cs[i])*self.Cs[i]) > self.Ds[i] for i in range(self.n)]))


    assert(all([int(self.Ds[i])==self.Ds[i] for i in range(self.n)]))
    assert(all([int(self.Cs[i])==self.Cs[i] for i in range(self.n)]))

    #trade size limit based on max leverage available TODO
    # (1 + F - sqrt(pow(F,2) * L + 2*F*(L+2) + L)/sqrt(L))*X/(-2*F)
  
  def P(self):
    return self.X/self.Y
  def LTV(self, i):
    return self.Ds[i] / (self.Cs[i] * self.P())
  def Equity(self, i):
    return (self.Cs[i] * self.P()) - self.Ds[i]


  def P_long(self, k):
    return self.X_long(k) / self.Y_long(k)

  def X_long(self, k):
    return self.X+k
  def Y_long(self, k):
    return (self.X * self.Y) / (self.X + (k * (1 - self.f)))
  def Ds_long(self, A):
    return [self.Ds[i] + A[i] for i in range(self.n)]
  def Cs_long(self, k, A):
    return [int(self.Cs[i] + A[i]/self.EP_long(k+sum(A))) for i in range(self.n)]
  def Ls_long(self, k, A):
    return [(self.Ds_long(A)[i]*self.Y_long(sum(A)+k))/(self.Cs_long(k,A)[i] * self.X_long(k+sum(A))) for i in range(self.n)]
  def Ts_long(self, k):
    return [self.Ls[i] / (1 + exp(self.W - log10(self.Cs[i] * self.P_long(k) - self.Ds[i]))) for i in range(self.n)]
  def EP_long(self, k):
    return (self.X + k*(1 - self.f))/(self.Y * (1 - self.f))

  def Gain(self, k, i):
    b = self.Long(k)
    return (b.Equity(i) / self.Equity(i)) - 1
  def Long(self, k):
    A = self.Solve_long(k)
    Ds_ = self.Ds_long(A)
    Cs_ = self.Cs_long(k, A)
    X_ = self.X_long(k + sum(A))
    Y_ = self.Y_long(k + sum(A))
    return Blamm(Ds_, Cs_, self.Ls, X_, Y_, self.f)

  def Approx_long(self, k, i):
    # if abs(self.Ls_long(k,[0 for x in range(self.n)])[i] - self.Ls[i]) < self.f:
      # print("not unbalanced enough to adjust")
      # return 0

    # a = int(max(0, self.EP_long(k) * (self.Cs[i] * self.Ls[i] * self.P_long(k) - self.Ds[i]) / (self.EP_long(k) - self.Ls[i]*self.P_long(k))))



    # T = self.Ls[i]/(1 + exp(6 - log10(self.Cs[i]*self.P_long(k) - self.Ds[i])))
    a = int(max(0, self.EP_long(k) * (self.Cs[i] * self.Ts_long(k)[i] * self.P_long(k) - self.Ds[i]) / (self.EP_long(k) - self.Ts_long(k)[i]*self.P_long(k))))





    # return 0
    # if self.P_long(k) < self.EP_long(k):
    
    #   print("bad long price")
    #   return 0
    # if a < 10:
    #   return 0
    # if int(a/self.EP_long(k+a)) > 0:
    if a < sqrt(self.Equity(i))/(1-self.Ls[i]):
      return 0
    return a


  def Solve_long(self, k):
    A = [0 for i in range(self.n)]
    A_ = [self.Approx_long(k+sum(A),i) for i in range(self.n)]
    while int(sum(A)) != int(sum(A_)):
      # print(A, A_)
      A = A_.copy()
      A_ = [self.Approx_long(k+sum(A),i) for i in range(self.n)]
    return [int(a) for a in A_]


  def P_short(self, k):
    return self.X_short(k) / self.Y_short(k)
  def X_short(self, k):
    return (self.X * self.Y) / (self.Y + (k * (1 - self.f)))
  def Y_short(self, k):
    return self.Y + k
  def Ds_short(self, k, A):
    return [int(self.Ds[i] - A[i]*self.EP_short(k+sum(A))) for i in range(self.n)]
  def Cs_short(self, A):
    return [self.Cs[i] - A[i] for i in range(self.n)]
  def Ls_short(self, k, A):
    return [(self.Ds_short(k, A)[i]*self.Y_short(sum(A)+k))/(self.Cs_short(A)[i] * self.X_short(k+sum(A))) for i in range(self.n)]
  def Ts_short(self, k):
    return [self.Ls[i] / (1 + exp(self.W - log10(self.Cs[i]*self.P_short(k) - self.Ds[i]))) for i in range(self.n)]
  def EP_short(self, k):
    return (self.X * (1 - self.f)) / (k * (1 - self.f) + self.Y)

  def Loss(self, k, i):
    b = self.Short(k)
    return b.Equity(i) / self.Equity(i) - 1

  def Short(self, k):
    A = self.Solve_short(k)
    Ds_ = self.Ds_short(k, A)
    Cs_ = self.Cs_short(A)
    X_ = self.X_short(k+sum(A))
    Y_ = self.Y_short(k+sum(A))
    return Blamm(Ds_, Cs_, self.Ls, X_, Y_, self.f)

  def Approx_short(self, k, i):

    # if abs(self.Ls_short(k,[0 for x in range(self.n)])[i] - self.Ls[i]) < self.f:
      # print("not unbalanced enough to adjust")
      # return 0


    # a = int(min(self.Cs[i],(self.Ds[i] - self.Cs[i]*self.Ls[i]*self.P_short(k)) / (self.EP_short(k) - self.Ls[i]*self.P_short(k))))

    # T_ = self.Ls[i]/(1 + exp(6 - log10(self.Cs[i]*self.P_short(k) - self.Ds[i])))
    a = int(min(self.Cs[i],(self.Ds[i] - self.Cs[i]*self.Ts_short(k)[i]*self.P_short(k)) / (self.EP_short(k) - self.Ts_short(k)[i]*self.P_short(k))))

    # if self.EP_short(k) < self.P_short(k):
    #   print("bad short price")
    #   #need to factor in how unbalanced we are...
    #   return 0
    # return 0
    # if a < 10:
    #   return 0
    # if int(a*self.EP_short(k+a)) > 0:
    if a < sqrt(self.Equity(i))/(1-self.Ls[i]):
      return 0
    return a


  def Solve_short(self, k):
    A = [0 for i in range(self.n)]
    A_ = [self.Approx_short(k+sum(A),i) for i in range(self.n)]
    while int(sum(A)) != int(sum(A_)):
      # print(A, A_)
      A = A_.copy()
      A_ = [self.Approx_short(k+sum(A),i) for i in range(self.n)]
    return [int(a) for a in A_]

m = pow(10,10)

ds = [0,1*m,2*m,3*m,4*m]
# cs = [100 for x in range(10,199,5)]
cs = [1*m,2*m,3*m,4*m,5*m] 
ls = [0,1/2,2/3,3/4,4/5]
x = pow(10,13)
y = pow(10,13)
f = 0.003

s = Blamm(ds, cs, ls, x, y, f)


ks = np.linspace(0,10000000, 10000)
ks_ = np.linspace(-s.YKMax, s.XKMax, 10000)

def plot_both(plt, long, short):
  for i in range(s.n):
    gs = [long(k,i) if k >= 0 else short(-k,i) for k in ks_]
    plt.plot(ks_, gs)

def plot_sol(plt):
  plot_both(plt, lambda k,i: s.Solve_long(k)[i], lambda k, i: -s.Solve_short(k)[i])

def plot_cs(plt):
  plot_both(plt, lambda k, i: s.Long(k).Cs[i], lambda k, i: s.Short(k).Cs[i])

def plot_ds(plt):
  plot_both(plt, lambda k, i: s.Long(k).Ds[i], lambda k, i: s.Short(k).Ds[i])

def plot_price(plt):
  plot_both(plt, lambda k, i: s.Long(k).P(), lambda k,i: s.Short(k).P())
  plot_both(plt, lambda k,i: s.EP_long(k), lambda k,i: s.EP_short(k))

def plot_equity(plt):
  plot_both(plt, lambda k,i: s.Long(k).Equity(i), lambda k,i: s.Short(k).Equity(i))

def plot_ltv(plt):
  plot_both(plt, lambda k,i: s.Ls_long(k, s.Solve_long(k))[i], lambda k,i: s.Ls_short(k, s.Solve_short(k))[i])
  plot_both(plt, lambda k,i: ls[i], lambda k,i: ls[i])

def plot_eff_lev(plt):
  plot_both(plt, lambda k,i: s.Gain(k,i)/(s.P_long(k+sum(s.Solve_long(k)))/s.P() - 1), lambda k,i: s.Loss(k, i)/(s.P_short(k+sum(s.Solve_short(k)))/s.P() - 1))

def plot():
  fig, axs = plt.subplots(6,1)

  (efl, rel, sol, col, deb, eqy) = axs

  efl.set(ylabel='Effective Leverage')
  plot_eff_lev(efl)

  rel.set(ylabel='Resulting Leverage')
  plot_ltv(rel)

  plot_sol(sol)
  sol.set(ylabel='Solution Size')

  plot_cs(col)
  col.set(ylabel='Collateral')

  deb.set(ylabel='Debt')
  plot_ds(deb)

  plot_equity(eqy)
  eqy.set(ylabel='Equity')


def show():
  plt.show()


