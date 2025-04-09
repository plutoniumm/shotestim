from pkg.vqe import decompose, quasi_dists, eval
from src.query import BStats, pd
from _config import read
import numpy as np

SYSTEM = "torino"
SYSTEM = "osaka"
DT = 35 #ns

if SYSTEM == "torino":
  backend: pd.DataFrame = BStats().torino_t2
else:
  backend: pd.DataFrame = BStats().osaka_h2
t1s = backend['t1'].values
t2s = backend['t2'].values

coeffs = np.array([0.0454, 0.0454, 0.0454, 0.0454, 0.1201, 0.1201, 0.1655, 0.1655, 0.1682, 0.1699, 0.1699, 0.174, -0.2189, -0.2189, -0.8153])
paulis = decompose(['YYYY', 'XXYY', 'YYXX', 'XXXX', 'IIZZ', 'ZZII', 'ZIIZ', 'IZZI', 'IZIZ', 'IIIZ', 'IZII', 'ZIZI', 'ZIII', 'IIZI', 'IIII'])

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

experiments_torino = [
  [10  , [0 , 4 ], [ 55,  46,  47,  48]],
  [100 , [4 , 8 ], [129, 114, 115, 116]],
  [10  , [8 , 12], [132, 126, 127, 128]],
  [1000, [12, 16], [  2,   3,   4,   5]],
  [100 , [16, 20], [ 18,  12,  13,  14]]
]

experiments_osaka = [
  [100 , [0 , 4 ], [ 68,  55,  49,  50]],
  [1000, [4 , 8 ], [114, 115, 116, 117]],
  [5000, [8 , 12], [120, 121, 122, 123]],
  [100 , [12, 16], [  1,   2,   3,   4]]
]

if SYSTEM == "torino":
  data = [read(f'h2/hfs_{i}') for i in range(3)]
else:
  data = [read(f'h2/hfssm_{i}') for i in range(3)]
data = [data[2], data[0], data[1]]
print(f"Data Shape: {len(data)}x{len(data[0])}x{len(data[0][0])}\n---")

def moment(t, T):
  tau = t/T
  exp = np.exp(-tau)

  EX = 1 - (tau + 1)*exp
  EX2 = -1*(tau**2)*exp + 2*EX
  return [EX, EX2]

total_err = 0
var_err = 0

expts = experiments_torino if SYSTEM == "torino" else experiments_osaka
for e in expts:
  e[0] = e[0] * DT

  T1 = min([t1s[i] for i in e[2]]) * 1000
  T2 = min([t2s[i] for i in e[2]]) * 1000
  H = 1.84

  t1_x, t1_xx = moment(e[0], T1)
  t2_x, t2_xx = moment(e[0], T2)

  var_t1 = (t1_xx - t1_x**2) * 4
  var_t2 = (t2_xx - t2_x**2) * 4

  if SYSTEM == "torino":
    OFFSET = 0
  else:
    OFFSET = 0.92

  errs = var_t1 + var_t2
  MVAR = 1.04 - OFFSET
  c_pred = 0.5* np.log2(np.abs(MVAR + errs)/(H**2))
  c_real = HF(data, e[1])

  var_h = (2**(2*c_real) * (H**2) - errs)

  print(f"Real: {c_real:.3f}, Pred: {c_pred:.3f}")
  print(f"Error: {np.abs(c_real - c_pred):.3f}\n---")
  total_err += np.abs(c_real - c_pred)
  var_err += np.abs(var_h - 1.04)

print(f"Total Error: {total_err:.3f}, Avg Error: {total_err/len(expts):.3f}")
print(f"Var Error: {var_err:.3f}, Avg Var Error: {var_err/len(expts):.3f}")

"""
0.5*log(sum(sigma)/(mu^2)) = -0.5
log(sum(sigma)/(mu^2)) = -1
sum(sigma) = 0.5 * (mu^2)
varH + varT1 + varT2 = 0.5 * 1.84^2 = 1.6944
"""