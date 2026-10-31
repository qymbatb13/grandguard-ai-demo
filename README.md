# GrandGuard AI — Support Copilot (Final MVP)

Local game support ticket triage prototype for Decentrathon 6.0. No access to Grand Mobile servers. **Not a fully validated production moderator.**

## Quick start (macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/setup_data.py --archive "$HOME/Downloads/grand-support-copilot-handout-2026-10-27.tgz"
python scripts/train.py --input data/tickets_train.jsonl.gz --data-dir data --max-rows 30000
GG_DATA_DIR=data python -m uvicorn app.main:app --reload --port 8001
```

In another terminal:

```bash
source .venv/bin/activate
GG_DATA_DIR=data python -m streamlit run ui/dashboard.py --server.port 8502
```

Open `http://localhost:8502`, API `http://127.0.0.1:8001/docs`. Note the Streamlit dashboard also runs a local inference engine, separately from the API. Restart it after training to load the new model.

## CLI / validation

```bash
python -m pytest -q
make predict IN=data/tickets_valid.jsonl OUT=artifacts/pred.jsonl DATA_DIR=data
python scripts/evaluate.py --input data/tickets_valid.jsonl --data-dir data
python scripts/create_review_set.py --input data/tickets_valid.jsonl --output data/manual_review.csv --size 100
# Fill gold_category, gold_priority manually using taxonomy.json, then:
python scripts/score_review.py --input data/manual_review.csv --data-dir data
```

`POST /triage` accepts `kind`, `messages` and optional evidence count/context, returns `lang`, `category`, `priority`, duplicate indicator, extracted facts, `draft_reply` and `needs_human`. The output is a **draft**, never an automatic punishment decision. The batch pipeline strips historical administrator answers.

## Architecture

* Normalization for legacy Kazakh characters, conservative language detection
* Weak-supervised TF-IDF/Logistic Regression with rule-based fallback (not independently verified accuracy)
* BM25 search against only existing official `rules[].points[].ref` and taxonomy whitelists
* Safe deterministic drafts in six languages; escalation for complaints, payment, account and sanctions
* Locally demonstrated Streamlit admin review interface; no official game integration

## Limitations

* The training labels come from heuristics. The holdout weak-label macro-F1 is **not** classification accuracy on human labeled or organizer hidden data.
* Retrieved citations are candidate rules, not proof of an offense or guaranteed relevance.
* Attachments are not supplied, only their counts; never assert evidence has been verified.
* Many requests are escalated to humans. Response quality on Kazakh and Uzbek needs review by native speakers.
* No external LLM API is used; cost per ticket excludes hardware/hosting. p95 must be measured on final deployment, not assumed.
* Demo approvals are in the browser session only.

## Privacy / submission

**Do not upload the provided Grand Mobile dataset.** `data/`, `artifacts/`, `.venv/`, and `.tgz` are excluded by `.gitignore`. Read [GITHUB_UPLOAD.md](GITHUB_UPLOAD.md) before pushing.
