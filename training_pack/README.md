# Company Assistant Training Pack

This pack is a practical starter for a company-specific assistant:
- FAQ and service consulting
- Sales guidance and lead capture
- Future tool calling and cross-system integration

It is model-agnostic and works for local models (for example 4B/8B) or cloud models.

## 1) Folder Layout

- `prompts/` system prompt templates
- `knowledge/` structured business knowledge
- `sft/` supervised fine-tuning samples (JSONL)
- `eval/` evaluation set and checklist
- `tools/` tool schema templates for later integration
- `scripts/` lightweight data validation scripts

## 2) Minimum Start (No Fine-tune)

1. Fill files under `knowledge/` with real company info.
2. Use `prompts/system_prompt.template.txt` as system prompt.
3. Build RAG from `knowledge/` documents.
4. Run evaluation with `eval/eval_set.jsonl`.

## 3) Fine-tune Start (LoRA/SFT)

1. Fill `sft/train.jsonl` and `sft/val.jsonl`.
2. Validate format:
   - `python3 training_pack/scripts/validate_jsonl.py training_pack/sft/train.jsonl`
3. Fine-tune with your preferred stack (for example LLaMA-Factory/Unsloth/vLLM ecosystem).
4. Re-run `eval/eval_set.jsonl` and compare.

## 4) Data Rules

- Do not include private customer PII unless explicitly authorized.
- Keep prices and policy-sensitive info versioned with a date.
- Add clear refusal/transfer rules for uncertain or risky requests.

## 5) Recommended Model Progression

- Step A: local 4B for FAQ and lead capture prototype
- Step B: local 8B for stronger intent parsing and formatting
- Step C: add tool calls for CRM/ERP/knowledge search

