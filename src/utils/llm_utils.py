# LLM utilities 

import pandas as pd
import random
import os

def get_feedback_fsl_examples(filename=os.path.join("data","raw","handwritten_feedback_improvements.xlsx")):
    """
    Reads an Excel file containing feedback examples and generates a list of dictionaries
    suitable for few-shot learning.

    Args:
        filename (str, optional): The name of the Excel file.
            Defaults to "handwritten_feedback_improvements.xlsx".

    Returns:
        list: A list of dictionaries, where each pair of dictionaries represents
              a user-assistant interaction for few-shot learning.
    """
    df = pd.read_excel(filename)
    examples = []
    
    # Get column headers and shuffle them
    column_headers = list(df.columns)[1:]  # Exclude the timestamp column
    random.shuffle(column_headers)
    
    for header in column_headers:
        # Get the data from the column, excluding the header
        column_data = df[header].tolist()[1:]
        
        # Filter out empty or short entries
        valid_entries = [entry for entry in column_data if isinstance(entry, str) and len(entry) >= 10]
        
        if valid_entries:
            # Randomly select an entry from the column
            selected_entry = random.choice(valid_entries)
            
            # Create the user and assistant dictionaries
            user_example = {"role": "user", "content": header.strip()}
            assistant_example = {"role": "assistant", "content": selected_entry.strip()}
            
            examples.append(user_example)
            examples.append(assistant_example)
            
    return examples