import argparse
import os
import yaml
from molopt.gpbo import GPBO
from rdkit import RDLogger
from rdkit import Chem
from oracle import rnamigos2_oracle as tpp_rnamigos2_oracle
from oracle import combined_rnamigos2_similarity_oracle
from oracle import precompute_reference_fingerprints

# Disable RDKit warnings for cleaner output
RDLogger.DisableLog("rdApp.warning")


if __name__ == "__main__":
    # ============================================================================
    # Parse Command-Line Arguments
    # ============================================================================
    parser = argparse.ArgumentParser(
        description="Run GP-BO optimization for RNA-ligand binding"
    )
    parser.add_argument(
        "--smi_file",
        type=str,
        default="inputs/ligands/robin_smiles.txt",
        help="Path to SMILES file with starting molecules",
    )
    parser.add_argument(
        "--max_oracle_calls",
        type=int,
        default=10000,
        help="Maximum number of oracle evaluations (default: 10000)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="opt_results/gp_bo",
        help="Directory to save results (default: opt_results/gp_bo)",
    )
    parser.add_argument(
        "--num_runs",
        type=int,
        default=1,
        help="Number of independent runs (default: 1)",
    )
    parser.add_argument(
        "--n_jobs",
        type=int,
        default=-1,
        help="Number of parallel jobs, -1 for all cores (default: -1)",
    )
    parser.add_argument(
        "--freq_log", type=int, default=100, help="Logging frequency (default: 100)"
    )
    parser.add_argument(
        "--initial_population_size",
        type=int,
        default=340,
        help="Initial population size for GP training (default: 340)",
    )

    # Combined objective arguments
    parser.add_argument(
        "--use_combined_objective",
        action="store_true",
        help="Use combined binding + similarity objective",
    )
    parser.add_argument(
        "--reference_file",
        type=str,
        default=None,
        help="Path to reference SMILES file for similarity (default: use smi_file)",
    )
    parser.add_argument(
        "--similarity_weight",
        type=float,
        default=0.3,
        help="Weight for similarity objective (default: 0.3)",
    )
    parser.add_argument(
        "--binding_weight",
        type=float,
        default=0.7,
        help="Weight for binding objective (default: 0.7)",
    )
    args = parser.parse_args()

    # ============================================================================
    # Load Reference Molecules for Combined Objective
    # ============================================================================
    reference_smiles = None
    reference_fingerprints = None
    if args.use_combined_objective:
        # Determine which file to use for reference molecules
        ref_file = args.reference_file if args.reference_file else args.smi_file

        # Load reference SMILES
        with open(ref_file, "r") as f:
            reference_smiles = []
            for line in f:
                smi = line.strip()
                if smi:  # Skip empty lines
                    mol = Chem.MolFromSmiles(smi)
                    if mol is not None:
                        reference_smiles.append(Chem.MolToSmiles(mol))  # Canonicalize

        print(f"Loaded {len(reference_smiles)} reference molecules from {ref_file}")

        # Pre-compute reference fingerprints for efficiency
        print("Pre-computing reference fingerprints...")
        reference_fingerprints = precompute_reference_fingerprints(reference_smiles)
        print(f"Pre-computed {len(reference_fingerprints)} reference fingerprints")
        print(
            f"Using combined objective: binding_weight={args.binding_weight}, similarity_weight={args.similarity_weight}"
        )

        # Modify output directory to indicate combined objective
        if not args.output_dir.endswith("_combined"):
            args.output_dir = args.output_dir.rstrip("/") + "_combined"

    # ============================================================================
    # Initialize GP-BO Optimizer
    # ============================================================================
    optimizer = GPBO(
        smi_file=args.smi_file,
        n_jobs=args.n_jobs,
        max_oracle_calls=args.max_oracle_calls,
        freq_log=args.freq_log,
        output_dir=args.output_dir,
    )

    # ============================================================================
    # Create Oracle Function
    # ============================================================================
    if args.use_combined_objective and reference_fingerprints:
        # Create combined oracle with similarity penalty using pre-computed fingerprints
        def oracle(smi):
            return combined_rnamigos2_similarity_oracle(
                smi=smi,
                reference_fingerprints=reference_fingerprints,
                similarity_weight=args.similarity_weight,
                binding_weight=args.binding_weight,
            )
    else:
        # Use standard RNAmigos2 oracle
        oracle = tpp_rnamigos2_oracle

    # ============================================================================
    # Run Optimization
    # ============================================================================
    # Create config file if non-default initial_population_size is used
    if args.initial_population_size != 340:
        config_dict = {"initial_population_size": args.initial_population_size}
        os.makedirs("config", exist_ok=True)
        config_path = f"config/gp_bo_temp_{args.initial_population_size}.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_dict, f)
        optimizer.production(oracle=oracle, config=config_path, num_runs=args.num_runs)
    else:
        # Use default config
        optimizer.production(oracle=oracle, config=None, num_runs=args.num_runs)
