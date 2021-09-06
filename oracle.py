'''
This file implements the phase oracle used in Task 1. 
'''




from qiskit import QuantumCircuit, assemble, Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np



# Input: input_vector, the initial input vector [1, 5, 7, 10] to determine m, n and initialize QRAM.
# Output: oracle, a QuantumCircuit object for m+1 qubits, representing the quantum phase oracle
#       that adds a phase of pi to solution states (with alternating bitstrings)
def oracle_circuit(input_vector):
    n = int(np.log2(len(input_vector)))      # since the size of input_vector is 2**n
    m = int(np.log2(max(input_vector))) + 1     # the length of each bitstring, determined by the
                                                # largest value in input_vector
    oracle = QuantumCircuit(n+1, name='Oracle')
    oracle.mcx(list(range(n)), n)
    return oracle

def test():
    qc = oracle_circuit([1, 5, 7, 10])
    qc.draw()
    plt.show()


if __name__ == '__main__':
    test()
