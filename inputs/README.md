# Input Files Guide

This directory is for organizing your input files for RNAmigos2 inference.

## Directory Structure

- **`rna_targets/`**: Place your RNA structure files (mmCIF format) here
- **`ligands/`**: Place your ligand files (SMILES format) here

## Structure Files (mmCIF format)

### Location
Place your structure files in the `rna_targets/` directory.

### Format Requirements
- File format: mmCIF (`.cif` extension)
- Contains 3D structure of the RNA molecule
- Should include the binding site residues you want to analyze

### Residue Selection
When calling `do_inference()`, you need to specify which residues form the binding pocket. The format is:
- Chain identifier + residue number (e.g., `"A.25"`, `"B.42"`)
- Provide a list of core binding site residues
- The algorithm will automatically expand around these residues using BFS (Breadth-First Search)

### Example
```python
residue_list = ["A.7", "A.8", "A.25", "A.26"]  # Chain A, residues 7, 8, 25, 26
```

### Getting Structure Files
You can download structure files from:
- RCSB PDB: https://www.rcsb.org/
- Use the mmCIF format download option

### Example File
See `../data/sample_files/3ox0.cif` for a reference example.

## Ligand Files (SMILES format)

### Location
Place your ligand files in the `ligands/` directory.

### Format Requirements
- File format: Plain text (`.txt` extension recommended)
- One SMILES string per line
- No header line required
- Empty lines are ignored
- Each SMILES string should be valid (will fail silently for invalid SMILES)

### Example File Format
```
CCC[S@](=O)c1ccc2[nH]/c(=N\C(=O)OC)[nH]c2c1
O=C(O)[C@@H](O)c1ccccc1
CC(=O)Oc1ccccc1C(=O)O
CN1[C@H]2CC[C@@H]1CC(OC(=O)[C@H](CO)c1ccccc1)C2
```

### SMILES String Guidelines
- Standard SMILES notation
- Supports stereochemistry (e.g., `[C@H]`, `[C@@H]`)
- Supports isotopes, charges, and other extensions
- Invalid SMILES will be encoded with default/zero features

### Example File
See `../data/sample_files/test_smiles.txt` for a reference example with 100 SMILES strings.

## Output Files

Results will be saved to the `outputs/` directory by default. The output CSV file contains:

- **`smiles`**: The input SMILES strings
- **Model scores**: Individual scores from each model (e.g., `is_native`, `dock`)
- **`mixed`**: Combined score from multiple models (if mixing is enabled)

### Output Format Example
```csv
smiles,is_native,dock,mixed
CCC[S@](=O)c1ccc2[nH]/c(=N\C(=O)OC)[nH]c2c1,0.75,0.82,0.85
O=C(O)[C@@H](O)c1ccccc1,0.68,0.71,0.72
```

Scores range from 0 to 1, with higher values indicating better binding likelihood.

## Usage Example

1. **Prepare your files:**
   ```bash
   # Copy your structure file
   cp my_structure.cif inputs/structures/
   
   # Copy your ligands file
   cp my_ligands.txt inputs/ligands/
   ```

2. **Run inference:**
   ```python
   from rnamigos.inference import do_inference
   
   results = do_inference(
       cif_path="inputs/structures/my_structure.cif",
       residue_list=["A.1", "A.2", "A.3", "A.4"],  # Adjust to your structure
       ligands_path="inputs/ligands/my_ligands.txt",
       out_path="outputs/my_results.csv"
   )
   ```

3. **Check results:**
   ```bash
   # View the output
   head outputs/my_results.csv
   ```

## Tips

- **Residue selection**: Start with 3-5 core residues at the binding site center. The algorithm expands automatically.
- **Large ligand sets**: Processing thousands of ligands may take time. Consider batching if needed.
- **File organization**: Keep input files organized in the appropriate subdirectories for easier management.
- **Backup**: Keep backups of your input files before processing large datasets.

## Troubleshooting

- **File not found**: Check that file paths are relative to the repository root or use absolute paths.
- **Invalid SMILES**: Some SMILES may fail to encode. Check the output to see which ligands were processed.
- **Structure errors**: Ensure your CIF file is valid and contains the residues you specified.
