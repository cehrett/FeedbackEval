# Run analysis and report generation pipeline

import sys
import os
import pandas as pd

from data_analysis.compute_scores import load_data as load_numerical_data, compute_statistics
from data_analysis.text_variability import (
    load_data as load_text_data,
    preprocess_text,
    generate_embeddings,
    compute_variability,
)
from llm_analysis.actionability_scoring import get_actionability_score
from llm_analysis.rewrite_feedback import rewrite_feedback
from utils.anonymization_utils import anonymize_batch
from report_generation.generate_reports import generate_report


def main(excel_file_path, output_html_path="report.html"):
    """
    Main pipeline for faculty feedback analysis.

    Args:
        excel_file_path (str): Path to the Excel file with feedback data.
        output_html_path (str): Path to save the output HTML report.
    """

    if not os.path.exists(excel_file_path):
        print(f"Error: File '{excel_file_path}' not found.")
        sys.exit(1)

    # Load numerical data and compute statistics
    print("Loading numerical data...")
    numerical_data_df = load_numerical_data(excel_file_path)
    statistics = compute_statistics(numerical_data_df, numerical_col="Multiple Choice Value")

    # Load text data and compute text variability
    print("Loading and preprocessing text data...")
    text_data = load_text_data(excel_file_path, text_column="Answer text")
    preprocessed_text = preprocess_text(text_data)
    embeddings = generate_embeddings(preprocessed_text)
    text_variability = compute_variability(embeddings)

    # Compute actionability scores
    print("Computing actionability scores...")
    avg_actionability, actionability_scores, llm_outputs = get_actionability_score(preprocessed_text)

    # Identify least actionable text and rewrite
    print("Finding least actionable text...")
    actionable_indices = sorted(range(len(actionability_scores)), key=lambda i: actionability_scores[i])[:5]
    least_actionable_texts = [preprocessed_text[i] for i in actionable_indices]
    rewritten_texts = rewrite_feedback(least_actionable_texts)

    # Anonymize text
    print("Anonymizing text...")
    anonymized_original_texts = anonymize_batch(least_actionable_texts)
    anonymized_rewritten_texts = anonymize_batch(rewritten_texts)

    # Prepare data for report
    report_data = {
        "text_variability": text_variability["mean_distance"],
        "numeric_mean": statistics["mean"],
        "numeric_std": statistics["std"],
        "actionability": avg_actionability,
    }

    # Generate and save report
    print("Generating report...")
    html_report = generate_report(
        report_data,
        unactionable_feedback_examples=anonymized_original_texts,
        rewritten_feedback_examples=anonymized_rewritten_texts,
    )
    with open(output_html_path, "w") as output_file:
        output_file.write(html_report)

    print(f"Report generated and saved to '{output_html_path}'.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <path_to_excel_file> [output_html_path]")
        sys.exit(1)

    excel_file_path = sys.argv[1]
    output_html_path = sys.argv[2] if len(sys.argv) > 2 else "report.html"
    main(excel_file_path, output_html_path)

