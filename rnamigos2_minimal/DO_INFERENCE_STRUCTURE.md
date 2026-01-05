# File Structure for Running `do_inference` Function

This document explains the file structure and dependencies needed to run the `do_inference` function from `rnamigos/inference.py`.

## Entry Point

**Main Function:** `do_inference()` in `rnamigos/inference.py`

## Function Call Flow

```
do_inference()
├── get_models() [rnamigos/inference.py:68]
│   └── get_model_from_dirpath() [rnamigos/learning/models.py:577]
│       ├── Loads config.yaml from model directory
│       ├── cfg_to_model() [rnamigos/learning/models.py:480]
│       └── Loads model.pth from model directory
│
├── get_dgl_graph() [rnamigos/utils/graph_utils.py:160]
│   ├── fr3d_to_graph() [external: rnaglib]
│   ├── multigraph_to_simple() [external: rnaglib]
│   ├── RNAFMTransform() [external: rnaglib] (if use_rnafm=True)
│   ├── rnaglib.algorithms.bfs() [external: rnaglib]
│   ├── prepare_pocket() [rnamigos/utils/graph_utils.py:37]
│   └── nx_to_dgl() [rnamigos/utils/graph_utils.py:128]
│
├── inference_raw() [rnamigos/inference.py:20]
│   ├── InferenceDataset() [rnamigos/learning/dataset.py:477]
│   │   ├── MolGraphEncoder() [rnamigos/learning/ligand_encoding.py:88]
│   │   └── MolFPEncoder() [rnamigos/learning/ligand_encoding.py:12]
│   ├── DataLoader() [PyTorch]
│   └── model.predict_ligands() [rnamigos/learning/models.py:445]
│
└── add_mixed_score() [rnamigos/utils/mixing_utils.py:24] (if do_mixing=True)
```

## Core File Structure

```
rnamigos/
├── inference.py                    # Main entry point with do_inference()
│
├── learning/
│   ├── models.py                   # Model classes, get_model_from_dirpath()
│   ├── dataset.py                  # InferenceDataset class
│   └── ligand_encoding.py          # MolGraphEncoder, MolFPEncoder
│
└── utils/
    ├── graph_utils.py              # get_dgl_graph(), prepare_pocket(), nx_to_dgl()
    └── mixing_utils.py             # add_mixed_score()
```

## Required Input Files

### For `do_inference()` function:

1. **cif_path**: Path to mmCIF structure file (e.g., `3ox0.cif`)
   - Used by `get_dgl_graph()` → `fr3d_to_graph()` to convert structure to graph

2. **ligands_path**: Text file with SMILES strings (one per line)
   - Read directly in `do_inference()` line 111

3. **models_path** (optional): Dictionary mapping model names to directories
   - Default: `{"is_native": "results/trained_models/is_native/native_42", "dock": "results/trained_models/dock/dock_42"}`
   - Each model directory must contain:
     - `config.yaml`: Model configuration
     - `model.pth`: Trained model weights

4. **ligand_cache** (optional): Path to cached ligand graphs
   - Used by `MolGraphEncoder` for performance

## Required Data Files

The following data files are required at runtime (loaded automatically from relative paths):

1. **data/map_files/edges_and_nodes_map.pickle** (required if using graph-based ligand encoding)
   - Loaded by `MolGraphEncoder` in `rnamigos/learning/ligand_encoding.py:95`
   - Contains mapping dictionaries: `edge_map`, `at_map`, `chi_map`, `charges_map`
   - Used for encoding molecular graphs

2. **data/ligands/lig_graphs.p** (optional, created if missing)
   - Cache file for ligand graphs
   - Used by `MolGraphEncoder` to speed up processing
   - Created automatically if it doesn't exist

3. **data/pocket_embeddings/** and **data/pocket_chain_embeddings/** (optional, only if use_rnafm=True)
   - Cache directories for RNA-FM embeddings
   - Used by `add_rnafm()` in `graph_utils.py` if RNA-FM features are enabled

## Model Directory Structure

Each model directory (default or custom) must contain:

```
model_directory/
├── config.yaml         # Model configuration (loaded by get_model_from_dirpath)
└── model.pth           # Model state dict (loaded by get_model_from_dirpath)
```

## Key Dependencies by Module

### `rnamigos/inference.py`
- `InferenceDataset` from `rnamigos.learning.dataset`
- `get_dgl_graph` from `rnamigos.utils.graph_utils`
- `get_model_from_dirpath` from `rnamigos.learning.models`
- `add_mixed_score` from `rnamigos.utils.mixing_utils`

### `rnamigos/utils/graph_utils.py`
- External: `rnaglib` package (for structure to graph conversion)
- External: `dgl`, `networkx`, `torch`, `numpy`

### `rnamigos/learning/dataset.py`
- `MolGraphEncoder`, `MolFPEncoder` from `rnamigos.learning.ligand_encoding`
- External: `dgl`, `torch`

### `rnamigos/learning/ligand_encoding.py`
- `MolGraphEncoder`: Encodes SMILES to molecular graphs (requires `data/map_files/edges_and_nodes_map.pickle`)
- `MolFPEncoder`: Encodes SMILES to molecular fingerprints (MACCS or Morgan)
- External: `rdkit`, `dgl`, `networkx`, `torch`, `numpy`, `pickle`

### `rnamigos/learning/models.py`
- Model architecture classes
- External: `torch`, `omegaconf`, `yaml`

### `rnamigos/utils/mixing_utils.py`
- External: `pandas`, `numpy`, `scipy.stats`

## Data Flow

1. **Structure Processing:**
   - `cif_path` → `get_dgl_graph()` → DGL graph with node features

2. **Ligand Processing:**
   - `ligands_path` → list of SMILES → `InferenceDataset` → batched ligand graphs/vectors

3. **Model Loading:**
   - `models_path` → `get_models()` → `get_model_from_dirpath()` → loaded PyTorch models

4. **Inference:**
   - DGL graph + batched ligands → `model.predict_ligands()` → scores

5. **Post-processing:**
   - Raw scores → flipped if needed → DataFrame → optional mixing → CSV output

## External Dependencies

- **rnaglib**: For RNA structure processing (fr3d_to_graph, BFS expansion, RNA-FM)
- **dgl**: Deep Graph Library for graph neural networks
- **torch**: PyTorch for models and tensors
- **networkx**: Graph operations
- **numpy**, **pandas**: Data manipulation
- **scipy**: For ranking in mixing
- **omegaconf**: Configuration management
- **hydra**: Configuration framework (used in main(), not required for do_inference())
- **rdkit**: For molecular fingerprint generation (MolFPEncoder)
- **yaml**: For loading model configuration files

## Minimal Working Example

```python
from rnamigos.inference import do_inference

results = do_inference(
    cif_path="path/to/structure.cif",
    residue_list=["A.25", "A.26", "A.7", "A.8"],  # or None for entire structure
    ligands_path="path/to/ligands.txt",  # SMILES, one per line
    out_path="results.csv",  # or None to skip saving
    models_path=None,  # Uses default models
    do_mixing=True,  # Combine scores from multiple models
    dump_all=False  # If True, keep all model scores; if False, only mixed score
)
```
