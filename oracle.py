'''
This file implements the phase oracle used in Task 1. The effect of this circuit is to reflect
the input state about state |w'>, the state orthogonal to the state |w>, an equal superposition of all
solution states. In other words, it adds a pi phase to each basis state corresponding to an
alternating bitstring in the input vector.
'''


from qiskit import QuantumCircuit, assemble, transpile, QuantumRegister, ClassicalRegister
from qiskit.providers.aer import AerSimulator
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
        
        QRAM_circ.barrier()
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
        QRAM_circ.barrier()

        # Finally, extract the value in m register using anciliary qubits
        for k in range(2**n):
            for l in range(m):
                QRAM_circ.ccx(q_tau[k], q_m[k*m + l], q_target[l])

        return QRAM_circ
    

    def VC():       # internal function to create the verification circuit, adding the extra pi phase to
                    # solution address states
        q_val = QuantumRegister(m, name='val')
        q_p = QuantumRegister(1, name='p')            
        VC_circ = QuantumCircuit(q_val, q_p)

        # First, check if the bitstring is alternating
        for i in range(m-1):
            VC_circ.cx(q_val[i+1], q_val[i])
        
        # Then, add |1> to phase qubit if it's alternating, completing the phase kickback
        VC_circ.x(q_p[0])
        VC_circ.h(q_p[0])
        VC_circ.mcx(list(range(m-1)), q_p[0])

        return VC_circ
    
    # Here we connect QRAM and VC together
    vc = VC()
    qram = QRAM()
    qram.add_register(QuantumRegister(1, name='p'))
    qram.barrier()
    n_qubits = qram.num_qubits
    oracle = qram.compose(vc, list(range(n_qubits - m - 1, n_qubits)))
    oracle.draw()
    plt.title('The oracle circuit, for input vector ' + str(input_vector))
    plt.savefig('oracle.svg')

    return oracle, m, n




# returns the bitstring stored in this address
def QRAM_test(address, oracle, m, n):
    # m is length of each bitstring stored, n is number of address qubits
    address_bitstring = list(format(address, 'b').zfill(n))
    address_bitstring.reverse()
    n_qubits = oracle.num_qubits
    prepare_circ = QuantumCircuit(n_qubits)
    '''for i in range(n):
        if address_bitstring[i] == '1':
            prepare_circ.x(i)'''
    for i in range(n):
        prepare_circ.h(i)        
    qc = prepare_circ.compose(oracle)
    c_result = ClassicalRegister(m, name='r')
    qc.add_register(c_result)
    qc.barrier()
    '''if address == 5:
        qc.add_register(ClassicalRegister(1))
        qc.measure(5, 0)
        qc.measure(8, 1)
        qc.draw()
        plt.savefig('circuit_6.svg')
        sim = AerSimulator(method='statevector')
        tcirc = transpile(qc, sim)
        counts = sim.run(tcirc).result().get_counts()
        print(counts)
        quit()'''
    
    reg = QuantumRegister(1)
    qc.add_register(reg)
    qc.h(reg[0])
    qc.measure(list(range(n_qubits-m, n_qubits)), list(range(m)))

    qc.draw()
    plt.savefig('test_circuit.svg')
    sim = AerSimulator(method='statevector', precision='single')
    # DO NOT use the matrix_product_state simulator!!!
    qc = transpile(qc, sim)
    result = sim.run(qc, shots=8000).result()
    counts = result.get_counts()
    print(counts)


# used to test the mysterious bit-flip bug
# confirmed: bug is caused by the matrix_product_state simulator
# confirmed to be bug-free
'''def QRAM_debug(input_vector, results):
    n = len(input_vector)
    for i in range(n):
        true_value = input_vector[i]
        sim_value = int(results[i], 2)
        xor_bitstring = list(format(true_value ^ sim_value, 'b'))     # 0 for correct bits, 1 for wrong bits
        xor_bitstring.reverse()
        flipped_bits = []
        for j in range(len(xor_bitstring)):
            if xor_bitstring[j] == '1':
                flipped_bits.append(j)
        print("Position {}, flipped bits: ".format(i), flipped_bits)'''


# used to test the verification circuit
'''def VC_test(vc, m, n):
    vc_prep = QuantumCircuit(m+1)
    for i in range(m):
        vc_prep.h(i) 
    vc = vc_prep.compose(vc)
    vc.save_statevector()
    vc.draw()
    plt.savefig('vc.svg')

    sim = AerSimulator(method='statevector', precision='single')
    vc = transpile(vc, sim)
    result = sim.run(vc, shots=4000).result()
    state = result.get_statevector()
    print(list(state))'''







if __name__ == '__main__':
    input_vector = list([0, 1, 2, 4, 8, 12, 16, 31]) 
    results = []
    oracle, m, n = oracle_circuit(input_vector)
    # oracle.draw()
    # plt.savefig('QRAM circuit.svg')
    # QRAM_test(0, oracle, m, n)
    # VC_test(vc, m, n)

    '''for i in range(len(input_vector)):
        results += QRAM_test(i, oracle, m, n)
    print(results)'''
    
