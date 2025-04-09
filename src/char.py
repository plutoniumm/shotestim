import warnings
warnings.warn = lambda *args, **kwargs: None
from qiskit import QuantumCircuit as QC, QuantumRegister as QR, ClassicalRegister as CR
from typing import Union
from numpy import random, pi

def dynamic_gate(qc: QC, gate:str, t: int):
  if gate == 'h':
    qc.h(t)
  elif gate == 'id':
    qc.id(t)
  elif gate == 'x':
    qc.x(t)
  elif gate == 'z':
    qc.z(t)
  else:
    raise ValueError("Gate must be one of Id, H, X")

def randoms(qc: QC, t:int, depth: int, name: str):
  gates = ['rx', 'ry', 'rz', 'x', 'y', 'z', 'id']
  qc.h(t)
  original = depth
  while depth > 0:
    rand = random.randint(0, len(gates))
    rand = gates[rand]
    ang = random.randint(-pi, pi)
    gate = getattr(qc, rand)
    if rand in ['rx', 'ry', 'rz']:
      gate(ang, t)
    else:
      gate(t)

    depth -= 1
    if qc.depth() > original:
      break
  # endwhile


  # H basis measurement
  qc.h(t)
  qc.measure(int(t), name)
# end


def t2(qc: QC, gate:str, t: int, name: str, mod:int):
  qc.h(t)

  if mod % 2 != 1:
    mod += 1

  if gate == 'dl':
    qc.delay(mod, t, unit='dt')
  else:
    for _ in range(mod):
      dynamic_gate(qc, gate, t)

  # H basis measurement
  qc.h(t)
  qc.measure(int(t), name)
# end

def t1(qc: QC, gate:str, t: int, name: str, mod:int):
  qc.h(t)

  if mod % 2 != 1:
    mod += 1

  if gate == 'dl':
    qc.delay(mod, t, unit='dt')
  else:
    for _ in range(mod):
      dynamic_gate(qc, gate, t)

  qc.measure(int(t), name)
# end

def spam(qc: QC, gate:str, t: int, name: str):
  qc.h(t)
  qc.measure(t, name)
  dynamic_gate(qc, gate, t)
# end

def q2(qc: QC, ts: Union[int, int], name: str, mod:int):
  [t1, t2] = ts
  qc.h(t1)
  qc.h(t2)

  if mod % 2 != 1:
    raise ValueError("Modifier must be odd")

  for i in range(mod):
    if i % 2 != 1: # even
      qc.cx(i, i+1)
    else: # odd
      qc.cx(i+1, i)
  # endfor
  qc.measure(t1, name)
# end