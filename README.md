# Requirement Knowledge Tracker (MVP)

Minimal scaffold to run the MVP web app.

Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Run

```bash
uvicorn app.main:app --reload
```

Environment

Set Trello env vars (optional): `TRELLO_KEY`, `TRELLO_TOKEN`, `TRELLO_LIST_ID`

Open http://127.0.0.1:8000/ and paste an email subject/body and attachments.
