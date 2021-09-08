# 2021 QOSF Mentoring Program Task 1
## Repository Structure
* This repository includes the solution to Task 1 of the 2021 QOSF mentoring program.

## Algorithm

## Important Notes
1. The best the Qiskit simulation can do (on my PC at least) is to solve the task for an input vector of length 4, consisting of elements 0~3, for the following reason:
    - For an input vector of length 2^n with each bitstring stored of length m, the total number of qubits needed is (using the Bucket-Brigade QRAM model) n + 2^n + m*2^n + m + 1 (the phase kickback qubit). Given an input vector [0, 1, 2, 3] (or a permutation of it), m=2. Since we need to double the size of search space for Grover's algorithm to work (as the number of solutions is exactly half of the size of search space), n=3 after appending four 0s. The total number of qubits happens to be 30.
    - For the Qiskit statevector simulator, each state would take up 16 bytes of RAM. There are 2^30 states in total whose amplitudes are to be tracked, requiring a total memory of 16 * 2^30 = 17GB of RAM.
    - Although my PC only has 16GB of RAM installed, I managed to make this simulation possible by changing the precision from "double" to "single" (as can be seen in the code) and therefore halving the total memory needed. However, any input vector with slightly larger m or n would require more qubits, and therefore impossible to get an answer using simulator.
    - The designated input vector [1, 5, 7, 10], in this case, has m=4 and n=3 (after doubling search space). This would require 48 qubits in total, hence solving the task for [1, 5, 7, 10] would not be possible without an entire computing centre or an actual quantum computer, which I do not have access to.
    - Another Qiskit simulator, matrix_product_state, would work for circuits with hundreds of qubits. However, it would always mess up the order of gates in the circuit after transpilation, and I eventually failed to use this simulator without a huge error in the result.
2. Also, the final statevector cannot be displayed up to a satisfactory precision, due to the memory problem as well.