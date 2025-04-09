from quantum_gates import (
  MrAndersonSimulator as MAS,
  EfficientCircuit as EC,
  standard_gates as cern_gates,
  DeviceParameters
)
from pkg.ibm_noise import noise_t1, noise_cx, noise_spam, NoiseModel
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit
from pkg.io2 import save
import numpy as np

def tpile(circ):
  qregs = circ.qregs
  cregs = circ.cregs
  newc = QuantumCircuit(*qregs, *cregs)
  basis_gates = ['rz', 'sx', 'x', 'cx', 'delay', 'measure', 'barrier']

  for i in circ.data:
    instr = i[0].name
    qargs = i[1]
    cargs = i[2]

    if instr == 'h':
      newc.rz(np.pi/2, qargs[0]._index)
      newc.sx(qargs[0]._index)
      newc.rz(np.pi/2, qargs[0]._index)
    elif instr == 'measure':
      newc.measure(qargs[0]._index, cargs[0]._index)
    else:
      if instr not in basis_gates:
        raise ValueError(f"Gate {instr} not supported")
      else:
        newc.append(i[0], qargs, cargs)
    # endif
  # endfor
  return newc

DT = 35e-9
TM = 1.5e-6
def param_defaults(size):
  return {
    "T1": [1_000]*size,
    "T2": [1_000]*size,
    "p": [0.0]*size,
    "rout": [0.0]*size,
    "p_int": [[0, 0]*size],
    "t_int": [[DT, DT]*size],
    "tm": [TM]*size,
    "dt": [DT],
    "metadata": {}
  }

class CernBackend:
  opts = {}
  name = ''
  dev = None
  qubits = 0

  def __init__(self, name, opts):
    self.name = name
    self.dev = None

    # make sure all keys are present
    keys = ['layout', 'params']
    for key in keys:
      if key not in opts:
        raise ValueError(f"Key {key} not found in opts")
      else:
        self.opts[key] = opts[key]
      # endif
    # endfor

    self.qubits = len(self.opts['layout'])
    defaults = param_defaults(self.qubits)
    for key in defaults:
      if key not in self.opts['params']:
        self.opts['params'][key] = defaults[key]
      # endif
    # endfor

    device_param = DeviceParameters(opts['layout'])
    save( "device_parameters.json", opts['params'])
    device_param.load_from_json("./")

    self.dev = MAS(cern_gates, CircuitClass=EC)
    from quantum_gates._simulation.simulator import _apply_gates_on_circuit

  # pass k args and kwargs to the simulator
  def run(self, circ, **kwargs):
    qc = tpile(circ)
    q = self.qubits
    sp = 2**q
    shots = kwargs['shots']
    self.dev: MAS

    psi0 = np.zeros(sp)
    psi0[0] = 1

    res = self.dev.run(
      t_qiskit_circ=qc,
      psi0=psi0,
      qubits_layout=self.opts['layout'],
      device_param=self.opts['params'],
      nqubit=q,
      **kwargs
    )
    res = {
      format(i, 'b').zfill(q): round(res[i]*shots) for i in range(0, sp)
    }
    res = np.array([k for k, v in res.items() for _ in range(v)])
    np.random.shuffle(res)
    np.random.shuffle(res)
    return res


class Backend:
  name = None
  dev = None
  opts = None

  def __init__(self, name, opts):
    backend = {
      "statevector_parallel_threshold": 2,
      "max_parallel_experiments": 32,
      "zero_threshold": 1e-7
    }
    self.opts = opts

    if name == '':
      self.name = 'Ideal'
      backend["method"] = 'statevector'
      self.dev = AerSimulator(**backend)
    elif name == 'random':
      self.name = 'random'
      self.dev = None
    elif name == 'custom':
      self.name = 'custom'
      self.dev = CernBackend(name, opts)
    else:
      nm = NoiseModel()
      self.name = name

      if name == 'spam':
        p, q = opts['p'], opts['q']
        backend['noise_model'] = noise_spam(nm, p, q)
      elif name.startswith('t1'):
        v = float(name[2:])
        backend['noise_model'] = noise_t1(nm, v)
      elif name.startswith('cx'):
        v = float(name[2:])
        backend['noise_model'] = noise_cx(nm, v)
      else:
        raise NotImplementedError
      # endif

      self.dev = AerSimulator(**backend)
    # endif
