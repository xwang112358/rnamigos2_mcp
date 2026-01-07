from molopt.graph_ga import GraphGA
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit import RDLogger
# Disable only warnings
RDLogger.DisableLog('rdApp.warning') 



# optimizer = GraphGA(smi_file=None, n_jobs=-1, max_oracle_calls=10000, freq_log=100, output_dir = 'results', log_results=True) 
# optimizer.optimize(oracle='qed', patience=5, seed=0)



# optimizer = GraphGA(smi_file=None, n_jobs=-1, max_oracle_calls=10000, freq_log=100, output_dir = 'results', log_results=True) 

def mol_wt(smi):
    m = Chem.MolFromSmiles(smi)
    if m is None:
        return 0
    else:
        return Descriptors.MolWt(m)

# optimizer.optimize(oracle=mol_wt, patience=5, seed=0)

print(mol_wt('C1CCCCC1'))