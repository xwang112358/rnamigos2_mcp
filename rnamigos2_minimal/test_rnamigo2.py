from rnamigos.inference import do_inference
from rnamigos.inference import do_inference_single
import numpy as np
import warnings
warnings.filterwarnings('ignore')




tpp_residue_list = np.load('inputs/residue_list/tpp.npy')
print(tpp_residue_list)

results = do_inference(
    cif_path="inputs/rna_targets/2gdi.cif",
    residue_list=tpp_residue_list,
    ligands_path="inputs/ligands/robin_smiles.txt",
    out_path="outputs/rnamigos2_robin_tpp_results.csv",
    do_mixing=True,
    dump_all=True
)

# results = do_inference(
#     cif_path="inputs/rna_targets/2gdi.cif",
#     residue_list=tpp_residue_list,
#     ligands_path="data/sample_files/test_smiles.txt",
#     out_path="outputs/tpp_test_results.csv",
#     do_mixing=True
# )

# print(results)

# smiles_list = [
#     "CCC[S@](=O)c1ccc2[nH]/c(=N\\C(=O)OC)[nH]c2c1",
#     "O=C(O)[C@@H](O)c1ccccc1",
#     "CC(=O)Oc1ccccc1C(=O)O",
#     "CN1[C@H]2CC[C@@H]1CC(OC(=O)[C@H](CO)c1ccccc1)C2",
#     "NC[C@H](CC(=O)O)c1ccc(Cl)cc1",
#     "CC(=O)Nc1ccc(C(=O)O)cc1",
#     "CCN(CC)C(=O)c1ccc(O)c(OC)c1",
#     "COc1ccc(/C(C)=N/OC(N)=O)cc1OC1CCCC1"
# ]
# scores = []
# for smiles in smiles_list:
#     score = do_inference_single(
#         cif_path="inputs/rna_targets/2gdi.cif",
#         residue_list=tpp_residue_list,
#         smiles=smiles,
#         # Don't use score_column='mixed' - mixing uses ranking which always returns 1.0 for single SMILES
#         # Instead, let it return the average of all model scores (default behavior)
#     )
#     scores.append(score)

# print(scores)
