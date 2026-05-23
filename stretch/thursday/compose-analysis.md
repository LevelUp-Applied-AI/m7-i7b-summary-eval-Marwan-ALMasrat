# Summarize-then-QA — Trade-Off Analysis Memo

## 1. Test Set Design

- Total questions: 20
- Article types chosen: All 20 questions were drawn from articles exceeding 400 words (range: 413–676 words), ensuring that at least some articles exceed the QA model's 512-token limit and trigger the chunking logic in Strategy A.
- Question types:
  - Factual / numeric (age, year, count): Q01, Q08, Q09, Q10, Q12, Q18, Q19 — 7 questions
  - Entity-attribution (who, which company/person): Q02, Q05, Q07, Q14, Q16, Q20 — 6 questions
  - Location: Q03, Q06 — 2 questions
  - Event / award: Q04, Q11, Q13, Q15, Q17 — 5 questions
- Why these choices: Articles were selected from diverse categories (film, technology, entertainment, crime) to test generalization. Long articles (600+ words) were prioritized to stress-test Strategy A's chunking logic and expose Strategy B's faithfulness limits. Question types were mixed to include both top-of-document signals (e.g., who was arrested) and answers buried deeper in the article (e.g., specific quotes or statistics).

## 2. Strategy A Results — QA on the Full Article (with Chunking)

- Aggregate EM: **0.9000**; Aggregate F1: **0.9333**
- Where Strategy A wins:
  - **Q10** (how many hijacking cases since 2006 — answer: 3200): The answer appears mid-article. Strategy A's chunking preserved the evidence window containing the exact number, while Strategy B's summary omitted this statistic entirely.
  - **Q13** (name of the casino attacked): The answer "Casino Royale" appears in the second paragraph. Chunking kept this context intact and the QA model extracted it precisely.
  - **Q17** (which film referenced napalm): The answer "Apocalypse Now" is embedded deep in the article opening sentence. Full-article QA scored EM=1 here.
- Where Strategy A loses:
  - **Q15** (what song did Beyoncé sing): The article contains multiple entity mentions (Beyoncé, Etta James, Cadillac Records) in close proximity, causing the QA model to occasionally return "Etta James" instead of "At Last" due to distractor entities in the same chunk.
  - **Q20** (what NBC sitcom): The answer appears near the end of a long article; in some chunk splits the relevant sentence straddled a boundary, reducing confidence.

## 3. Strategy B Results — QA on the Summary

- Aggregate EM: **0.6500**; Aggregate F1: **0.6500**
- Where Strategy B wins:
  - **Q01** (how old was Polanski when arrested): This is a top-of-document fact that summarizers reliably preserve. The summary retained "76" and QA extracted it correctly.
  - **Q02** (which country was Polanski arrested in): High-level geographic fact that always appears in the lead sentence — summaries consistently include it.
  - **Q14** (who serenaded the Obamas): A prominent headline-level fact retained in every summary variant.
- Where Strategy B loses:
  - **Q10** (how many hijacking cases): The specific statistic "3200" was dropped by the summarizer as a supporting detail, causing Strategy B to return an empty or wrong answer.
  - **Q09** (since what year): The year "2006" appeared in a subordinate clause that the summarizer consistently removed, resulting in EM=0 for Strategy B on this question.

## 4. Faithfulness Analysis (Strategy B)

**Example — Q09 / Q10 (NEWS_0007)**

> **Article (excerpt):** "Since 2006, nearly 3,200 account hijacking cases have been reported to the Internet Crime Complaint Center, a partnership between the FBI, the National White Collar Crime Center and the Bureau of Justice Assistance."

> **Summary (Strategy B input):** "Cybercriminals are increasingly targeting social networking sites, stealing personal information from millions of users, according to the FBI."

> **Question (Q10):** How many account hijacking cases have been reported since 2006?
> **Strategy B prediction:** "millions" *(wrong)*
> **Gold:** 3200

> **What was lost in summarization:** The summarizer compressed the statistical evidence ("3,200 cases since 2006") into the vaguer phrase "millions of users," discarding the precise number and the year anchor entirely. The QA model had no choice but to latch onto the only numeric-like token remaining in the summary — "millions" — producing a confident but incorrect answer.

## 5. Recommendation

| Use Strategy A when… | Use Strategy B when… |
|---|---|
| Article > 500 tokens AND question targets a specific statistic, date, name, or fact that may appear anywhere in the document | Article > 1,500 tokens AND question is high-level or top-of-document (e.g., who is the subject, what event occurred) |
| Answer location is unknown or answer is in the middle/end of the article | Latency or compute budget is the primary constraint and EM loss of ~25% is acceptable |

**Justification:** Strategy A achieved EM=0.90 vs. Strategy B's EM=0.65 — a 25-point gap driven almost entirely by summarization-induced information loss on numeric and detail-heavy questions. Strategy B is viable only when the question targets information prominent enough to survive abstractive compression (top-of-document entities and events). For any question requiring precise figures, dates, or mid-document evidence, the faithfulness cost of summarization outweighs its compute savings.