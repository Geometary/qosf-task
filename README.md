# 2021 QOSF Mentoring Program Screening Task 1
## Repository Structure
* This repository is divided into 4 main parts: oracle.py, diffuser.py, main.py, and from2to4.py, with other files as either reference documents or circuit diagrams.
* The file oracle.py defines the function oracle_circuit, which provides the phase oracle circuit in Grover's algorithm corresponding to the given input vector, as a Qiskit QuantumCircuit object. The oracle consists of QRAM, which stores the values in the input vector corresponding to their indices; VC, the verification circuit that adds an extra pi phase to each address state that satisfies the "alternating bitstring" requirement. Other functions in oracle.py are mostly just for testing and debugging.
* The file diffuser.py defines the function diffuser_circuit, which provides the diffuser circuit in Grover's algorithm given the number of address qubits needed, as a Qiskit QuantumCircuit object. Other functions in diffuser.py, as before, are for testing purposes.
* The file main.py provides the function Grovers_circuit, which use these two circuits to construct the overall circuit used to solve Task 1, given an arbitrary input vector. At the end of the file, an arbitrary input vector of length 2^n with bitstrings of length m can be given to generate the circuit (where it is important to determine whether n is equal to 2 or not. See the from2to4.py and Important Notes sections for reason why). 
* The file from2to4.py exists to specifically help solve Task 1 for the case n = 2. Aside from testing functions, it defines two new quantum circuits, superpose ('SUP' gate) and superpose_2 ('SUP_2' gate), and the function improve, which directly generates the overall circuit needed to solve Task 1 if n = 2. See the Important Notes section on the general idea behind this and why this file is necessary. 

## Algorithm
* The solution combines the idea from Grover's algorithm and QRAM (based on the Bucket-Brigade model, can be seen in the "QRAM Primer.pdf" document for reference).
* QRAM: by classically reading the input vector, quantum X, CX, and MCX gates are classically added to entangle address qubits with their corresponding values, in order to mimic the function of a classical RAM, without destroying the state of the address qubits.
* Grover's algorithm: as the search space is 2^n and the number of solutions is 2 (two types of alternation), the relationship between the number of iterations needed, t, the angle between state |s> (equal superposition state) and state |w'> (state orthogonal to superposition of solution states), theta, is (2t+1)*theta = pi/2, where sin(theta) = sqrt(2/2^n). The solution is trivial for n=1. However, if n happens to be 2 (given an input vector of length 4), solutions would occupy exactly half the search space, making it impossible to converge to a superposition of solution states. In this case, the size of the search space needs to be doubled by adding four 0s to the input vector, making t=1. The third address qubit as a result of this addition needs to be ignored in the output.

## Important Notes
1. Although this program should work for length m bitstring and length 2^n input vector in general, the best the Qiskit simulation can do without from2to4.py (on my PC at least) is to solve the task for an input vector of length 4, consisting of elements 0~3, for the following reason:
    - For an input vector of length 2^n with each bitstring stored of length m, the total number of qubits needed is (using the Bucket-Brigade QRAM model) n + 2^n + m*2^n + m + 1 (the phase kickback qubit). Given an input vector [0, 1, 2, 3] (or a permutation of it), m=2. Since we need to manually double the size of search space for Grover's algorithm to work (as the number of solutions is exactly half of the size of search space), n=3 after appending four 0s. The total number of qubits happens to be 30.
    - For the Qiskit statevector simulator, each state would take up 16 bytes of RAM. There are 2^30 states in total whose amplitudes are to be tracked, requiring a total memory of 16 bytes * 2^30 = 17GB of RAM.
    - Although my PC only has 16GB of RAM installed, I managed to make this simulation possible by changing the precision from "double" to "single" (as can be seen in the code) and therefore halving the total memory needed. However, any input vector with slightly larger m or n would require more qubits, and therefore impossible to get an answer using the simulator.
    - The designated input vector [1, 5, 7, 10], in this case, has m=4 and n=3 (after doubling search space). This would require 48 qubits in total, hence solving the task for [1, 5, 7, 10] would not be possible without an entire computing centre or an actual quantum computer, which I do not have access to.
    - Another Qiskit simulator, matrix_product_state, would work for circuits with hundreds of qubits. However, it would always mess up the order of gates in the circuit after transpilation, and I eventually failed to use this simulator without a huge error in the result.
2. The subsection above is my previous idea about why the program can theoretically generate a solution for [1, 5, 7, 10], but cannot **simulate** the circuit without thousands of GB of RAM. However, after a few days of pondering, I have come up with a solution to get around this problem that uses exactly 30 qubits (therefore barely simulatable) for an input vector like [1, 5, 7, 10]. Here's how:
    - Usually one would need to manually double the size of the search space to make Grover's algorithm work for n = 2, which is the major contributing factor to the memory problem. But since we know for sure there are 2 solutions (which are distinguishable from each other) in a 4-dimensional search space, why can't we check these solutions one by one, requiring exactly one iteration for each search?
    - Without manually doubling the size of the search space, the QRAM for [1, 5, 7, 10] (or m=4, n=2) would require 26 qubits. To check these solutions one by one and combine them later, I added two more address qubits also initialized to |+>|+> and two phase kickback qubits (since we need to check twice), resulting in a total of 30 qubits.
    - Since the value register needs to be reused for the second check after the first check, the diffuser circuit is redesigned such that the value register would recover to its previous state just after QRAM querying (which is, |000..0>, since the QRAM circuit also reverses the changes made to the state). Details can be seen in the overall circuit diagram for n = 2.
    - Two solutions states are distinguished by using slightly different verification circuits in the oracle, namely VC_1 and VC_2.
    - After applying the oracle and diffusing both address registers, each in a two-qubit basis state corresponding to the index of each solution, they are then fed into the superpose_2 circuit ('SUP_2' gate) to create an equal superposition of these two solution states, which is the answer.
3. This has successfully made the simulation for [1, 5, 7, 10] possible. However, currently the result can be known only through directly measuring the final address qubits (and the results are expected, measuring 01 and 11 both exactly half of the times), as my PC still doesn't have enough memory to output the final statevector. I tried to lower the precision of the simulation in multiple ways, and the RAM of my PC is still a few GB short at the best. But with m=3 and an input vector like [1, 2, 5, 7], the final statevector can be correctly returned.
4. For higher m and n, I currently do not have a good idea to lower the number of qubits needed.