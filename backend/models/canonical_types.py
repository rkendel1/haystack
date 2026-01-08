# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Canonical context type models.

This module defines the six canonical types that normalize all context artifacts:
1. Ideas - Uncommitted concepts and hypotheses
2. Decisions - Explicit commitments
3. Assumptions - Beliefs taken as true
4. Evidence - Support or refutation
5. Plans - Intent and execution tracking
6. Outcomes - What actually happened
"""

from datetime import date as DateType
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IdeaContent(BaseModel):
    """
    Uncommitted concepts that may or may not be pursued.
    
    Purpose:
    - Compare new ideas to prior thinking
    - Detect idea recycling
    - Enable challenge before commitment
    """
    problem_statement: str = Field(..., description="Problem or opportunity being addressed")
    proposed_solution: str = Field(..., description="How this idea proposes to solve the problem")
    target_user: str = Field(..., description="Who benefits from this idea")
    claimed_advantage: str = Field(..., description="Why this is better than alternatives")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in viability (0.0-1.0)")
    constraints: Optional[List[str]] = Field(default=None, description="Constraints to consider")
    risks: Optional[List[str]] = Field(default=None, description="Potential risks")


class DecisionContent(BaseModel):
    """
    Explicit commitments that prevent re-litigation and enable historical reasoning.
    
    Purpose:
    - Prevent decision re-litigation
    - Enable historical reasoning
    - Support "what changed?" queries
    """
    decision: str = Field(..., description="The decision that was made")
    date: DateType = Field(..., description="Date the decision was made")
    options_considered: List[str] = Field(..., min_length=1, description="Alternative options that were evaluated")
    rationale: str = Field(..., description="Why this decision was made")
    tradeoffs: Dict[str, str] = Field(..., description="Key tradeoffs accepted (what was gained vs lost)")
    owner: str = Field(..., description="Person or team responsible for this decision")
    reversibility: Optional[str] = Field(default=None, description="How hard would it be to reverse this decision")
    success_criteria: Optional[List[str]] = Field(default=None, description="How to measure if this decision was correct")


class AssumptionContent(BaseModel):
    """
    Beliefs taken as true that underpin decisions and plans.
    
    Purpose:
    - Surface hidden risk
    - Enable assumption decay tracking
    - Allow contradiction detection
    """
    assumption: str = Field(..., description="The assumption being made")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence this assumption is valid (0.0-1.0)")
    risk_if_wrong: str = Field(..., description="What happens if this assumption is incorrect")
    validity_period: Optional[str] = Field(default=None, description="How long this assumption is expected to hold")
    evidence_refs: Optional[List[str]] = Field(default=None, description="References to supporting evidence")


class EvidenceContent(BaseModel):
    """
    Support or refutation for claims, assumptions, or decisions.
    
    Purpose:
    - Enable contradiction detection
    - Support confidence scoring
    - Track source reliability
    """
    source: str = Field(..., description="Where this evidence came from")
    claim_supported_or_refuted: str = Field(..., description="The claim this evidence addresses")
    freshness: DateType = Field(..., description="When this evidence was gathered")
    reliability_score: float = Field(..., ge=0.0, le=1.0, description="How reliable this source is (0.0-1.0)")
    external: bool = Field(..., description="Whether this evidence came from outside the organization")
    contradicts: Optional[List[str]] = Field(default=None, description="References to context this contradicts")


class PlanContent(BaseModel):
    """
    Intent and execution tracking.
    
    Purpose:
    - Compare plan to outcome
    - Detect execution drift
    - Enable "why didn't we do X?" queries
    """
    goal: str = Field(..., description="What this plan aims to achieve")
    steps: List[Dict[str, Any]] = Field(..., min_length=1, description="Steps to execute the plan")
    timeline: str = Field(..., description="When this plan should be executed")
    dependencies: List[str] = Field(..., description="What this plan depends on")
    success_metrics: Optional[List[str]] = Field(default=None, description="How to measure plan success")
    owner: Optional[str] = Field(default=None, description="Who is responsible for this plan")


class OutcomeContent(BaseModel):
    """
    What actually happened.
    
    Purpose:
    - Compare to plan/expectations
    - Derive lessons learned
    - Improve future predictions
    """
    expected_outcome: str = Field(..., description="What was expected to happen")
    actual_outcome: str = Field(..., description="What actually happened")
    delta: str = Field(..., description="Difference between expected and actual")
    lessons_learned: List[str] = Field(..., min_length=1, description="What we learned from this outcome")
    date: Optional[DateType] = Field(default=None, description="When this outcome occurred")
    related_plan: Optional[str] = Field(default=None, description="Reference to the plan this relates to")


# Map of canonical type names to their model classes
CANONICAL_TYPE_MAP: Dict[str, type[BaseModel]] = {
    "idea": IdeaContent,
    "decision": DecisionContent,
    "assumption": AssumptionContent,
    "evidence": EvidenceContent,
    "plan": PlanContent,
    "outcome": OutcomeContent,
}


# Relationship types
class RelationshipType:
    """Relationship types between context objects."""
    SUPPORTS = "supports"
    REFUTES = "refutes"
    LEADS_TO = "leads_to"
    RESULTED_IN = "resulted_in"
    IMPLEMENTS = "implements"
    DEPENDS_ON = "depends_on"


class ContextRelationship(BaseModel):
    """Model for a relationship between two context objects."""
    from_context_id: str = Field(..., description="Source context ID")
    to_context_id: str = Field(..., description="Target context ID")
    relationship_type: str = Field(..., description="Type of relationship")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional relationship metadata")


def is_canonical_type(type_name: str) -> bool:
    """
    Check if a type name is a valid canonical type.
    
    Args:
        type_name: The type name to check
        
    Returns:
        True if the type is canonical, False otherwise
    """
    return type_name in CANONICAL_TYPE_MAP


def validate_canonical_content(context_type: str, content: Dict[str, Any]) -> BaseModel:
    """
    Validate that content conforms to the canonical schema for the given type.
    
    Args:
        context_type: The canonical type name
        content: The content dictionary to validate
        
    Returns:
        Validated Pydantic model instance
        
    Raises:
        ValueError: If the type is not canonical or content is invalid
    """
    if not is_canonical_type(context_type):
        raise ValueError(f"'{context_type}' is not a canonical type")
    
    model_class = CANONICAL_TYPE_MAP[context_type]
    
    try:
        return model_class(**content)
    except Exception as e:
        raise ValueError(f"Content validation failed for type '{context_type}': {str(e)}")


def get_required_fields(type_name: str) -> List[str]:
    """
    Get the list of required fields for a canonical type.
    
    Args:
        type_name: The canonical type name
        
    Returns:
        List of required field names
        
    Raises:
        ValueError: If the type is not canonical
    """
    if not is_canonical_type(type_name):
        raise ValueError(f"'{type_name}' is not a canonical type")
    
    model_class = CANONICAL_TYPE_MAP[type_name]
    required_fields = []
    
    for field_name, field_info in model_class.model_fields.items():
        if field_info.is_required():
            required_fields.append(field_name)
    
    return required_fields
