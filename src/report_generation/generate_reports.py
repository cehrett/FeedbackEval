# Generate human-readable reports for faculty feedback analysis

from report_generation.text_templates import (
    PREAMBLE_TEXT,
    VARIABILITY_TEXTS,
    NUMERIC_VARIABILITY_TEXTS,
    ACTIONABILITY_TEXTS,
)


def select_template(category_texts, decision_score, **format_args):
    """
    Select and format a text template based on the decision score and additional formatting arguments.
    
    Args:
        category_texts (dict): A dictionary mapping score levels to text templates.
        decision_score (float): The score used to decide which template to select (0 to 1).
        **format_args: Additional arguments for formatting the template.
    
    Returns:
        str: The formatted text template.
    """
    if decision_score < 0.33:
        template = category_texts["low"]
    elif decision_score < 0.66:
        template = category_texts["medium"]
    else:
        template = category_texts["high"]

    return template.format(**format_args)


def generate_report(scores, unactionable_feedback_examples, rewritten_feedback_examples):
    """
    Generate an HTML report based on provided scores and examples.

    Args:
        scores (dict): A dictionary containing:
            - "text_variability": float score for text variability (0 to 1).
            - "numeric_mean": float mean score for numerical feedback.
            - "numeric_std": float standard deviation for numerical feedback.
            - "actionability": float score for actionability (0 to 1).
        unactionable_feedback_examples (list): List of strings with original unactionable feedback examples.
        rewritten_feedback_examples (list): List of strings with rewritten actionable feedback examples.

    Returns:
        str: The full report as an HTML string.
    """
    # Select and format text variability section
    text_variability_text = select_template(
        VARIABILITY_TEXTS,
        decision_score=scores["text_variability"],
        score=scores["text_variability"]
    )

    # Select and format numerical variability section
    numeric_variability_text = select_template(
        NUMERIC_VARIABILITY_TEXTS,
        decision_score=scores["numeric_std"],
        score_mean=scores["numeric_mean"],
        score_std=scores["numeric_std"]
    )

    # Select and format actionability section
    actionability_text = select_template(
        ACTIONABILITY_TEXTS,
        decision_score=scores["actionability"],
        score=scores["actionability"]
    )

    # Assemble the HTML report
    report = f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <title>Feedback Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; }}
            p {{ margin-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f4f4f4; color: #2c3e50; }}
            ul {{ margin-top: 0; }}
        </style>
    </head>
    <body>
        <h1>Feedback Analysis Report</h1>

        <p>{PREAMBLE_TEXT}</p>

        <h2>Text Variability</h2>
        <p>{text_variability_text}</p>

        <h2>Numerical Variability</h2>
        <p>{numeric_variability_text}</p>

        <h2>Actionability</h2>
        <p>{actionability_text}</p>

        <h2>Examples of Actionable Feedback</h2>
        <p>Below are examples of unactionable feedback, along with rewritten versions that are more actionable:</p>
        <table>
            <tr>
                <th>Original Feedback</th>
                <th>Rewritten Feedback</th>
            </tr>
            {''.join(f'<tr><td>{orig}</td><td>{rewritten}</td></tr>' for orig, rewritten in zip(unactionable_feedback_examples, rewritten_feedback_examples))}
        </table>
    </body>
    </html>
    """
    return report

if __name__ == "__main__":
    # Example input scores
    scores = {
        "text_variability": 0.72,
        "numeric_mean": 3.45,
        "numeric_std": 0.56,
        "actionability": 0.25,
    }

    # Example unactionable feedback
    unactionable_examples = [
        "You need to improve your communication skills.",
        "You should be more organized."
    ]

    # Example rewritten actionable feedback
    rewritten_examples = [
        "Consider focusing feedback on specific skills such as communication.",
        "Provide clear examples to illustrate your points."
    ]

    # Generate the report
    report = generate_report(scores, unactionable_examples, rewritten_examples)
    with open("feedback_report.html", "w") as file:
        file.write(report)
    print("Report generated successfully! File saved as 'feedback_report.html'.")
    print(report)