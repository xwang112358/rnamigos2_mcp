from rnamigos.inference import do_inference
import numpy as np

results = do_inference(
    cif_path="data/sample_files/3ox0.cif",
    residue_list=["A.7", "A.8", "A.25", "A.26"],
    ligands_path="data/sample_files/test_smiles.txt",
    out_path="outputs/test_results.csv",
    do_mixing=True
)


tpp_residue_list = np.load('inputs/residue_list/tpp.npy')
print(tpp_residue_list)

results = do_inference(
    cif_path="inputs/rna_targets/2gdi.cif",
    residue_list=tpp_residue_list,
    ligands_path="data/sample_files/test_smiles.txt",
    out_path="outputs/tpp_test_results.csv",
    do_mixing=True
)

