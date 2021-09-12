import time
from qiskit.circuit.classicalregister import ClassicalRegister
from oracle import oracle_circuit
from diffuser import diffuser_circuit
# from qiskit import QuantumCircuit, assemble, transpile, QuantumRegister, ClassicalRegister
import from2to4 as dlc
from qiskit.providers.aer import AerSimulator
from qiskit import transpile, ClassicalRegister
from qiskit.quantum_info import partial_trace, Statevector
# from qiskit.visualization import plot_histogram
# import matplotlib.pyplot as plt
import numpy as np


def Grovers_circuit(input_vector):
    oracle, m, n = oracle_circuit(input_vector)
    diffuser = diffuser_circuit(n)
    return


def Grovers_test(input_vector):
    Grovers_circ = Grovers_circuit(input_vector)
    return


if __name__ == '__main__':
    input_vector = [1, 5, 7, 10]
    qram, vc1, vc2, m = oracle_circuit(input_vector)
    dif = diffuser_circuit(2)
    qc = dlc.improve(dif, qram, vc1, vc2, m)
    num_q = qc.num_qubits
    sim = AerSimulator(method='statevector', precision='single')
  
    if m < 4:
        qc.save_statevector()
        qc = transpile(qc, sim)
        result = sim.run(qc).result()
        state = result.get_statevector()
        reduced_dm = partial_trace(state, list(range(2, num_q)))
        wanted_state = np.diagonal(reduced_dm)
        print(wanted_state)
    else:
        meas = ClassicalRegister(2, name='c')
        qc.add_register(meas)
        qc.measure(0, meas[0])
        qc.measure(1, meas[1])
        qc = transpile(qc, sim)
        result = sim.run(qc).result()
        counts = result.get_counts()
        print(counts)
    

    

    

    


