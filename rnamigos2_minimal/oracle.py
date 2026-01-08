"""
Oracle functions for RNAmigos2-based optimization.
"""
import numpy as np
import torch
from rnamigos.inference import do_inference_single


def rnamigos2_oracle(
    smi,
    cif_path='./inputs/rna_targets/2gdi.cif',
    residue_list_path='./inputs/residue_list/tpp.npy',
    residue_list=None,
    score_column='dock'
):
    """
    Run RNAmigos2 inference for a single SMILES string.
    
    Args:
        smi: SMILES string to score
        cif_path: Path to the CIF file for the RNA target
        residue_list_path: Path to the numpy file containing residue list
        residue_list: Optional pre-loaded residue list. If None, will load from residue_list_path
        score_column: Which score column to return (default: 'dock')
    
    Returns:
        float: The score value for the input SMILES
    
    Note:
        This function preserves dtype context. Some optimizers (like GP-BO) set
        torch.set_default_dtype(torch.float64), but RNAmigos2 models were trained
        with float32. This function ensures inference runs with the correct dtype.
    """
    # Load residue list if not provided
    if residue_list is None:
        residue_list = np.load(residue_list_path)
    
    # Save current default dtype and ensure float32 for RNAmigos2 inference
    # RNAmigos2 model was trained with float32, so we need to ensure all tensors
    # created during inference use float32 to match the pre-trained weights
    original_dtype = torch.get_default_dtype()
    torch.set_default_dtype(torch.float32)
    
    try:
        # Run inference with correct dtype
        score = do_inference_single(
            cif_path=cif_path,
            residue_list=residue_list,
            smiles=smi,
            score_column=score_column
        )
    finally:
        # Always restore the original dtype, even if an error occurs
        torch.set_default_dtype(original_dtype)
    
    return score
