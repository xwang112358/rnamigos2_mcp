from molopt.smiles_ga import SmilesGA
from rdkit import RDLogger
from oracle import rnamigos2_oracle as tpp_rnamigos2_oracle

# Disable only warnings
RDLogger.DisableLog('rdApp.warning')


# SMILES GA Hyperparameters (loaded from hparams_default.yaml):
# - gene_size (default: 200): Length of gene encoding for SMILES grammar representation.
#   Controls the maximum complexity of molecules that can be represented.
# - population_size (default: 50): Number of molecules maintained in the population.
#   Larger populations explore more diverse solutions but require more evaluations.
# - n_mutations (default: 500): Number of mutations to perform in each generation.
#   Higher values allow more exploration but increase computational cost per iteration.

optimizer = SmilesGA(
    smi_file='inputs/ligands/robin_smiles.txt',  
    n_jobs=-1,
    max_oracle_calls=1000,
    freq_log=100,
    output_dir='opt_results/smiles_ga'
) 

# patience: Number of iterations without improvement before stopping early
optimizer.optimize(oracle=tpp_rnamigos2_oracle, patience=50, seed=0)


