from qiskit.circuit.library import ExcitationPreserving
from src.char import QC, QR, CR
from _config import Service
from src.utils import run

print(ExcitationPreserving(4, 'iswap', 'linear', 2).decompose())
raise SystemExit
backend = Service().torino
hfs = CR(20, 'hfs')
qc = QC(QR(133), hfs)
# qc = QC(QR(20), hfs)

Q = [57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 75, 90, 89, 88, 87]
# Q = list(range(20))

qc.x([Q[0], Q[1], Q[2], Q[10], Q[11], Q[12]])
qc.append(ExcitationPreserving(20, 'iswap', 'linear', 1), Q)

qcs = []
qcx = qc.copy()
qcy = qc.copy()
qcz = qc.copy()

qcx.h(Q)
qcy.sdg(Q)
qcy.h(Q)


for ckt in [qcx, qcy, qcz]:
  for i in range(len(Q)):
    ckt.measure(Q[i], hfs[i])

  ckt = ckt.decompose(reps=3)
  ckt = ckt.assign_parameters({k:0.1 for k in ckt.parameters})
  qcs.append(ckt)
# lithium

res = run(qcs, backend, shots=2**14)
