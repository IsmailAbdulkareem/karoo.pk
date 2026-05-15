# Karoo Constitution
<!-- AI Service Orchestrator for Informal Economy -->

<!--
Sync Impact Report:
Version: 1.0.0 (initial constitution)
Modified Principles: N/A (initial creation)
Added Sections: All sections (initial creation)
Removed Sections: None
Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md (to be validated)
  ✅ .specify/templates/spec-template.md (to be validated)
  ✅ .specify/templates/tasks-template.md (to be validated)
Follow-up TODOs: None
-->

## Core Principles

### I. AI-First Orchestration
Every user interaction flows through Google Antigravity agent powered by Gemini API. The agent is the single source of truth for intent parsing, provider matching, and decision reasoning. All business logic requiring judgment (ranking, clarification, dispute handling) MUST be delegated to the agent, not hardcoded. Agent traces MUST be logged for every request to enable debugging and improvement.

**Why:** Antigravity provides transparent, auditable AI reasoning that adapts to natural language input in multiple languages (Urdu, Roman Urdu, English). Hardcoded rules cannot handle the linguistic and contextual variability of informal economy interactions.

**How to apply:** When adding new features, first define MCP tools for the agent to call. Never bypass the agent for user-facing decisions. Always capture and store agent traces in the database.

### II. Real-Time Location Accuracy
Provider matching MUST use real-time travel time from Google Routes API, not straight-line distance. Location text (e.g., "F-10", "G-11") MUST be geocoded via Google Geocoding API before any distance calculation. Provider coordinates MUST be stored at registration and updated when providers change service areas.

**Why:** Informal economy workers operate in areas with complex traffic patterns and road networks. Straight-line distance produces incorrect ETAs and poor user experience. Real travel time is the primary ranking factor.

**How to apply:** Never calculate distance without calling Google Routes API. Always geocode location strings before querying providers. Cache geocoding results for common area names to reduce API costs.

### III. Bidirectional Trust & Accountability
Both users and providers MUST rate each other after service completion. User reliability scores affect provider acceptance decisions. Provider ratings affect user matching results. Ratings MUST be blind (neither party sees the other's rating until both submit). Rating window is 72 hours after job completion.

**Why:** Informal economy lacks institutional trust mechanisms. Mutual ratings create accountability on both sides, protecting providers from problematic customers and users from unreliable providers.

**How to apply:** Trigger rating prompts when booking status changes to "completed". Store ratings in separate table with rater_role field. Update rolling averages for both provider.rating and user.reliability_score. Display user reliability score to providers before they accept bookings.

### IV. Multi-Language Natural Language Processing
The system MUST accept input in Urdu, Roman Urdu, and English without requiring language selection. Intent extraction via Gemini MUST handle code-switching (mixing languages in one sentence). Clarification questions MUST be asked in the same language as the user's input.

**Why:** Informal economy workers and customers often use Roman Urdu or mix languages. Forcing language selection creates friction. Natural code-switching is the norm in Pakistan's urban centers.

**How to apply:** Pass full conversation context to Gemini for language detection. Never use language-specific regex or keyword matching. Test with mixed-language inputs during development.

### V. Mobile-First, Cross-Platform Design
All features MUST work on both web and mobile from a single Expo codebase. UI components MUST use NativeWind (Tailwind for React Native) for consistent styling. Navigation MUST use Expo Router file-based routing. No platform-specific code unless absolutely necessary.

**Why:** Users access the service from mobile devices, but providers may prefer web dashboards. Maintaining separate codebases is unsustainable for a hackathon project and early-stage product.

**How to apply:** Test every feature on both web and mobile before marking complete. Use Expo's Platform API only when native features (camera, location) require it. Prefer responsive design over platform-specific layouts.

### VI. Security & Privacy by Default
All API requests MUST include JWT authentication. User phone numbers and location data MUST NOT be exposed to providers until booking is confirmed. Passwords MUST be hashed with bcrypt. API keys MUST be stored in .env files, never committed to git. Provider CNIC photos MUST be stored securely and only accessible to admin verification.

**Why:** Informal economy workers are vulnerable to exploitation. Location and contact data must be protected until trust is established through booking confirmation. Regulatory compliance (data protection) is critical for scaling.

**How to apply:** Validate JWT on every protected endpoint. Use Supabase Row Level Security policies. Never log sensitive data (passwords, tokens, CNIC numbers). Implement rate limiting on auth endpoints to prevent brute force.

### VII. Observability & Debugging
Every agent decision MUST produce a trace log stored in the database. API errors MUST return structured error codes and messages. Provider ranking decisions MUST include reasoning (why provider X ranked #1). Booking state transitions MUST be logged with timestamps.

**Why:** AI-driven systems are opaque without explicit logging. When users complain about poor matches or providers question rankings, traces provide evidence for debugging and improvement.

**How to apply:** Store agent_trace field in messages table. Return agent reasoning in API responses during development. Create admin dashboard to view traces. Log all Google Cloud API calls with request/response for cost tracking.

## Technology Stack Constraints

### Required Services
- **Frontend:** Expo + React Native + NativeWind + Expo Router (no alternative frameworks)
- **Backend:** FastAPI (Python) with async/await for all I/O operations
- **AI Orchestration:** Google Antigravity with Gemini API (no other LLM providers)
- **Location Services:** Google Cloud (Geocoding, Routes, Places APIs) - no alternative mapping services
- **Database:** Supabase (PostgreSQL) with Realtime enabled
- **Authentication:** JWT tokens with Supabase Auth for OTP
- **Deployment:** Render (backend), Expo Go (mobile)

### API Rate Limits & Cost Management
- Google Routes API: Cache results for 15 minutes per provider-user pair
- Google Geocoding API: Cache common area names (F-10, G-11, etc.) indefinitely
- Gemini API: Use prompt caching for system instructions to reduce token costs
- Supabase: Use connection pooling, limit query result sets to 100 rows

### Prohibited Dependencies
- No additional LLM providers (OpenAI, Anthropic, etc.) - Gemini via Antigravity only
- No alternative mapping services (Mapbox, OpenStreetMap) - Google Cloud only
- No native mobile code (Swift, Kotlin) - Expo managed workflow only
- No custom authentication - Supabase Auth only

## Development Workflow

### Feature Development Process
1. **Spec First:** Create `specs/<feature>/spec.md` with user stories and acceptance criteria
2. **Plan Architecture:** Create `specs/<feature>/plan.md` with API contracts, data models, and Google Cloud API usage
3. **Generate Tasks:** Create `specs/<feature>/tasks.md` with testable checkboxes
4. **Implement:** Follow Red-Green-Refactor for backend, component-first for frontend
5. **Test:** Manual testing on Expo Go (mobile) + web browser, verify agent traces
6. **Document:** Update README with new endpoints, create PHR in `history/prompts/<feature>/`

### Testing Requirements
- **Backend:** Manual API testing via Swagger docs (`/docs` endpoint)
- **Frontend:** Manual testing on Expo Go (Android/iOS) + web browser
- **Agent:** Verify intent extraction accuracy, provider ranking correctness, trace completeness
- **Integration:** End-to-end flow from user message → provider notification → rating submission
- **No automated tests required for hackathon scope** (add in post-hackathon phase)

### Git Workflow
- **Main branch:** Always deployable, protected
- **Feature branches:** `feature/<feature-name>` for new work
- **Commit messages:** Conventional commits format (`feat:`, `fix:`, `docs:`, `refactor:`)
- **Pull requests:** Required for all changes, must include demo video or screenshots
- **No force push to main:** Ever

### Code Review Checklist
- [ ] JWT authentication present on protected endpoints
- [ ] Agent trace logged and stored
- [ ] Google Cloud API calls cached appropriately
- [ ] Error responses include structured error codes
- [ ] Mobile and web both tested
- [ ] No hardcoded secrets or API keys
- [ ] User/provider data privacy maintained
- [ ] Multi-language support verified (if user-facing)

## Governance

### Constitution Authority
This constitution supersedes all other development practices and preferences. When in doubt, refer to this document. Violations must be flagged in code review and corrected before merge.

### Amendment Process
1. Propose amendment with rationale in GitHub issue
2. Discuss with team (minimum 24 hours)
3. Update constitution with version bump (see versioning rules below)
4. Update dependent templates (plan, spec, tasks)
5. Create ADR if architecturally significant
6. Commit with message: `docs: amend constitution to vX.Y.Z (<brief change>)`

### Versioning Rules
- **MAJOR (X.0.0):** Backward incompatible changes (e.g., removing a principle, changing tech stack)
- **MINOR (0.X.0):** New principle added or existing principle materially expanded
- **PATCH (0.0.X):** Clarifications, wording improvements, typo fixes

### Compliance Verification
- All PRs must reference relevant constitution principles in description
- Architecture decisions must cite principles that influenced the choice
- When principles conflict, escalate to team discussion (document in ADR)
- Quarterly constitution review to remove outdated constraints

### Runtime Development Guidance
For agent-specific development guidance and prompt engineering patterns, see `CLAUDE.md` in the project root. For Google Antigravity agent configuration, see `backend/agents/README.md`.

**Version**: 1.0.0 | **Ratified**: 2026-05-16 | **Last Amended**: 2026-05-16
