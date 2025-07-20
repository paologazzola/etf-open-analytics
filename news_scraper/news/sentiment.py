import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Load FinBERT model and tokenizer once
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

# FinBERT label mapping
label_map = {
    0: "negative",
    1: "neutral",
    2: "positive"
}

def _classify(text: str) -> tuple[str, float]:
    """
    Classifies sentiment for a single text.
    Returns:
    - label (str): predicted label
    - score (float): confidence score
    """
    if not text:
        return "neutral", 0.0

    inputs = tokenizer(text[:512], return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)

    scores = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
    label_index = torch.argmax(scores).item()
    label = label_map[label_index]
    score = scores[label_index].item()
    return label, score

def analyze_sentiment(description: str, content: str) -> tuple[str, float, float]:
    """
    Analyze sentiment based on both description and content fields.

    Returns:
    - final_label: combined label (if both same, use that; otherwise pick highest score)
    - final_score: average of scores
    - weight: adjusted score (0.0 if both are neutral or empty, otherwise average score)
    """
    label_desc, score_desc = _classify(description)
    label_cont, score_cont = _classify(content)

    # Determine the final label
    if label_desc == label_cont:
        final_label = label_desc
    else:
        final_label = label_desc if score_desc > score_cont else label_cont

    # Average only non-zero scores
    valid_scores = [s for s in [score_desc, score_cont] if s > 0.0]
    final_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

    weight = final_score if final_label != "neutral" else 0.0

    return final_label, final_score, weight
