from src.query import BStats, pd
from t2s import keys as RUN_KEYS
from _config import read
import numpy as np

backend: pd.DataFrame = BStats().torino_t2

def toFrame(arr):
  for i in range(len(arr)):
    arr[i] = [int(i) for i in arr[i]]

  return np.array(arr).astype(np.ushort)
# end

t2s = read("res/t2s_1720674")
t2s = toFrame(t2s).transpose()


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

def t2spam(t, t2, p0m1, p1m0):
  up, dn = p0m1, p1m0
  frac = t/t2

  G = np.exp(-1*frac)
  B = (1 + G)/(1 - G)

  nu = B*(1 - up) + dn
  de = B*(up) + (1 - dn)

  return L(nu/de)


def post(series, keys):
  X_OFFSET = 4
  f = open("./t2s.csv", "w")
  f.write(" cbit,qbit,      c,  gate,   t2, t2_spam, match\n")
  names = list(keys.keys())

  t2 = backend.loc[:, "t2"].values * 1000 # make everything in ns
  p0m1 = backend.loc[:, "p0m1"].values
  p1m0 = backend.loc[:, "p1m0"].values
  sx_t = backend.loc[:, "sx_t"].values

  all_data = []
  for i, row in enumerate(series):
    if np.all(row == 0):
      continue

    points = pproc(row, W_START=X_OFFSET, W_END=10, MAX_W=32)
    xs = np.arange(X_OFFSET, len(points) + X_OFFSET, 1)

    b = np.round(np.mean(points + 0.5*xs), 3)
    values = RUN_KEYS[names[i]]
    q = values["qubit"]

    runtime = sx_t[q] * (values['reps'] + 1)
    if values["gate"] == "sx":
      runtime *= 2
    # for the H in the beginning
    runtime += 2

    t2_spam = t2spam(runtime, t2[q], p0m1[q], p1m0[q])

    match = None
    diff = np.abs(np.round(b - t2_spam, 4))
    if diff < 0.03:
      match = "✅"
      diff = 0
    elif t2_spam < b:
      match = "under"
    else:
      match = "OVER "
    # endif

    data = {
      "cbit": leftpad(names[i], 5),
      "qubit": leftpad(q, 3),
      "c": leftpad(b, 6),
      "reps": leftpad(str(values['reps']) + values["gate"], 6),
      "t2": leftpad(int(t2[q]/1000), 3),
      "t2_spam": leftpad(t2_spam, 7),
      "match": match + " by " + leftpad(diff, 6)
    }
    all_data.append(data)
    write_vals = [str(data[key]) for key in data.keys()]
    f.write(", ".join(write_vals) + "\n")
  # endfor
  f.close()

# run it
post(t2s, keys={f"t2_{i}": i for i in range(0, 36)})