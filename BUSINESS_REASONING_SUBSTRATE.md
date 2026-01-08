# Business Reasoning Substrate

## Vision Statement

**Haystack is no longer just a search engine or document store — it is a persistent, actionable thinking substrate for organizations.**

This document formalizes the transformation of Haystack's Smart Contextual Onboarding system and first-class context layer into a **Business Reasoning Substrate**: a system that stores, governs, and activates critical thinking artifacts to support strategic decision-making.

---

## Core Purpose

The Business Reasoning Substrate serves four foundational purposes:

1. **Store and govern all critical thinking artifacts in a structured way**
   - Ideas, decisions, assumptions, evidence, plans, and outcomes as first-class, queryable entities
   - Strict validation and confidence scoring for all artifacts
   - Version tracking and audit trails for accountability

2. **Enable traceability of decisions, assumptions, and outcomes**
   - Explicit relationship graphs connecting ideas → decisions → outcomes
   - Evidence linking to support or refute assumptions
   - Historical context preservation to prevent decision re-litigation

3. **Provide institutional memory that supports reasoning**
   - Persistent organizational knowledge that survives personnel changes
   - Searchable archive of past thinking and rationale
   - Context-aware memory for vendors, regulations, competitors, and personas

4. **Serve as a foundation for predictive, context-aware, risk-conscious decision-making**
   - Active comparison of new decisions against historical patterns
   - Risk detection through assumption tracking and contradiction analysis
   - Learning from outcomes to improve future decisions

---

## Current Foundation

### What Already Exists

The Business Reasoning Substrate builds on existing infrastructure delivered in previous phases:

#### 1. **Canonical Context Types** (6 Types)
Defined in `backend/CANONICAL_TYPES.md` and implemented in `backend/models/canonical_types.py`:

- **Ideas** - Uncommitted concepts and hypotheses
- **Decisions** - Explicit commitments with rationale and tradeoffs
- **Assumptions** - Beliefs taken as true, with confidence and risk assessment
- **Evidence** - Support or refutation with source, freshness, and reliability
- **Plans** - Intent and execution tracking with dependencies
- **Outcomes** - Expected vs. actual results with lessons learned

Each type has strict Pydantic schema validation and required fields.

#### 2. **Context Management Database** 
Defined in `supabase/init/003_context_management.sql`:

- `context_objects` table - Stores all context with type, content, source, confidence, status
- `context_evidence` table - Detailed evidence and provenance
- `context_links` table - Graph relationships between context objects
- `onboarding_sessions` table - Tracks user onboarding progress

#### 3. **Smart Contextual Onboarding**
Implemented in `backend/reasoning/context_extraction.py`:

- AI-powered context discovery from company information
- Automatic inference of industry, regulations, competitors, and personas
- Confidence scoring and evidence tracking
- User review and confirmation workflow

#### 4. **Relationship Graph**
Implemented in `backend/services/context_db.py`:

Explicit relationship types:
- `leads_to` - Idea → Decision
- `resulted_in` - Decision → Outcome
- `supports` / `refutes` - Evidence → Assumption
- `implements` - Plan → Decision
- `depends_on` - Plan → Plan
- `contradicts` - Context → Context

#### 5. **Hybrid Search Infrastructure**
Implemented in `haystack/document_stores/supabase/` and `haystack/components/retrievers/supabase/`:

- Semantic vector search using pgvector
- Keyword full-text search using PostgreSQL
- Weighted score fusion for hybrid retrieval
- Metadata filtering for context-aware queries

### What This Enables Today

With the current foundation, the system can:

✅ **Store thinking artifacts** - Not just documents, but structured reasoning  
✅ **Track decision history** - Why decisions were made and what was considered  
✅ **Manage assumptions** - Surface hidden risks and validate beliefs  
✅ **Link evidence** - Ground reasoning in facts, not hallucinations  
✅ **Monitor outcomes** - Learn from what actually happened vs. what was expected  
✅ **Query by type** - "Show me all decisions made about vendors"  
✅ **Traverse relationships** - "What assumptions supported this decision?"

---

## The Transformation

### From Passive Memory to Active Reasoning

| Before | After |
|--------|-------|
| Generic document storage | Typed thinking artifacts |
| Manual search | Proactive insight and comparison |
| Disconnected facts | Explicit causal relationships |
| Static snapshots | Temporal reasoning with delta analysis |
| Reactive lookups | Predictive risk detection |

### The Business Value

The Business Reasoning Substrate transforms Haystack into a **must-have strategic tool** by:

1. **Preventing costly mistakes** - Surface weak assumptions and contradicting evidence before decisions are made
2. **Accelerating decision-making** - "Have we seen this before? What happened?" instant answers
3. **Preserving institutional knowledge** - Critical thinking persists beyond individual tenure
4. **Enabling strategic analysis** - Pattern detection across decisions, outcomes, and risks
5. **Supporting compliance and audit** - Complete traceability of reasoning and evidence

---

## Roadmap: Must-Have Enhancements

The following seven enhancements transform the current foundation into a complete Business Reasoning Substrate. Each should be opened as a separate GitHub issue for iterative implementation.

### Overview of Enhancements

| # | Enhancement | Why It Matters | Status |
|---|-------------|----------------|--------|
| 1️⃣ | Active Reasoning & Delta Analysis | Converts passive memory into proactive insight | 📋 To be opened as issue |
| 2️⃣ | Assumption & Risk Management | Prevents failure due to untested beliefs | 📋 To be opened as issue |
| 3️⃣ | Automated Learning & Feedback Loops | Turns historical memory into actionable intelligence | 📋 To be opened as issue |
| 4️⃣ | Persona & Context-Aware Reasoning | Ensures precision and relevance in all queries | 📋 To be opened as issue |
| 5️⃣ | External Signal Integration | Keeps reasoning substrate current and evidence-backed | 📋 To be opened as issue |
| 6️⃣ | Query-Driven Decision Workflows | Makes system immediately useful to teams | 📋 To be opened as issue |
| 7️⃣ | Visualization & Insights | Turns memory system into a decision cockpit | 📋 To be opened as issue |

### Enhancement Details

#### 1️⃣ Active Reasoning & Delta Analysis

**Description:** Automatically compare proposed decisions, plans, or ideas to historical artifacts to highlight similarities, differences, and changes over time.

**Deliverables:**
- Delta analysis pipeline
- Similarity scoring for past artifacts
- Alerts for "repeat of prior decisions"

---

#### 2️⃣ Assumption & Risk Management

**Description:** Surface weak or low-confidence assumptions and track their risk exposure over time.

**Deliverables:**
- Assumption confidence scoring
- Risk highlighting dashboard
- Alerts when assumptions are contradicted by new evidence

---

#### 3️⃣ Automated Learning & Feedback Loops

**Description:** Detect patterns in past decisions, outcomes, and failures, and synthesize lessons for future reasoning.

**Deliverables:**
- Outcome → decision pattern analysis
- Retrospective summarization
- Recommendations for similar future decisions

---

#### 4️⃣ Persona & Context-Aware Reasoning

**Description:** Filter reasoning and decision support by customer, vendor, or organizational context (personas).

**Deliverables:**
- Persona-scoped context tagging
- Persona-aware risk impact
- Contextual query filtering

---

#### 5️⃣ External Signal Integration as Evidence

**Description:** Continuously ingest and link external signals (regulations, competitor moves, market trends) to context artifacts.

**Deliverables:**
- Scheduled external data ingestion
- Evidence linking to assumptions/decisions
- Temporal context tagging (freshness, source, reliability)

---

#### 6️⃣ Query-Driven Decision Workflows

**Description:** Enable actionable, natural-language queries across all artifact types to support operational decisions.

**Deliverables:**
- Pre-defined query templates: "Do we already have a vendor like this?"
- Query parser → hybrid search → artifact relevance ranking
- Actionable output with links to context artifacts

---

#### 7️⃣ Visualization & Insights

**Description:** Graphical views for relationships, dependencies, and impact across ideas, decisions, assumptions, and outcomes.

**Deliverables:**
- Idea → Decision → Outcome graph
- Assumption → Evidence → Risk dashboards
- Delta highlighting across past and proposed actions

---

### Implementation Principles

All enhancements must:

✅ **Not disrupt existing onboarding flows** - Build on top, don't replace  
✅ **Leverage existing infrastructure** - Use canonical types, relationships, and hybrid search  
✅ **Maintain audit readiness** - All reasoning must be traceable and explainable  
✅ **Be user-governed** - No auto-decisions; always require human confirmation  
✅ **Support incremental deployment** - Each enhancement can be implemented and tested independently

---

## Current System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Business Reasoning Substrate              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Ideas      │  │  Decisions   │  │  Assumptions │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         │  leads_to        │  resulted_in     │  supports   │
│         ▼                  ▼                  ▼              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Plans      │  │   Outcomes   │  │   Evidence   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Context Management Database                   │  │
│  │  • context_objects (type, content, confidence)       │  │
│  │  • context_evidence (source, freshness, reliability) │  │
│  │  • context_links (relationship graph)                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Hybrid Search Engine                          │  │
│  │  • Semantic (pgvector) + Keyword (PostgreSQL FTS)    │  │
│  │  • Metadata filtering + Confidence scoring           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Use Cases Enabled

### Vendor & Procurement
- **"Do we already have a vendor that does something similar?"**
  - Search across past decisions and vendor context
  - Detect overlap and redundancy
  - Surface past outcomes with similar vendors

- **"What new risks does this vendor introduce?"**
  - Compare vendor capabilities to existing assumptions
  - Identify contradicting evidence
  - Highlight untested assumptions

### Strategic Planning
- **"Have we tried this approach before? What happened?"**
  - Search past plans and outcomes
  - Compare expected vs. actual results
  - Extract lessons learned

- **"What assumptions are we making that might be wrong?"**
  - List all low-confidence assumptions
  - Show evidence that supports or refutes each
  - Calculate risk exposure

### Compliance & Risk
- **"What regulations apply to this decision?"**
  - Filter by industry, geography, and context
  - Show evidence for regulatory applicability
  - Link to past compliance decisions

- **"Show me all decisions that depend on this assumption"**
  - Traverse relationship graph
  - Calculate downstream impact of assumption failure
  - Prioritize validation efforts

---

## Implementation Status

### ✅ Completed (Phase 1 & 2)
- Database schema for context management
- 6 canonical document types with validation
- Smart contextual onboarding with AI extraction
- Relationship graph infrastructure
- Hybrid search (semantic + keyword)
- REST API for context CRUD and relationships
- Frontend UI for onboarding and context review

### 📋 Planned (Must-Have Enhancements)
See [Roadmap](#roadmap-must-have-enhancements) section above for all enhancement details.

### 🔮 Future (Nice-to-Have)
- Multi-tenant support for organizations
- Advanced visualization with D3.js or similar
- Real-time collaboration on context review
- Webhook integrations for external data sources
- Mobile app for on-the-go context capture
- Export/import for context portability

---

## Getting Started

### For Developers

1. **Review the foundation:**
   - Read `backend/CANONICAL_TYPES.md` to understand the 6 canonical types
   - Review `supabase/init/003_context_management.sql` for database schema
   - Study `backend/services/context_db.py` for API patterns

2. **Explore the enhancements:**
   - Review the [Roadmap](#roadmap-must-have-enhancements) section above for enhancement details
   - Pick an enhancement to implement based on business priority
   - Follow the deliverables defined in each enhancement description

3. **Test with existing infrastructure:**
   - Use the onboarding flow to create sample context
   - Experiment with relationship creation
   - Test hybrid search across artifact types

### For Product Managers

1. **Prioritize enhancements:**
   - Review each enhancement's "Why it matters" section
   - Consider user impact and implementation complexity
   - Align with current business objectives

2. **Define success metrics:**
   - Time-to-insight for strategic queries
   - Decision traceability coverage (% of decisions with full context)
   - Risk coverage (% of assumptions validated with evidence)
   - Outcome learning rate (% of outcomes with lessons applied)

3. **Plan rollout:**
   - Start with high-impact, low-complexity enhancements
   - Gather user feedback after each enhancement
   - Iterate based on actual usage patterns

---

## Architecture Decisions

### Why 6 Canonical Types?

The 6 types (Ideas, Decisions, Assumptions, Evidence, Plans, Outcomes) represent the complete lifecycle of business reasoning:

1. **Ideas** - Where thinking starts (hypothesis)
2. **Assumptions** - What we believe to be true (beliefs)
3. **Evidence** - What we know to be true (facts)
4. **Decisions** - What we commit to (action)
5. **Plans** - How we execute (execution)
6. **Outcomes** - What actually happens (reality)

This creates a closed loop: Outcomes feed back into Evidence, which informs future Ideas.

### Why Explicit Relationships?

Implicit relationships (inferred from content) are unreliable and expensive. Explicit relationships:
- Enable efficient graph traversal
- Support precise queries ("What assumptions supported this decision?")
- Provide audit trails for compliance
- Allow contradiction detection
- Scale to millions of artifacts

### Why Confidence Scoring?

Not all context is equally reliable. Confidence scoring:
- Prioritizes high-quality artifacts in search results
- Surfaces low-confidence assumptions for validation
- Enables risk calculation (low confidence × high impact = high risk)
- Supports adversarial analysis and red-teaming

### Why Hybrid Search?

Different queries require different search strategies:
- **Semantic search** - "Find vendors similar to Salesforce"
- **Keyword search** - "Find all GDPR-related decisions"
- **Hybrid** - Best of both, weighted by use case

---

## Success Criteria

The Business Reasoning Substrate is successful when:

1. **Decision-makers use it daily** - Not just for onboarding, but for ongoing strategic queries
2. **Time-to-insight is <30 seconds** - Any strategic question answered in under 30 seconds
3. **Decision traceability is >80%** - At least 80% of major decisions have full context (assumptions, evidence, outcomes)
4. **Risk detection is proactive** - System alerts to weak assumptions before they cause problems
5. **Learning is continuous** - Outcomes automatically inform future decisions

---

## Next Steps

1. **Review this document** with stakeholders for alignment
2. **Open GitHub issues** for each of the 7 must-have enhancements using the template below
3. **Prioritize enhancements** based on business impact (recommended: Assumption & Risk first, Visualization last)
4. **Assign ownership** to development teams
5. **Begin implementation** with highest-priority enhancement

### Issue Template for Enhancements

When creating GitHub issues for each enhancement, use this structure:

```markdown
## Enhancement: [Name]

**Description:** [As defined in BUSINESS_REASONING_SUBSTRATE.md]

**Why it matters:** [Business value from main document]

**Deliverables:**
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
- [ ] [Deliverable 3]

**Dependencies:**
- Canonical context types (implemented ✓)
- Context relationships API (implemented ✓)
- Hybrid search infrastructure (implemented ✓)

**Implementation Notes:**
- No changes to existing onboarding flows
- Leverage Supabase tables and hybrid search
- Ensure all pipelines remain audit-ready and user-governed

**Acceptance Criteria:**
- [ ] Feature implementation complete
- [ ] Unit tests with >80% coverage
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Security scan passing (CodeQL)
- [ ] User-facing UI/API documented

**Labels:** enhancement, business-reasoning-substrate
```

---

## Related Documentation

- [Canonical Types Documentation](./backend/CANONICAL_TYPES.md) - Detailed schemas for all 6 types
- [Smart Onboarding Documentation](./docs/SMART_ONBOARDING.md) - How context is discovered and validated
- [Supabase Implementation](./SUPABASE_IMPLEMENTATION.md) - Database and hybrid search architecture
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) - Phase 1 & 2 delivery summary

---

**Last Updated:** January 8, 2025  
**Status:** Foundation Complete ✅ | Enhancements Planned 📋  
**Version:** 1.0
