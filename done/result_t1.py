from src.query import BStats, pd
from t1s import keys as RUN_KEYS
from _config import read
import numpy as np

backend: pd.DataFrame = BStats().torino_t1

def toFrame(arr):
  for i in range(len(arr)):
    arr[i] = [int(i) for i in arr[i]]

  return np.array(arr).astype(np.ushort)

# end

t1s = read("res/t1s_1719212")
t1s = toFrame(t1s).transpose()

def pproc(res, W_START, W_END, MAX_W=16):
  stats = []
  for w in range(W_START, W_END):
    probs = []
    shots = 2**w
    for o in range(0, MAX_W):
      re = res[o*shots: (o+1)*shots]
      probs.append(np.mean(re))
    # endfor o
    s, m = np.std(probs) , np.mean(probs)
    stats.append(s/m)
  # endfor w

  return np.round(np.log2(stats), 3)

leftpad = lambda s, l:" "*(l - len(str(s))) + str(s)
L = lambda x: 0.5*np.round(np.log2(x), 4)

def t1spam(t, t1, p0m1, p1m0):
  up, dn = p0m1, p1m0
  E = 1 - 1/np.exp(t/t1)
  tau = (1 - E)/(1 + E)

  nu = 1 - up + tau*dn
  de = tau*(1 - dn) + up

  return L(nu/de)


def post(series, keys=None):
  X_OFFSET = 4
  # if keys is none just do t1_index
  if keys is None:
    keys = {f"t1_{i}": i for i in range(0, len(series))}

  f = open("./t1s.csv", "w")
  f.write(" cbit,qbit,      c,  gate,   t1,  t1_spam, match\n")
  names = list(keys.keys())

  t1 = backend.loc[:, "t1"].values * 1000 # make everything in ns
  p0m1 = backend.loc[:, "p0m1"].values
  p1m0 = backend.loc[:, "p1m0"].values
  sx_t = backend.loc[:, "sx_t"].values

  all_data = []
  for i, row in enumerate(series):
    if np.all(row == 0):
      continue

    points = pproc(row, W_START=X_OFFSET, W_END=11, MAX_W=32)
    xs = np.arange(X_OFFSET, len(points) + X_OFFSET, 1)

    b = np.round(np.mean(points + 0.5*xs), 3)
    values = RUN_KEYS[names[i]]
    q = values["qubit"]
    reps = values['reps'] + 1

    runtime = sx_t[q] * reps
    if values["gate"] == "sx":
      runtime *= 2
    # for the H in the beginning
    runtime += 2

    t1_spam = t1spam(runtime, t1[q], p0m1[q], p1m0[q])

    match = None
    diff = np.abs(np.round(b - t1_spam, 4))
    if diff < 0.01:
      match = "✅"
      diff = 0
    elif t1_spam < b:
      match = "under"
    else:
      match = "OVER "
    # endif


    data = {
      "cbit": leftpad(names[i], 5),
      "qubit": leftpad(q, 3),
      "c": leftpad(b, 6),
      "reps": leftpad(str(values['reps']) + values["gate"], 6),
      "t1": leftpad(int(t1[q]/1000), 3),
      "t1_spam": leftpad(t1_spam, 8),
      "match": match + " by " + leftpad(diff, 6)
    }
    all_data.append(data)
    write_vals = [str(data[key]) for key in data.keys()]
    f.write(", ".join(write_vals) + "\n")
  # endfor
  f.close()


post(t1s)