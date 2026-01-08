# First-Class Context Canonicalization

This document describes the canonical context model system that transforms Haystack from "AI with memory" into a persistent organizational thinking substrate.

## Overview

All context artifacts are now normalized into **six canonical document types** that explicitly support business reasoning:

1. **Ideas** - Uncommitted concepts and hypotheses
2. **Decisions** - Explicit commitments
3. **Assumptions** - Beliefs taken as true
4. **Evidence** - Support or refutation
5. **Plans** - Intent and execution tracking
6. **Outcomes** - What actually happened

## Canonical Document Types

### 1. Ideas

Uncommitted concepts that may or may not be pursued.

**Purpose:**
- Compare new ideas to prior thinking
- Detect idea recycling
- Enable challenge before commitment

**Required Fields:**
- `problem_statement` - Problem or opportunity being addressed
- `proposed_solution` - How this idea proposes to solve the problem
- `target_user` - Who benefits from this idea
- `claimed_advantage` - Why this is better than alternatives
- `confidence` - Confidence in viability (0.0-1.0)

**Example:**
```json
{
  "type": "idea",
  "content": {
    "problem_statement": "Sales team lacks visibility into customer context during calls",
    "proposed_solution": "Build real-time context panel that surfaces relevant documents",
    "target_user": "Account Executives in B2B sales",
    "claimed_advantage": "Reduces prep time from 30min to 2min per call",
    "confidence": 0.7,
    "constraints": ["Must integrate with Salesforce", "Budget: $50k"],
    "risks": ["May slow down call flow", "Privacy concerns"]
  }
}
```

### 2. Decisions

Explicit commitments that prevent re-litigation and enable historical reasoning.

**Purpose:**
- Prevent decision re-litigation
- Enable historical reasoning
- Support "what changed?" queries

**Required Fields:**
- `decision` - The decision that was made
- `date` - Date the decision was made
- `options_considered` - Alternative options that were evaluated
- `rationale` - Why this decision was made
- `tradeoffs` - Key tradeoffs accepted (what was gained vs lost)
- `owner` - Person or team responsible for this decision

**Example:**
```json
{
  "type": "decision",
  "content": {
    "decision": "Use PostgreSQL instead of MongoDB for customer data storage",
    "date": "2024-01-15",
    "options_considered": ["MongoDB", "PostgreSQL", "DynamoDB"],
    "rationale": "Need ACID compliance for financial data, team has strong SQL expertise",
    "tradeoffs": {
      "gained": "Data consistency, relational querying, team expertise",
      "lost": "Schema flexibility, horizontal scaling simplicity"
    },
    "owner": "Engineering Lead - Sarah Chen",
    "reversibility": "High - would require significant migration effort (2-3 months)",
    "success_criteria": ["Zero data inconsistencies", "Query performance <100ms"]
  }
}
```

### 3. Assumptions

Beliefs taken as true that underpin decisions and plans.

**Purpose:**
- Surface hidden risk
- Enable assumption decay tracking
- Allow contradiction detection

**Required Fields:**
- `assumption` - The assumption being made
- `confidence` - Confidence this assumption is valid (0.0-1.0)
- `risk_if_wrong` - What happens if this assumption is incorrect

**Example:**
```json
{
  "type": "assumption",
  "content": {
    "assumption": "Customers will pay $99/month for unlimited usage tier",
    "confidence": 0.6,
    "risk_if_wrong": "Revenue model collapses, need to pivot to usage-based pricing",
    "evidence_links": ["survey_results_2024Q1.pdf"],
    "category": "market",
    "validated_date": "2024-01-10",
    "expiration_date": "2024-04-10"
  }
}
```

### 4. Evidence

Support or refutation that grounds reasoning and prevents hallucination.

**Purpose:**
- Ground reasoning in facts
- Prevent hallucination loops
- Support adversarial analysis

**Required Fields:**
- `source` - Where this evidence came from
- `claim_supported_or_refuted` - What claim this evidence addresses
- `freshness` - When this evidence was collected or last verified
- `reliability_score` - How reliable is this source (0.0-1.0)
- `external` - Whether this evidence is from external source (vs internal)

**Example:**
```json
{
  "type": "evidence",
  "content": {
    "source": "Gartner Market Analysis Report 2024",
    "claim_supported_or_refuted": "Enterprise market for AI tools growing at 40% YoY",
    "freshness": "2024-01-05",
    "reliability_score": 0.9,
    "external": true,
    "summary": "Report shows enterprise AI spending up 42% in 2023",
    "methodology": "Survey of 500 enterprise CIOs",
    "sample_size": 500
  }
}
```

### 5. Plans

Intent and execution tracking that bridges strategy to reality.

**Purpose:**
- Detect execution drift
- Track progress against goals
- Bridge strategy → reality

**Required Fields:**
- `goal` - What this plan aims to achieve
- `steps` - Ordered list of steps to execute
- `timeline` - Expected timeline for completion
- `dependencies` - External dependencies or blockers

**Example:**
```json
{
  "type": "plan",
  "content": {
    "goal": "Launch self-service onboarding flow for SMB customers",
    "steps": [
      {
        "description": "Design onboarding screens",
        "owner": "Design team",
        "deadline": "2024-02-01",
        "status": "completed"
      },
      {
        "description": "Implement signup API",
        "owner": "Backend team",
        "deadline": "2024-02-15",
        "status": "in_progress"
      }
    ],
    "timeline": "6 weeks (Jan 15 - Feb 28, 2024)",
    "dependencies": ["Stripe integration", "Email service setup"],
    "success_metrics": ["50% of SMB signups complete without sales call"]
  }
}
```

### 6. Outcomes

What actually happened versus what was expected.

**Purpose:**
- Enable learning from results
- Prevent repeating mistakes
- Provide outcome-driven memory

**Required Fields:**
- `expected_outcome` - What was expected to happen
- `actual_outcome` - What actually happened
- `delta` - Explanation of the difference
- `lessons_learned` - Key lessons from this outcome

**Example:**
```json
{
  "type": "outcome",
  "content": {
    "expected_outcome": "Reduce customer churn by 15% through proactive engagement",
    "actual_outcome": "Churn reduced by 22%, but support costs increased 30%",
    "delta": "Exceeded churn reduction target, but underestimated support resource needs",
    "lessons_learned": [
      "Proactive outreach works better than expected",
      "Need automation to scale engagement without linear support growth",
      "Should have piloted with subset before full rollout"
    ],
    "completion_date": "2024-03-31",
    "success_level": "partial",
    "would_repeat": false
  }
}
```

## Relationship Graph

Context objects can be explicitly linked to show causal relationships:

**Relationship Types:**
- `leads_to` - Idea → Decision
- `resulted_in` - Decision → Outcome
- `supports` - Evidence → Assumption
- `refutes` - Evidence → Assumption
- `implements` - Plan → Decision
- `depends_on` - Plan → Plan
- `contradicts` - Context → Context

**Example Queries:**
- "What assumptions supported this decision?"
- "What evidence was available at the time?"
- "Did the outcome justify the decision?"
- "Show me the full path from idea to outcome"

## API Endpoints

### Context Management

- `GET /context` - List context objects with filters
- `GET /context/{id}` - Get specific context
- `POST /context` - Create new context (auto-validates canonical format)
- `PATCH /context/{id}` - Update context
- `DELETE /context/{id}` - Soft delete context
- `POST /context/{id}/confirm` - Approve context
- `POST /context/{id}/reject` - Reject context

### Relationships

- `POST /context/relationships` - Create relationship between contexts
- `GET /context/{id}/relationships` - Get all relationships for a context
- `GET /context/{id}/related` - Get related context objects
- `DELETE /context/relationships` - Delete a relationship

### Validation

- `POST /context/validate` - Validate content against canonical schema
- `GET /context/types` - Get canonical type information and schemas

## Migration

To migrate existing context objects to canonical format:

```bash
# Dry run (shows what would be migrated)
python backend/scripts/migrate_to_canonical.py --dry-run

# Limit to first 10 contexts
python backend/scripts/migrate_to_canonical.py --dry-run --limit 10

# Apply migration
python backend/scripts/migrate_to_canonical.py
```

## Vendor & Procurement Reasoning

Without adding new ingestion flows, the canonical system now supports:

- **Contract ingestion** → Evidence
- **Vendor capabilities** → Assumptions
- **Risk assessments** → Decisions
- **Performance reviews** → Outcomes

**Example Queries:**
- "Do we already have a vendor that does something similar?"
- "What new risks does this vendor introduce?"
- "Have we made this procurement decision before?"
- "What assumptions were wrong last time?"

## Backward Compatibility

- Existing documents are automatically migrated via type inference
- No API breakage
- No required user action
- Legacy types (company, regulation, competitor, persona) map to Evidence

## Implementation Details

**Models:** `backend/models/canonical_types.py`
- Pydantic models for all 6 canonical types
- Validation schemas with required/optional fields
- Type inference and migration utilities

**Services:** `backend/services/context_db.py`
- Relationship CRUD operations
- Graph traversal methods

**Type Mapper:** `backend/reasoning/type_mapper.py`
- Legacy type → canonical type inference
- Content migration logic
- Backward compatibility layer

## Testing

Run tests for canonical types:

```bash
# If pytest is available
pytest backend/tests/test_canonical_types.py
pytest backend/tests/test_type_mapper.py
pytest backend/tests/test_relationships.py
```

## What This Enables

This canonicalization transforms Haystack into:

- **A business context layer** - Structured thinking artifacts, not loose documents
- **A decision memory system** - Never re-litigate past decisions
- **A risk detection engine** - Surface contradicting evidence and assumptions
- **A learning loop** - Compare outcomes to expectations continuously

You are no longer storing documents. **You are storing thinking artifacts.**
