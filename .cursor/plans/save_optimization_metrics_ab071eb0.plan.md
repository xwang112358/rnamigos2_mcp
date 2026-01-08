---
name: Save optimization metrics
overview: Add functionality to save summary metrics (avg_top1, avg_top10, avg_top100, AUC values, SA, diversity) to a YAML file in the output directory with clear naming.
todos:
  - id: add-save-metrics-method
    content: Add save_metrics() method to Oracle class with naming pattern
    status: completed
  - id: call-save-metrics
    content: Call save_metrics() from log_intermediate() when finish=True
    status: completed
  - id: final-log
    content: Add log_intermediate(finish=True) call in optimize() before save_result()
    status: completed
---

# Save Optimization Metrics to File

## Problem

Currently, optimization metrics (avg_top1, avg_top10, avg_top100, AUC values, SA scores, diversity) are computed in [`mol-opt-rna/molopt/base.py`](mol-opt-rna/molopt/base.py) lines 128-138 but only printed to console, never saved to a file.

## Solution

Make minimal changes to save the `result_dict` to a file with clear naming.

### Changes Required

**1. Modify `Oracle` class in [`mol-opt-rna/molopt/base.py`](mol-opt-rna/molopt/base.py)**

- Add a `save_metrics()` method similar to `save_result()` that saves `result_dict` to a YAML file
- Use naming convention matching existing results: `metrics_{task_label}.yaml` where `task_label` is `{model}_{oracle}_{seed}`
- The method will be called from `log_intermediate()` when `finish=True`
- Save as human-readable YAML format with proper float formatting

**2. Update `Oracle.log_intermediate()` in [`mol-opt-rna/molopt/base.py`](mol-opt-rna/molopt/base.py)**

- When `finish=True`, call the new `save_metrics()` method after creating `result_dict`
- Pass the `result_dict` to save final metrics

**3. Ensure final metrics are saved in `BaseOptimizer.optimize()` in [`mol-opt-rna/molopt/base.py`](mol-opt-rna/molopt/base.py)**

- Add a call to `log_intermediate(finish=True)` before `save_result()` (around line 353)
- This ensures final metrics are always saved, even if early stopping doesn't trigger

### Expected Output

After running any optimizer (GraphGA, SMILES GA, REINVENT, etc.), the `output_dir` will contain:

- `results_<model>_<oracle>_<seed>.yaml` - Full molecule buffer (existing)
- `metrics_<model>_<oracle>_<seed>.yaml` - Final summary metrics including:
- avg_top1, avg_top10, avg_top100
- auc_top1, auc_top10, auc_top100
- avg_sa (synthetic accessibility)
- diversity_top100
- n_oracle (number of oracle calls)

For example, with GraphGA, RNAmigos2 oracle, and seed=0:

- `results_graph_ga_rnamigos2_oracle_0.yaml`
- `metrics_graph_ga_rnamigos2_oracle_0.yaml`

### Files Modified

- [`mol-opt-rna/molopt/base.py`](mol-opt-rna/molopt/base.py) - Two small additions (save metrics file + final log call)