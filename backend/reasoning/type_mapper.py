# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Type inference and migration utilities for canonical context types.

This module provides utilities to:
1. Infer canonical types from legacy context objects
2. Migrate existing data to canonical format
3. Map loosely-typed context to structured canonical types
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from backend.models.canonical_types import (
    AssumptionContent,
    DecisionContent,
    EvidenceContent,
    IdeaContent,
    OutcomeContent,
    PlanContent,
)


def infer_canonical_type(legacy_type: str, content: Dict[str, Any]) -> str:
    """
    Infer the canonical type from a legacy context type.

    Args:
        legacy_type: The old type (e.g., 'company', 'regulation', 'competitor')
        content: The content dictionary

    Returns:
        The canonical type (idea, decision, assumption, evidence, plan, outcome)
    """
    # Direct mappings
    type_mapping = {
        "assumption": "assumption",
        "decision": "decision",
        "idea": "idea",
        "evidence": "evidence",
        "plan": "plan",
        "outcome": "outcome",
        "retrospective": "outcome",
    }

    if legacy_type in type_mapping:
        return type_mapping[legacy_type]

    # Infer from content structure
    if "assumption" in content or "risk_if_wrong" in content:
        return "assumption"
    elif "decision" in content or "options_considered" in content:
        return "decision"
    elif "expected_outcome" in content and "actual_outcome" in content:
        return "outcome"
    elif "goal" in content and "steps" in content:
        return "plan"
    elif "source" in content and "claim_supported_or_refuted" in content:
        return "evidence"
    elif "proposed_solution" in content or "problem_statement" in content:
        return "idea"

    # Default to evidence for external facts (company, regulation, competitor, etc.)
    return "evidence"


def migrate_legacy_to_canonical(legacy_type: str, content: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Migrate a legacy context object to canonical format.

    Args:
        legacy_type: The legacy type
        content: The legacy content
        metadata: Optional metadata about the source

    Returns:
        Dictionary with 'type' and 'content' in canonical format
    """
    metadata = metadata or {}
    canonical_type = infer_canonical_type(legacy_type, content)

    # If already in canonical format, validate and return
    if canonical_type == legacy_type and _is_canonical_format(canonical_type, content):
        return {"type": canonical_type, "content": content}

    # Migrate based on canonical type
    if canonical_type == "assumption":
        return _migrate_to_assumption(content, metadata)
    elif canonical_type == "decision":
        return _migrate_to_decision(content, metadata)
    elif canonical_type == "evidence":
        return _migrate_to_evidence(legacy_type, content, metadata)
    elif canonical_type == "idea":
        return _migrate_to_idea(content, metadata)
    elif canonical_type == "plan":
        return _migrate_to_plan(content, metadata)
    elif canonical_type == "outcome":
        return _migrate_to_outcome(content, metadata)

    # Fallback to evidence
    return _migrate_to_evidence(legacy_type, content, metadata)


def _is_canonical_format(canonical_type: str, content: Dict[str, Any]) -> bool:
    """Check if content is already in canonical format."""
    required_fields = {
        "assumption": ["assumption", "confidence", "risk_if_wrong"],
        "decision": ["decision", "date", "options_considered", "rationale", "tradeoffs", "owner"],
        "evidence": ["source", "claim_supported_or_refuted", "freshness", "reliability_score", "external"],
        "idea": ["problem_statement", "proposed_solution", "target_user", "claimed_advantage", "confidence"],
        "plan": ["goal", "steps", "timeline", "dependencies"],
        "outcome": ["expected_outcome", "actual_outcome", "delta", "lessons_learned"],
    }

    if canonical_type not in required_fields:
        return False

    return all(field in content for field in required_fields[canonical_type])


def _migrate_to_assumption(content: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate legacy content to AssumptionContent format."""
    # Extract assumption text
    assumption_text = content.get("assumption") or content.get("description") or content.get("category", "Unknown assumption")

    if isinstance(assumption_text, dict):
        assumption_text = assumption_text.get("assumption") or str(assumption_text)

    canonical_content = {
        "assumption": assumption_text,
        "confidence": content.get("confidence", 0.5),
        "risk_if_wrong": content.get("risk_if_wrong") or content.get("rationale") or "Unknown risk",
        "evidence_links": content.get("evidence_links", []),
        "category": content.get("category"),
    }

    return {"type": "assumption", "content": canonical_content}


def _migrate_to_decision(content: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate legacy content to DecisionContent format."""
    canonical_content = {
        "decision": content.get("decision", "Decision not specified"),
        "date": content.get("date") or date.today().isoformat(),
        "options_considered": content.get("options_considered", ["Not documented"]),
        "rationale": content.get("rationale", "Rationale not documented"),
        "tradeoffs": content.get("tradeoffs", {"gained": "Not documented", "lost": "Not documented"}),
        "owner": content.get("owner", "Unknown"),
    }

    return {"type": "decision", "content": canonical_content}


def _migrate_to_evidence(legacy_type: str, content: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate legacy content to EvidenceContent format."""
    # Determine what claim this evidence supports
    claim = _extract_claim_from_legacy(legacy_type, content)

    canonical_content = {
        "source": content.get("source") or metadata.get("source") or f"Legacy {legacy_type} data",
        "claim_supported_or_refuted": claim,
        "freshness": content.get("freshness") or date.today().isoformat(),
        "reliability_score": content.get("reliability_score") or content.get("confidence", 0.5),
        "external": content.get("external", True),
        "summary": _summarize_legacy_content(content),
    }

    return {"type": "evidence", "content": canonical_content}


def _migrate_to_idea(content: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate legacy content to IdeaContent format."""
    canonical_content = {
        "problem_statement": content.get("problem_statement", "Problem not specified"),
        "proposed_solution": content.get("proposed_solution", "Solution not specified"),
        "target_user": content.get("target_user", "User not specified"),
        "claimed_advantage": content.get("claimed_advantage", "Advantage not specified"),
        "confidence": content.get("confidence", 0.5),
    }

    return {"type": "idea", "content": canonical_content}


def _migrate_to_plan(content: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate legacy content to PlanContent format."""
    steps = content.get("steps", [])
    if isinstance(steps, list) and steps and isinstance(steps[0], str):
        # Convert string steps to PlanStep format
        steps = [{"description": step} for step in steps]

    canonical_content = {
        "goal": content.get("goal", "Goal not specified"),
        "steps": steps or [{"description": "No steps defined"}],
        "timeline": content.get("timeline", "Timeline not specified"),
        "dependencies": content.get("dependencies", []),
    }

    return {"type": "plan", "content": canonical_content}


def _migrate_to_outcome(content: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate legacy content to OutcomeContent format."""
    canonical_content = {
        "expected_outcome": content.get("expected_outcome", "Expected outcome not documented"),
        "actual_outcome": content.get("actual_outcome", "Actual outcome not documented"),
        "delta": content.get("delta", "Delta not documented"),
        "lessons_learned": content.get("lessons_learned", ["Lessons not documented"]),
    }

    return {"type": "outcome", "content": canonical_content}


def _extract_claim_from_legacy(legacy_type: str, content: Dict[str, Any]) -> str:
    """Extract a claim from legacy content for evidence mapping."""
    if legacy_type == "company":
        name = content.get("name") or content.get("description", "")
        return f"Company profile and business model information for {name}"
    elif legacy_type == "regulation":
        name = content.get("name", "regulation")
        return f"Regulatory framework {name} applies to the business"
    elif legacy_type == "competitor":
        name = content.get("name", "competitor")
        relationship = content.get("relationship", "competitor")
        return f"{name} is a {relationship} in the market"
    elif legacy_type == "persona":
        archetype = content.get("archetype_name", "customer")
        return f"{archetype} represents a key customer segment"
    else:
        return f"Information about {legacy_type}"


def _summarize_legacy_content(content: Dict[str, Any]) -> str:
    """Create a summary from legacy content."""
    # Try common summary fields
    if "description" in content:
        return str(content["description"])
    elif "summary" in content:
        return str(content["summary"])
    elif "name" in content:
        return f"Information about {content['name']}"

    # Create a brief summary from available fields
    summary_parts = []
    for key, value in list(content.items())[:3]:
        if isinstance(value, (str, int, float)) and len(str(value)) < 100:
            summary_parts.append(f"{key}: {value}")

    return " | ".join(summary_parts) if summary_parts else "Legacy context data"
