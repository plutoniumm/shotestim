from qiskit_aer.noise.errors.standard_errors import amplitude_damping_error
from qiskit_aer.noise import pauli_error, NoiseModel, ReadoutError
import numpy as np

def noise_cx(nm: NoiseModel, p):
  e_gate1 = pauli_error([('X', p), ('I', 1 - p)])
  e_gate2 = e_gate1.tensor(e_gate1)

  nm.add_all_qubit_quantum_error(e_gate2, ["cx"])
  return nm

def noise_t1(nm: NoiseModel, T1):
  gate_time = 0.1
  param_amp = 1 - np.exp(-gate_time / T1)

  error = amplitude_damping_error(param_amp)
  nm.add_all_qubit_quantum_error(error, ['u'])
  return nm

# spam = Readout Err + State Prep Err
def noise_spam(nm: NoiseModel, p0, p1):
  err = ReadoutError([
    [1 - p0, p0],
    [p1, 1 - p1]
  ])
  nm.add_all_qubit_readout_error(err)
  return nm