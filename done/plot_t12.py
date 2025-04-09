import pandas as pd
import numpy as np
import re

with open("./images/torino_blank.svg", "r") as f:
  svg = f.read().strip()

df = pd.read_csv("./t2s.csv")
df = df.rename(columns=lambda x: x.strip())

df["match"] = df["match"].str.extract(r"(\d+\.\d+)")

def orig(val):
  return f'<circle r="16" /><text dy="0.2em">{val}</text>'

def new(val, color, size):
  return f'<circle r="16" fill="{color}" /><text dy="0.2em" font-size="{size}">{val}</text>'

keys = {
  "0.1": "#3C5",
  "0.5": "#F90",
  "1.0": "#F43",
  "10.0": "#000"
}

marked = []
for i, row in df.iterrows():
  qbit = row["qbit"]
  match = row["match"]
  gate = row["gate"]
  color = "#000"

  val = re.search(r"\d+", row["gate"]).group(0)
  letter = re.search(r"[a-z]", row["gate"]).group(0)
  val = int(np.log10(int(val)))
  val = f"{letter}-{val}"

  for k in keys:
    if float(match) <= float(k):
      color = keys[k]
      break
    # endif
  # endfor

  marked.append(qbit)
  print(f"GATE: {gate} -> {val} | {match} -> {color}")
  svg = svg.replace(orig(qbit), new(val, color, 16))
# endfor

for i in range(0, 133):
  if i not in marked:
    svg = svg.replace(orig(i), new(i, "#A5E5", 12))
# endfor


with open("./torino_t2.svg", "w") as f:
  f.write(svg)
