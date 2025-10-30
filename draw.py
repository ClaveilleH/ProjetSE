#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt

# Charger le CSV brut
csv_file = "bench_results_raw.csv"
df = pd.read_csv(csv_file)

# Grouper les données par méthode, max_bits et n, puis calculer la moyenne
agg = df.groupby(['method', 'max_bits', 'n'])[['compress_time_avg', 'decompress_time_avg']].mean().reset_index()

# Plot compress_time_avg
plt.figure(figsize=(10, 6))
for method, color in zip(['method1', 'method2'], ['blue', 'orange']):
    subset = agg[agg['method'] == method]
    for max_bits in sorted(subset['max_bits'].unique()):
        subsub = subset[subset['max_bits'] == max_bits]
        plt.plot(subsub['n'], subsub['compress_time_avg'], marker='o',
                 label=f"{method}, max_bits={max_bits}", color=color, linestyle='-' if method=='method1' else '--')

plt.xlabel("Taille du tableau (n)")
plt.ylabel("Temps moyen compress (s)")
plt.title("Temps moyen de compression selon la taille et max_bits")
plt.legend()
plt.grid(True)
plt.xscale('log')  # optionnel : log si n varie beaucoup
plt.savefig("compress_times.png", dpi=300)
plt.show()

# Plot decompress_time_avg
plt.figure(figsize=(10, 6))
for method, color in zip(['method1', 'method2'], ['blue', 'orange']):
    subset = agg[agg['method'] == method]
    for max_bits in sorted(subset['max_bits'].unique()):
        subsub = subset[subset['max_bits'] == max_bits]
        plt.plot(subsub['n'], subsub['decompress_time_avg'], marker='o',
                 label=f"{method}, max_bits={max_bits}", color=color, linestyle='-' if method=='method1' else '--')

plt.xlabel("Taille du tableau (n)")
plt.ylabel("Temps moyen decompress (s)")
plt.title("Temps moyen de décompression selon la taille et max_bits")
plt.legend()
plt.grid(True)
plt.xscale('log')
plt.savefig("decompress_times.png", dpi=300)
plt.show()
