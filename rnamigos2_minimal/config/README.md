# Configuration Files

This directory contains configuration files for the optimization algorithms.

## Usage

### Automatic (Recommended)
The run scripts automatically create temporary config files when you use non-default parameters:

```bash
# This automatically creates config/gp_bo_temp_10000.yaml
python run_gp_bo.py --initial_population_size 10000
```

### Manual Configuration
You can also create your own config files and pass them using the `--config` argument:

```bash
# Create custom config
cp config/gp_bo_example.yaml config/my_custom_gp_bo.yaml
# Edit my_custom_gp_bo.yaml as needed
# (Note: Manual config passing not yet implemented in run scripts)
```

## Example Configs

- `gp_bo_example.yaml` - Example GP-BO configuration with all available parameters
- `graph_ga_example.yaml` - Example Graph GA configuration
- `smiles_ga_example.yaml` - Example SMILES GA configuration

## Temporary Configs

Temporary config files are automatically created with naming pattern:
- `gp_bo_temp_<initial_pop_size>.yaml`
- `graph_ga_temp_<pop_size>.yaml`
- `smiles_ga_temp_<pop_size>.yaml`

These can be safely deleted after experiments complete.

## Default Values

If no custom parameters are provided, the algorithms use default values from:
- GP-BO: `mol-opt-rna/molopt/gpbo/hparams_default.yaml`
- Graph GA: `mol-opt-rna/molopt/graph_ga/hparams_default.yaml`
- SMILES GA: `mol-opt-rna/molopt/smiles_ga/hparams_default.yaml`
- REINVENT: `mol-opt-rna/molopt/reinvent/hparams_default.yaml`
