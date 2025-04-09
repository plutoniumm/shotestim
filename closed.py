import numpy as np

def closed(Q, tau1, tau2, s, D, eplg):
  tau1 = 1 - tau1**2 * np.exp(-tau1) - (1 + tau1)**2 * np.exp(-2*tau1)
  tau2 = 1 - tau2**2 * np.exp(-tau2) - (1 + tau2)**2 * np.exp(-2*tau2)
  gate = D*(eplg**2)/2

  variance = Q/(2*s) * (tau1 + tau2 + gate)

  return variance**0.5

def pred(s, u):
  logS = np.log2(s)
  logS_m = -0.5*logS - 2.871
  s = (2**logS_m) * u

  return s