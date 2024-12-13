import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch.nn.functional as F

def get_actionability_score(texts, max_new_tokens=5, batch_size=4):
    """
    Get the actionability score for a batch of texts using a pre-trained language model.

    Args:
        texts (list of str): A list of input texts to score for actionability.
        max_new_tokens (int): The maximum number of tokens to generate for each text.
        batch_size (int): The number of texts to process in each batch.

    Returns:
        float: The average actionability score for the batch of texts.
        list of float: The actionability score for each text.
        list of str: The generated responses for each text.
    """
    # Load the model and tokenizer
    model_id = "meta-llama/Llama-3.2-3B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left")
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")

    # Define the conversation template
    base_messages = [
        {"role": "system", "content": "You are a helpful assistant that classifies statements as actionable or not actionable. \"Actionable\" statements are statements that imply a specific task, action, or strategy for improvement. Vague or general instructions that do not imply a specific task, action or strategy for improvement are not actionable. The user will submit statements; you respond to each with either \"Actionable\" or \"Not Actionable\", followed by a clear summary of the implied specific task, action, or strategy for improvement, if the statement is actionable. If not, then provide a reason why the statement is not actionable."},
        {"role": "user", "content": "You need to spend more time practicing your surgical technique."},
        {"role": "assistant", "content": "Actionable. Action: Spend more time practicing surgical technique."},
        {"role": "user", "content": "There are things you could do better."},
        {"role": "assistant", "content": "Not Actionable. Reason: Statement does not specify what could be done better."},
        {"role": "user", "content": "You're doing terribly. Reread your textbook to fill gaps in your knowledge."},
        {"role": "assistant", "content": "Actionable. Action: Reread textbook to fill gaps in knowledge."}
    ]

    # Initialize accumulators
    actionable_probs = []
    new_generated_texts = []

    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]

        # Prepare inputs for each text in the batch
        batch_messages = []
        for text in batch_texts:
            messages = base_messages + [{"role": "user", "content": text}]
            batch_messages.append(messages)

        # Tokenize the messages using chat template
        tokenizer.pad_token = tokenizer.eos_token
        model_inputs = tokenizer.apply_chat_template(
            batch_messages,
            add_generation_prompt=True,
            return_tensors="pt",
            padding=True,
            return_dict=True
        ).to("cuda")

        # Run model to get logits and generated output
        with torch.no_grad():
            outputs = model.generate(
                **model_inputs,
                max_new_tokens=max_new_tokens,
                pad_token_id=tokenizer.pad_token_id,
                return_dict_in_generate=True,
                output_scores=True
            )
            generated_token_ids = outputs.sequences

        # Extract generated text
        for j, text in enumerate(batch_texts):
            input_ids = model_inputs['input_ids'][j]
            generated_ids = generated_token_ids[j]

            # The new response starts after the input
            new_token_ids = generated_ids[len(input_ids):]
            new_response = tokenizer.decode(new_token_ids, skip_special_tokens=True).strip()
            new_generated_texts.append(new_response)

        logits = outputs.scores[0]

        # Tokenize the labels "actionable" and "not actionable" to compare logits
        labels = ["Actionable.", "Not Actionable."]
        label_ids = [tokenizer.encode(label, add_special_tokens=False)[0] for label in labels]

        # Extract logits for the target labels and apply softmax to get probabilities
        label_logits = logits[:, label_ids]
        probabilities = F.softmax(label_logits, dim=-1)

        # Get the probability for "actionable" for each text in the batch
        actionable_probs.extend(probabilities[:, 0].tolist())

    # Calculate average actionability score
    average_score = sum(actionable_probs) / len(actionable_probs)

    return average_score, actionable_probs, new_generated_texts

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

    # Get actionability score for each text
    avg_score, scores, outputs = get_actionability_score(texts)
    print("Actionability Scores:")
    for text, score, output in zip(texts, scores, outputs):
        print(f"Text: {text}\nActionability score: {score:.5f}\nModel Output: {output.split('\n')[-1]}\n\n")
    print(f"Average Actionability Score: {avg_score:.2f}\n\n")
