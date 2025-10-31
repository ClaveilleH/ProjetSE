# ProjetSE — CLAVEILLE Hugo

## 🧠 Objectif

Ce projet implémente une méthode de compression d’un tableau d’entiers avec **accès direct** (`get(i)` en O(1)) tout en gérant les **valeurs en dépassement** (overflow).
Chaque entier est encodé sur un nombre fixe de bits (`maxbits`), sauf ceux qui dépassent cette limite et sont stockés dans une zone **overflow** séparée.

---

## ⚙️ Principe de fonctionnement

1. Tout le fonctionnement est detaillé dans le rapport.

---

## 📁 Arborescence du projet

Voici la structure générale des fichiers et dossiers :

```
ProjetSE/
│
├── compressor/         # Code source python
│   ├── base.py         # Classe de base pour les compresseurs
│   ├── factory.py      # Classe factory pour créer des compresseurs
│   ├── method1.py      # Implémentation de la méthode 1
│   ├── method2.py      # Implémentation de la méthode 2
│   ├── utils.py        # Fonctions utilitaires pour la compression
│   └── quick_test.py   # Script de test rapide
│
├── out/                # Dossiers pour résultats de benchmark / CSV / graphiques
│   ├── data/           # Fichiers CSV générés par les benchmarks
│   └── *.png           # Graphiques générés
│
├── benchmarks.py       # Script pour exécuter les benchmarks
│
├── README.md           # Ce fichier
│
├── draw.py             # Script pour générer des graphiques à partir des CSV
│
└── rapport.pdf         # Rapport final en PDF

```


## 🚀 Exécution

Un exemple d'execution est fourni avec le fichier `quick_test.py`

```
python3 -m compressor.quick_test
```

Et afin de générer les CSV, vous pouvez utiliser le fichier `benchmark.py`

```
python3 benchmark.py
```
