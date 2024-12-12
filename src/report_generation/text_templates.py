# Preamble text
PREAMBLE_TEXT = "This report provides an analysis of the feedback you have provided. The analysis includes text variability, numerical variability, and actionability of the feedback. Please review the analysis provided to see how you can improve your feedback in these areas."

# Text blurbs for text variability scores
VARIABILITY_TEXTS = {
    "low": "The feedback shows low lexical variability (score: {score:.2f}), indicating somewhat homogenous evaluations. Consider lorem ipsuming.",
    "medium": "The feedback shows moderate variability (score: {score:.2f}), suggesting an intermediate level of text homogeneity in the feedback. Consider lorem ipsuming.",
    "high": "The feedback shows high variability (score: {score:.2f}), reflecting dynamic and diverse feedback. This is beneficial to the subjects of your feedback in giving them targeted and individualized comments.",
}

# Text blurbs for numerical variability scores
NUMERIC_VARIABILITY_TEXTS = {
    "low": "Your numerical feedback scores have an average value of {score_mean:.2f} and a standard deviation of {score_std:.2f}. This suggests that the feedback scores are relatively homogenous and hence do not provide a wide range of feedback. Consider providing more diverse ratings.",
    "medium": "Your numerical feedback scores have an average value of {score_mean:.2f} and a standard deviation of {score_std:.2f}. This suggests that the feedback scores are moderately diverse, but there is room for improvement. Consider providing more diverse ratings.",
    "high": "Your numerical feedback scores have an average value of {score_mean:.2f} and a standard deviation of {score_std:.2f}. This suggests that the feedback scores are highly diverse, which is beneficial for providing targeted and individualized feedback.",
}

# Text blurbs for actionability scores
ACTIONABILITY_TEXTS = {
    "low": "The feedback scores low (score: {score:.2f}) in terms of actionability, in the sense that feedback often does not directly indicate what steps the subject can take to improve their performance. Consider providing more specific suggestions.",
    "medium": "The feedback scores medium (score: {score:.2f}) in terms of actionability, suggesting that some feedback is actionable, but there is room for improvement. Consider providing more specific suggestions.",
    "high": "The feedback scores high (score: {score:.2f}) in terms of actionability, indicating that feedback is often actionable and provides clear steps for improvement. Keep up the good work!f",
}