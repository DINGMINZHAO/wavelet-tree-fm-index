# Wavelet Trees & FM-Index

**Course:** MA6207L3 | The University of Tokyo  
**Project Type:** Course Final Project  
**Date:** July 2026

## Overview

This repository contains my final course project for MA6207L3 at the University of Tokyo.

The project implements and analyzes Wavelet Trees and FM-Index for efficient string queries and pattern counting.

## Contents

- `code/wavelet_tree.py` — Wavelet Tree implementation with Access, Rank, and Select operations.
- `code/fm_index.py` — FM-Index implementation for pattern counting.
- `code/experiments.py` — Correctness tests and performance benchmarks.
- `code/plot_results.py` — Experimental visualization.
- `report.pdf` — Final project report, including algorithmic analysis, complexity proofs, and experimental results.

## Running the Experiments

Requirements: Python 3 and Matplotlib.

```bash
python3 -m pip install matplotlib
cd code
python3 experiments.py
python3 plot_results.py
```

## Implementation Notes

The Wavelet Tree implementation uses explicit arrays for educational purposes rather than a succinct bit-vector representation.

The project focuses on algorithmic correctness, theoretical complexity, and empirical performance comparison.

## Report

[Read the Final Report](report.pdf)

## Acknowledgment

This is an academic coursework project. The report includes an AI assistance disclosure.
