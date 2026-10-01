# lolllm — Living Off The Land: Large Language Models

A community-driven repository of forensic artifacts, detection rules, and threat intelligence
for local LLM inference engines and cloud LLM API clients abused on endpoints.

## What is lolllm?

As large language models become commoditised, threat actors and insiders increasingly deploy
local inference runtimes (Ollama, llama.cpp, LM Studio, vLLM) directly on endpoints to:

- Bypass corporate DLP and content-filtering policies
- Run uncensored models for C2 scripting, phishing generation, and data analysis
- Exfiltrate sensitive data by piping it through a local model with no network egress
- Stage persistent AI-assisted tooling invisible to SaaS-based LLM audit logs

lolllm documents the **forensic footprint** of these tools so defenders can detect them.

## Quick Start for SOC Analysts

Download the machine-readable feeds directly:

- **JSON** — [/api/tools.json](https://lolllm.io/api/tools.json) — full structured data, one object per tool
- **CSV** — [/api/tools.csv](https://lolllm.io/api/tools.csv) — flat lookup table for SIEM ingestion (Elastic, Splunk)

## Browse Tools

See the [Tools](tools/) index for the full catalogue.

## Contribute

See [Contributing](contribute.md) to add a new tool or improve an existing entry.
