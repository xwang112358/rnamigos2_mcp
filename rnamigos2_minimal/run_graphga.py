from molopt.graph_ga import GraphGA
from rdkit import RDLogger
from oracle import rnamigos2_oracle as tpp_rnamigos2_oracle

# Disable only warnings
RDLogger.DisableLog('rdApp.warning')


optimizer = GraphGA(
    smi_file='inputs/ligands/robin_smiles.txt',  
    n_jobs=-1,
    max_oracle_calls=1000,
    freq_log=100,
    output_dir='opt_results/graph_ga'
) 

# patience: Number of iterations without improvement before stopping early
optimizer.optimize(oracle=tpp_rnamigos2_oracle, patience=50, seed=0)


