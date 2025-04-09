from qiskit import QuantumCircuit
import numpy as np

to_int = lambda x: int(x)
DT = 1e-9

def memory(qc, bnd, shots):
  if bnd.name != 'custom':
    res = bnd.dev.run(qc, shots=shots, memory=True)
    res = res.result().get_memory()
    res = list(map(to_int, res))
  else:
    res = bnd.dev.run(qc, shots=int(shots))

  return res

def proc(res, W_START, W_END, MAX_W=16):
  stats = []
  for w in range(W_START, W_END):
    probs = []
    shots = 2**w
    for o in range(0, MAX_W):
      re = res[o*shots: (o+1)*shots]
      prob = np.mean(re)
      probs.append(np.mean(prob))
    # endfor o
    s, m = np.std(probs) , np.mean(probs)
    stats.append(s/m)
  # endfor w

  return np.round(np.log2(stats), 3)

def pproc(res, q, W_START, W_END, MAX_W=16):
  stats = []
  for w in range(W_START, W_END):
    probs = []
    shots = 2**w
    for o in range(0, MAX_W):
      re = res[o*shots: (o+1)*shots]
      prob = re.count("0"*q) / len(re)
      probs.append(np.mean(prob))
    # endfor o
    s, m = np.std(probs) , np.mean(probs)
    stats.append(s/m)
  # endfor w

  return np.round(np.log2(stats), 3)

def U(qc):
  qc.h(0)
  for i in range(0, qc.num_qubits - 1):
    qc.cx(i, i + 1)

def Ut(qc):
  for i in range(qc.num_qubits - 1, 0, -1):
    qc.cx(i - 1, i)
  qc.h(0)

def random():
  FROM = 2 # 2^from
  TILL = 12 # 2^till
  WINDOW = 7 # blocks of 2^window for averaging

  res = np.random.choice([0, 1], 2**(TILL+WINDOW))

  avgs = []
  stdv = []
  for exp in range(FROM, TILL, 1):
    probs = []
    shots = 2**exp
    for w in range(0, 2**WINDOW, 1):
      re = res[w*shots: (w+1)*shots]
      prob = re.tolist().count(0) / len(re)
      probs.append(prob)
    # endfor w
    avgs.append(np.mean(probs))
    stdv.append(np.std(probs))
  # endfor exp

  # ratios
  reses = []
  for i in range(0, len(avgs), 1):
    if stdv[i] == 0:
      reses.append(0)
    else:
      reses.append(stdv[i]/avgs[i])

  return np.round(reses, 4)