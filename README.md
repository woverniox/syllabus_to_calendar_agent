engineer-track/
├── README.md                 # This file
├── docker-compose.yml        # API + Postgres + Redis
├── .env.example              # Environment template
├── db/
│   └── init.sql              # Database schema
├── agent-api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py               # FastAPI app and routes
│   ├── agent.py              # Agent loop implementation
│   ├── config.py             # Settings and constants
│   ├── models.py             # Pydantic schemas
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── score_lead.py     # Lead scoring tool
│   │   ├── upsert_lead.py    # Sheet update tool
│   │   ├── create_task.py    # Task creation tool
│   │   ├── draft_email.py    # Email drafting tool
│   │   └── memory.py         # Company history tool
│   ├── guardrails/
│   │   ├── __init__.py
│   │   ├── approval.py       # Approval gate logic
│   │   └── validators.py     # Input validation
│   └── db/
│       ├── __init__.py
│       ├── postgres.py       # Trace logging
│       └── redis.py          # Memory/cache
├── eval/
│   ├── run_eval.py           # Eval runner script
│   ├── sample-leads.json     # 20 test cases
│   └── expected-outputs.json # Ground truth
└── data/
    └── traces/               # JSON trace files
