PYTHON ?= python
IN ?= demo_data/tickets_demo.jsonl
OUT ?= artifacts/pred.jsonl
DATA_DIR ?= demo_data
.PHONY: install api ui predict evaluate train test
install:
	$(PYTHON) -m pip install -r requirements.txt
api:
	GG_DATA_DIR=$(DATA_DIR) $(PYTHON) -m uvicorn app.main:app --reload --port 8000
ui:
	GG_DATA_DIR=$(DATA_DIR) $(PYTHON) -m streamlit run ui/dashboard.py
predict:
	$(PYTHON) scripts/predict.py --input $(IN) --output $(OUT) --data-dir $(DATA_DIR)
evaluate:
	$(PYTHON) scripts/evaluate.py --input $(IN) --data-dir $(DATA_DIR)
train:
	$(PYTHON) scripts/train.py --input $(IN)
test:
	GG_DATA_DIR=$(DATA_DIR) $(PYTHON) -m pytest -q

.PHONY: review-set score-review
review-set:
	$(PYTHON) scripts/create_review_set.py --input data/tickets_valid.jsonl
score-review:
	$(PYTHON) scripts/score_review.py --input data/manual_review.csv --data-dir data
