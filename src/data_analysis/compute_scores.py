# compute_scores.py
import pandas as pd
import os
import argparse

def load_data(filepath: str) -> pd.DataFrame:
    """Loads data from an Excel file and prepares it for analysis."""
    df = pd.read_excel(filepath)
    return df

def calculate_mean(data: pd.Series) -> float:
    """Calculates the mean of a pandas Series."""
    return data.mean()

def calculate_median(data: pd.Series) -> float:
    """Calculates the median of a pandas Series."""
    return data.median()

def calculate_std(data: pd.Series) -> float:
    """Calculates the standard deviation of a pandas Series."""
    return data.std()

def calculate_mode_and_frequency(data: pd.Series) -> tuple:
    """Calculates the mode and its frequency as a percentage of non-null values."""
    mode = data.mode()[0]
    mode_freq = data.value_counts(normalize=True).max()
    return mode, mode_freq

def compute_statistics(data: pd.DataFrame, numerical_col: str) -> dict:
    """Computes statistical summaries for a specified numerical column."""
    numeric_data = data[numerical_col]
    stats = {
        "mean": calculate_mean(numeric_data),
        "median": calculate_median(numeric_data),
        "std": calculate_std(numeric_data),
        "mode": calculate_mode_and_frequency(numeric_data)
    }
    return stats

if __name__ == "__main__":
    # Define default file path and column name
    default_filepath = os.path.join('faculty_feedback_analysis', 'data', 'raw', 'Oasis Eval June 2023 M4.xlsx')
    default_numerical_col = 'Multiple Choice Value'

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Compute statistics from an Excel file.')
    parser.add_argument('--filepath', type=str, default=default_filepath, help='Path to the Excel file')
    parser.add_argument('--numerical_col', type=str, default=default_numerical_col, help='Name of the numerical column')

    # Parse arguments
    args = parser.parse_args()

    # Load data
    df = load_data(args.filepath)

    # Compute statistics
    stats = compute_statistics(df, args.numerical_col)
    
    # Display results
    print(f"Mean: {stats['mean']}")
    print(f"Median: {stats['median']}")
    print(f"Standard Deviation: {stats['std']}")
    print(f"Mode: {stats['mode'][0]} with frequency {stats['mode'][1]}")
