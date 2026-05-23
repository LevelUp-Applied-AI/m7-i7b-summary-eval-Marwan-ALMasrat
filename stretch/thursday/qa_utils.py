import re
import string
from collections import Counter
from transformers import pipeline


def get_qa_model_name() -> str:
    return "deepset/roberta-base-squad2"


def build_qa_pipeline(model_name: str):
    return pipeline("question-answering", model=model_name)


def predict_one(qa, question: str, context: str) -> str:
    result = qa(question=question, context=context)
    return result["answer"]


def normalize_answer(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = " ".join(text.split())
    return text


def exact_match(pred: str, gold: str) -> int:
    return int(normalize_answer(pred) == normalize_answer(gold))


def token_f1(pred: str, gold: str) -> float:
    pred_tokens = normalize_answer(pred).split()
    gold_tokens = normalize_answer(gold).split()
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_common = sum(common.values())
    if num_common == 0:
        return 0.0
    precision = num_common / len(pred_tokens)
    recall = num_common / len(gold_tokens)
    return (2 * precision * recall) / (precision + recall)