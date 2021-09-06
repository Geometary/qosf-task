'''
This file implements the phase oracle used in Task 1. 
'''


from qiskit import QuantumCircuit, assemble, Aer, QuantumRegister, ClassicalRegister
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np




# Input: input_vector, the initial input vector [1, 5, 7, 10] to determine m, n and initialize QRAM.
# Output: oracle, a QuantumCircuit object for m+1 qubits, representing the quantum phase oracle
#       that adds a phase of pi to solution states (with alternating bitstrings)
def oracle_circuit(input_vector):
    n = int(np.log2(len(input_vector)))         # the number of address qubits
    m = int(np.log2(max(input_vector))) + 1     # the length of each bitstring, determined by the
                                                # largest value in input_vector
    def QRAM():     # internal function to create the QRAM circuit, using Bucket-Brigade model
        q_a = QuantumRegister(n, name='a')
        q_tau = QuantumRegister(2**n, name='tau')
        q_m = QuantumRegister(m*2**n, name='m')
        q_target = QuantumRegister(m, name='t')
        QRAM_circ = QuantumCircuit(q_a, q_tau, q_m, q_target)   
        # consists of a, tau, m, target registers

        # First, write on the m register using values from input_vector
        for i in range(2**n):
            value = input_vector[i]
            value_bitstring = list(format(value, 'b').zfill(m))
            value_bitstring.reverse()   # to iterate from LSB to MSB
            for j in range(m):
                if value_bitstring[j] == '1':
                    QRAM_circ.x(q_m[i*m + j])
        
        # Then, connect register a with tau (translation from address qubits to anciliary qubits)
        QRAM_circ.x(q_tau[0])      # initializes tau_0 to |1>
        QRAM_circ.cx(q_a[0], q_tau[1])
        QRAM_circ.cx(q_tau[1], q_tau[0])
        base = 2
        for i in range(1, n):
            # Step 1: entangle the address qubit with each anciliary qubit where
            #           the corresponding bit is 1
            for j in range(2**i):
                QRAM_circ.ccx(q_a[i], q_tau[j], q_tau[base+j])
            # Step 2: use higher anciliary qubits to cancel the excitations of
            #           lower ones
            for j in range(2**i):
                QRAM_circ.cx(q_tau[base+j], q_tau[j])
            base *= 2
        
        # Finally, extract the value in m register using anciliary qubits
        for k in range(2**n):
            for l in range(m):
                QRAM_circ.ccx(q_tau[k], q_m[k*m + l], q_target[l])
            QRAM_circ.barrier()

        return QRAM_circ
    
    qr = QRAM()
    #oracle.mcx(list(range(n)), n)
    return qr, m, n

def QRAM_test(address):
    oracle, m, n = oracle_circuit([4, 9, 12, 15])
    # Note: longer input_vector or larger contents will exceed memory limit
    #           of the simulator (34GB memory is needed for values up to 31)
    address_bitstring = list(format(address, 'b').zfill(n))
    address_bitstring.reverse()
    n_qubits = oracle.num_qubits
    prepare_circ = QuantumCircuit(n_qubits)
    for i in range(n):
        if address_bitstring[i] == '1':
            prepare_circ.x(i)
    qc = prepare_circ.compose(oracle)
    c_result = ClassicalRegister(m, name='r')
    qc.add_register(c_result)
    qc.measure(list(range(n_qubits-m, n_qubits)), list(range(m)))
    qobj = assemble(qc)
    sim = Aer.get_backend("qasm_simulator")
    counts = sim.run(qobj).result().get_counts()
    plot_histogram(counts)
    #qc.draw()
    plt.show()

if __name__ == '__main__':
    QRAM_test(0)
    QRAM_test(1)
    QRAM_test(2)
    QRAM_test(3)
