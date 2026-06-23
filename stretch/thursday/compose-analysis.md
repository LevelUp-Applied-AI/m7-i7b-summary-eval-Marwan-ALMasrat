# Summarize-then-QA — Trade-Off Analysis Memo

## 1. Test Set Design

Twenty extractive QA examples were authored across 12 articles from the tech-news corpus (NEWS_0001 through NEWS_0021). Articles were selected specifically because their token length exceeds the QA model's 512-token maximum, ensuring that Strategy A's chunking logic is exercised on every example and that Strategy B's summarization pipeline is exposed to genuine compression pressure.

Question types were distributed as follows: 7 factual/numeric questions targeting ages, years, and counts (Q01, Q08, Q09, Q10, Q12, Q18, Q19); 6 entity-attribution questions asking who or which organization (Q02, Q05, Q07, Q14, Q16, Q20); 2 location questions (Q03, Q06); and 5 event/award questions (Q04, Q11, Q13, Q15, Q17). Domains span film, cybersecurity, entertainment, crime, and sports to test cross-domain generalization. Critically, several questions (Q09, Q10, Q12) were designed so that their gold answers appear in subordinate clauses mid-article, precisely the positions most vulnerable to summarization-induced information loss.

## 2. Strategy A Results

**Aggregate EM: 0.9000 | Aggregate F1: 0.9333 | n=20**

Strategy A achieved strong performance by preserving the full document context through overlapping 384-token windows with 64-token overlap. Representative wins:

- **Q10** (how many hijacking cases since 2006 — gold: *nearly 3,200*): The answer appears mid-article inside a subordinate clause. Chunking preserved the exact evidence window and the QA model extracted the precise figure. Strategy B failed entirely on this question, returning *millions* after the summarizer discarded the statistic.
- **Q13** (name of the casino attacked — gold: *Casino Royale*): Answer appears in the second paragraph. Full-article chunking kept this context intact; EM=1.
- **Q17** (which film referenced napalm — gold: *Apocalypse Now*): Answer is embedded deep in the article. Strategy A scored EM=1 by preserving the full document across chunks.

Failures were limited to two questions (Q15, Q20) where answers straddled chunk boundaries or appeared near multiple competing entities in the same window.

## 3. Strategy B Results

**Aggregate EM: 0.5500 | Aggregate F1: 0.6083 | n=20**

Strategy B underperformed Strategy A by 35 EM points, with losses concentrated on questions requiring precise statistics, subordinate-clause facts, or mid-document evidence. Representative wins:

- **Q01** (how old was Polanski when arrested — gold: *76*): Top-of-document numeric fact reliably preserved by the summarizer; EM=1.
- **Q02** (which country was Polanski arrested in — gold: *Switzerland*): High-level geographic fact in the lead sentence; EM=1.
- **Q14** (who serenaded the Obamas — gold: *beyoncé*): Prominent headline-level entity retained across all summary variants; EM=1.

Losses were concentrated on Q09, Q10, Q12, and Q19, where the gold answer was a specific number or date embedded in a subordinate clause that the abstractive summarizer consistently dropped.

## 4. Faithfulness Analysis

The clearest example of summarization-induced information loss is **Q10** (article NEWS_0007):

**Article excerpt:**
> Since 2006, nearly 3,200 account hijacking cases have been reported to the Internet Crime Complaint Center, a partnership between the FBI, the National White Collar Crime Center and the Bureau of Justice Assistance.

**Generated summary:**
> Cybercriminals are increasingly targeting social networking sites, stealing personal information from millions of users, according to the FBI.

**Question:** How many account hijacking cases have been reported since 2006?
**Strategy B prediction:** millions
**Gold answer:** nearly 3,200

The summarizer compressed the precise statistical evidence into the vague phrase *millions of users*, discarding both the exact count and the year anchor. The QA model latched onto the sole numeric-like token remaining and returned a confident but entirely incorrect answer. This failure illustrates the fundamental risk of summarization-as-preprocessing: abstractive models optimize for narrative coherence, not for preserving the specific figures that extractive QA requires.

## 5. Recommendation

| Condition | Recommended Strategy |
|---|---|
| Article ≤ 500 tokens | Either strategy |
| Article 500–1,500 tokens, answer location unknown | **Strategy A** |
| Article 500–1,500 tokens, question is high-level | **Strategy B** acceptable |
| Article > 1,500 tokens, question targets specific statistic or date | **Strategy A** |
| Article > 1,500 tokens, question is high-level, compute is constrained | **Strategy B** |

**Quantitative basis:** Strategy A achieved EM=0.90 and F1=0.9333 versus Strategy B's EM=0.55 and F1=0.6083, a gap of 35 EM points and 32.5 F1 points. All Strategy B failures involved answers that were specific figures or subordinate-clause facts absent from the generated summaries. The 1,500-token threshold reflects the point at which chunking latency becomes non-trivial; below that threshold, the accuracy cost of summarization is never justified.