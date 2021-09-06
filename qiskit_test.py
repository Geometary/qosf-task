from qiskit import QuantumCircuit, assemble, Aer, transpile
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np



def test_intro():       # an introductory test of qiskit
    n = 8
    n_q = n     # number of qubits in the circuit
    n_b = n     # number of output bits at the end
    qc_output = QuantumCircuit(n_q, n_b)

    for j in range(n):
        qc_output.measure(j, j)     # adds a measurement that
                                    # tells qubit j to write
                                    # an output to bit j
    # qc_output.draw()
    # plt.show()

    sim = Aer.get_backend('aer_simulator')      # the simulator we will use
    qobj = assemble(qc_output)      # turns the circuit into a runnable object
    result = sim.run(qobj).result()     # result of the simulation experiment
    # the result is a dictionary containing the number of times each result appeared
    counts = result.get_counts()
    # plot_histogram(counts)
    # plt.show()

    qc_encode = QuantumCircuit(n, n)
    qc_encode.x(7)      # Apply a NOT (PauliX) gate to qubit 7
    # qc_encode.draw()
    # plt.show()

    qc_encode.measure_all()
    # qc_encode.draw()
    # plt.show()

    # an implementation of the half adder circuit
    qc_ha = QuantumCircuit(4, 2)
    # encode inputs in qubits 0 and 1
    qc_ha.x(0)  # set a = 1
    qc_ha.x(1)  # set b = 1
    qc_ha.barrier()
    # use cnots to write the XOR of the inputs on qubit 2
    qc_ha.cx(0, 2)
    qc_ha.cx(1, 2)
    # use ccx (Toffoli) to write the AND of the inputs on qubit 3
    qc_ha.ccx(0, 1, 3)
    qc_ha.barrier()
    # extract outputs
    qc_ha.measure(2, 0) # extract XOR value
    qc_ha.measure(3, 1)

    #qc_ha.draw()
    #plt.show()
    qobj = assemble(qc_ha)
    counts = sim.run(qobj).result().get_counts()
    plot_histogram(counts)
    plt.show()

'''def dj_algorithm(n, oracle_n):         # implements the Deutsch-Jozsa algorithm
    oracle = dj_problem_oracle(oracle_n)    # the constant/balanced oracle to be used
    qc = QuantumCircuit(n+1, n)     # the quantum circuit
    # First, apply H gate on the first n qubits to create an equal superposition
    # of all basis states from |0> to |2^n-1>
    qc.h(range(n))
    # Then, convert the |0> state of qubit n to |-> for phase kickback to work
    qc.x(n)
    qc.h(n)
    # Now we append the oracle to qc, adding each f(x) to qubit n
    qc.append(oracle, range(n+1))
    # Here, if qubit n is still considered to be in |-> state, then an extra pi phase will 
    # appear for those x with f(x) = 1

    # Now qubit n is unimportant, and we apply H gate to every qubit 0 to n-1, such that the
    # sum is now over both x and y, where the term becomes (-1)^(f(x) + x.y)|y>.
    # Here a bitwise dot product between x and y appears because H|0> = |+>, H|1> = |->,
    #   - if |y> happens to be 0 at position k, then a factor of 1 appears
    #   - if |y> happens to be 1 at position k, 
    #       - if |x> happens to be 0 at position k, then a factor of 1 appears
    #       - if |x> happens to be 1 at position k, then a factor of -1 appears
    qc.h(range(n))

    # The amplitude of |000..000> state is then sum of (-1)^(f(x)) over all possible x
    # If the oracle is constant, then this amplitude is +/- 1, vice versa
    # If the oracle is balanced, then this amplitude is 0
    # So we measure the first n qubits. Result is 0000.0000 => constant, otherwise balanced
    qc.measure(range(n), range(n))

    sim = Aer.get_backend('qasm_simulator')
    transpiled_qc = transpile(qc, sim)
    qobj = assemble(transpiled_qc, sim)
    result = sim.run(qobj).result()
    counts = result.get_counts()
    plot_histogram(counts)
    plt.show()

    qc.draw()
    plt.show()
'''

    



def main():
    test_intro()



if __name__ == '__main__':
    main()