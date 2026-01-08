# Progress Bar Guide for Molecular Optimization

## What Was Added

Progress bars using `tqdm` have been added to both optimization methods:

### 1. **GraphGA Optimizer** (`molopt/graph_ga/run.py`)
- Shows total molecules evaluated vs. max_oracle_calls
- Displays current best score
- Shows patience counter (for early stopping)
- Updates in real-time as new molecules are generated and evaluated

### 2. **Screening Optimizer** (`molopt/screening/run.py`)
- Shows progress through the molecule library
- Displays current best score found
- Shows total molecules evaluated
- Updates every 100 molecules

## Example Output

### GraphGA Progress Bar:
```
GraphGA Optimization: 450/1000 molecules [02:15<03:30, 2.5molecules/s, Best=0.9481, Patience=2]
```

### Screening Progress Bar:
```
Screening: 300/1000 molecules [00:45<01:30, 6.7molecules/s, Best=0.8523, Evaluated=300]
```

## What Each Field Means:

- **450/1000**: Current evaluations / Maximum oracle calls
- **[02:15<03:30]**: Time elapsed < Time remaining (estimated)
- **2.5molecules/s**: Evaluation speed
- **Best=0.9481**: Best score found so far
- **Patience=2**: Iterations without improvement (GraphGA only)
- **Evaluated=300**: Total unique molecules evaluated (Screening only)

## Benefits:

1. **Real-time feedback**: See optimization progress without waiting
2. **Time estimation**: Know approximately how long the run will take
3. **Performance monitoring**: Track the best score as it improves
4. **Early stopping insight**: See patience counter to know if optimization is converging

## Usage:

No changes needed to your code! The progress bars are automatically displayed when you run:

```python
# Your existing code works the same
optimizer = GraphGA(smi_file='robin_smiles.txt', max_oracle_calls=1000)
optimizer.optimize(oracle=rnamigos2_oracle, patience=50, seed=0)
```

The progress bar will appear in your terminal during optimization.

## Disabling Progress Bars (Optional):

If you want to disable progress bars (e.g., for logging to files), set the TQDM environment variable:

```bash
export TQDM_DISABLE=1
python run_graphga.py
```
