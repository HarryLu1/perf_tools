#!/bin/sh
"eval" "SPARTA_SCRIPTS_DIR=$(dirname $(readlink -f ${BASH_SOURCE[0]}));" \
       "[ -f \$SPARTA_SCRIPTS_DIR/venv/bin/activate ] || \$SPARTA_SCRIPTS_DIR/virtualenv \$SPARTA_SCRIPTS_DIR/venv"
"exec" "$SPARTA_SCRIPTS_DIR/venv/bin/python" "$0" "$@"

import csv
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import argparse

def calculate_row_differences(df):
    """Calculate difference between consecutive rows"""
    return df.diff().dropna()

def calculate_stats(diff_df):
    """Calculate mean and stderr for each column"""
    means = diff_df.mean()
    stderrs = diff_df.sem()  # Standard error of mean
    return means, stderrs

def perform_t_test(means1, stderrs1, n1, means2, stderrs2, n2):
    """Perform independent t-test between two datasets"""
    t_values = {}
    df_values = {}
    p_values = {}
    significant = {}
    
    for col in means1.index:
        if col in means2.index:
            # Calculate pooled standard error
            se_pooled = np.sqrt(stderrs1[col]**2 + stderrs2[col]**2)
            
            # Calculate t-statistic
            if se_pooled != 0:
                t_stat = (means1[col] - means2[col]) / se_pooled
                t_values[col] = t_stat
                
                # Degrees of freedom
                df = n1 + n2 - 2
                df_values[col] = df
                
                # Calculate p-value (two-tailed)
                p_val = 2 * (1 - stats.t.cdf(abs(t_stat), df))
                p_values[col] = p_val
                
                # Check significance at 0.05 level
                significant[col] = 'Yes' if p_val < 0.05 else 'No'
            else:
                t_values[col] = np.nan
                df_values[col] = np.nan
                p_values[col] = np.nan
                significant[col] = 'N/A'
    
    return (pd.Series(t_values), pd.Series(df_values), 
            pd.Series(p_values), pd.Series(significant))

def main():
    parser = argparse.ArgumentParser(
        description='Compare performance counters between two CSV files using t-test',
        epilog='''
Example:
  %(prog)s data1.csv data2.csv --output results.csv
  
  Input CSV format:
    time,counter1,counter2,counter3
    1,12,45,28
    2,25,58,72
    3,30,65,85
  
  Output will contain t-values, degrees of freedom, p-values, and significance tests.
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('csv1', type=Path, help='First CSV file')
    parser.add_argument('csv2', type=Path, help='Second CSV file')
    parser.add_argument('--output', type=str, default='t_statistics.csv', help='Output file for t-statistics')
    args = parser.parse_args()

    # Read CSV files
    df1 = pd.read_csv(args.csv1)
    df2 = pd.read_csv(args.csv2)
    
    # Calculate row differences
    diff1 = calculate_row_differences(df1)
    diff2 = calculate_row_differences(df2)
    
    # Calculate statistics
    means1, stderrs1 = calculate_stats(diff1)
    means2, stderrs2 = calculate_stats(diff2)
    
    # Perform t-test
    t_values, df_values, p_values, significant = perform_t_test(
        means1, stderrs1, len(diff1), means2, stderrs2, len(diff2))
    
    # Create output dataframe
    result_df = pd.DataFrame([t_values, df_values, p_values, significant], 
                           index=['t_value', 'degrees_of_freedom', 'p_value', 'significant_0.05'])
    
    # Save results
    result_df.to_csv(args.output)
    print(f"T-statistics saved to {args.output}")
    print("\nT-statistics:")
    print(result_df)
    
    # Print significant columns
    significant_cols = result_df.loc['significant_0.05'] == 'Yes'
    if significant_cols.any():
        print(f"\nSignificant columns (p < 0.05):")
        for col in result_df.columns[significant_cols]:
            print(f"  {col}")
    else:
        print(f"\nNo significant differences found (p < 0.05)")

if __name__ == '__main__':
    main()
