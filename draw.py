#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# -----------------------------
# PARAMÈTRES
# -----------------------------
csv_file = "out/data/bench_results_raw.csv"
out_r = "out/graphs/"

# Lire le CSV
df = pd.read_csv(csv_file)

# Agréger les données par moyenne pour éviter les doublons
df = df.groupby(['method', 'max_bits', 'n']).agg({
    'compress_time_avg': 'mean',
    'decompress_time_avg': 'mean',
    'get_time_avg': 'mean'
}).reset_index()

# Listes uniques
methods = df['method'].unique()
max_bits_list = sorted(df['max_bits'].unique())
ns = sorted(df['n'].unique())

# -----------------------------
# 1️⃣ Courbes compress/decompress
# -----------------------------
for metric in ['compress_time_avg', 'decompress_time_avg']:
    plt.figure(figsize=(10,6))
    for method in methods:
        df_method = df[df['method'] == method]
        for max_bits in max_bits_list:
            df_plot = df_method[df_method['max_bits'] == max_bits]
            plt.plot(df_plot['n'], df_plot[metric],
                     marker='o', label=f"{method} max_bits={max_bits}")
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("Taille du tableau n (log scale)")
    plt.ylabel(f"{metric} (s, log scale)")
    plt.title(f"{metric} vs n pour différentes méthodes et max_bits")
    plt.legend()
    plt.grid(True, which="both", ls="--", lw=0.5)
    plt.tight_layout()
    plt.savefig(f"{out_r}{metric}_curves.png", dpi=300)

# -----------------------------
# 2️⃣ Heatmaps compress/decompress
# -----------------------------
for metric in ['compress_time_avg', 'decompress_time_avg']:
    for method in methods:
        df_method = df[df['method'] == method]
        pivot = df_method.pivot(index="max_bits", columns="n", values=metric)
        plt.figure(figsize=(8,6))
        sns.heatmap(pivot, annot=True, fmt=".4f", cmap="YlGnBu")
        plt.title(f"Heatmap {metric} pour {method}")
        plt.xlabel("Taille du tableau n")
        plt.ylabel("max_bits")
        plt.tight_layout()
        plt.savefig(f"{out_r}{metric}_heatmap_{method}.png", dpi=300)

# -----------------------------
# 3️⃣ Surface 3D compress/decompress
# -----------------------------
for metric in ['compress_time_avg', 'decompress_time_avg']:
    for method in methods:
        df_method = df[df['method'] == method]
        X, Y = np.meshgrid(ns, max_bits_list)
        Z = np.zeros_like(X, dtype=float)
        for i, mb in enumerate(max_bits_list):
            for j, n_val in enumerate(ns):
                Z[i,j] = df_method[(df_method['max_bits']==mb) & (df_method['n']==n_val)][metric].values[0]

        fig = plt.figure(figsize=(10,6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, Z, cmap='viridis')
        ax.set_xlabel("Taille du tableau n")
        ax.set_ylabel("max_bits")
        ax.set_zlabel(metric)
        ax.set_title(f"Surface 3D {metric} pour {method}")
        plt.tight_layout()
        plt.savefig(f"{out_r}{metric}_3D_{method}.png", dpi=300)

print("Graphiques générés !")
