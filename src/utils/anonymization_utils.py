# anonymization utilities (e.g., reading/writing data)

from transformers import pipeline
import re
import torch
from typing import List

def anonymize_batch(texts: List[str], batch_size: int = 16) -> List[str]:
    """
    Anonymize a batch of texts by replacing names with '[NAME]' and dates with '[DATE]'.
    
    Args:
        texts (List[str]): List of texts to anonymize.
        batch_size (int): Number of texts to process at once.
    
    Returns:
        List[str]: Anonymized texts.
    """
    # Check if a GPU is available
    device = 0 if torch.cuda.is_available() else -1

    # Load NER pipeline with GPU support
    ner_pipeline = pipeline(
        "ner",
        model="dbmdz/bert-large-cased-finetuned-conll03-english",
        aggregation_strategy="simple",
        device=device
    )

    anonymized_texts = []

    # Split texts into batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        # Run NER on the batch
        ner_results = ner_pipeline(batch)

        # Process each text in the batch
        for text, entities in zip(batch, ner_results):
            # Replace detected names with [NAME]
            for entity in entities:
                if entity['entity_group'] == 'PER':  # 'PER' is the label for persons
                    text = text.replace(entity['word'], '[NAME]')

            # Replace dates with [DATE]
            date_pattern = r'\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{1,2}-\d{1,2}-\d{2,4}\b'
            text = re.sub(date_pattern, '[DATE]', text)

            # Append anonymized text to the result
            anonymized_texts.append(text)

    return anonymized_texts

if __name__ == "__main__":
    # Example usage
    feedbacks = [
        "Dr. Anjali Gupta said that Santiago Rojas did well on 12/05/2024.",
        "Fatima Donaldson and Dr. Hiroshi Tanaka worked together on 10-10-2023.",
        "This feedback was provided by Dr. Ebere Okafor on 3/3/2021."
    ]

    print("Original Feedback:")
    for feedback in feedbacks:
        print(feedback)

    # Call the anonymization function
    anonymized_feedbacks = anonymize_batch(feedbacks, batch_size=2)

    print("\nAnonymized Feedback:")
    for anonymized_feedback in anonymized_feedbacks:
        print(anonymized_feedback)
