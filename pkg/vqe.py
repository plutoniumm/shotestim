from qiskit.result import sampled_expectation_value as sampex
from qiskit import QuantumCircuit
import numpy as np

def XYZ(qc: QuantumCircuit):
  qcx: QuantumCircuit = qc.copy()
  qcy: QuantumCircuit = qc.copy()
  qcz: QuantumCircuit = qc.copy()

  qcx.h(range(qcx.num_qubits))
  qcy.sdg(range(qcx.num_qubits))
  qcy.h(range(qcx.num_qubits))

  return [qcz, qcx, qcy]
# end

def quasibits(ps, n):
  return {format(k, 'b').zfill(n): v for k, v in ps.items()}

def decompose(paulis: list) -> dict:
  obs_dict = {'x': [], 'y': [], 'z': []}
  map = {
    'I': ['I', 'I', 'I'],
    'X': ['Z', 'I', 'I'],
    'Y': ['I', 'Z', 'I'],
    'Z': ['I', 'I', 'Z'],
  }

  for obs in paulis:
    x_obs = [map[p][0] for p in obs]
    y_obs = [map[p][1] for p in obs]
    z_obs = [map[p][2] for p in obs]

    obs_dict['x'].append(''.join(x_obs))
    obs_dict['y'].append(''.join(y_obs))
    obs_dict['z'].append(''.join(z_obs))
  # endfor

  return obs_dict
# end

def eval(paulis, coeffs, counts):
  oblen = len(paulis[list(paulis)[0]])
  expvals_loc = [1] * oblen
  for idx, key in enumerate(['z', 'x', 'y']):
    for ob_idx in range(len(paulis[key])):
      obs = paulis[key][ob_idx]
      expvals_loc[ob_idx] *= sampex(counts[idx], obs)
    # endfor
  # endfor

  return np.real(np.dot(expvals_loc, coeffs))

# bstrs => quasi-probability distributions
def quasi_dists(bstrs):
  n = len(bstrs[0])
  nums = {}
  total = 0
  for bstr in bstrs:
    if bstr not in nums:
      nums[bstr] = 0
    nums[bstr] += 1
    total += 1

  nums = {int(k, 2): v/total for k, v in nums.items()}
  nums = {format(k, 'b').zfill(n): v for k, v in nums.items()}
  return nums