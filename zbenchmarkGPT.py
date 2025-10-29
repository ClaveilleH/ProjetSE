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

# -----------------------------
# FONCTION DE BENCHMARK D'UNE CONFIG
# -----------------------------
def benchmark_config(method, max_bits, n):
    """Benchmark d'une configuration method/max_bits/n"""
    rng_seed = seed_global  # graine fixe pour reproductibilité
    arr_orig = generate_array(n, max_bits, rng_seed)

    # Création du compresseur
    c = CompressorFactory.get_compressor(method, Config(max_bits=max_bits))

    # WARMUPS
    for _ in range(warmups):
        arr_tmp = arr_orig.copy()
        c.compress(arr_tmp)
        c.decompress(arr_tmp)

    # MESURES
    results = []
    for run_id in range(1, reps + 1):
        arr_tmp = arr_orig.copy()

        # mesure compress
        t0 = time.perf_counter()
        c.compress(arr_tmp)
        t1 = time.perf_counter()
        compress_time = t1 - t0

        # mesure get
        get_indices = random.sample(range(n), min(get_samples, n))
        get_times = []
        for i in get_indices:
            t0 = time.perf_counter()
            print(f"Getting value at index {i}")
            val = c.get(arr_tmp, i)
            t1 = time.perf_counter()
            get_times.append(t1 - t0)
        get_time_avg = sum(get_times) / len(get_times)
        get_time_median = sorted(get_times)[len(get_times)//2]

        # mesure decompress
        t0 = time.perf_counter()
        c.decompress(arr_tmp)
        t1 = time.perf_counter()
        decompress_time = t1 - t0

        # intégrité
        integrity_ok = arr_tmp == arr_orig

        # taille compressée
        compressed_len_ints = len(arr_tmp)
        compressed_size_bytes = compressed_len_ints * 4
        uncompressed_size_bytes = n * 4
        compression_ratio = compressed_size_bytes / uncompressed_size_bytes

        # timestamp
        timestamp = datetime.utcnow().isoformat() + "Z"

        results.append({
            "timestamp": timestamp,
            "platform": platform.platform(),
            "python_version": sys.version.split()[0],
            "method": method,
            "max_bits": max_bits,
            "n": n,
            "run_id": run_id,
            "seed": rng_seed,
            "compress_time_s": compress_time,
            "decompress_time_s": decompress_time,
            "get_time_avg_s": get_time_avg,
            "get_time_median_s": get_time_median,
            "compressed_len_ints": compressed_len_ints,
            "compressed_size_bytes": compressed_size_bytes,
            "uncompressed_size_bytes": uncompressed_size_bytes,
            "compression_ratio": compression_ratio,
            "integrity_ok": integrity_ok,
            "notes": ""
        })

    return results

# -----------------------------
# MAIN : parcours de la grille
# -----------------------------
all_results = []
for method in methods:
    for max_bits in max_bits_list:
        for n in ns:
            print(f"Benchmarking {method}, max_bits={max_bits}, n={n} ...")
            config_results = benchmark_config(method, max_bits, n)
            all_results.extend(config_results)

# -----------------------------
# ÉCRITURE CSV BRUT
# -----------------------------
with open(csv_brut, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
    writer.writeheader()
    for row in all_results:
        writer.writerow(row)

# -----------------------------
# ÉCRITURE CSV AGRÉGÉ
# -----------------------------
from collections import defaultdict
import statistics

agg_results = []
grouped = defaultdict(list)
for row in all_results:
    key = (row["method"], row["max_bits"], row["n"])
    grouped[key].append(row)

for key, rows in grouped.items():
    method, max_bits, n = key
    compress_times = [r["compress_time_s"] for r in rows]
    decompress_times = [r["decompress_time_s"] for r in rows]
    get_times = [r["get_time_avg_s"] for r in rows]
    ratios = [r["compression_ratio"] for r in rows]
    integrities = [r["integrity_ok"] for r in rows]

    agg_results.append({
        "method": method,
        "max_bits": max_bits,
        "n": n,
        "median_compress_s": statistics.median(compress_times),
        "median_decompress_s": statistics.median(decompress_times),
        "median_get_s": statistics.median(get_times),
        "iqr_compress_s": statistics.quantiles(compress_times, n=4)[2] - statistics.quantiles(compress_times, n=4)[0],
        "iqr_decompress_s": statistics.quantiles(decompress_times, n=4)[2] - statistics.quantiles(decompress_times, n=4)[0],
        "iqr_get_s": statistics.quantiles(get_times, n=4)[2] - statistics.quantiles(get_times, n=4)[0],
        "compression_ratio_median": statistics.median(ratios),
        "integrity_ok_pct": sum(integrities)/len(integrities)*100
    })

with open(csv_agg, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=agg_results[0].keys())
    writer.writeheader()
    for row in agg_results:
        writer.writerow(row)

# -----------------------------
# ÉCRITURE JSON RÉSUMÉ
# -----------------------------
summary = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "platform": platform.platform(),
    "python_version": sys.version.split()[0],
    "methods": methods,
    "max_bits_list": max_bits_list,
    "ns": ns,
    "reps": reps,
    "warmups": warmups,
    "get_samples": get_samples,
    "seed_global": seed_global,
    "aggregated_results": agg_results
}

with open(json_summary, "w") as f:
    json.dump(summary, f, indent=2)

print("Benchmark terminé !")
print(f"CSV brut : {csv_brut}")
print(f"CSV agrégé : {csv_agg}")
print(f"JSON résumé : {json_summary}")

# -----------------------------
# POUR PLUS GRAND n (décommenter si nécessaire)
# -----------------------------
# ns = [100, 1000, 10000, 100000]
# max_bits_list = list(range(4,21,2))
