---
id: 0001
title: Initial Karoo Constitution
stage: constitution
date: 2026-05-16
surface: agent
model: Claude Opus 4.6
feature: none
branch: main
user: Ismail
command: /sp.constitution
labels: ["constitution", "governance", "principles", "karoo", "ai-orchestrator"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (documentation artifact)
---

## Prompt

```text
# 🤝 Karoo — AI Service Orchestrator

[User provided extensive project documentation including:]
- AI-powered service booking agent for informal economy
- Google Antigravity Hackathon — Challenge 2: AI Service Orchestrator
- Tech stack: Expo + React Native, FastAPI, Google Antigravity (Gemini API), Google Cloud APIs
- Architecture: AI-first orchestration with real-time location matching
- Bidirectional rating system (users rate providers, providers rate users)
- Multi-language NLP (Urdu, Roman Urdu, English)
- Database schema with users, providers, bookings, ratings tables
- Complete API endpoints and team work distribution
- Mobile-first cross-platform design with Expo
```

## Response snapshot

Created comprehensive Karoo Constitution v1.0.0 with 7 core principles:

1. **AI-First Orchestration**: Google Antigravity agent as single source of truth for all business logic requiring judgment
2. **Real-Time Location Accuracy**: Google Routes API for travel time (not straight-line distance)
3. **Bidirectional Trust & Accountability**: Mutual ratings between users and providers
4. **Multi-Language NLP**: Urdu/Roman Urdu/English support with code-switching via Gemini
5. **Mobile-First, Cross-Platform Design**: Single Expo codebase for web + mobile
6. **Security & Privacy by Default**: JWT auth, data protection, bcrypt passwords
7. **Observability & Debugging**: Agent trace logging for all decisions

Additional sections:
- Technology Stack Constraints (required services, rate limits, prohibited dependencies)
- Development Workflow (spec-first, testing requirements, git workflow, code review)
- Governance (amendment process, versioning rules, compliance verification)

## Outcome

- ✅ Impact: Established foundational governance document for Karoo project with clear principles aligned to AI service orchestrator architecture
- 🧪 Tests: N/A (constitution is a governance document)
- 📁 Files: Created .specify/memory/constitution.md (v1.0.0)
- 🔁 Next prompts: Validate dependent templates (spec, plan, tasks), begin feature specification with /sp.specify
- 🧠 Reflection: Constitution successfully captures the unique constraints of AI-first informal economy platform (Antigravity orchestration, real-time location, bidirectional trust, multi-language). Principles are testable and actionable.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation — PASS (all placeholders filled, principles aligned to project context, versioning correct)
- Prompt variant (if applicable): Standard /sp.constitution workflow
- Next experiment (smallest change to try): Monitor whether principles are actually referenced in code reviews and feature planning
