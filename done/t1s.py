from src.char import t1, spam, QC, QR, CR
from _config import Service, write
from src.utils import run

backend = Service().torino
keys = {}

cbits = (5*6) + 6 + 2
t1s = CR(cbits, 't1s')
qc = QC(QR(133), t1s)

qubits = [
  [0, 4, 14, 23, 27, 31],
  [38, 41, 44, 47, 52],
  [76, 79, 82, 86, 90],
  [95, 98, 100, 103, 106],
  [129, 130, 120, 123, 128],
  [20, 22, 26, 29, 33],
  [57, 59, 62, 65, 69],
]

offset = 0
for idx, i in enumerate(qubits[0]):
  j = idx + offset
  keys[f"t1_{cbits - j - 1}"] = {'gate': 'id', 'reps': 10, 'qubit': i}
  t1(qc, 'id', i, t1s[j], 10)
offset += 6

for idx, i in enumerate(qubits[1]):
  j = idx + offset
  keys[f"t1_{cbits - j - 1}"] = {'gate': 'id', 'reps': 100, 'qubit': i}
  t1(qc, 'id', i, t1s[j], 100)
offset += 5

for idx, i in enumerate(qubits[2]):
  j = idx + offset
  keys[f"t1_{cbits - j - 1}"] = {'gate': 'id', 'reps': 1000, 'qubit': i}
  t1(qc, 'id', i, t1s[j], 1000)
offset += 5

for idx, i in enumerate(qubits[3]):
  j = idx + offset
  keys[f"t1_{cbits - j - 1}"] = {'gate': 'x', 'reps': 10, 'qubit': i}
  t1(qc, 'x', i, t1s[j], 10)
offset += 5

for idx, i in enumerate(qubits[4]):
  j = idx + offset
  keys[f"t1_{cbits - j - 1}"] = {'gate': 'x', 'reps': 100, 'qubit': i}
  t1(qc, 'x', i, t1s[j], 100)
offset += 5

for idx, i in enumerate(qubits[5]):
  j = idx + offset
  keys[f"t1_{cbits - j - 1}"] = {'gate': 'x', 'reps': 1000, 'qubit': i}
  t1(qc, 'x', i, t1s[j], 1000)
offset += 5

for idx, i in enumerate(qubits[6]):
  j = idx + offset
  keys[f"t1_{cbits - j - 1}"] = {'gate': 'h', 'reps': 10, 'qubit': i}
  t1(qc, 'h', i, t1s[j], 100)

# res = run(qc, backend, shots=2**16)
