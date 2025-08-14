# Rheumatology – Patient Scenario → Evidence Mapper (Streamlit MVP)

This MVP takes a patient profile and returns ranked evidence (guidelines, trials, drugs) with safety flags and an evidence pack.

**Data is synthetic for demo purposes.** Replace with your real connectors and AI calls.

## Quickstart
```
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Pages
1. Patient Profile
2. Evidence (ranked lists, AI summaries, safety flags, draft plan)
3. Evidence Pack (download ZIP)
4. Admin (preview datasets)

## Where to plug real AI
- `app/backend/ai.py` – replace templates with LLM calls that **return JSON only**.
- `app/backend/engine.py` – replace heuristic ranking with embeddings + reranker.

> Not for clinical use. Engineering demo only.
