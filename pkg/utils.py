from signal import signal, SIGINT
import sys

name = '' if len(sys.argv) < 2 else sys.argv[1]
def args():
  if len(sys.argv) < 2:
    return ''
  else:
    return sys.argv[1]

def sig_hand(_, __):
  m.error('Stopping program!')
  exit(0)
# end

signal(SIGINT, sig_hand)

from numpy import ndarray
from json import dumps
from time import time
import numpy as np

def t():
  return int(time())

t0 = t()

# write as class to be able to use .
class m:
  def log(f, data):
    try:
      f  = 'log/' + f
      fp = open(f, 'a')

      if not isinstance(data, str):
        for key in data:
          if isinstance(data[key], ndarray):
            data[key] = data[key].tolist()

        data = dumps(data)

      fp.write(data + '\n')
      fp.close()
    except Exception as e:
      print(f'Error writing to log file: {e}')
  # end

  def init(f):
    try:
      f  = 'log/' + f
      fp = open(f, 'w')
      fp.write('')
      fp.close()
    except Exception as e:
      print(f'Error writing to log file: {e}')
  # end


  def info(string):
    print('\033[94m{}\033[0m'.format(string))

  def done(string):
    print('\033[92m{}\033[0m'.format(string))

  def warn(string):
    print('\033[93m{}\033[0m'.format(string))

  def error(string):
    print('\033[91m{}\033[0m'.format(string))
# endclass