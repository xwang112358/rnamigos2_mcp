# RNAmigos2 Minimal Inference Package

This is a minimal distribution of RNAmigos2 containing only the files needed to run inference using the `do_inference()` function.

## Overview

This minimal structure includes:
- Core Python modules for inference
- Pre-trained model checkpoints (is_native and dock models)
- Required data files for molecular encoding
- Example input files
- Organized directories for user inputs and outputs

## Installation

### 1. Install Dependencies

```bash
git clone --branch only_inference git@github.com:xwang112358/rnamigos2_mcp.git 
cd rnamigo2_minimal/
conda create -n rnamigos2 python=3.10
conda activate rnamigos2
pip install numpy==1.26
pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121
pip install  dgl -f https://data.dgl.ai/wheels/torch-2.2/repo.html
pip install -r requirements.txt
```

### 2. Verify Installation

You can test the installation by running inference on the example files, according tp `test.py`:

```python
from rnamigos.inference import do_inference

results = do_inference(
    cif_path="data/sample_files/3ox0.cif",
    residue_list=["A.7", "A.8", "A.25", "A.26"],
    ligands_path="data/sample_files/test_smiles.txt",
    out_path="outputs/test_results.csv",
    do_mixing=True
)
```

## Directory Structure

```
rnamigos2_minimal/
├── rnamigos/                  # Python package
│   ├── inference.py          # Main inference function
│   ├── learning/             # Model and dataset modules
│   └── utils/                # Utility functions
├── data/
│   ├── map_files/            # Required mapping files
│   └── sample_files/         # Example input files
├── inputs/                   # User input files
│   ├── structures/           # Place your CIF files here
│   ├── ligands/              # Place your SMILES files here
|   |
│   └── README.md             # Input file instructions
├── outputs/                  # Inference results
├── results/
│   └── trained_models/       # Pre-trained model checkpoints
│       ├── is_native/        # Native ligand prediction models
│       └── dock/             # Docking score prediction models
```

## Using Pre-trained Models

The minimal package includes two pre-trained models:
- **is_native/native_42**: Predicts whether a ligand is native to the RNA pocket
- **dock/dock_42**: Predicts docking scores for ligands

These are used by default when calling `do_inference()` without specifying custom models.



## Adding Input Files

### Structure Files (CIF format)

Place your mmCIF structure files in `inputs/rna_targets/`. The CIF file should contain the RNA structure you want to screen.

### Ligand Files (SMILES format)

Place your SMILES files in `inputs/ligands/`. Each file should contain one SMILES string per line.

See `inputs/README.md` for detailed format requirements.


