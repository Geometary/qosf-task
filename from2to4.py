'''
This file provides utility functions that modify the original Grover's circuit to dramatically improve
the maximum m allowed in the simulation from 2 to 4, with n = 2. Using these utility functions, the size
of the search space is no longer needed to be doubled for a length 4 input vector, in theory.
'''

from qiskit import QuantumCircuit, assemble, transpile, QuantumRegister, ClassicalRegister
from qiskit.providers.aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np


# returns a two-qubit circuit that do the transformation |b>|a> -> 1/sqrt(2) * (|a>+|b>)|a>
# in other words, it generates a equal superposition of two input states
# |a> and |b> are guaranteed to be two Z basis states and are not the same state
def superpose():
    a = QuantumRegister(1, name='a')
    b = QuantumRegister(1, name='b')
    u = QuantumCircuit(a, b)

    u.ch(a[0], b[0])    # completes the transformation if a=1
    u.x(a[0])
    u.cx(a[0], b[0])    
    u.ch(a[0], b[0])    # completes the transformation if a=0
    u.x(a[0])           # recovers the original a

    u.draw()
    plt.savefig('.\circuit_diagrams\superpos_circ.svg')
    return u


# returns a 6-qubit circuit that do the transformation |j1>|j0>|b1>|b0>|a1>|a0> -> 1/sqrt(2) * |j1'>|j0'>(|a1a0>+|b1b0>)|a1a0>
# |a1a0> and |b1b0> are guaranteed to be two different two-qubit Z basis states
def superpose_2():
    sup = superpose().to_gate(label='SUP')
    csup = sup.control(1)
    ccsup = sup.control(2)
    a = QuantumRegister(2, name='a')    # stores state |a> = |a1a0>
    b = QuantumRegister(2, name='b')    # stores state |b> = |b1b0>
    j = QuantumRegister(2, name='j')    # judge qubit, reusing the previous two phase qubits
    w = QuantumCircuit(a, b, j)
    w.h(j[0])  # change the state of j0 and j1 to |1>, as previously they are reused phase-kickback qubits in |->
    w.h(j[1])
    w.save_statevector(label='psi_0')

    # First, check both statement C (a0 == b0) and statement C' (a1 == b1), record them in j0 and j1, respectively
    w.cx(a[0], b[0])
    w.x(b[0])
    w.cx(b[0], j[0])
    w.x(b[0])
    w.cx(a[0], b[0])        # encodes the statement C, and recovers b0 state
    w.cx(a[1], b[1])
    w.x(b[1])
    w.cx(b[1], j[1])
    w.x(b[1])
    w.cx(a[1], b[1])        # encodes the statement C', and recovers b1 state
    w.save_statevector(label='psi_1')

    # Second, deal with cases where C or C' is true
    w.x(j[1])
    w.append(csup, [j[1], a[0], b[0]])
    w.x(j[1])       # deal with the case where C' is true
    w.x(j[0])
    w.append(csup, [j[0], a[1], b[1]])
    w.x(j[0])       # deal with the case where C is true
    w.save_statevector(label='psi_2')

    # Finally, deal with the case where neither C nor C' is true
    w.append(ccsup, [j[0], j[1], a[0], b[0]])
    w.cx(b[0], a[0])
    w.x(a[0])
    w.mcx([a[0], j[0], j[1]], b[1])
    w.x(a[0])
    w.cx(b[0], a[0])
    w.save_statevector(label='psi_3')

    w.draw()
    plt.title('Circuit diagram for two-qubit superposition')
    plt.savefig('.\circuit_diagrams\superpos_2_circ.svg')
    return w


# Goes beyond the qubit limit for n = 2!
# Returns the final QuantumCircuit to be used for simulating Task 1 with n = 2 and m < 5
def improve(oracle, m, n, diffuser):
    print("Crossing the limit...")

    return


# Test finished. No bug has been detected.
def dlc_test(a, b):
    sim = AerSimulator(method='statevector', precision='single')
    sup_2 = superpose_2()

    prepare_circ = QuantumCircuit(6)
    prepare_circ.x(4)
    prepare_circ.x(5)
    prepare_circ.h(4)       
    prepare_circ.h(5)       # initializes the state of qubit 4 and 5 to |-> to simulate the real situation

    a_bitstring = list(format(a, 'b').zfill(2))
    a_bitstring.reverse()
    b_bitstring = list(format(b, 'b').zfill(2))
    b_bitstring.reverse()
    for i in range(2):
        if a_bitstring[i] == '1':
            prepare_circ.x(i)
        if b_bitstring[i] == '1':
            prepare_circ.x(2 + i)

    prepare_circ.barrier()

    qc = prepare_circ.compose(sup_2)

    # sup = superpose().to_gate(label='SUP')
    # prepare_circ = QuantumCircuit(2)
    # # prepare_circ.x(0)
    # prepare_circ.x(1)
    # prepare_circ.append(sup, [0, 1])
    # qc = prepare_circ
    # qc.save_statevector()

    qc = transpile(qc, sim)
    result = sim.run(qc, shots=8000).result()
    state = result.data(0)['psi_3']
    print(state[27], state[31])


if __name__ == '__main__':
    dlc_test(3, 2)





