# RuSnipe — Rutgers Course Availability AI Agent

A natural-language AI agent that wraps Rutgers' Schedule of Classes API and lets students query course availability in plain English — plus a polling service that monitors seat openings in high-demand classes and alerts users when seats free up.

Built with **Google's Agent Development Kit (ADK)**.

---

## The problem

Course registration at Rutgers is a manual scramble. Popular sections fill within minutes of opening, and the official Schedule of Classes portal returns a single undifferentiated blob of data with no real filtering — so students end up either F5-ing the page or cross-referencing dense degree-requirement lists by hand to figure out what they can even take.

RuSnipe solves both problems:

1. **Plain-English course search.** Ask the agent things like *"give me 3-credit classes that fulfill the writing requirement and have open seats on Busch"* and it returns matching sections.
2. **Automated seat sniping.** Tell the polling service which sections to watch; it checks every 15 minutes and notifies you the moment a seat opens.

---

## Demo

![short gif of adk agent answering query](https://github.com/TheChickenKnight/rusnipe/blob/main/media/trial.gif?raw=true)

---

## What's in here

```
rusnipe/
├── rusnipe/             # The ADK agent + polling service (start here)
│   ├── agent.py         # Agent definition, tools, instructions
│   ├── [polling file]   # Scheduled seat-availability poller
│   └── ...
├── README.md            # You are here
└── [API research notes — see "How this works" below]
```

---

## Stack

- **Python**
- **Google ADK** (Agent Development Kit) — orchestrates the LLM workflow and tool-use over the live course API
- **LLMs** — Llama / HuggingFace integrations
- **Rutgers SOC API** — the (undocumented) data source

---

## Key design decisions

- **Encoded degree requirements as LLM-readable plain text.** Rutgers' requirement docs are dense and cross-referenced. Translating them into something an LLM can reason over removes the manual lookup step entirely.
- **Built on ADK rather than rolling a custom agent loop.** ADK gives you tool-calling, multi-step orchestration, and a built-in web UI for free — the right call for a project where the *interesting* work is the domain modeling, not the agent plumbing.
- **15-minute polling cadence.** Frequent enough to catch most seat openings (which usually persist a few minutes before someone else grabs them), infrequent enough to be a polite consumer of Rutgers' API.

---

## Status

Working — actively used by me and a few classmates each registration window. Expanding to handle [next thing on the roadmap].

---

## How this works — API research notes

The Rutgers Schedule of Classes API is barely documented anywhere public. Most of the early work on this project was reverse-engineering it. Notes below in case it's useful to anyone else trying to build on the same data source.

### Endpoint

The only mention I could find of the API was in [@rpatel3001's RU-Interested repo](https://github.com/rpatel3001/RU-Interested/) — credit there.

```
https://classes.rutgers.edu/soc/courses.gz?term=1&year=2025&campus=NB
```

### Parameters

| Param  | Type   | Notes |
|--------|--------|-------|
| `term` | int 1–4 | 1 = Spring, 2 = Summer, 3 = Fall, 4 = Winter |
| `year` | int    | Year of classes |
| `campus` | string | `NB` for New Brunswick (the only one I needed) |

There doesn't appear to be a `subject` param or any way to narrow the request server-side — the response is a single payload covering the whole campus/term.

### Response format

The endpoint returns a gzipped file (no extension) containing a single JSON document. Decompressed with [pako](https://www.npmjs.org/package/pako) on the JS side; the Python agent uses the standard library `gzip` module.

---