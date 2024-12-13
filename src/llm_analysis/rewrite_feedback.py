# Rewrite non-actionable feedback using LLM

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch.nn.functional as F

def rewrite_feedback(texts, max_new_tokens=250):
    """
    Rewrite non-actionable feedback using a pre-trained language model.

    Args:
        texts (list of str): A list of non-actionable feedback texts to rewrite.
        max_new_tokens (int): The maximum number of tokens to generate for each text.

    Returns:
        list of str: The rewritten feedback for each input text.
    """

    # Load the model and tokenizer
    model_id = "meta-llama/Llama-3.2-3B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left")
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")

    # Define the conversation using a list of messages (chat template)
    base_messages = [
        {"role": "system", "content": "You are a helpful assistant that rewrites feedback from mentors to medical students, to make it more actionable for the student. \"Actionable\" statements are statements that imply a specific task, action, or strategy for improvement. Vague or general instructions that do not imply a specific task, action or strategy for improvement are not actionable. The user will submit a piece of feedback which is not actionable; you respond with an example of similar feedback which is actionable."},
        {"role": "user", "content": "Your notes were hard to follow."},
        {"role": "assistant", "content": "Your notes were hard to follow. Structure your notes by separating subjective and objective findings clearly, and keep them concise."},
        {"role": "user", "content": "Your diagnosis wasn’t the best."},
        {"role": "assistant", "content": "To improve diagnostic accuracy, focus on reviewing differential diagnoses for common symptoms."},
        {"role": "user", "content": "Dr. Renheren needs to take initiative."},
        {"role": "assistant", "content": "Dr. Renheren needs to take initiative by volunteering for at least one procedure or patient handoff per shift."},
        {"role": "user", "content": "You should be more confident."},
        {"role": "assistant", "content": "During patient discussions, present your diagnosis first and explain your reasoning confidently."},
        {"role": "user", "content": "Dr. Quelcanne needs to work on her communication skills."},
        {"role": "assistant", "content": "To improve communication, Dr. Quelcanne should start by summarizing the patient’s concerns clearly during handovers."},
        {"role": "user", "content": "The patients seem to like Dr. Algun."},
        {"role": "assistant", "content": "Patients appreciate Dr. Algun's empathy; he could strengthen these interactions further by maintaining eye contact and using the patients' name during interactions."},
    ]

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
    rewritten_feedback = rewrite_feedback(texts)
    print("Rewritten Feedback:")
    for text, output in zip(texts, rewritten_feedback):
        print(f"Original Feedback: {text}\nRewritten Feedback: {output}\n\n")

