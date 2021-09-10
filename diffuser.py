'''
This file implements the diffuser circuit used in Task 1. The effect of this circuit is to reflect about
the initial equal superposition state |s>. Referencing the Qiskit tutorial of Grover's algorithm, this 
can be done by applying an unitary transformation that: 1. rotates |s> to |00...0>; 2. reflects about
|00...0>; 3. rotates |00...0> to |s>.

The overall effect of this transformation is a reflection about |s> because two rotations and one reflection
definitely makes up a reflection, and |s> does not change after the transformation.
'''

from qiskit import Aer, QuantumCircuit, assemble, transpile, QuantumRegister, ClassicalRegister
from qiskit.providers.aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np


# Accepts n, the number of address qubits
# Returns DF_circ, a QuantumCircuit that acts as a diffuser for an address state
def diffuser_circuit(n):
    DF_circ = QuantumCircuit(n+1)
    # qubit 0~n-1 are connected to address qubits of the oracle circuit
    # qubit n is connected to the phase qubit of the oracle circuit, in order to
    # reuse the qubit in |-> state from before

    # Step 1: rotates |s> to |00...0>
    for i in range(n):
        DF_circ.h(i)
    
    # Step 2: reflects about |00...0>
    for j in range(n+1):     
        DF_circ.x(j)    # where a pi phase is first added to the phase qubit
    DF_circ.mcx(list(range(n)), n)      # the extra phase is removed only if qubit 0~n-1 were initially
                                        # in state |00...0>
    for k in range(n):
        DF_circ.x(k)    # recovers the initial state of qubit 0~n-1
    

    # Step 3: rotates |00...0> to |s>
    for l in range(n):
        DF_circ.h(l)
    
    DF_circ.draw()
    plt.title("The diffuser circuit, with {} address qubits".format(n))
    plt.savefig('.\circuit_diagrams\diffuser.svg')
    return DF_circ


# Accepts n as the number of address qubits and tests the diffuser circuit
def DF_test(n):
    test_circ = QuantumCircuit(n+1)
    test_circ.x(n)
    test_circ.h(n)
    DF = diffuser_circuit(n)
    test_circ.barrier()
    qc = test_circ.compose(DF)
    qc.save_statevector()
    
    sim = AerSimulator(method='statevector', precision='single')
    qc = transpile(qc, sim)
    result = sim.run(qc).result()
    state = result.get_statevector()
    print(state)


if __name__ == '__main__':
    n = 3
    DF_test(n)