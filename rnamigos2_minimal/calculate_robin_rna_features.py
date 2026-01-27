"""
Pre-calculate RNA-specific features for the ROBIN library (~24k molecules).

This script calculates 6 RNA-specific molecular features:
- n6aHRing: 6-membered aromatic heterocycles
- naHRing: Total aromatic heterocycles
- C1SP3: Fraction of sp3 carbons
- nHBAcc: Hydrogen bond acceptors
- SlogP_VSA11: Lipophilicity surface area descriptor
- JGI3: Topological charge index

Usage:
    cd rnamigos2_minimal
    python calculate_robin_rna_features.py

Output:
    display_outputs/robin_rna_features.csv

This pre-calculated file will be automatically loaded by nb_drug_likeliness_analysis.ipynb
"""

import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from mordred import Calculator, descriptors
import warnings
from tqdm import tqdm
from joblib import Parallel, delayed
import multiprocessing
from pathlib import Path
import matplotlib.pyplot as plt
import os
warnings.filterwarnings('ignore')

print("Loading ROBIN library...")
robin_df = pd.read_csv('../robin_clean.csv')[['Smile', 'TPP']]
print(f"Loaded {len(robin_df)} molecules")

# Get number of available CPU cores
n_jobs = multiprocessing.cpu_count()
print(f"Using {n_jobs} CPU cores for parallel processing")

def calc_rna_features(smiles, tpp):
    """Calculate RNA-specific features for a single molecule"""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return None
    
    try:
        # Create calculator per process to avoid sharing issues
        calc = Calculator(descriptors, ignore_3D=True)
        result = calc(mol)
        
        # Count 6-membered aromatic heterocycles
        n6aHRing = 0
        for ring in mol.GetRingInfo().AtomRings():
            if len(ring) == 6:
                is_aromatic = all(mol.GetAtomWithIdx(i).GetIsAromatic() for i in ring)
                has_hetero = any(mol.GetAtomWithIdx(i).GetSymbol() != 'C' for i in ring)
                if is_aromatic and has_hetero:
                    n6aHRing += 1
        
        return {
            'Smile': smiles,
            'TPP': tpp,
            'n6aHRing': n6aHRing,
            'naHRing': rdMolDescriptors.CalcNumAromaticHeterocycles(mol),
            'C1SP3': Descriptors.FractionCSP3(mol),
            'nHBAcc': Descriptors.NumHAcceptors(mol),
            'SlogP_VSA11': Descriptors.SlogP_VSA11(mol),
            'JGI3': float(result['JGI3']) if result['JGI3'] is not None else 0
        }
    except Exception:
        return None

# Calculate features for all ROBIN molecules in parallel
print("\nCalculating RNA features for ROBIN library...")
results = Parallel(n_jobs=n_jobs, backend='multiprocessing')(
    delayed(calc_rna_features)(row['Smile'], row['TPP']) 
    for _, row in tqdm(robin_df.iterrows(), total=len(robin_df), desc="Calculating RNA features")
)

# Filter out None results
features_list = [r for r in results if r is not None]

# Create DataFrame
df_features = pd.DataFrame(features_list)
print(f"\nSuccessfully calculated features for {len(df_features)}/{len(robin_df)} molecules")

# Save to CSV
output_path = 'display_outputs/robin_rna_features.csv'
df_features.to_csv(output_path, index=False)
print(f"Saved features to: {output_path}")

# Print summary statistics
print("\nSummary statistics:")
print(df_features[['n6aHRing', 'naHRing', 'C1SP3', 'nHBAcc', 'SlogP_VSA11', 'JGI3']].describe())

# =============================================================================
# Load optimization methods and create visualization
# =============================================================================
print("\n" + "="*80)
print("Loading optimized molecules from optimization methods...")
print("="*80)

methods = ['graph_ga', 'gp_bo', 'reinvent', 'smiles_ga']
seeds = [0, 1, 2, 3, 5]
opt_results_base = Path('opt_results/run_combined_sim')
oracle_name = "oracle"
topk = 500

opt_smiles_dict = {}
for method in methods:
    opt_smiles_dict[method] = []
    for seed in seeds:
        csv_path = opt_results_base / method / f'results_{method}_{oracle_name}_{seed}.csv'
        if csv_path.exists():
            df_method = pd.read_csv(csv_path).sort_values('rnamigos2_score', ascending=False).head(topk)
            opt_smiles_dict[method].extend(df_method['smiles'].tolist())
    print(f"{method}: {len(opt_smiles_dict[method])} molecules")

# Calculate features for optimization methods
print("\nCalculating RNA features for optimization methods...")
opt_features_dict = {}
for method in methods:
    results = Parallel(n_jobs=n_jobs, backend='multiprocessing')(
        delayed(calc_rna_features)(smiles, 0) 
        for smiles in tqdm(opt_smiles_dict[method], desc=f"Calculating {method}")
    )
    opt_features_dict[method] = [r for r in results if r is not None]

# Prepare dataframes for visualization
df_robin_hits_rna = df_features[df_features['TPP'] == 1][['n6aHRing', 'naHRing', 'C1SP3', 'nHBAcc', 'SlogP_VSA11', 'JGI3']].copy()
df_robin_hits_rna['dataset'] = 'ROBIN hits'

df_rna_list = [df_robin_hits_rna]
for method in methods:
    df_method = pd.DataFrame(opt_features_dict[method])
    df_method_rna = df_method[['n6aHRing', 'naHRing', 'C1SP3', 'nHBAcc', 'SlogP_VSA11', 'JGI3']].copy()
    df_method_rna['dataset'] = method
    df_rna_list.append(df_method_rna)

df_all_rna = pd.concat(df_rna_list, ignore_index=True)
print(f"Total molecules for visualization: {len(df_all_rna)}")

# Create visualization
print("\nGenerating RNA features boxplot...")
rna_features = ['n6aHRing', 'naHRing', 'C1SP3', 'nHBAcc', 'SlogP_VSA11', 'JGI3']
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

datasets = ['ROBIN hits', 'graph_ga', 'gp_bo', 'reinvent', 'smiles_ga']
colors = ['lightcoral', 'lightgreen', 'lightyellow', 'lightpink', 'lavender']
labels = ['ROBIN\nhits', 'graph_ga', 'gp_bo', 'reinvent', 'smiles_ga']

for idx, feature in enumerate(rna_features):
    ax = axes[idx]
    data = [df_all_rna[df_all_rna['dataset'] == ds][feature] for ds in datasets]
    
    bp = ax.boxplot(data, labels=labels, patch_artist=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax.set_ylabel(feature, fontsize=12)
    ax.set_title(feature, fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.tick_params(axis='x', rotation=45)

plt.suptitle('RNA-Specific Molecular Features Comparison', fontsize=16, fontweight='bold', y=1.00)
plt.tight_layout()

# Create figures directory if it doesn't exist
os.makedirs('display_outputs/figures', exist_ok=True)

# Save figure
fig_path = 'display_outputs/figures/rna_features_comparison_combined_sim.png'
plt.savefig(fig_path, dpi=600, bbox_inches='tight')
print(f"Figure saved to: {fig_path}")

plt.close()
print("\n✅ Complete! RNA features calculated and visualized.")
