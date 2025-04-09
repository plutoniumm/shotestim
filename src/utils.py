def run(qc, backend, shots):
  from qiskit_ibm_runtime import SamplerV2 as Sampler
  sampler = Sampler(backend=backend)

  bname = backend.__class__.__name__
  if bname != 'AerSimulator':
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager as gpm
    qc = gpm(optimization_level=0, backend=backend).run(qc)

  print(qc[1].depth())
  raise SystemExit
  if isinstance(qc, list):
    print(f"Running {qc[0].num_qubits} qubits on {bname} with {shots} shots")
    return sampler.run(qc, shots=shots).result()
  else:
    print(f"Running {qc.num_qubits} qubits on {bname} with {shots} shots")
    return sampler.run([qc], shots=shots).result()