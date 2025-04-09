from src.char import t2, QC, QR, CR
from qiskit_aer import AerSimulator
from _config import Service, write
from src.utils import run

import warnings
warnings.warn = lambda *args, **kwargs: None

backend = Service().torino
# backend = AerSimulator()
F = False

cbits = 7*5 + 2
wastes = CR(25, 'wastes')
t2s = CR(cbits, 't2s')
qc = QC(QR(133), t2s, wastes)

torino_grid = [
   [0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14],
  #15              19,             17,             18,
  [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33],
  #        34,             35,             36,             37,
  [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52],
  #53,             54,             55,             56,
  [57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
  #        72,             73,             74,             75,
  [76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90],
  #91,             92,             93,             94,
  [95, 96, 97, 98, 99,100,101,102,103,104,105,106,107,108,109],
  #       110,            111,            112,            113,
 [114,115,116,117,118,119,120,121,122,123,124,125,126,127,128],
 #129,            130,            131,            132
]

"""
t2_id-10 = row 0
t2_id-100 = row 1
t2_id-1000 = row 2
t2_h-10 = row 3
t2_x-10 = row 4
t2_x-100 = row 5
t2_x-1000 = row 6
"""

qubits = [
  [0,  F,  F,  F,  4, F,  F,      7, F,  9, F, F, F, F, 14],
  [F, 20,  F,  F, 23, F,  F,     26, F,  F,29, F, F, F, 33],
  [38, F,  F, 41,  F, F, 44,      F, F, 47, F, F, F, F, 52],
  [57, F, 59,  F,  F,62,  F,      F,65,  F, F, F,69, F,  F],
  [76, F,  F, 79,  F, F, 82,      F, F,  F,86, F, F, F, 90],
  [95, F,  F, 98,  F,100, F,      F,103, F, F,106,F, F,  F],
  [129,F,  F,  F,  F,119, F,      F,122, F, F, F,132,F,  F],
]

keys = {}
offset = 0
wasted = 0
def add_experiment(qc, gate, row, reps):
  global keys, offset, cbits, wasted, skip
  skip = 0
  idx = 0
  for i in row:
    if i is False:
      skip += 1
      continue
    else:
      idx += 1
    # endif

    if idx + skip <= int(len(row) / 2):
      qc.measure(i, wastes[wasted])
      wasted += 1

    j = idx + offset
    keys[f"t2_{cbits - j - 1}"] = {
      'gate': gate,
      'reps': reps,
      'qubit': i,
      'cbit': cbits - j - 1,
      'waste': wasted if idx + skip <= int(len(row) / 2) else None
    }
    t2(qc, gate, i, t2s[j], reps)
  # endfor
  offset += idx

add_experiment(qc, 'id', qubits[0], 10)
add_experiment(qc, 'id', qubits[1], 100)
add_experiment(qc, 'id', qubits[2], 1000)
add_experiment(qc, 'h', qubits[3], 10)
add_experiment(qc, 'x', qubits[4], 10)
add_experiment(qc, 'x', qubits[5], 100)
add_experiment(qc, 'x', qubits[6], 1000)
# res = run(qc, backend, shots=2**14)
# filename = ('t2_rand' if RANDOM else 't2') + '.png'
# qc.draw(filename=filename, output='mpl', fold=640, scale=0.5)