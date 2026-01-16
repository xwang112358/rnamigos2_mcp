"""
Oracle functions for RNAmigos2-based optimization.
"""

import numpy as np
import torch
from rnamigos.inference import do_inference_single
from rdkit import Chem
from rdkit import DataStructs
from rdkit.Chem import rdFingerprintGenerator


def rnamigos2_oracle(
    smi,
    cif_path="./inputs/rna_targets/2gdi.cif",
    residue_list_path="./inputs/residue_list/tpp.npy",
    residue_list=None,
    score_column="dock",
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
            score_column=score_column,
        )
    finally:
        # Always restore the original dtype, even if an error occurs
        torch.set_default_dtype(original_dtype)

    return score


def precompute_reference_fingerprints(reference_smiles, radius=2, fp_size=2048):
    """
    Pre-compute Morgan fingerprints for a list of reference molecules.

    This avoids recomputing fingerprints on every similarity calculation,
    providing significant speedup when the same references are used repeatedly.

    Args:
        reference_smiles: List of reference SMILES strings
        radius: Morgan fingerprint radius (default: 2)
        fp_size: Fingerprint size in bits (default: 2048)

    Returns:
        list: List of pre-computed fingerprints (same order as input SMILES)
    """
    mfpgen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=fp_size)
    reference_fps = []

    for ref_smi in reference_smiles:
        ref_mol = Chem.MolFromSmiles(ref_smi)
        if ref_mol is None:
            continue
        try:
            ref_fp = mfpgen.GetFingerprint(ref_mol)
            reference_fps.append(ref_fp)
        except:
            continue

    return reference_fps


def compute_max_similarity(
    smi,
    reference_smiles=None,
    reference_fingerprints=None,
    similarity_threshold=0.7,
    radius=2,
    fp_size=2048,
):
    """
    Compute maximum Tanimoto similarity to a set of reference molecules.

    Args:
        smi: SMILES string to evaluate
        reference_smiles: List of reference SMILES strings (used if reference_fingerprints is None)
        reference_fingerprints: Pre-computed reference fingerprints (preferred for efficiency)
        similarity_threshold: Minimum acceptable similarity (not used for max, kept for compatibility)
        radius: Morgan fingerprint radius (default: 2)
        fp_size: Fingerprint size in bits (default: 2048)

    Returns:
        float: Maximum similarity score (0-1, higher is more similar to closest reference)

    Note:
        If both reference_smiles and reference_fingerprints are provided,
        reference_fingerprints takes precedence for efficiency.
    """
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return 0.0

    # Generate Morgan fingerprint for the candidate molecule
    try:
        mfpgen = rdFingerprintGenerator.GetMorganGenerator(
            radius=radius, fpSize=fp_size
        )
        fp = mfpgen.GetFingerprint(mol)
    except:
        return 0.0

    # Use pre-computed fingerprints if available (much faster!)
    if reference_fingerprints is not None:
        if len(reference_fingerprints) == 0:
            return 0.0

        similarities = []
        for ref_fp in reference_fingerprints:
            try:
                sim = DataStructs.TanimotoSimilarity(fp, ref_fp)
                similarities.append(sim)
            except:
                continue

        if not similarities:
            return 0.0
        return max(similarities)

    # Fallback: compute fingerprints on-the-fly (slower, for backward compatibility)
    elif reference_smiles is not None:
        similarities = []
        for ref_smi in reference_smiles:
            ref_mol = Chem.MolFromSmiles(ref_smi)
            if ref_mol is None:
                continue
            try:
                ref_fp = mfpgen.GetFingerprint(ref_mol)
                sim = DataStructs.TanimotoSimilarity(fp, ref_fp)
                similarities.append(sim)
            except:
                continue

        if not similarities:
            return 0.0
        return max(similarities)

    else:
        # No references provided
        return 0.0


def combined_rnamigos2_similarity_oracle(
    smi,
    cif_path="./inputs/rna_targets/2gdi.cif",
    residue_list_path="./inputs/residue_list/tpp.npy",
    residue_list=None,
    score_column="dock",
    reference_smiles=None,
    reference_fingerprints=None,
    similarity_weight=0.3,
    binding_weight=0.7,
    similarity_threshold=0.7,
):
    """
    Combined oracle that balances RNAmigos2 binding affinity with similarity to references.

    This oracle uses a weighted sum approach:
        combined_score = binding_weight * binding_score + similarity_weight * similarity_score

    Args:
        smi: SMILES string to score
        cif_path: Path to the CIF file for the RNA target
        residue_list_path: Path to the numpy file containing residue list
        residue_list: Optional pre-loaded residue list
        score_column: Which score column to return from RNAmigos2
        reference_smiles: List of reference SMILES to maintain similarity to (fallback)
        reference_fingerprints: Pre-computed reference fingerprints (preferred for efficiency)
        similarity_weight: Weight for similarity objective (default: 0.3)
        binding_weight: Weight for binding affinity objective (default: 0.7)
        similarity_threshold: Minimum acceptable similarity (passed to similarity function)

    Returns:
        float: Combined score (weighted sum of binding and similarity)

    Note:
        - If no reference molecules/fingerprints provided, returns pure binding score
        - Similarity is computed as maximum Tanimoto similarity to any reference
        - Weights should sum to 1.0 for interpretability, but this is not enforced
        - Using reference_fingerprints is much more efficient than reference_smiles
    """
    # Get binding affinity from RNAmigos2
    binding_score = rnamigos2_oracle(
        smi=smi,
        cif_path=cif_path,
        residue_list_path=residue_list_path,
        residue_list=residue_list,
        score_column=score_column,
    )

    # If no reference molecules/fingerprints provided, just return binding score
    if reference_fingerprints is None and (
        reference_smiles is None or len(reference_smiles) == 0
    ):
        return binding_score

    # Get similarity score (max similarity to any reference molecule)
    similarity_score = compute_max_similarity(
        smi=smi,
        reference_smiles=reference_smiles,
        reference_fingerprints=reference_fingerprints,
        similarity_threshold=similarity_threshold,
    )

    # Combine scores using weighted sum
    combined_score = (
        binding_weight * binding_score + similarity_weight * similarity_score
    )

    return combined_score
