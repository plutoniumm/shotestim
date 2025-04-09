from src.char import t1, QC, QR, CR
from pkg.utils import m, t0, np
from backends import Backend
from pkg.circ import memory
from _config import write

DT = 35 * 10**-9

t1s = CR(1, 't1s')
qc = QC(QR(1), t1s)
qc.h(0)
qc.measure(0, 0)

file = f"t1_test.log"
m.init(file)
lim = 1000
b = Backend("custom", {
  'params': {
    "T1": [1_000_000] * 7,
    "T2": [1_000_000] * 7,
    # p is probability of depolarizing
    "p": [0] * 7,
    "rout": [0.001] * 7,
    "p_cnot": [[0, 0]*6],
    "t_cnot": [[0, 0]*6],
    "tm": [DT] * 7,
    "dt": [DT] * 7,
    "metadata": {}
  },
  'layout': list(range(7)),
})
reses = memory(qc, b, shots=2**15)
print(reses)
write(f"t1_sim", reses)
