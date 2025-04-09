from src.query import BStats, pd
from t2s import keys as RUN_KEYS
from _config import read
import numpy as np

backend: pd.DataFrame = BStats().torino_t2
RUN_KEYS = pd.DataFrame(RUN_KEYS).transpose()
RUN_KEYS.drop(["reps", "gate", "cbit"], axis=1, inplace=True)
RUN_KEYS = RUN_KEYS[RUN_KEYS['waste'].apply(lambda x: isinstance(x, int))]

def toFrame(arr):
  for i in range(len(arr)):
    arr[i] = [int(i) for i in arr[i]][::-1]

  return np.array(arr).astype(np.ushort)
# end

t2s = read("res/wastes_1720674")
t2s = toFrame(t2s).transpose()

def post(series):
  for i, row in enumerate(series):
    try:
      data_row = RUN_KEYS.iloc[i]
    except IndexError:
      break

    qubit = data_row['qubit']
    waste = data_row['waste']
    print(f"{i}=={waste}: {np.mean(row)*100:.2f}:: Q{qubit}")
  # endfor

# run it
post(t2s)