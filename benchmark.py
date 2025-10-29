#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Runner pour benchmarker les compresseurs
Mesure compress, decompress et get
Produit CSV brut, CSV agrégé et JSON résumé
"""

import time
import csv
import json
import platform
import sys
from datetime import datetime
import random
from compressor.factory import CompressorFactory
from compressor.base import Config

# -----------------------------
# PARAMÈTRES DE LA GRILLE
# -----------------------------

methods = ["method1", "method2"]  # les deux méthodes à tester
max_bits_list = list(range(4, 21, 2))  # de 4 à 20 par pas de 2
ns = [100, 1000]  # taille des tableaux (pilotage), pour plus : 10000, 100000
reps = 7          # répétitions mesurées
warmups = 3       # warmups non mesurés
get_samples = 1000  # nombre d'appels get
seed_global = 42  # graine pour reproductibilité

# Fichiers de sortie
csv_brut = "bench_results_raw.csv"
csv_agg = "bench_results_agg.csv"
json_summary = "bench_summary.json"

# -----------------------------
# FONCTION UTILITAIRE : générer un tableau aléatoire
# -----------------------------
def generate_array(n, max_bits, seed):
    """Génère un tableau d'entiers uniformes dans [0, 2^max_bits-1]"""
    rng = random.Random(seed)
    return [rng.randint(0, 2**max_bits - 1) for _ in range(n)]


def bench(method, max_bits, n, arr_orig):
    """Benchmark d'une configuration method/max_bits/n"""

    # Création du compresseur
    c = CompressorFactory.get_compressor(method, Config(max_bits=max_bits))

    # WARMUPS
    for _ in range(warmups):
        arr_tmp = arr_orig.copy()
        c.compress(arr_tmp)
        c.decompress(arr_tmp)

    # MESURES
    compress_times = []
    decompress_times = []
    get_times = []

    for _ in range(reps):
        arr = arr_orig.copy()

        # Mesure compress
        start = time.perf_counter()
        c.compress(arr)
        end = time.perf_counter()
        compress_times.append(end - start)



        # Mesure get
        get_indices = [random.randint(0, n - 1) for _ in range(get_samples)]
        start = time.perf_counter()
        for idx in get_indices:
            _ = c.get(arr, idx)
        end = time.perf_counter()
        get_times.append(end - start)

        # Mesure decompress
        start = time.perf_counter()
        c.decompress(arr)
        end = time.perf_counter()
        decompress_times.append(end - start)

        # Vérification
        if arr != arr_orig:
            print("ERROR: decompressed data does not match original!")
            sys.exit(1)


    # Résultats agrégés
    result = {
        "method": method,
        "max_bits": max_bits,
        "n": n,
        "compress_time_avg": sum(compress_times) / reps,
        "decompress_time_avg": sum(decompress_times) / reps,
        "get_time_avg": sum(get_times) / reps,
    }

    print(f"Result: {result}")
    return result





def main():
    for n in ns:
        for method in methods:
            for max_bits in max_bits_list:
                print(f"Benchmarking method={method}, max_bits={max_bits}, n={n}")
                arr_orig = generate_array(n, max_bits, seed_global)
                print("len arr_orig =", len(arr_orig))
                bench(method, max_bits, n, arr_orig)


if __name__ == "__main__":
    # Code de benchmark principal ici
    main()