# Module 7 Integrated Evaluation Report — Fine-Tuning vs. Pre-Trained Inference

> The Module 7 deliverable. Synthesizes Lab 7A (fine-tuning), Integration 7A (domain shift), Lab 7B (QA), and Integration 7B (summarization).

---

## 1. Comparison Table

| Task | Approach | Model | Training cost | Inference cost | Quality metric | Value |
|---|---|---|---|---|---|---|
| Sentiment classification (Lab 7A) | Fine-tuning | distilbert-base-uncased | ~56 min CPU + 5,977 labels | ~50 ms / example | Macro-F1 | 0.6326 |
| Domain transfer (Integration 7A) | Fine-tuned model out-of-domain | (same) | already trained | ~50 ms / example | Domain-shift judgment | Severely degraded — median confidence 0.584; 53.6% of predictions below 0.6 |
| Extractive QA (Lab 7B) | Pre-trained inference | distilbert-base-cased-distilled-squad | 0 | ~50 ms / example | EM / token-F1 | EM = 0.344 / F1 = 0.461 |
| Summarization (Integration 7B) | Pre-trained inference | sshleifer/distilbart-cnn-6-6 | 0 | ~3 sec / example | ROUGE-1 / 2 / L F1 | 0.3683 / 0.1572 / 0.2670 |

## 2. Findings

- **Fine-tuning works within its domain but collapses under domain shift.** The DistilBERT classifier reached Macro-F1 = 0.6326 on in-domain app reviews, but on tech news articles the median confidence dropped to 0.584 with 53.6% of predictions falling below 0.6 — indicating the model learned consumer complaint vocabulary, not general sentiment reasoning.
- **Pre-trained QA achieves moderate accuracy with a meaningful EM-F1 gap.** EM = 0.344 vs. F1 = 0.461 on 1,000 tech-news examples reveals the model frequently finds the right span neighborhood but returns slightly misaligned boundaries — a known weakness on long articles without chunking.
- **Pre-trained summarization captures topics but not precise phrasing.** ROUGE-1 = 0.3683 reflects reasonable lexical overlap, but ROUGE-2 = 0.1572 reveals that bigram-level precision drops sharply — the model generates domain-generic language rather than the terse, entity-precise style of CNN editorial summaries.
- **Domain shift is the central failure mode across all tasks.** Every model was evaluated on a different distribution than its training corpus. The fine-tuned classifier suffered the most visibly; the pre-trained models generalized better but still show measurably sub-optimal results — EM = 0.344 and ROUGE-2 = 0.1572 both confirm this ceiling.
- **No single approach dominates.** Fine-tuning delivers higher within-domain precision but is brittle to distribution shift. Pre-trained inference generalizes more gracefully but achieves a lower quality ceiling. The right choice depends on labeled data availability and the production cost of domain-shift errors.

## 3. Faithfulness Check

### Example A — High ROUGE (NEWS_0118)

> **Article excerpt:** "John Mayer says he has a granuloma next to his vocal cords. Granuloma is a small area of tissue inflammation. Mayer's soon-to-be-released album 'Born and Raised' will be delayed."
>
> **Predicted summary:** "John Mayer has suffered from a granuloma, a small area of tissue inflammation in the lungs. The singer and songwriter said he had undergone months of monitoring. His soon-to-be-released album 'Born and Raised' also will be delayed."
>
> **ROUGE-1:** 0.6575; **ROUGE-2:** 0.4507; **ROUGE-L:** 0.6027
>
> **Faithful?** Partially. The summary correctly reports the granuloma, the album delay, and the medical definition — but introduces "in the lungs" which does not appear in the article (the granuloma is next to the vocal cords). ROUGE scored this highly due to strong n-gram overlap but completely missed the hallucinated anatomical detail. This is the canonical high-ROUGE unfaithful case.

### Example B — Mid ROUGE (NEWS_0061)

> **Article excerpt:** "On 'Follow Friday,' CNN.com recommends Twitter feeds on a news topic. This week's topic: The U.S. debate over health care. SusannahFox comments on health care and social media. kevinmd posts insights from his life as a physician."
>
> **Predicted summary:** "CNN.com highlights five recommended Twitter feeds about a hot topic in the news. Sen. Olympia Snowe of Maine doesn't appear to be on Twitter. PolitiFact: The health care reform debate has been nothing if not confusing."
>
> **ROUGE-1:** 0.3333; **ROUGE-2:** 0.1053; **ROUGE-L:** 0.2821
>
> **Faithful?** Mostly faithful but incomplete. The summary correctly identifies CNN.com's Twitter recommendation framing but omits the primary contributors (SusannahFox, kevinmd), replacing them with Sen. Snowe and PolitiFact — mentioned later in the article but not the main focus. ROUGE-2 = 0.1053 correctly reflects the low bigram overlap caused by this entity substitution.

### Example C — Low ROUGE (NEWS_0042)

> **Article excerpt:** "One high-profile film producer has fired hundreds of personal assistants. Naomi Campbell's treatment of her employees has landed her in court. And would you really want to answer to Simon Cowell or Al Capone?"
>
> **Predicted summary:** "New grads are looking for jobs near their college or hometowns. Indianapolis, Philadelphia and Cincinnati are the top cities for new grads. The list is based on the ranking of the top U.S. cities with the highest concentration of young adults."
>
> **ROUGE-1:** 0.1282; **ROUGE-2:** 0.0000; **ROUGE-L:** 0.0769
>
> **Faithful?** No — completely wrong content. The predicted summary describes a jobs-for-graduates article and shares zero content with the celebrity-assistant source article. ROUGE-2 = 0.0000 correctly flags this as a total failure. ROUGE identified the catastrophic mismatch but cannot explain the root cause — likely a data alignment error between article_id and article text.

## 4. Production Decision Matrix

| Scenario | Recommendation | Justification |
|---|---|---|
| Real-time app store review triage dashboard for a product team | **Fine-tuning** | The fine-tuned DistilBERT reached Macro-F1 = 0.6326 on in-domain app reviews; pre-trained models have no sentiment training signal for this task and would produce unreliable results. |
| Daily tech / entertainment news summary digest for an internal newsroom | **Pre-trained inference** | distilbart-cnn-6-6 achieves ROUGE-1 = 0.3683 at zero training cost and ~3 sec/article; the quality is sufficient for a low-stakes internal digest and no labeled summarization dataset exists to justify fine-tuning. |
| Domain-expert QA on legal contracts | **Fine-tuning** | Pre-trained distilbert-squad achieved only EM = 0.344 on out-of-domain news text; legal contracts are even further from the SQuAD training distribution, making fine-tuning on labeled contract QA pairs a prerequisite for reliable production extraction. |

## 5. What You Would Do Differently

If a labeled summarization dataset were available for the tech and entertainment news domain, the highest-leverage investment would be fine-tuning distilbart-cnn-6-6 on domain-matched article–summary pairs. The current ROUGE-2 = 0.1572 reveals that the model struggles with bigram-level precision — it captures the right topics but misses exact phrasing, suggesting it generates plausible but domain-generic language rather than the terse, entity-precise style of CNN editorial summaries. Fine-tuning on even 2,000–3,000 labeled pairs from the same distribution would likely push ROUGE-2 above 0.22–0.25, the range where downstream consumers begin reporting qualitatively better summaries in human evaluations. Beyond ROUGE, I would also add an NLI-based faithfulness filter as a post-processing step to catch hallucinated spans like "in the lungs" in Example A — a problem ROUGE cannot detect but a calibrated entailment model can flag reliably at inference time.

## 6. Limits of the Evaluation

The most important limit of these numbers is that ROUGE does not measure faithfulness and EM/F1 do not measure calibration — both gaps matter acutely for the production scenarios in Section 4. The faithfulness check exposed a high-ROUGE summary (ROUGE-1 = 0.6575) that introduced a factual error invisible to ROUGE, meaning any system that gates on ROUGE alone will pass unfaithful summaries at a rate that scales with corpus size — an editorial liability for the newsroom digest scenario. Similarly, EM = 0.344 says nothing about how confident the model is when it is wrong: a model that is 34% accurate and uniformly 95% confident is far more dangerous than one that correctly expresses uncertainty, because downstream consumers cannot distinguish reliable from unreliable predictions. These evaluations were also conducted at single-request latency on CPU with no concurrency; throughput under production load was not measured and cannot be inferred from these numbers.