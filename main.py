from oracle import oracle_circuit
from diffuser import diffuser_circuit
from qiskit import QuantumCircuit, assemble, transpile, QuantumRegister, ClassicalRegister
from qiskit.providers.aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np


def Grovers_circuit(input_vector):
    oracle, m, n = oracle_circuit(input_vector)
    diffuser = diffuser_circuit(n)
    return


def Grovers_test(input_vector):
    Grovers_circ = Grovers_circuit(input_vector)
    return


if __name__ == '__main__':
    input_vector = [2, 3, 1, 0]
    Grovers_test(input_vector)