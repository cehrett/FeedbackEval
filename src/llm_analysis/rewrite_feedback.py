# Rewrite non-actionable feedback using LLM

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch.nn.functional as F
from .feedback_prompts import ACTIONABILITY_SYSTEM_PROMPT, SPECIFICITY_SYSTEM_PROMPT
from utils.llm_utils import get_feedback_fsl_examples

def rewrite_feedback(texts, system_prompt, max_new_tokens=250):
    """
    Rewrite feedback using a pre-trained language model.

    Args:
        texts (list of str): A list of feedback texts to rewrite.
        system_prompt (str): The system prompt to use for rewriting the feedback.
        max_new_tokens (int): The maximum number of tokens to generate for each text.

    Returns:
        list of str: The rewritten feedback for each input text.
    """

    # Load the model and tokenizer
    model_id = "Qwen/Qwen2.5-32B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left")
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype=torch.bfloat16)

    # Define the base messages with system prompt and few-shot examples
    base_messages = [{"role": "system", "content": system_prompt}] + get_feedback_fsl_examples()

    # Prepare inputs for each text in the batch
    batch_messages = []
    for text in texts:
        messages = base_messages + [{"role": "user", "content": text}]
        batch_messages.append(messages)

    # Tokenize the messages using chat template
    tokenizer.pad_token = tokenizer.eos_token  # Set pad token to eos
    model_inputs = tokenizer.apply_chat_template(batch_messages, add_generation_prompt=True, return_tensors="pt", padding=True, return_dict=True).to("cuda")

    # Run model to get logits and generated output
    with torch.no_grad():
        outputs = model.generate(**model_inputs, max_new_tokens=max_new_tokens, return_dict_in_generate=True, output_scores=False)
        generated_token_ids = outputs.sequences

    # Extract only the newly generated text for each response
    new_generated_texts = []
    for i, text in enumerate(texts):
        input_ids = model_inputs['input_ids'][i]
        generated_ids = generated_token_ids[i]

        # The new response starts after the input
        new_token_ids = generated_ids[len(input_ids):]
        new_response = tokenizer.decode(new_token_ids, skip_special_tokens=True).strip()
        new_generated_texts.append(new_response)

    return new_generated_texts

if __name__ == "__main__":
    # Example usage
    texts = [
        "We should schedule a meeting to discuss the new project.",
        "Great job, keep it up.",
        "I think there are aspects of your work that could be improved.",
        "You should spend some time practicing your patient communication skills.",
        "You're doing wonderfully.",
        "There's probably some surgical stuff you can work on."
    ]

    # Get rewritten feedback for each text
    rewritten_feedback = rewrite_feedback(texts, ACTIONABILITY_SYSTEM_PROMPT)
    print("Rewritten feedback (for actionability):")
    for text, output in zip(texts, rewritten_feedback):
        print(f"Original Feedback: {text}\nRewritten Feedback: {output}\n\n")

