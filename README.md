# RealEstate Agent

``!! Work in progress - Active Development``

## Overview

An AI-powered real estate deal discovery system that scrapes listings,stores structured data,and uses agent-based AI to help users find
matching properties and receive alerts. 

---

## Documents
- [Database Schema](docs/DB_SCHEMA.md)
- [Flow](docs/FLOW.md)

---

## Current Features
- **Fast scraper:** Playwright_async based fast multipage scraper with continuous updater.
- **PostgreSQL storage:** Listing and user data are stored in Supabase.
- **AI agent:** LangGraph based agent that can chat,query and assist users.
- **Ml analysis prototype:** Experimental realestate price prediction models.  
- **Streamlit frontend:** Prototype for actual Svelte frontend.
- **Oauth:** Google oauth with fastapi.
- **Fastapi:** Fastapi endpoints for data querying and oauth.

## Planned Features
- Data extraction(multi-source)
- Agentic research tools
- Airflow orchestration 
- User-defined alerts
- Svelte frontend
- Ranking / ML-based recommendations

---

## Project structure
```text
realestate_agent/
├── ai_agent        # LangGraph/llm logic
├── data            # Contains temporary listing data , and some core data cleaning logic
├── manage_db       # Core module that manages the entire database
├── ml_analysis     # Experimental ml logic
├── scraper         # Scraper (playwright_async)
├── test            # Test logic
├── ui              # The ui logic , also includes apis and oauth(streamlit/fastapi)
├── utils           # Contains loging logic
├── requirements.txt # Contains project requirements 
├── .env            # Contains project secretes (database connection,LLM api,...)
├── docs            # Documents            
└── README.md
```

---

## Currently working on :
- [Data migration](docs/MIGRATION.md)

---

## Status
This project is under active development. Architecture and features
may change.

