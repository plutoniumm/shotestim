from pkg.vqe import decompose, quasi_dists, eval
from src.query import BStats, pd
from closed import closed, pred
from _config import read
import numpy as np

SYSTEM = "fixed"
SYSTEM = "variational"
DT = 35 #ns

backend: pd.DataFrame = BStats().torino_doub
t1s = backend['t1'].values
t2s = backend['t2'].values

coeffs = read('li2/li_coeffs.txt')
coeffs = np.array([float(i) for i in coeffs.strip().split('\n')])
paulis = read('li2/li_paulis.txt')
paulis = decompose([i for i in paulis.strip().split('\n')])

def pproc(res, W_START, W_END, MAX_W=32):
  stats = []
  for w in range(W_START, W_END):
    probs = []
    shots = 2**w
    for o in range(0, MAX_W):
      re = [i[o*shots: (o+1)*shots] for i in res]
      re = [quasi_dists(i) for i in re]

      expval = eval(paulis, coeffs, re)
      probs.append(expval)
    # endfor o
    s, m = np.std(probs) , np.mean(probs)
    print(f"{w}->{s:.4f}")
    stats.append(np.abs(s/m))
  # endfor w
  return np.round(np.log2(stats), 3)

def bits(arr, a, b):
  arr2 = [
    [[] for _ in range(len(arr[0]))]
      for _ in range(len(arr))
  ]

  # we need to flip a, b to read from the right
  a = len(arr[0][0]) - a
  b = len(arr[0][0]) - b

  for i in range(len(arr2)):
    for j in range(len(arr2[i])):
      arr2[i][j] = arr[i][j][b:a]

  return arr2

X_OFFSET = 4
def HF(d, meas: list):
  sliced = bits(d, *meas)
  RSDs = pproc(sliced, W_START=4, W_END=11, MAX_W=16)
  upper = len(RSDs) + X_OFFSET
  c = np.round(np.mean(RSDs + 0.5*np.arange(X_OFFSET, upper)), 2)
  return c


if SYSTEM == "fixed":
  data = [read(f'li2/stat/hfs_{i}') for i in range(3)]
else:
  data = [read(f'li2/var/hfs_{i}') for i in range(3)]
  # data = [read(f'li2/doub/hfs_{i}') for i in range(3)]
data = [data[2], data[0], data[1]]

def moment(t, T):
  tau = t/T
  exp = np.exp(-tau)

  EX = 1 - (tau + 1)*exp
  EX2 = -1*(tau**2)*exp + 2*EX
  return [EX, EX2]

Q = [57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 75, 90, 89, 88, 87]

if SYSTEM == "fixed":
  DEPTH = 11
else:
  DEPTH = 833
  # DEPTH = 925

ELPG = .7/100
T1 = np.min([t1s[i] for i in Q]) * 1000
T2 = np.min([t2s[i] for i in Q]) * 1000
H = 16.34
MVAR = np.sum(coeffs**2)
Q = len(paulis['x'][0])

# def closed(Q, tau1, tau2, s, D, eplg):
runtime = DEPTH * DT

stdv_pred = closed(Q, runtime/T1, runtime/T2, 2**9, DEPTH, ELPG)
stdv_real = pred(2**9, H)
print(f"Pred: {stdv_pred:.3f}, Real: {stdv_real:.3f}")
raise SystemExit
t1_x, t1_xx = moment(runtime, T1)
t2_x, t2_xx = moment(runtime, T2)

var_t1 = (t1_xx - t1_x**2) * Q
var_t2 = (t2_xx - t2_x**2) * Q

ELPG = ELPG/2
var_elpg = Q*(ELPG**2)*DEPTH/1

if SYSTEM != "fixed":
  MVAR = MVAR - 88.6
print(f"Var T1: {var_t1:.3f}, T2: {var_t2:.3f}, ELPG: {var_elpg:.3f}, H: {MVAR:.3f}")


errs = (var_t1 + var_t2 + var_elpg)
c_pred = 0.5* np.log2(np.abs(MVAR + errs)/(H**2))

c_real = HF(data, [0, Q])
var_li = 2**(2*c_real) * (H**2) - errs

print(f"Real: {c_real:.3f}, Pred: {c_pred:.3f}")
print(f"Error: {np.abs(c_real - c_pred):.3f}\n---")
print(f"Var Error: {np.abs(var_li - MVAR):.3f}")