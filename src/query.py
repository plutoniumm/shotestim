from json import load
from os import path
import pandas as pd

"""USAGE:
# will be downloaded if you don't have the json/csv file
backend = BStats().ibm_torino

# get all t1s
t1s = col(backend, 't1', 250, 10)
# get all t1s with a value of 250 +- 10
t1s = t1s.to_numpy()
print(np.mean(t1s), np.max(t1s), np.min(t1s))
"""
def fromJson(main: dict):
  qubits = []
  for qubit_properties in main['qubits']:
    qubit = {}
    for prop in qubit_properties:
      qubit[prop['name']] = prop['value']
    qubits.append(qubit)

  for gate in main['gates']:
    if len(gate['qubits']) > 1:
      continue

    name = gate['gate']
    if name == 'reset' or name == 'x' or name == 'id' or name == 'rz':
      continue

    qubit = gate['qubits'][0]
    error = gate['parameters'][0]['value']
    gate_time = gate['parameters'][1]['value']

    qubits[qubit][f"{name}_err"] = error
    qubits[qubit][f"{name}_t"] = gate_time

  return qubits


class BStats:
  df = None
  cols = []

  def getFile(self, file: str):
    prefix = "./backends/"
    if path.exists(f"{prefix}{file}.csv"):
      return pd.read_csv(f"{prefix}{file}.csv", index_col=False)
    elif path.exists(f"{prefix}{file}.json"):
      jsonf = open(f"{prefix}{file}.json")
      data = load(jsonf)
      jsonf.close()

      return pd.DataFrame(fromJson(data))
    else:
      raise FileNotFoundError(f"File {file} not found")


  def getRemote(self, name: str):
    url = f"https://api.quantum.ibm.com/api/backends/{name}/properties"
    df = pd.read_json(url)
    df.to_csv(f"./backends/ibm_{name}.csv", index=False)
    return df

  def __getattr__(self, file: str):
    try:
      df = self.getFile(file)
    except FileNotFoundError:
      df = self.getRemote(file)

    df.columns = (df.columns
      .str.replace('\(.*\)', '', regex=True)
      .str.strip()
      .str.replace('-', '_')
      .str.replace(' ', '_')
      .str.replace('__', '_')
      .str.lower()
    )
    df.rename(
      columns={
        '√x_error':'sx_err',
        'prob_meas0_prep1': 'p1m0',
        'prob_meas1_prep0': 'p0m1',
        'readout_assignment_error': 'readout_err',
        'readout_errors': 'readout_err',
      },
      inplace=True,
      errors='ignore'
    )

    df['readout_bias'] = df['p1m0'] - df['p0m1']
    if 'operational' in df.columns:
      df = df[df['operational'] == True]

    # df = df.drop(
    #   columns=['operational', 'anharmonicity', 'frequency', 'qubit'],
    #   errors='ignore'
    # )

    df['t1'] = df['t1'].astype(int)
    df['t2'] = df['t2'].astype(int)

    # qubit, t1, t2, readout_err, p1m0, p0m1, id_error, sx_error, pauli_x_error, z_axis_rotation_error, cz_error, gate_time
    self.df = df
    return df

def query(df:pd.DataFrame, col:str, value:float, tol:float):
  if col not in df.columns:
    raise ValueError(f"{col} not in Valid cols")

  df = df.drop(df[(df[col] < value - tol) | (df[col] > value + tol)].index)
  return df