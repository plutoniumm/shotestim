from src.char import t2, randoms, QC, QR, CR
from _config import Service
from src.utils import run

backend = Service().osaka

wasted = 0
wastes = CR(20, 'dump')

def HF(qc: QC, rng: list, wait: int, basis: str, meas: list):
  global wasted
  if len(rng) > 4:
    raise ValueError("Too many qubits")

  # pre-measure
  for i in rng:
    qc.measure(i, wastes[wasted])
    wasted += 1
    if wasted > 19:
      wasted = 0

  qc.x(rng[0])
  qc.x(rng[2])

  for _ in range(wait):
    for j in rng:
      qc.id(j)
  # endfor

  # basis transformation
  if basis == 'x':
    for i in rng:
      qc.h(i)
  elif basis == 'y':
    for i in rng:
      qc.sdg(i)
      qc.h(i)
    # endfor
  else:
    pass
  # endif

  for i, j in zip(meas, rng):
    qc.measure(j, i)
  # endfor
# end

# we'll now make 5 HF experiments
# TORINO
# HF_0 = [55, 46, 47, 48] # 10
# HF_1 = [129, 114, 115, 116] # 100
# HF_2 = [132, 126, 127, 128] # 10
# HF_3 = [2, 3, 4, 5] # 1000
# HF_4 = [18, 12, 13, 14] # 100

# OSAKA
HF_0 = [68, 55, 49, 50]
HF_1 = [114, 115, 116, 117]
HF_2 = [120, 121, 122, 123]
HF_3 = [1, 2, 3, 4]

qcs = []

for B in ['x', 'y', 'z']:
  hfs = CR(20, 'hfs')
  qc = QC(QR(127), hfs, wastes)

  HF(qc, HF_0, 100, B, hfs[0:4])
  HF(qc, HF_1, 1000, B, hfs[4:8])
  HF(qc, HF_2, 5000, B, hfs[8:12])
  HF(qc, HF_3, 100, B, hfs[12:16])

  qcs.append(qc)
# endfor
res = run(qcs, backend, shots=2**14)
