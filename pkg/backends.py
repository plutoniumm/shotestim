from qiskit.providers.fake_provider import Fake7QPulseV1
from qiskit_aer.noise import pauli_error, NoiseModel
from qiskit_aer import AerSimulator
from io import save
from circ import DT
import numpy as np

keys = {
  'channel': 'ibm_quantum',
  'instance': 'ibm-q-iitmadras/mphasis-iitm/default',
  'token': '777debb866fb6c27c20fe7e0326fb7b4fd280461d60cc8519fb475592c218073e1bb1d15977c62b85d443bf8cb4e1c264e27950e9635f37bcfe53930bf5efaa5',
}

def noise_cx(nm, value):
  e_gate1 = pauli_error([
    ('X', value),
    ('I', 1 - value)
  ])
  e_gate2 = e_gate1.tensor(e_gate1)

  nm.add_all_qubit_quantum_error(e_gate2, ["cx"])
  return nm

class CernBackend:
  opts = {}
  name = ''
  dev = None

  def __init__(self, name, opts):
    from quantum_gates.simulators import MrAndersonSimulator
    from quantum_gates.gates import standard_gates as gates
    from quantum_gates.circuits import EfficientCircuit
    from quantum_gates.utilities import DeviceParameters

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

    device_param = DeviceParameters(opts['layout'])
    save( "device_parameters.json", opts['params'])
    device_param.load_from_json("./")

    self.dev = MrAndersonSimulator(gates, CircuitClass=EfficientCircuit)

  def run(self, circ):
    return self.dev.run(
      t_qiskit_circ=circ,
      qubits_layout=self.opts.layout,
      psi0=np.array([1,0,0,0]),
      shots=1024,
      device_param=self.opts.params.__dict__(),
      nqubit=2
    )



class Backend:
  def __init__(self, name, opts=None):

    backend = {
      "statevector_parallel_threshold": 2,
      "max_parallel_experiments": 32,
      "zero_threshold": 1e-7
    }

    if name == '':
      self.name = 'Ideal'
      backend["method"] = 'statevector'
      self.dev = AerSimulator(**backend)
    elif name == 'random':
      self.name = 'random'
      self.dev = None
    elif isinstance(name, dict):
      self.name = 'custom'
      self.dev = CernBackend(name, opts)
    else:
      if name == '7':
        self.name = 'fake7'
        self.dev = Fake7QPulseV1()
      else:
        nm = NoiseModel()
        self.name = name

        if name.startswith('cx'):
          v = float(name[2:])
          backend['noise_model'] = noise_cx(nm, v)
        else:
          raise NotImplementedError
        # endif

        self.dev = AerSimulator(**backend)
      # endif
    # endif

  def refresh(self):
    raise NotImplementedError