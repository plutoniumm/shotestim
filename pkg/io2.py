from json import dumps
from math import isnan

def parsekv(s):
  if isnan(s):
    raise ValueError('Invalid values')
  values = s.split(';')
  val_dict = {}

  for val in values:
    k, v = val.split(':')
    val_dict[k] = v
  # endfor val

  return val_dict

def save(file, data):
  isJSON = file.split('.')[-1] == 'json'
  if isJSON:
    with open(file, 'w') as f:
      f.write(dumps(data))
  else:
    with open(file, 'w') as f:
      f.write(data)
  # end