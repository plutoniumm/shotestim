from json import dumps, load
from time import time

token = {
  'channel': 'ibm_quantum',
  'instance': 'ibm-q-iitmadras/internal/default',
  'token': '',
}

class Service:
  service = None

  def __init__(self):
    from qiskit_ibm_runtime import QiskitRuntimeService
    self.service = QiskitRuntimeService(**token)

  def __getattr__(self, name):
    if name.startswith('ibm_'):
      return self.service.get_backend(name)
    else:
      return self.service.get_backend(f'ibm_{name}')

def write(name, data):
  date = int(time()/1000)
  fname = f'{name}_{date}.json'

  with open(fname, 'w') as f:
    f.write(dumps(data))
  print(f"Saved to {fname}")

def read(name):
  if not name.endswith('.json') and not name.endswith('.txt'):
    fname = f'./{name}.json'
    with open(fname) as f:
      d = load(f)
  else:
    fname = f'./{name}'
    with open(fname) as f:
      d = f.read()

  return d

# reg=['hfs'], dir='h2'
def fetch(id, regs, dir):
  service = Service().service
  jobs = service.job(id).result()

  for idx, job in enumerate(jobs):
    for reg in regs:
      counts = job.data[reg].get_bitstrings()

      with open(f'{dir}/{reg}_{idx}.json', 'w') as f:
        f.write(dumps(counts))