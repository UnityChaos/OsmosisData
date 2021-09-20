from scipy.optimize import minimize_scalar
from scipy.optimize import minimize, Bounds

from matplotlib import pyplot as plt
import numpy as np


class Blamm:
  def __init__(self, Ds, Cs, Ls, X, Y, f):
    self.n = len(Ds) #assert ds,cs,ls same len
    self.Ds = Ds
    self.Cs = Cs 
    self.Ls = Ls
    self.X = X
    self.Y = Y
    self.f = f
    assert(all([self.Ds[i] >= 0 for i in range(self.n)]))
    assert(all([self.Cs[i] >= 0 for i in range(self.n)]))
  
  def P(self):
    return self.X/self.Y
  def LTV(self, i):
    # return (self.Ds[i] * self.Y)/(self.Cs[i] * self.X)
    return self.Ds[i] / (self.Cs[i] * self.P())
  def Equity(self, i):
    return (self.Cs[i] * self.P()) - self.Ds[i]


  def P_long(self, k):
    return self.X_long(k) / self.Y_long(k)
    # return ((self.X + k) * (self.X + k*(1-self.f)))/(self.X * self.Y)

  def X_long(self, k):
    return self.X+k
  def Y_long(self, k):
    return (self.X * self.Y) / (self.X + (k * (1 - self.f)))
  def Ds_long(self, A):
    return [self.Ds[i] + A[i] for i in range(self.n)]
  def Cs_long(self, k, A):
    return [self.Cs[i] + A[i]/self.EP_long(k+sum(A)) for i in range(self.n)]
  def Ls_long(self, k, A):
    return [(self.Ds_long(A)[i]*self.Y_long(sum(A)+k))/(self.Cs_long(k,A)[i] * self.X_long(k+sum(A))) for i in range(self.n)]
  def EP_long(self, k):
    return (self.X + k*(1 - self.f))/(self.Y * (1 - self.f))

  def Gain(self, k, i):
    b = self.Long(k)
    return (b.Equity(i) / self.Equity(i)) - 1
  def Long(self, k):
    # A = solve_it(self.Ds, self.Cs, self.X, self.Y, k, self.f)
    A = self.Solve_long(k)
    Ds_ = self.Ds_long(A)
    Cs_ = self.Cs_long(k, A)
    # Ls_ = self.Ls_long(k, A)

    X_ = self.X_long(k + sum(A))
    Y_ = self.Y_long(k + sum(A))
    return Blamm(Ds_, Cs_, self.Ls, X_, Y_, self.f)

  def Approx_long(self, k, i):
    return max(0, self.EP_long(k) * (self.Cs[i] * self.Ls[i] * self.P_long(k) - self.Ds[i]) / (self.EP_long(k) - self.Ls[i]*self.P_long(k)))

  def Solve_long(self, k):
    A = [0 for i in range(self.n)]
    A_ = [self.Approx_long(k+sum(A),i) for i in range(self.n)]
    while int(sum(A)) != int(sum(A_)):
      print(A, A_)
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
    return [self.Ds[i] - A[i]*self.EP_short(k+sum(A)) for i in range(self.n)]
  def Cs_short(self, A):
    return [self.Cs[i] - A[i] for i in range(self.n)]
  def Ls_short(self, k, A):
    return [(self.Ds_short(k, A)[i]*self.Y_short(sum(A)+k))/(self.Cs_short(A)[i] * self.X_short(k+sum(A))) for i in range(self.n)]
  def EP_short(self, k):
    # return (self.Y + k*(1 - self.f))/(self.X * (1 - self.f))
    # return k*self.X*(1 - self.f)/((k + self.Y)*(k*(1 - self.f) + self.Y))
    return (self.X * (1 - self.f)) / (k * (1 - self.f) + self.Y)

  def Loss(self, k, i):
    b = self.Short(k)
    return b.Equity(i) / self.Equity(i) - 1

  def Short(self, k):
    A = self.Solve_short(k)
    Ds_ = self.Ds_short(k, A)
    Cs_ = self.Cs_short(A)
    # Ls_ = self.Ls_short(k, A)
    X_ = self.X_short(k+sum(A))
    Y_ = self.Y_short(k+sum(A))
    return Blamm(Ds_, Cs_, self.Ls, X_, Y_, self.f)

  def Approx_short(self, k, i):

    # E * (CLP - D) / (ELP - 1)
    # close but sinus
    # return self.EP_short(k) * (self.Cs[i] * self.Ls[i] * self.P_short(k) - self.Ds[i]) / (self.EP_short(k) * self.Ls[i] * self.P_short(k) - 1)


    # (D-(A*E))/(P*(C - A)) = L
    # A = (D - CLP) / (E - LP)
    return min(self.Cs[i],(self.Ds[i] - self.Cs[i]*self.Ls[i]*self.P_short(k)) / (self.EP_short(k) - self.Ls[i]*self.P_short(k)))
    # return 0



    # return self.EP_short(k) * (self.Ds[i] - self.Cs[i] * self.Ls[i] * self.P_short(k)) / (self.EP_short(k) - self.Ls[i]*self.P_short(k))
    # return self.EP_long(k) * (self.Cs[i] * self.Ls[i] * self.P_long(k) - self.Ds[i]) / (self.EP_long(k) - self.Ls[i]*self.P_(k))

  def Solve_short(self, k):
    A = [0 for i in range(self.n)]
    A_ = [self.Approx_short(k+sum(A),i) for i in range(self.n)]
    while int(sum(A)) != int(sum(A_)):
      print(A, A_)
      A = A_.copy()
      A_ = [self.Approx_short(k+sum(A),i) for i in range(self.n)]
    return [int(a) for a in A_]

ks = np.linspace(0,100000, 1000)
ks_ = np.linspace(-100000, 100000, 1000)

def plot_both(plt, long, short):
  for i in range(s.n):
    gs = [long(k) if k >= 0 else short(k) for k in ks_]
    plt.plot(ks_, gs)

def plot_sol(plt):
  for i in range(s.n):
    gs = [s.Solve_long(k)[i] if k>=0 else -s.Solve_short(-k)[i] for k in ks_]
    plt.plot(ks_, gs)

def plot_sol_long(plt):
  # ks = np.linspace(0, 100000,1000)
  for i in range(s.n):
    gs = [s.Solve_long(k)[i] for k in ks]
    plt.plot(ks, gs)

def plot_sol_short(plt):
  # ks = np.linspace(0, 1000000,1000)
  for i in range(s.n):
    gs = [s.Solve_short(k)[i] for k in ks]
    plt.plot(ks, gs)

def plot_cs(plt):
  for i in range(s.n):
    gs = []

def plot_cs_short(plt):
  # ks = np.linspace(0,1000000,1000)
  for i in range(s.n):
    gs = [s.Short(k).Cs[i] for k in ks]
    plt.plot(ks, gs)
def plot_ds_short(plt):
  for i in range(s.n):
    gs = [s.Short(k).Ds[i] for k in ks]
    plt.plot(ks, gs)

def plot_cs_long(plt):
  # ks = np.linspace(0,1000000,1000)
  for i in range(s.n):
    gs = [s.Long(k).Cs[i] for k in ks]
    plt.plot(ks, gs)
def plot_ds_long(plt):
  for i in range(s.n):
    gs = [s.Long(k).Ds[i] for k in ks]
    plt.plot(ks, gs)

def plot_price_long(plt):
  # s = Blamm(ds, cs, ls, x, y, f)
  # ks = np.linspace(0,100000,1000)
  for i in range(5):
    gs = [s.Long(k).P() for k in ks]
    es = [s.EP_long(k) for k in ks]
    plt.plot(ks, gs)
    plt.plot(ks, es)

def plot_equity_long(plt):
  # s = Blamm(ds, cs, ls, x, y, f)
  # ks = np.linspace(0,100000,1000)
  for i in range(5):
    gs = [s.Long(k).Equity(i) for k in ks]
    plt.plot(ks, gs)

def plot_lev_long(plt):
  # s = Blamm(ds, cs, ls, x, y, f)
  # ks = np.linspace(0,100000,1000)
  for i in range(5):
    gs_ = [s.Ls_long(k, s.Solve_long(k))[i] for k in ks]
    ls_ = [ls[i] for k in ks]
    # zs = [0 for k in ks]
    plt.plot(ks, gs_)
    plt.plot(ks, ls_)

def plot_price_short(plt):
  # s = Blamm(ds, cs, ls, x, y, f)
  # ks = np.linspace(0,100000,1000)
  # for i in range(s.n):
  ps = [s.P() for k in ks]
  es = [s.EP_short(k) for k in ks]
  # gs = [s.Short(k).P() for k in ks]
  gs_ = [s.P_short(k) for k in ks]
  # plt.plot(gs)
  plt.plot(ks, gs_)
  # plt.plot(ps)
  plt.plot(ks, es)

def plot_equity_short(plt):
  # ks = np.linspace(0,1000000,1000)
  for i in range(5):
    gs = [s.Short(k).Equity(i) for k in ks]
    zs = [0 for k in ks]
    plt.plot(ks, gs)
    plt.plot(ks, zs)

def plot_lev_short(plt):
  # s = Blamm(ds, cs, ls, x, y, f)
  # ks = np.linspace(0,100000,1000)
  for i in range(5):
    # gs_ = [s.Ls_short(k, s.Solve_short(k))[i] for k in ks]
    gs = [s.Short(k).LTV(i) for k in ks]
    ls_ = [ls[i] for k in ks]
    plt.plot(ks, gs)
    # plt.plot(gs_)
    plt.plot(ks, ls_)

def plot_eleverage_short(plt):
  # s = Blamm(ds, cs, ls, x, y, f)
  # ks = np.linspace(0,100000,1000)
  for i in range(5):
    gs = [s.Loss(k, i) for k in ks]
    # gs = [Gain(ds, cs, x, y, i, k, f) for k in ks]
    # ps = [DP(x, y, sum(solve_it(ds, cs, x, y, k, f))+k, f) for k in ks]
    ps = [s.P_short(k+sum(s.Solve_short(k)))/s.P() for k in ks]
    ls_ = [s.Short(k).Ls[i] for k in ks]
    # plt.plot(ls_)
    # plt.plot([ls[i] for k in ks])
    # ps = [s.P_short(k+sum(solve_it(ds, cs, x, y, k, f)))/s.P() for k in ks]
    # plt.plot(gs)
    rs = [(gs[k])/(ps[k]-1) for k in range(len(gs))]
    plt.plot(ks, rs)
    # plt.plot(rs)  
    # plt.plot(ps)


def plot_eleverage_long(plt):
  # s = Blamm(ds, cs, ls, x, y, f)
  # ks = np.linspace(0,1000000,1000)
  for i in range(5):
    # ls_ = [s.Long(k).Ls[i] for k in ks]
    # plt.plot(ls_)
    gs = [s.Gain(k, i) for k in ks]
    # gs = [Gain(ds, cs, x, y, i, k, f) for k in ks]
    # ps = [DP(x, y, sum(solve_it(ds, cs, x, y, k, f))+k, f) for k in ks]
    ps = [s.P_long(k+sum(s.Solve_long(k)))/s.P() for k in ks]
    # plt.plot(gs)
    rs = [(gs[k])/(ps[k]-1) for k in range(len(gs))]
    plt.plot(ks, rs)  
    # plt.plot(ps)



def plot():
  fig, axs = plt.subplots(5,2)

  ((efs, efl), (ss, sl), (cs, cl), (ds, dl), (es, el)) = axs
  # ((efs, efl), (ls, ll), (ss, sl), (cs, cl), (ds, dl), (es, el)) = axs
  # ((ps, pl), (efs, efl), (ls, ll), (ss, sl), (cs, cl), (ds, dl), (es, el)) = axs

  # ps.set_title('Price Short')
  # plot_price_short(ps)
  # ps.set(xlabel='trade size', ylabel='price')

  # pl.set_title('Price Long')
  # plot_price_long(pl)
  # pl.set(xlabel='trade size', ylabel='price')

  # efs.set_title('Effective Leverage Short')
  plot_eleverage_short(efs)
  efs.set(ylabel='Effective Leverage')

  # efl.set_title('Effective Leverage Long')
  plot_eleverage_long(efl)
  efl.set(ylabel='Effective Leverage')

  # ls.set_title('Resulting Leverage Short')
  # plot_lev_short(ls)
  # ls.set(ylabel='Resulting Leverage')

  # ll.set_title('Resulting Leverage Long')
  # plot_lev_long(ll)
  # ll.set(ylabel='Resulting Leverage')

  # ss.set_title('Adjustment Long')
  plot_sol_long(ss)
  ss.set(ylabel='Adjustment Size')

  # sl.set_title('Adjustment Short')
  plot_sol_short(sl)
  sl.set(ylabel='Adjustment Size')

  # cs.set_title('Collateral Short')
  plot_cs_short(cs)
  cs.set(ylabel='Collateral')

  # cl.set_title('Collateral Long')
  plot_cs_long(cl)
  cl.set(ylabel='Collateral')

  # ds.set_title('Debt Short')
  plot_ds_short(ds)
  ds.set(ylabel='Debt')

  # dl.set_title('Debt Long')
  plot_ds_long(dl)
  dl.set(ylabel='Debt')

  # es.set_title('Equity Short')
  plot_equity_short(es)
  es.set(ylabel='Equity')

  # el.set_title('Equity Long')
  plot_equity_long(el)
  el.set(ylabel='Equity')





# fig, axs = plt.subplots(2, 2)
# axs[0, 0].plot(x, y)
# axs[0, 0].set_title('Axis [0, 0]')
# axs[0, 1].plot(x, y, 'tab:orange')
# axs[0, 1].set_title('Axis [0, 1]')
# axs[1, 0].plot(x, -y, 'tab:green')
# axs[1, 0].set_title('Axis [1, 0]')
# axs[1, 1].plot(x, -y, 'tab:red')
# axs[1, 1].set_title('Axis [1, 1]')

# for ax in axs.flat:
#     ax.set(xlabel='x-label', ylabel='y-label')

# # Hide x labels and tick labels for top plots and y ticks for right plots.
# for ax in axs.flat:
#     ax.label_outer()













S = lambda X,Y: X/Y

EP = lambda X,Y,A,f: (X + A*(1-f))/(Y*(1-f))

X_ = lambda X,A: X+A

Y_ = lambda X,Y,A,f: (X*Y)/(X+A*(1-f))


D_ = lambda D, A: D+A

C_ = lambda C,X,Y,A,k,f: C + A/EP(X,Y,A+k,f)


P_ = lambda X,Y,k,f: ((X+k)*(X+k*(1-f)))/(X*Y)

Equity = lambda D,C,X,Y: (C * X / Y) - D
Equity_ = lambda Ds,Cs,X,Y,A,i,k,f: Equity(D_(Ds[i], A[i]), C_(Cs[i], X, Y, A[i], k+sum(A)-A[i], f), X_(X,k+sum(A)), Y_(X,Y,k+sum(A),f))

Gain = lambda Ds, Cs, X,Y, i, k, f: (lambda A: (Equity_(Ds, Cs, X, Y, A, i, k, f)/Equity(Ds[i], Cs[i], X, Y)))(solve_it(Ds, Cs, X, Y, k, f))

DP = lambda X,Y,k,f: P_(X,Y,k,f)/(X/Y)

LTV = lambda D,C,X,Y: (D*Y)/(C*X)

LTV_ = lambda D,C,X,Y,A,k,f: LTV(D_(D,A), C_(C,X,Y,A,k,f), X_(X,A+k), Y_(X,Y,A+k,f))

DLTV = lambda D,C,X,Y,A,k,f: LTV_(D,C,X,Y,A,k,f)/LTV(D,C,X,Y)

Constraint = lambda D,C,X,Y,A,k,f: abs(LTV(D,C,X,Y) - LTV_(D,C,X,Y,A,k,f))

solve_single = lambda D,C,X,Y,k,f: minimize_scalar(lambda a: Constraint(D,C,X,Y,a,k,f))

def plot_single(D,C,X,Y,f):
  ks = np.linspace(0,X,X/10)
  as_ = [solve_single(D,C,X,Y,k,f).x for k in ks]
  plt.plot(ks, as_)

def slippage(X,Y,f):
  ks = np.linspace(0,100000,1000)
  ss = [(P_(X,Y,a,f)) for a in ks]
  plt.plot(ks, ss)

def show():
  plt.show()

MLTV_ = lambda D,C,X,Y,As,i,k,f: LTV(D_(D,As[i]), C_(C,X,Y,As[i], k+sum(As)-As[i], f), X_(X,k+sum(As)), Y_(X,Y,k+sum(As),f))

Multcon = lambda Ds, Cs, X, Y, As, k, f: sum([abs(LTV(Ds[i],Cs[i],X,Y) - MLTV_(Ds[i],Cs[i],X,Y,As,i,k,f)) for i in range(len(Ds))])

vMCF = lambda Ds,Cs,X,Y,k,f: lambda a: Multcon(Ds, Cs, X, Y, a, k, f)

# ds = [x for x in range(10,199,5)]
ds = [25,50,66,75,80]
# cs = [100 for x in range(10,199,5)]
cs = [100,100,100,100,100]
ls = [ds[i]/cs[i] for i in range(len(ds))]
x = 1000000
y = 1000000
f = 0.003

s = Blamm(ds, cs, ls, x, y, f)

g = [0,0,0,0,0]

r = lambda k: minimize(vMCF(ds,cs,x,y,k,f),g, bounds=Bounds(0,np.inf)).x

def multiplot():
  ks = np.linspace(0,100000,1000)
  rs = [r(k) for k in ks]
  rs_ = [solve_it(ds, cs, x, y, k, f) for k in ks]
  for i in range(5):
    plt.plot(ks, [r[i] for r in rs])
    as_ = [App(ds[i],cs[i],x,y,k,f) for k in ks]
    plt.plot(ks, as_)
    plt.plot(ks, [r[i] for r in rs_])


def multichange():
  ks = np.linspace(0,100000,1000)
  for i in range(5):
    bs_ = [1/(1-MLTV_(ds[i], cs[i], x,y, [0,0,0,0,0], i, k,f)) for k in ks]
    rs_ = [1/(1-MLTV_(ds[i], cs[i], x,y, solve_it(ds, cs, x,y,k,f),i, k,f)) for k in ks]
    gs_ = [1/(1-MLTV_(ds[i], cs[i], x,y, r(k), i, k, f)) for k in ks]
    ss_ = [i+1 for k in ks]
    plt.plot(ks, rs_)
    # plt.plot(ks, bs_)
    plt.plot(ks, ss_)
    plt.plot(ks, gs_)

def expansion():
  ks = np.linspace(0,100000, 1000)
  for i in range(5):
    es = [sum(solve_it([d*10 for d in ds], [c*10 for c in cs], x, y, k, f))/k for k in ks]
    plt.plot(ks, es)



App = lambda D,C,X,Y,k,f: (C*D*EP(X,Y,k,f)*(P_(X,Y,k,f) - X/Y)) / (C*EP(X,Y,k,f)*(X/Y) - D*P_(X,Y,k,f))


# can be used to move to target, rather than maintain current
App_ = lambda D,C,L,X,Y,k,f: EP(X,Y,k,f)*(C*L*P_(X,Y,k,f) - D)/(EP(X,Y,k,f) - L*P_(X,Y,k,f))



fapprox = lambda D,C,X,Y,k,f: (C*D*k*((1-f)*(k+X)+X))/(X*(C*X - D*Y))

# re_solve = lambda Ds, Cs, X, Y, k, f: re_solve_(Ds, Cs, X, Y, k, f, [0 for i in range(len(Ds))])

def solve_it(Ds, Cs, X, Y, k, f):
  A = [0 for i in range(len(Ds))]
  # print(A)
  A_ = [App(Ds[i], Cs[i], X,Y, k+sum(A), f) for i in range(len(Ds))]
  # print(A_)
  while int(sum(A)) != int(sum(A_)):
    print(A, A_)  
  # while sum([abs(A[i] - A_[i]) for i in range(len(Ds))]) > 0.001:
    A = A_.copy()
    A_ = [App(Ds[i], Cs[i], X,Y, k + sum(A_), f) for i in range(len(Ds))]
  
  # print(A_)
  return [int(x) for x in A_]