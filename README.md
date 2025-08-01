# perf_tools

## compare_pcounters_t_test.py

A Python script that compares performance counters between two CSV files using statistical t-tests to identify significant differences.

### Description

This script performs statistical analysis on performance counter data by:
1. Reading two CSV files containing time-series performance counter data
2. Calculating row-to-row differences (consecutive row differences)
3. Computing mean and standard error for each counter column
4. Performing independent t-tests to compare the two datasets
5. Determining statistical significance at the 0.05 level

### Usage

```bash
python compare_pcounters_t_test.py <csv1> <csv2> [--output OUTPUT]
```

**Arguments:**
- `csv1`: First CSV file path
- `csv2`: Second CSV file path  
- `--output`: Output file for t-statistics (default: `t_statistics.csv`)

**Example:**
```bash
python compare_pcounters_t_test.py baseline.csv experiment.csv --output results.csv
```

### Input Format

CSV files should contain time-series performance counter data:

```csv
time,counter1,counter2,counter3
1,12,45,28
2,25,58,72
3,30,65,85
```

### Output

The script generates a CSV file with statistical results containing:
- **t_value**: t-statistics for each counter column
- **degrees_of_freedom**: degrees of freedom (n1 + n2 - 2)
- **p_value**: p-values for two-tailed t-tests
- **significant_0.05**: "Yes"/"No" indicating significance at α = 0.05

### Console Output

The script prints:
- Summary of t-statistics table
- List of significantly different columns (p < 0.05)
- Location of saved results file

### Statistical Method

- Uses consecutive row differences to analyze counter deltas
- Performs independent t-tests with pooled standard error
- Two-tailed significance testing at 0.05 level
- Handles missing data and zero variance cases
