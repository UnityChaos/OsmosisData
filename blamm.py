from scipy.optimize import minimize_scalar
from scipy.optimize import minimize, Bounds

from matplotlib import pyplot as plt
import numpy as np

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
x = 1000000
y = 1000000
f = 0.003

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



def plotgain():
  ks = np.linspace(0,100000,1000)
  for i in range(5):
    gs = [Gain(ds, cs, x, y, i, k, f) for k in ks]
    ps = [DP(x, y, sum(solve_it(ds, cs, x, y, k, f))+k, f) for k in ks]
    # plt.plot(gs)
    rs = [(gs[i]-1)/(ps[i]-1) for i in range(len(gs))]
    plt.plot(rs)
    # plt.plot(rs)  
    # plt.plot(ps)

  

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