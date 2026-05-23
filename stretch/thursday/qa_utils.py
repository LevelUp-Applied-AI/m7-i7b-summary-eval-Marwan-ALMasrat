<<<<<<< Updated upstream
"""
qa_utils.py — QA pipeline utilities for stretch/thursday/pipeline_compose.py
Provides: get_qa_model_name, build_qa_pipeline, predict_one,
          normalize_answer, exact_match, token_f1
"""

import re
import string
from collections import Counter

=======
import re
import string
from collections import Counter
>>>>>>> Stashed changes
from transformers import pipeline


def get_qa_model_name() -> str:
<<<<<<< Updated upstream
    """Return the QA model name."""
=======
>>>>>>> Stashed changes
    return "deepset/roberta-base-squad2"


def build_qa_pipeline(model_name: str):
<<<<<<< Updated upstream
    """Build and return a Hugging Face QA pipeline."""
=======
>>>>>>> Stashed changes
    return pipeline("question-answering", model=model_name)


def predict_one(qa, question: str, context: str) -> str:
<<<<<<< Updated upstream
    """
    Run a single QA prediction.
    Returns the answer string.
    """
=======
>>>>>>> Stashed changes
    result = qa(question=question, context=context)
    return result["answer"]


def normalize_answer(text: str) -> str:
<<<<<<< Updated upstream
    """
    Lowercase, remove punctuation, articles, and extra whitespace.
    Standard SQuAD normalization.
    """
    text = text.lower()
    # Remove articles
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    # Collapse whitespace
=======
    text = text.lower()
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
>>>>>>> Stashed changes
    text = " ".join(text.split())
    return text


def exact_match(pred: str, gold: str) -> int:
<<<<<<< Updated upstream
    """
    Return 1 if normalized prediction == normalized gold, else 0.
    """
=======
>>>>>>> Stashed changes
    return int(normalize_answer(pred) == normalize_answer(gold))


def token_f1(pred: str, gold: str) -> float:
<<<<<<< Updated upstream
    """
    Compute token-level F1 between prediction and gold answer.
    Standard SQuAD F1 metric.
    """
    pred_tokens = normalize_answer(pred).split()
    gold_tokens = normalize_answer(gold).split()

    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_common = sum(common.values())

    if num_common == 0:
        return 0.0

    precision = num_common / len(pred_tokens)
    recall = num_common / len(gold_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1
=======
    pred_tokens = normalize_answer(pred).split()
    gold_tokens = normalize_answer(gold).split()
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_common = sum(common.values())
    if num_common == 0:
        return 0.0
    precision = num_common / len(pred_tokens)
    recall = num_common / len(gold_tokens)
    return (2 * precision * recall) / (precision + recall)
>>>>>>> Stashed changes
