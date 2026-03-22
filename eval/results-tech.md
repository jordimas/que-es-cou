# Tech Topic Filter — Eval Results

Dataset: 266 world + 234 catalunya articles (500 total) — run 2026-03-22

Inference providers: Anthropic API (Claude), Groq (all other models).

| Metric    | claude-sonnet-4-6 | gpt-oss-120b | llama-4-scout-17b | qwen3-32b | llama-3.3-70b-versatile | kimi-k2-instruct |
|-----------|-------------------|--------------|-------------------|-----------|-------------------------|------------------|
| F1        | 0.93              | 0.94         | 0.89              | 0.93      | 0.87                    | 0.83             |
| Precision | 0.90              | 0.92         | 0.92              | 0.91      | 0.92                    | 0.95             |
| Recall    | 0.96              | 0.96         | 0.86              | 0.94      | 0.82                    | 0.73             |
| TP        | 240               | 241          | 216               | 235       | 206                     | 183              |
| FP        | 26                | 21           | 19                | 22        | 19                      | 9                |
| FN        | 10                | 9            | 34                | 15        | 44                      | 67               |
| Time      | 497s              | 317s         | 30s               | 486s      | 172s                    | 210s             |

gpt-oss-120b edges ahead with the best F1 (0.94) matching Claude's recall; llama-4-scout remains the fastest option (30s) at a modest quality cost.
