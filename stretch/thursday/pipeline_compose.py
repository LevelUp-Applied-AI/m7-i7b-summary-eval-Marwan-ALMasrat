"""
Module 7 Week B — Thursday Stretch (Honors): Summarize-then-QA.
"""

import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import summarize  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import qa_utils  # noqa: E402
except ImportError as e:
    raise ImportError(
        "qa_utils.py not found. Copy build_qa_pipeline, predict_one, exact_match, "
        "token_f1, normalize_answer, and get_qa_model_name from your Lab 7B lab.py "
        "into stretch/thursday/qa_utils.py."
    ) from e


def qa_full_article(qa, question: str, article: str, max_chunk: int = 384) -> str:
    """
    Run QA over the full article, chunking with overlap when it exceeds max_chunk tokens.
    Returns the answer span from the highest-scoring chunk.
    """
    # Tokenize using the QA pipeline's tokenizer for an accurate token count
    tokenizer = qa.tokenizer
    tokens = tokenizer.encode(article, add_special_tokens=False)

    # If the article fits within max_chunk, run QA directly
    if len(tokens) <= max_chunk:
        result = qa(question=question, context=article)
        return result["answer"]

    # Otherwise, split into overlapping windows
    overlap = 64
    stride = max_chunk - overlap

    best_answer = ""
    best_score = -float("inf")

    start = 0
    while start < len(tokens):
        end = min(start + max_chunk, len(tokens))
        chunk_tokens = tokens[start:end]

        # Decode the chunk back to text
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)

        result = qa(question=question, context=chunk_text)
        score = result.get("score", 0.0)

        if score > best_score:
            best_score = score
            best_answer = result["answer"]

        if end == len(tokens):
            break
        start += stride

    return best_answer


def qa_via_summary(qa, summ, question: str, article: str, max_summary_length: int = 120) -> str:
    """
    Summarize the article first, then run QA on the summary.
    Returns the answer string.
    """
    # Step 1: Summarize the article using Integration 7B's summarize_one
    summary = summarize.summarize_one(
    summ,
    article,
    max_length=max_summary_length,
)

    # Step 2: Run QA on the summary
    answer = qa_utils.predict_one(qa, question, summary)

    return answer


def evaluate_strategies(qa, summ, test_set: pd.DataFrame, articles_df: pd.DataFrame) -> dict:
    """
    Run both strategies on every row of the test set; compute per-strategy EM/F1.
    """
    predictions = []

    for _, row in test_set.iterrows():
        qid = str(row["qid"])
        question = str(row["question"])
        article_id = row["article_id"]
        gold_answer = str(row["gold_answer"])

        # Look up the article text
        article_rows = articles_df[articles_df["article_id"] == article_id]
        if article_rows.empty:
            # Try matching by index or id column as fallback
            article_rows = articles_df[articles_df.index == article_id]

        if article_rows.empty:
            print(f"Warning: article_id={article_id} not found, skipping qid={qid}")
            continue

        article_text = str(article_rows.iloc[0]["text"])

        # Strategy A: QA on the full article (with chunking)
        pred_a = qa_full_article(qa, question, article_text)

        # Strategy B: Summarize-then-QA
        pred_b = qa_via_summary(qa, summ, question, article_text)

        # Compute EM and F1 for both strategies
        em_a = qa_utils.exact_match(pred_a, gold_answer)
        f1_a = qa_utils.token_f1(pred_a, gold_answer)
        em_b = qa_utils.exact_match(pred_b, gold_answer)
        f1_b = qa_utils.token_f1(pred_b, gold_answer)

        predictions.append({
            "qid": qid,
            "question": question,
            "strategy_a_pred": pred_a,
            "strategy_b_pred": pred_b,
            "gold_answer": gold_answer,
            "strategy_a_em": em_a,
            "strategy_a_f1": f1_a,
            "strategy_b_em": em_b,
            "strategy_b_f1": f1_b,
        })

    n = len(predictions)

    if n == 0:
        return {
            "strategy_a": {"em": 0.0, "f1": 0.0, "n": 0},
            "strategy_b": {"em": 0.0, "f1": 0.0, "n": 0},
            "predictions": [],
        }

    avg_em_a = sum(p["strategy_a_em"] for p in predictions) / n
    avg_f1_a = sum(p["strategy_a_f1"] for p in predictions) / n
    avg_em_b = sum(p["strategy_b_em"] for p in predictions) / n
    avg_f1_b = sum(p["strategy_b_f1"] for p in predictions) / n

    return {
        "strategy_a": {"em": avg_em_a, "f1": avg_f1_a, "n": n},
        "strategy_b": {"em": avg_em_b, "f1": avg_f1_b, "n": n},
        "predictions": predictions,
    }


def main() -> None:
    """Load test set + articles, build pipelines, run both strategies, write artifacts."""
    test_set = pd.read_csv("stretch/thursday/qa_test_set.csv")
    articles_df = pd.read_csv("data/tech_news_articles.csv")

    qa = qa_utils.build_qa_pipeline(qa_utils.get_qa_model_name())
    summ = summarize.build_summarizer(summarize.get_summarizer_model_name())

    result = evaluate_strategies(qa, summ, test_set, articles_df)

    pred_df = pd.DataFrame(result["predictions"])
    pred_df.to_csv("stretch/thursday/compose_predictions.csv", index=False)

    metrics = {
        "strategy_a": result["strategy_a"],
        "strategy_b": result["strategy_b"],
        "qa_model": qa_utils.get_qa_model_name(),
        "summarizer_model": summarize.get_summarizer_model_name(),
    }
    with open("stretch/thursday/compose_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Strategy A (full-article QA) — EM={result['strategy_a']['em']:.4f}, F1={result['strategy_a']['f1']:.4f}")
    print(f"Strategy B (summarize-then-QA) — EM={result['strategy_b']['em']:.4f}, F1={result['strategy_b']['f1']:.4f}")


if __name__ == "__main__":
    main()