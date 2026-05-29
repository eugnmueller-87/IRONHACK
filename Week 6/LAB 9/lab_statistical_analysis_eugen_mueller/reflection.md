# Reflection — LAB 9: In God We Trust, Everyone Else Bring the Data

## What surprised you about the results?

The sheer magnitude of Email's dominance was striking — a CPA of $0.77 vs $52 for Display isn't a marginal difference, it's a different universe. Cohen's d of -11.72 between Email and Display is off the charts (anything above 0.8 is "large" — this is 14x that threshold). In a real business context, this would be screaming "you have massively under-invested in Email."

The second surprise: after applying FDR correction, *nothing got knocked out*. Every single one of our 14 CPA comparisons and all 21 conversion rate comparisons survived. With 90 days of data and large true effect sizes, the signal was just too strong to be noise. In real-world analyses this often goes the other way — many apparent differences evaporate under correction.

## How did multiple comparisons correction change your conclusions?

Technically, it didn't change the conclusions here — the differences were too large. But it *validated* that we weren't fooling ourselves. Before correction, you might wonder: "Are some of these 35 significant results just Type I errors?" After FDR, the answer is definitively no. The adjusted p-values barely moved because the raw p-values were so small (many below 1e-50).

The more important lesson is in what *would* have happened with weaker data: if we'd only had 14 days of data per channel instead of 90, many of those significant results would have evaporated under Bonferroni — and the FDR survivors would have been the ones worth trusting.

## What are the limitations of this analysis?

1. **Attribution is flat.** We're doing last-click style channel comparisons. Email converting well doesn't mean Email is the *reason* customers converted — they may have clicked a Social ad first. A proper multi-touch model would redistribute credit.

2. **CPA comparisons assume channels compete for the same customer.** They don't. Email hits warm leads. Display hits cold ones. Comparing their CPAs directly is a bit like comparing apples to aircraft carriers.

3. **The 'base CPA' in power simulations was Paid Search only.** Using a single channel's variance as a universal standard is a simplification. Display and Email have very different CPA distributions.

4. **Synthetic data.** The dataset was generated with fixed channel parameters. Real data has hidden correlations (Black Friday spikes all channels, a product goes viral, a competitor's ad goes down). Our simulated noise is clean Gaussian — reality is messier.

5. **No budget constraint modeling.** The recommended reallocation assumes Email and SEO can absorb more spend. In reality, Email has diminishing returns once you exhaust your list, and SEO investment takes 3-6 months to yield.

## How would you communicate these findings to non-technical stakeholders?

Skip the p-values entirely in the exec summary. Replace with:

> "We can say with 99.99% confidence that Email delivers cheaper customers than Display — this isn't luck or a measurement error. Over 90 days, Email consistently cost us $0.77 per customer while Display cost $52. That's a 67x difference in efficiency."

Use analogies for statistical power:

> "With our current data, if a channel really is 15% more efficient than another, we'd catch that 80% of the time. Think of it like a quality control check that catches 4 in 5 defects — good, but we'd want to run the line longer before making permanent capital decisions."

For multiple comparisons correction:

> "When you flip a coin 20 times, you might get 4 heads in a row — not because the coin is rigged, just because. We ran 36 statistical tests, so we expected to see ~2 flukes. We applied a filter (Benjamini-Hochberg) that removes those flukes. Everything we're recommending passed that filter."
