# Combined Binding-Similarity Objective

## Overview

The combined objective approach balances RNAmigos2 binding affinity predictions with structural similarity to reference molecules. This prevents optimized molecules from drifting too far from known drugs or validated compounds, addressing the issue of unrealistic molecules with high predicted binding scores.

## Mathematical Formulation

The combined score is computed as a weighted sum:

```
combined_score = binding_weight × binding_score + similarity_weight × similarity_score
```

Where:
- **binding_score**: RNAmigos2 predicted binding affinity
- **similarity_score**: Maximum Tanimoto similarity to any reference molecule (using Morgan fingerprints, radius=2, 2048 bits)
- **binding_weight**: Weight for binding objective (default: 0.7)
- **similarity_weight**: Weight for similarity objective (default: 0.3)

## Usage

All optimization methods now support the combined objective via command-line flags:

### Basic Usage (Using Starting Molecules as References)

```bash
python run_graphga.py \
  --use_combined_objective \
  --max_oracle_calls 10000 \
  --similarity_weight 0.3 \
  --binding_weight 0.7
```

This will:
1. Load starting molecules from `inputs/ligands/robin_smiles.txt` as references
2. Optimize molecules to have high binding affinity while maintaining similarity to these references
3. Save results to `opt_results/graph_ga_combined/`

### Using Custom Reference Molecules

```bash
python run_graphga.py \
  --use_combined_objective \
  --reference_file inputs/ligands/approved_drugs.txt \
  --max_oracle_calls 10000 \
  --similarity_weight 0.3 \
  --binding_weight 0.7
```

This uses molecules from a separate file as references (e.g., FDA-approved drugs).

### Available for All Methods

The combined objective works with all optimization algorithms:

```bash
# Graph GA
python run_graphga.py --use_combined_objective --population_size 120

# GP-BO
python run_gp_bo.py --use_combined_objective --initial_population_size 340

# SMILES GA
python run_smiles_ga.py --use_combined_objective --population_size 50

# REINVENT
python run_reinvent.py --use_combined_objective
```

## Weight Selection Guidelines

### Conservative (Prioritize Similarity)
```bash
--binding_weight 0.5 --similarity_weight 0.5
```
Use when you want to stay very close to known molecules.

### Balanced (Default)
```bash
--binding_weight 0.7 --similarity_weight 0.3
```
Good starting point - prioritizes binding but constrains drift.

### Aggressive (Prioritize Binding)
```bash
--binding_weight 0.9 --similarity_weight 0.1
```
Use when you want more exploration but some similarity constraint.

## Implementation Details

### Similarity Computation

- **Fingerprint**: Morgan fingerprints with radius=2 and 2048 bits (standard in cheminformatics)
- **Metric**: Tanimoto similarity (ranges from 0 to 1)
- **Aggregation**: Maximum similarity to any reference molecule (allows exploration while maintaining one anchor)

### Oracle Function

The combined oracle is defined in `oracle.py`:

```python
def combined_rnamigos2_similarity_oracle(
    smi,
    reference_smiles=None,
    similarity_weight=0.3,
    binding_weight=0.7,
    ...
)
```

Key features:
- Gracefully handles invalid SMILES (returns 0.0 for similarity)
- Falls back to pure binding score if no references provided
- Caches fingerprints for efficiency (handled by RDKit)

### Output Directory

When `--use_combined_objective` is used, the output directory automatically gets a `_combined` suffix to prevent overwriting pure binding optimization results.

## Example Workflow

### 1. Quick Test (1000 oracle calls)

```bash
python run_graphga.py \
  --use_combined_objective \
  --max_oracle_calls 1000 \
  --output_dir opt_results/test_combined
```

### 2. Compare with Pure Binding Optimization

```bash
# Pure binding
python run_graphga.py \
  --max_oracle_calls 10000 \
  --output_dir opt_results/graph_ga_pure

# Combined objective
python run_graphga.py \
  --use_combined_objective \
  --max_oracle_calls 10000 \
  --output_dir opt_results/graph_ga_combined
```

### 3. Analyze Results

After optimization, compare:
- **Binding scores**: Check if combined objective maintains competitive binding
- **Similarity scores**: Verify molecules are more similar to references
- **Chemical validity**: Assess drug-likeness properties (SA scores, PAINS filters)

Results are saved in:
- `results_*.yaml`: All evaluated molecules with scores
- `metrics_*.yaml`: Summary statistics (top-1, top-10, top-100, diversity, SA scores)

## Troubleshooting

### Issue: Combined scores are dominated by similarity

**Solution**: Increase `binding_weight`:
```bash
--binding_weight 0.9 --similarity_weight 0.1
```

### Issue: Molecules still drift too far from references

**Solutions**:
1. Increase `similarity_weight`:
   ```bash
   --binding_weight 0.5 --similarity_weight 0.5
   ```
2. Use a more diverse set of references
3. Consider using a harder similarity threshold (would require modifying the oracle)

### Issue: Want to track both metrics separately

Currently, only the combined score is logged. To track separately, you would need to modify the `base.py` Oracle class to log multiple objectives. This is a potential future enhancement.

## Advanced: Custom Similarity Functions

To implement alternative similarity penalties (e.g., multiplicative, constraint-based), modify the oracle in `oracle.py`. See the main documentation for examples of these approaches.

## Performance Considerations

- **Computational cost**: Computing fingerprints adds ~1-5ms per molecule (negligible compared to RNAmigos2 inference)
- **Memory**: Reference fingerprints are recomputed for each call (optimization opportunity: pre-compute and cache)
- **Parallelization**: Works seamlessly with parallel optimization methods (GP-BO, GAs)

## Citation

If you use the combined objective in your research, please cite both:
1. The original optimization method (GraphGA, GP-BO, etc.)
2. RNAmigos2 for the binding prediction
3. Consider mentioning the similarity-constrained optimization approach
