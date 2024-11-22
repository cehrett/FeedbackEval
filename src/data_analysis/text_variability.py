# Calculate text variability using NLP techniques
import argparse
import pandas as pd
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
import numpy as np
import torch

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Calculate variability in freeform text data.")
    parser.add_argument("file_path", type=str, help="Path to the input CSV file.")
    parser.add_argument("text_column", type=str, default="Answer text", help="Name of the column containing text data.")
    parser.add_argument("--model_name", type=str, default="all-MiniLM-L6-v2", 
                        help="Name of the SentenceTransformer model to use.")
    parser.add_argument("--output_path", type=str, default=None, 
                        help="Path to save the results (optional).")
    return parser.parse_args()

def load_data(file_path, text_column):
    """Load the excel file and extract the specified text column,
    excluding NaN values and purely numeric rows."""
    try:
        df = pd.read_excel(file_path)
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in the input file.")
        # Filter out NaN values and purely numeric rows
        filtered_data = df[text_column].dropna()
        filtered_data = filtered_data[~filtered_data.apply(lambda x: isinstance(x, (int, float)) or str(x).strip().isdigit())]
        return filtered_data.tolist()
    except Exception as e:
        raise ValueError(f"Error loading data: {e}")

def preprocess_text(text_data):
    """Minimal preprocessing for text data."""
    # Strip whitespace and remove empty strings.
    return [stripped for text in text_data if (stripped := text.strip())]

def generate_embeddings(text_data, model_name):
    """Generate embeddings for text data using a SentenceTransformer model."""
    try:
        model = SentenceTransformer(model_name)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)  # Move model to GPU if available
        embeddings = model.encode(text_data, show_progress_bar=True, device=device)
        return embeddings
    except Exception as e:
        raise RuntimeError(f"Error generating embeddings: {e}")

def compute_variability(embeddings):
    """Compute variability as the average pairwise cosine distance."""
    n = len(embeddings)
    if n < 2:
        raise ValueError("Not enough data to compute variability.")
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            distances.append(cosine(embeddings[i], embeddings[j]))
    # Return mean and standard deviation of distances.
    return {
        "mean_distance": np.mean(distances),
        "std_distance": np.std(distances),
    }

def main():
    """Main script workflow."""
    args = parse_arguments()
    
    # Load and preprocess data
    text_data = load_data(args.file_path, args.text_column)
    text_data = preprocess_text(text_data)
    if not text_data:
        raise ValueError("No valid text data found after preprocessing.")
    
    # Generate embeddings
    embeddings = generate_embeddings(text_data, args.model_name)
    
    # Compute variability
    results = compute_variability(embeddings)
    
    # Display results
    print("Variability Metrics:")
    for key, value in results.items():
        print(f"{key}: {value:.4f}")
    
    # Optionally save results
    if args.output_path:
        pd.DataFrame([results]).to_csv(args.output_path, index=False)
        print(f"Results saved to {args.output_path}")

if __name__ == "__main__":
    main()
