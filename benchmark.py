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

# Dossier de données
out_dir = "out"
data_dir = f"{out_dir}/data"


# -----------------------------
# PARAMÈTRES DE LA GRILLE
# -----------------------------

methods = ["method1", "method2"]  # les deux méthodes à tester
distributions = ['uniform_small', 'skewed', 'outlier']  # distributions à tester
max_bits_list = list(range(4, 21, 2))  # de 4 à 20 par pas de 2
ns = [100, 1000, 10000]  # taille des tableaux (pilotage), pour plus : 10000, 100000
reps = 7          # répétitions mesurées
warmups = 3       # warmups non mesurés
get_samples = 1000  # nombre d'appels get
seed_global = 42  # graine pour reproductibilité


# Fichiers de sortie
csv_brut = f"{data_dir}/bench_results_raw.csv"
csv_agg = f"{data_dir}/bench_results_agg.csv"
json_summary = f"{data_dir}/bench_summary.json"

# -----------------------------
# FONCTION UTILITAIRE : générer un tableau aléatoire
# -----------------------------

def generate_array(n, max_bits, seed, distribution='uniform_small'):
    if distribution == 'uniform_small':
        rng = random.Random(seed)
        return [rng.randint(0, 2**max_bits - 1) for _ in range(n)]
    elif distribution == 'skewed':
        return generate_skewed_array(n, max_bits, seed)
    elif distribution == 'outlier':
        return generate_outlier_array(n, max_bits, seed)
    else:
        raise ValueError(f"Distribution inconnue: {distribution}")


# def generate_array(n, max_bits, seed):
#     """Génère un tableau d'entiers uniformes dans [0, 2^max_bits-1]"""
#     rng = random.Random(seed)
#     return [rng.randint(0, 2**max_bits - 1) for _ in range(n)]

def generate_skewed_array(n, max_bits, seed):
    rng = random.Random(seed)
    arr = []
    for _ in range(n):
        if rng.random() < 0.9:
            arr.append(rng.randint(0, 2**(max_bits//2) - 1))
        else:
            arr.append(rng.randint(0, 2**max_bits - 1))
    return arr

def generate_outlier_array(n, max_bits, seed):
    rng = random.Random(seed)
    arr = [rng.randint(0, 2**(max_bits//2) - 1) for _ in range(n)]
    # ajouter 1 ou 2 outliers
    num_outliers = max(1, n // 50)  # ~2% outliers
    for _ in range(num_outliers):
        arr[rng.randint(0, n-1)] = 2**max_bits - 1
    return arr


def bench(distribution, method, max_bits, n, arr_orig):
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
        "distribution": distribution,
        "method": method,
        "max_bits": max_bits,
        "n": n,
        "compress_time_avg": sum(compress_times) / reps,
        "decompress_time_avg": sum(decompress_times) / reps,
        "get_time_avg": sum(get_times) / reps,
    }

    # print(f"Result: {result}")
    return result



# def test_bench(

def main():
    import os
    # Créer le dossier data s'il n'existe pas
    os.makedirs(data_dir, exist_ok=True)
    
    with open(csv_brut, mode='w', newline='') as csvfile_raw :

        fieldnames = ['distribution', 'method', 'max_bits', 'n', 'compress_time_avg', 'decompress_time_avg', 'get_time_avg']
        writer_raw = csv.DictWriter(csvfile_raw, fieldnames=fieldnames)
        writer_raw.writeheader()


        total_runs = len(methods) * len(max_bits_list) * len(ns) * len(distributions)
        current_run = 1

        for distribution in distributions:
            for n in ns:
                for max_bits in max_bits_list:
                    arr_orig = generate_array(n, max_bits, seed_global, distribution=distribution)
                    for method in methods: # après avoir généré l'array pour réutiliser la même donnée
                        print(f"{current_run}/{total_runs} Benchmarking method={method}, max_bits={max_bits}, n={n}, distribution={distribution}")
                        result = bench(distribution, method, max_bits, n, arr_orig)
                        writer_raw.writerow(result)
                        current_run += 1

def make_agg_csv():

    fieldnames = ['distribution', 'method', 'max_bits', 'n', 'compress_time_avg', 'decompress_time_avg', 'get_time_avg']
    with open(csv_brut, 'r') as f_raw, open(csv_agg, 'w', newline='') as f_agg:
        reader = csv.DictReader(f_raw)
        agg_results = {}
        for row in reader:
            key = (row['distribution'], row['method'], int(row['max_bits']), int(row['n']))
            if key not in agg_results:
                agg_results[key] = {
                    'compress_time_avg': [],
                    'decompress_time_avg': [],
                    'get_time_avg': []
                }
            agg_results[key]['compress_time_avg'].append(float(row['compress_time_avg']))
            agg_results[key]['decompress_time_avg'].append(float(row['decompress_time_avg']))
            agg_results[key]['get_time_avg'].append(float(row['get_time_avg']))

        writer_agg = csv.DictWriter(f_agg, fieldnames=fieldnames)
        writer_agg.writeheader()
        for key, times in agg_results.items():
            distribution, method, max_bits, n = key
            writer_agg.writerow({
                'distribution': distribution,
                'method': method,
                'max_bits': max_bits,
                'n': n,
                'compress_time_avg': sum(times['compress_time_avg']) / len(times['compress_time_avg']) * 1000, #en miliseconds
                'decompress_time_avg': sum(times['decompress_time_avg']) / len(times['decompress_time_avg']) * 1000,
                'get_time_avg': sum(times['get_time_avg']) / len(times['get_time_avg']) * 1000,
            })



def to_json_summary():
    """Lit le CSV brut et produit un résumé JSON agrégé"""
    import pandas as pd

    df = pd.read_csv(csv_brut)

    summary = {}
    for method in methods:
        df_method = df[df['method'] == method]
        summary[method] = {
            "compress_time_avg_overall": df_method['compress_time_avg'].mean(),
            "decompress_time_avg_overall": df_method['decompress_time_avg'].mean(),
            "get_time_avg_overall": df_method['get_time_avg'].mean(),
        }

    with open(json_summary, 'w') as f:
        json.dump(summary, f, indent=4)


def gen_csv_rapport():
    """
    Génère des CSV agrégés séparés pour le rapport
    -----------------------------
    Créé un fichier séparé pour chaque méthode :
    - moy_method1.csv 
    - moy_method2.csv
    Et aussi moy_all.csv (trié par méthode puis par n)
    """
    import pandas as pd
    import os
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs(data_dir, exist_ok=True)

    df = pd.read_csv(csv_brut)

    fieldnames = ['n', 'method', 'compress_decompress_time_avg']
    
    # Fichier global (trié correctement)
    with open(f"{data_dir}/moy_all.csv", 'w', newline='') as f_all:
        writer_all = csv.DictWriter(f_all, fieldnames=fieldnames)
        writer_all.writeheader()
        
        for method in methods:
            df_method = df[df['method'] == method]
            
            # Fichier séparé pour cette méthode
            with open(f"{data_dir}/moy_{method}.csv", 'w', newline='') as f_method:
                writer_method = csv.DictWriter(f_method, fieldnames=['n', 'compress_decompress_time_avg'])
                writer_method.writeheader()
                
                for n in sorted(ns):  # Tri important !
                    df_n = df_method[df_method['n'] == n]
                    compress_avg = df_n['compress_time_avg'].mean() * 1000  # en ms
                    decompress_avg = df_n['decompress_time_avg'].mean() * 1000  # en ms
                    compress_decompress_avg = (compress_avg + decompress_avg) 
                    
                    # Écrire dans le fichier global
                    writer_all.writerow({
                        'n': n,
                        'method': method,
                        'compress_decompress_time_avg': compress_decompress_avg
                    })
                    
                    # Écrire dans le fichier spécifique à la méthode
                    writer_method.writerow({
                        'n': n,
                        'compress_decompress_time_avg': compress_decompress_avg
                    })
            
            with open(f"{data_dir}/moy_get_{method}.csv", 'w', newline='') as f_method_get:
                writer_method_get = csv.DictWriter(f_method_get, fieldnames=['n', 'get_time_avg'])
                writer_method_get.writeheader()
                
                for n in sorted(ns):  # Tri important !
                    df_n = df_method[df_method['n'] == n]
                    get_avg = df_n['get_time_avg'].mean() * 1000  # en ms
                    
                    # Écrire dans le fichier spécifique à la méthode
                    writer_method_get.writerow({
                        'n': n,
                        'get_time_avg': get_avg
                    })


            with open(f"{data_dir}/heatmap_{method}.csv", 'w', newline='') as f_heatmap:
                writer_heatmap = csv.DictWriter(f_heatmap, fieldnames=['max_bits', 'n', 'time_avg'])
                writer_heatmap.writeheader()
                
                for max_bits in sorted(max_bits_list):
                    for n in sorted(ns):
                        df_subset = df_method[(df_method['max_bits'] == max_bits) & (df_method['n'] == n)]
                        compress_avg = df_subset['compress_time_avg'].mean() * 1000  # en ms
                        decompress_avg = df_subset['decompress_time_avg'].mean() * 1000
                        
                        writer_heatmap.writerow({
                            'n': n,
                            'max_bits': max_bits,
                            'time_avg': compress_avg + decompress_avg
                        })


if __name__ == "__main__":
# Code de benchmark principal ici
    # main()
    make_agg_csv()
    gen_csv_rapport()
