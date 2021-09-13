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
# Output: 
#   - if n = 2, returns a tuple consisting of QRAM, VC_1, VC_2, m, and n
#   - otherwise, returns a tuple consisting of oracle, None, None, m, and n 
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
        
        # QRAM_circ.barrier()
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
        # QRAM_circ.barrier()


        # Extract the value in m register using anciliary qubits
        for k in range(2**n):
            for l in range(m):
                QRAM_circ.ccx(q_tau[k], q_m[k*m + l], q_target[l])
        

        # Then recover the state of tau register
        for i in range(n-1, 0, -1):
            base = base // 2
            for j in range(2**i-1, -1, -1):
                QRAM_circ.cx(q_tau[base+j], q_tau[j])
            
            for j in range(2**i-1, -1, -1):
                QRAM_circ.ccx(q_a[i], q_tau[j], q_tau[base+j])              
        QRAM_circ.cx(q_tau[1], q_tau[0])
        QRAM_circ.cx(q_a[0], q_tau[1])
        QRAM_circ.x(q_tau[0])

        # And also recover m register
        for i in range(2**n):
            value = input_vector[i]
            value_bitstring = list(format(value, 'b').zfill(m))
            value_bitstring.reverse()   # to iterate from LSB to MSB
            for j in range(m):
                if value_bitstring[j] == '1':
                    QRAM_circ.x(q_m[i*m + j])
        
        QRAM_circ.draw()
        plt.title("QRAM circuit for input_vector " + str(input_vector) + "; 'QRAM' gate")
        plt.savefig('.\circuit_diagrams\QRAM.svg')

        return QRAM_circ
    

    def VC(type=0):     # internal function to create the verification circuit, adding the extra pi phase to
                        # solution address states
                        # There are 3 different types of VC, namely VC_0, VC_1, and VC_2
                        # since the value qubits need to be accessed twice for n = 2, the circuit is now 
                        # designed to not change the state of value qubits

        q_val = QuantumRegister(m, name='val')      # value qubits
        q_p = QuantumRegister(1, name='p')          # phase qubit, already initialized to |-> 
        VC_circ = QuantumCircuit(q_val, q_p)

        # First, check if the bitstring is alternating
        for i in range(m-1):
            VC_circ.cx(q_val[i+1], q_val[i])
        
        # Then, add |1> to phase qubit if it's alternating, completing the phase kickback
        if type == 1:     # for VC_1, do the phase flip only for the solution starting with |0>
                            # (i.e. |0101010...>)
            VC_circ.x(q_val[m-1])
            VC_circ.mcx(list(range(m)), q_p[0])
            VC_circ.x(q_val[m-1])
        elif type == 2:     # for VC_2, do the phase flip only for the solution starting with |1>
                            # (i.e. |101010101...>)
            VC_circ.mcx(list(range(m)), q_p[0])
        else:
            type = 0
            VC_circ.mcx(list(range(m - 1)), q_p[0])     # otherwise, do the flip for both solutions
        
        # Finally, recover the previous value state
        for j in range(m-2, -1, -1):
            VC_circ.cx(q_val[j+1], q_val[j])

        VC_circ.draw()
        plt.title("Type {} verification circuit, for input vector ".format(type) + str(input_vector) + "; 'VC_{}' gate".format(type))
        plt.savefig('.\circuit_diagrams\\vc_{}.svg'.format(type))
        return VC_circ
    
    if n == 2:      # in which case we assemble the components and
                    # go beyond the qubit limit
        return QRAM(), VC(type=1), VC(type=2), m, n

    # Now we deal with the case n != 2
    # Here we connect QRAM and VC together
    vc = VC()
    qram = QRAM()
    n_qubits = qram.num_qubits          # number of qubits used in QRAM
    vc = vc.to_gate(label='VC_0')
    qram = qram.to_gate(label='QRAM')

    oracle = QuantumCircuit(n_qubits + 1)       # since an extra phase qubit is needed for the oracle
    oracle.append(qram, list(range(n_qubits)))    
    oracle.append(vc, list(range(n_qubits - m, n_qubits + 1)))
    oracle.append(qram, list(range(n_qubits)))  # append another QRAM to restore state of t/val register
    oracle.draw()
    plt.title("Circuit diagram of the oracle for input vector " + str(input_vector) + ", with m = {} and n = {}; 'ORACLE' gate".format(m, n))
    plt.savefig('.\circuit_diagrams\oracle.svg')

    return oracle, None, None, m, n




# returns the bitstring stored in this address
def oracle_test(address, oracle, m, n):
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
    qc.measure(list(range(n_qubits-m-1, n_qubits-1)), list(range(m)))       # measures the value state
                                                                            # after verification

    qc.draw()
    plt.savefig('test_circuit.svg')
    sim = AerSimulator(method='statevector')
    # DO NOT use the matrix_product_state simulator in any case!!!
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
    input_vector = list([1, 5, 7, 10]) 
    results = []
    oracle, m, n = oracle_circuit(input_vector)
    # oracle.draw()
    # plt.savefig('QRAM circuit.svg')
    oracle_test(0, oracle, m, n)
    # VC_test(vc, m, n)

    '''for i in range(len(input_vector)):
        results += QRAM_test(i, oracle, m, n)
    print(results)'''
    
