---
name: Chemical Space Visualization
overview: Create a UMAP visualization comparing the chemical space of ROBIN dataset molecules and graph_ga optimized molecules using ECFP fingerprints, with color-coding for hits/non-hits and optimization scores.
todos: []
---

# Chemical Space Comparison with UMAP

## Implementation Plan

Add a new cell to [`rnamigos2_minimal/analyze_chemical_space.ipynb`](rnamigos2_minimal/analyze_chemical_space.ipynb) with the following components:

### 1. Load Optimized Molecules Function

Create `load_optimized_molecules(method, seed, topk=100)` function that:

- Reads CSV from `opt_results/{method}/results_{method}_rnamigos2_oracle_{seed}.csv`
- Sorts by `rnamigos2_score` descending
- Returns top-k molecules (default 100)

### 2. Load ROBIN Dataset

- Read [`robin_clean.csv`](robin_clean.csv) 
- Select only `Smile` and `TPP` columns
- Handle ~24k molecules

### 3. SMILES to ECFP Fingerprints

Convert all SMILES to ECFP fingerprints using RDKit:

- Parameters: radius=2, nBits=1024
- Use `AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=1024)`
- Convert to numpy arrays for UMAP processing

### 4. UMAP Dimensionality Reduction

- Combine all fingerprints (ROBIN + optimized molecules)
- Apply UMAP with default parameters (n_neighbors=15, min_dist=0.1)
- Generate 2D embeddings

### 5. Visualization

Create scatter plot with matplotlib:

- **ROBIN molecules**: Plot first
  - Black points (TPP=0, non-hits)
  - Red points (TPP=1, hits)
  - Use smaller marker size, lower alpha for background
- **Optimized molecules**: Plot on top
  - Color gradient based on `rnamigos2_score` using viridis/plasma colormap
  - Larger marker size for visibility
  - Add colorbar showing score range
- Add legend, labels, and title
- Set figure size appropriately (e.g., 12x10)

### 6. Code Structure

```python
# Imports: pandas, numpy, rdkit, umap-learn, matplotlib
# Function: load_optimized_molecules(method, seed, topk)
# Function: smiles_to_ecfp(smiles_list)
# Load data: graph_ga seed 0, ROBIN dataset
# Compute fingerprints for both datasets
# Apply UMAP on combined fingerprints
# Create visualization with proper coloring
# Display plot
```

### Dependencies

- rdkit (chemistry toolkit)
- umap-learn (dimensionality reduction)
- matplotlib (visualization)
- Already have: pandas, numpy

The code will be clear, modular, and well-commented for easy understanding and reusability.