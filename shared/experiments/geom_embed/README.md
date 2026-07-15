# Geometric Embeddings Experiments

**Parallel Development Approach**: Platform building and experimental validation proceed simultaneously with daily progress updates.

**Core Philosophy**: Innovation as "building foundations upward while connecting castle in the air downward" – we start with bold frameworks and rationalize them iteratively.

## Goal
Quantitative comparison of Euclidean vs Hyperbolic vs Spherical embeddings on standard semantic tasks.

## Datasets
- **WordNet** (hierarchical relations)
- **BATS** (analogy relations)
- **SimLex-999** (similarity)

## Evaluation Metrics
- Mean rank (MR)
- Mean average precision (MAP)
- Spearman's correlation (ρ)
- Training time

## Success Criteria (Exploratory Mindset)

**Philosophy**: Innovation often starts with a bold conceptual framework that is later grounded in rigor. We embrace exploratory research.

**Quantitative Goals**:
- ≥10% improvement over Euclidean baseline is considered **positive signal**
- We're looking for **proof of concept**, not production-ready performance
- "Unreasonable" aspects should be **rationalized**, not rejected

**Decision Points**:
- If results show <5% improvement: reconsider approach, but continue platform development
- If results show 5-10% improvement: promising, continue both platform and experiments
- If results show >10% improvement: strong signal, allocate more resources

## Directory Structure
```
shared/experiments/geom_embed/
├── configs/          # Experiment configurations
├── scripts/          # Training/evaluation scripts
├── results/          # Experimental results
└── visualization/    # Visualization scripts (optional)
```

## Baseline Models
1. Euclidean (standard baseline)
2. Poincaré ball (hyperbolic)
3. Unit sphere (spherical)

## Implementation
- Python 3.11+
- PyTorch 2.3+
- geoopt for Riemannian optimization
- Scripts designed to run locally or on Colab