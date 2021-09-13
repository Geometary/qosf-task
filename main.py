from qiskit.circuit.classicalregister import ClassicalRegister
from qiskit.circuit.quantumcircuit import QuantumCircuit
from oracle import oracle_circuit
from diffuser import diffuser_circuit
import from2to4 as dlc
from qiskit.providers.aer import AerSimulator
from qiskit import transpile, ClassicalRegister
from qiskit.quantum_info import partial_trace
import matplotlib.pyplot as plt
import numpy as np


# The main function that returns a QuantumCircuit that solves Task 1 for arbitrary m and n
def Grovers_circuit(input_vector):
    qc, vc1, vc2, m, n = oracle_circuit(input_vector)
    diffuser = diffuser_circuit(n)
    overall_circ = None

    if n == 1:      # the trivial case, directly returns the |+> state
        overall_circ = QuantumCircuit(1)
        overall_circ.h(0)

    elif n == 2:
        # where we go beyond the qubit limit using from2to4.py
        overall_circ = dlc.improve(diffuser, qc, vc1, vc2, m)
    else:
        # where we just apply the normal Grover's algorithm      
        n_qubits = qc.num_qubits        # The total number of qubits of the oracle
        overall_circ = QuantumCircuit(n_qubits)
        oracle = qc.to_gate(label='ORACLE')
        dif = diffuser.to_gate(label='DIF')        
        theta = np.arcsin(np.sqrt(2 / 2 ** n))     # the angle between |s> and |w'>, as M=2 and N=2^n
        t = round((np.pi / 2 / theta - 1) / 2)      # number of iterations needed
        # First, initialize the address state to |s>, and phase qubit to |->
        for i in range(n):
            overall_circ.h(i)
        overall_circ.x(n_qubits - 1)
        overall_circ.h(n_qubits - 1)

        for _ in range(t):
            overall_circ.append(oracle, list(range(n_qubits)))
            overall_circ.append(dif, list(range(n)) + [n_qubits - 1])    # Connects DIF to oracle
        
    overall_circ.draw()
    plt.title("Overall circuit for input_vector " + str(input_vector) + " , with n = {}, m = {}".format(n, m))
    plt.savefig(".\circuit_diagrams\overall.svg")
        
  
    return overall_circ, n


# The test function
# If return_state, return the final state; otherwise, only measure the final state. Default to be False.
# n_shots is the total number of experiments to be run if measurement is used
def Grovers_test(input_vector, return_state=False, n_shots=8000):
    Grovers_circ, n = Grovers_circuit(input_vector)
    num_q = Grovers_circ.num_qubits     # the total number of qubits of the overall circuit
    sim = AerSimulator(method='statevector', precision='single')
    if return_state:        # to directly return the final state
        Grovers_circ.save_statevector()
        qc = transpile(Grovers_circ, sim)
        result = sim.run(qc).result()
        state = result.get_statevector(decimals=3)
        reduced_dm = partial_trace(state, list(range(n, num_q)))    # only focus on the state of n address qubits
        wanted_state = np.diagonal(reduced_dm)
        print("The final statevector is: " + str(wanted_state))
        print("The circuit diagram file is saved as .\circuit_diagrams\overall.svg")
    else:                   # to only measure the final state
        meas = ClassicalRegister(n)
        Grovers_circ.add_register(meas)
        for i in range(n):
            Grovers_circ.measure(i, meas[i])        # measure the address qubits
        qc = transpile(Grovers_circ, sim)
        result = sim.run(qc, shots=n_shots).result()
        counts = result.get_counts()
        print("Out of {} experiments, ".format(n_shots), end="")
        for index in counts.keys():
            print("{} was measured {} times, ".format(index, counts[index]), end="")
        print("while also saving the circuit diagram file as .\circuit_diagrams\overall.svg.")


if __name__ == '__main__':
    input_vector = [1, 5, 7, 10]
    Grovers_test(input_vector)
    # Optional return_state variable (default to be False) and n_shots variable (default to be 8000)
    # can also be entered in the Grovers_test function to manually adjust the format of the output
