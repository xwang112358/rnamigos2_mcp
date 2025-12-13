module load GCC/13.3.0
python rnamigos/inference.py cif_path=data/sample_files/3ox0.cif \
                                pdbid=3ox0 \
                                residue_list=\[A.20,A.19,A.18,A.17,A.16\] \
                                ligands_path=data/sample_files/test_smiles.txt \
                                out_path=scores.txt