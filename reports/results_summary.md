# Results summary (auto-generated from measured data)

Quality tolerance: 5 points. Pricing source: https://groq.com/pricing ; https://ai.google.dev/gemini-api/docs/pricing (checked 2026-11-15). Actual expenditure recorded: $0.0.

## Model-level

| tier   |   mean_quality |   median_quality |   cost_per_task_usd |   total_cost_usd |   mean_latency_ms |   p95_latency_ms |
|:-------|---------------:|-----------------:|--------------------:|-----------------:|------------------:|-----------------:|
| cheap  |        89.8833 |             91.5 |              0.0003 |           0.0187 |           1498.87 |          2588.8  |
| medium |        93.6667 |            100   |              0.0009 |           0.0561 |           1995.18 |          3950.67 |
| strong |        94.0667 |             97.5 |              0.0005 |           0.032  |           2118.52 |          3406.4  |

## Mean quality by category

| category        |   cheap |   medium |   strong | best_tier   |
|:----------------|--------:|---------:|---------:|:------------|
| data_extraction |    88.7 |     90.1 |     89   | medium      |
| email_draft     |    95.2 |     97.9 |     97.1 | medium      |
| meeting_summary |    91.5 |     91.2 |     97.4 | strong      |
| research_brief  |    84.2 |     94.4 |     92.8 | medium      |
| slide_outline   |    89.8 |     94.8 |     94.1 | medium      |

## Mean quality by difficulty

| difficulty   |   cheap |   medium |   strong |
|:-------------|--------:|---------:|---------:|
| easy         |    92.7 |     94.2 |     93.3 |
| hard         |    86.7 |     92.8 |     92.8 |
| medium       |    90.2 |     94.1 |     96.1 |

## Router strategies

|                  |   mean_quality |   median_quality |   cost_per_task_usd |   total_cost_usd |   mean_latency_ms |   median_latency_ms |   p95_latency_ms |   quality_failures |   pct_cheap |   pct_medium |   pct_strong |   cost_saving_vs_strongest_pct |   quality_delta_vs_strongest |   escalated_pct |
|:-----------------|---------------:|-----------------:|--------------------:|-----------------:|------------------:|--------------------:|-----------------:|-------------------:|------------:|-------------:|-------------:|-------------------------------:|-----------------------------:|----------------:|
| always_cheap     |        89.8833 |             91.5 |              0.0003 |           0.0187 |           1498.87 |             1474.04 |          2588.8  |                 26 |    100      |       0      |       0      |                        41.4056 |                      -4.1833 |        nan      |
| always_strong    |        94.0667 |             97.5 |              0.0005 |           0.032  |           2118.52 |             1974.52 |          3406.4  |                  0 |      0      |       0      |     100      |                         0      |                       0      |        nan      |
| rule_router      |        94.1667 |            100   |              0.0007 |           0.0425 |           1924.3  |             1727.82 |          3562.21 |                 10 |     20      |      43.3333 |      36.6667 |                       -32.9269 |                       0.1    |        nan      |
| ml_router        |        93.8    |             98.5 |              0.0007 |           0.0397 |           1921.27 |             1668.78 |          3953.79 |                 10 |     43.3333 |      21.6667 |      35      |                       -24.0022 |                      -0.2667 |        nan      |
| ml_plus_fallback |        93.8167 |            100   |              0.0006 |           0.0334 |           1894.6  |             1702.6  |          3358.78 |                  5 |      6.6667 |      36.6667 |      56.6667 |                        -4.4798 |                      -0.25   |         58.3333 |

## Questions

1. **Best overall:** strong (mean quality 94.1).
2. **Best model by category:** data_extraction: medium; email_draft: medium; meeting_summary: strong; research_brief: medium; slide_outline: medium.
3. **Quality vs cost:** cheap: 89.9 @ $0.00031/task; medium: 93.7 @ $0.00093/task; strong: 94.1 @ $0.00053/task.
4. **Can a simpler model suffice?** Share of tasks within 5 pts of the strongest model: cheap: 57%, medium: 75%, strong: 100%.
5. **Does the ML router learn the pattern?** Routing accuracy vs best-value label (grouped OOF): 0.60 (majority-class baseline 0.42). n is small; treat as indicative.
6-8. **ML+fallback vs always-strongest:** quality 93.8 vs 94.1 (delta -0.25); cost/task saving -4.5%; quality failures 5. ML router alone: delta -0.27, saving -24.0%, failures 10.
9. **Fallback:** escalated 58% of requests; quality +0.02; extra cost $-0.00010/task; extra latency -27 ms; failures 10 -> 5.
10. **Where it fails:** see reports/error_analysis.md.
