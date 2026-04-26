# RUSnipe 
### Rutgers Course Availability AI Agent

> An AI-powered natural language agent that lets Rutgers students query the Schedule of Classes in plain English — no more manually cross-referencing hundreds of open sections against degree requirement lists.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green?logo=node.js)](https://nodejs.org)
[![Google ADK](https://img.shields.io/badge/Google-ADK-orange?logo=google)](https://google.github.io/adk-docs/)
[![LLaMA](https://img.shields.io/badge/LLM-LLaMA%20%2F%20HuggingFace-yellow)](https://huggingface.co)
[![REST API](https://img.shields.io/badge/API-REST-lightgrey)](https://classes.rutgers.edu/soc)

---

## What It Does

Rutgers' Schedule of Classes (SOC) API returns undifferentiated bulk data — a compressed `.gz` file containing thousands of course entries with no filtering for subject, credits, or requirements. **RUSnipe wraps this raw API in a multi-step LLM agent** that understands natural language queries like:

> *"Give me 3-credit Writing-requirement classes open on Tuesdays"*
> *"What Computer Science courses still have open sections this spring?"*
> *"Find me a Gen Ed arts class that doesn't conflict with my 10am lecture"*

Instead of making students manually sift through bulk data and cross-reference degree requirements, the agent handles that reasoning end-to-end.

---

## Architecture

```
User (Natural Language Query)
        │
        ▼
  Google ADK Agent Layer
  (Multi-step LLM Orchestration + Tool Use)
        │
        ├──► LLaMA / HuggingFace LLM
        │    (Query understanding, requirement reasoning)
        │
        └──► SOC REST API Tool
             (Live data fetch from classes.rutgers.edu)
                    │
                    ▼
             Decompress .gz → Parse JSON
                    │
                    ▼
             Filter + Rank Results
                    │
                    ▼
        Natural Language Response to User
```

**Key components:**
- **Google ADK** orchestrates multi-step agent workflows with tool-use access to the live Rutgers SOC API
- **LLaMA / HuggingFace LLMs** handle natural language understanding and encode degree-requirement logic as structured, LLM-readable knowledge
- **pako** decompresses the `.gz` API response client-side before JSON parsing
- **ADK's built-in web UI** provides real-time agent monitoring and step-by-step workflow visibility

---

## The Problem It Solves

Rutgers' SOC API is almost entirely undocumented. Its endpoint:

```
https://classes.rutgers.edu/soc/courses.gz?term=1&year=2025&campus=NB
```

...returns a compressed blob of every course offered — with no subject filtering, no requirement tagging, and no human-readable structure. Students are left to manually:
1. Download and parse the bulk data
2. Cross-reference open sections against complex, often opaque degree requirement lists
3. Check for time conflicts

RUSnipe eliminates all three steps through **agentic reasoning** — the LLM encodes the requirement logic as structured knowledge and uses the API as a tool, not a dump.

---

## 🔌 API Reference

### SOC Endpoint

```
GET https://classes.rutgers.edu/soc/courses.gz
```

| Parameter | Type     | Description                              |
|-----------|----------|------------------------------------------|
| `term`    | int (1–4)| 1=Spring, 2=Summer, 3=Fall, 4=Winter     |
| `year`    | int      | Calendar year (e.g. `2025`)              |
| `campus`  | string   | Campus code — `NB` for New Brunswick     |

**Response:** A `.gz` compressed file containing a raw JSON array of course objects.

> API discovery credit: [rpatel3001/RU-Interested](https://github.com/rpatel3001/RU-Interested/)

---

## Tech Stack

| Layer              | Technology                        |
|--------------------|-----------------------------------|
| Agent Orchestration| Google ADK                        |
| LLM                | LLaMA, HuggingFace Transformers   |
| Backend            | Python                            |
| Frontend / Tooling | Node.js                           |
| Decompression      | pako (`.gz` → JSON)               |
| Data Source        | Rutgers SOC REST API              |

---

## Getting Started

> This project is under active development. Setup instructions will be added as the build stabilizes.

```bash
# Clone the repo
git clone https://github.com/TheChickenKnight/rusnipe.git
cd rusnipe

# Install dependencies (Node)
npm install

# Install dependencies (Python)
pip install -r requirements.txt

# Run the ADK agent
# (instructions coming soon)
```

---

## Roadmap

- [x] SOC API discovery and endpoint documentation
- [x] `.gz` decompression pipeline with pako
- [ ] Google ADK agent setup with tool-use for live API calls
- [ ] LLaMA / HuggingFace LLM integration
- [ ] Degree requirement encoding as structured LLM-readable knowledge
- [ ] Natural language query interface
- [ ] ADK web UI monitoring integration
- [ ] Conflict detection (time-based filtering)

---

## Why This Project

Building an agent on top of a poorly-documented, bulk-data API is a real-world agentic AI challenge — the same kind of structured knowledge and tool-use problem that underlies AI-powered curriculum tools and enterprise data assistants. RUSnipe is a demonstration of using **Google ADK**, **LLM tool use**, and **structured knowledge encoding** to turn raw, unusable data into a genuinely helpful natural language interface.

---

## 📄 License

MIT