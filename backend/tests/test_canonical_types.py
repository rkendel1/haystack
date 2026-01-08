# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for canonical context types.

These tests validate the canonical type schemas and validation logic.
"""

import pytest
from datetime import date
from pydantic import ValidationError

from backend.models.canonical_types import (
    IdeaContent,
    DecisionContent,
    AssumptionContent,
    EvidenceContent,
    PlanContent,
    OutcomeContent,
    validate_canonical_content,
    is_canonical_type,
    get_required_fields,
    CANONICAL_TYPE_MAP,
)


class TestIdeaContent:
    """Tests for IdeaContent canonical type."""

    def test_valid_idea(self):
        """Test creating a valid idea."""
        idea = IdeaContent(
            problem_statement="Sales team lacks context during calls",
            proposed_solution="Build real-time context panel",
            target_user="Account Executives",
            claimed_advantage="Reduces prep time from 30min to 2min",
            confidence=0.7,
        )
        assert idea.problem_statement == "Sales team lacks context during calls"
        assert idea.confidence == 0.7

    def test_idea_missing_required_field(self):
        """Test that missing required fields raise validation error."""
        with pytest.raises(ValidationError):
            IdeaContent(
                problem_statement="Some problem",
                # Missing required fields
            )

    def test_idea_with_optional_fields(self):
        """Test idea with optional fields."""
        idea = IdeaContent(
            problem_statement="Sales team lacks context during calls",
            proposed_solution="Build real-time context panel",
            target_user="Account Executives",
            claimed_advantage="Reduces prep time from 30min to 2min",
            confidence=0.7,
            constraints=["Must integrate with Salesforce"],
            risks=["Privacy concerns"],
        )
        assert len(idea.constraints) == 1
        assert len(idea.risks) == 1


class TestDecisionContent:
    """Tests for DecisionContent canonical type."""

    def test_valid_decision(self):
        """Test creating a valid decision."""
        decision = DecisionContent(
            decision="Use PostgreSQL instead of MongoDB",
            date=date(2024, 1, 15),
            options_considered=["MongoDB", "PostgreSQL", "DynamoDB"],
            rationale="Need ACID compliance",
            tradeoffs={"gained": "Consistency", "lost": "Flexibility"},
            owner="Engineering Lead",
        )
        assert decision.decision == "Use PostgreSQL instead of MongoDB"
        assert len(decision.options_considered) == 3

    def test_decision_requires_options(self):
        """Test that decisions require at least one option considered."""
        with pytest.raises(ValidationError):
            DecisionContent(
                decision="Some decision",
                date=date.today(),
                options_considered=[],  # Empty list should fail
                rationale="Some rationale",
                tradeoffs={"gained": "X", "lost": "Y"},
                owner="Someone",
            )


class TestAssumptionContent:
    """Tests for AssumptionContent canonical type."""

    def test_valid_assumption(self):
        """Test creating a valid assumption."""
        assumption = AssumptionContent(
            assumption="Customers will pay $99/month",
            confidence=0.6,
            risk_if_wrong="Revenue model collapses",
        )
        assert assumption.confidence == 0.6
        assert "revenue" in assumption.risk_if_wrong.lower()

    def test_assumption_confidence_bounds(self):
        """Test that confidence is bounded between 0 and 1."""
        with pytest.raises(ValidationError):
            AssumptionContent(
                assumption="Some assumption",
                confidence=1.5,  # Invalid: > 1.0
                risk_if_wrong="Some risk",
            )

        with pytest.raises(ValidationError):
            AssumptionContent(
                assumption="Some assumption",
                confidence=-0.1,  # Invalid: < 0.0
                risk_if_wrong="Some risk",
            )


class TestEvidenceContent:
    """Tests for EvidenceContent canonical type."""

    def test_valid_evidence(self):
        """Test creating valid evidence."""
        evidence = EvidenceContent(
            source="Gartner Report 2024",
            claim_supported_or_refuted="AI market growing at 40% YoY",
            freshness=date(2024, 1, 5),
            reliability_score=0.9,
            external=True,
        )
        assert evidence.external is True
        assert evidence.reliability_score == 0.9

    def test_evidence_requires_all_fields(self):
        """Test that all required fields are necessary."""
        with pytest.raises(ValidationError):
            EvidenceContent(
                source="Some source",
                claim_supported_or_refuted="Some claim",
                # Missing freshness, reliability_score, external
            )


class TestPlanContent:
    """Tests for PlanContent canonical type."""

    def test_valid_plan(self):
        """Test creating a valid plan."""
        plan = PlanContent(
            goal="Launch self-service onboarding",
            steps=[
                {"description": "Design screens", "owner": "Design team"},
                {"description": "Implement API", "owner": "Backend team"},
            ],
            timeline="6 weeks",
            dependencies=["Stripe integration"],
        )
        assert len(plan.steps) == 2
        assert plan.steps[0]["description"] == "Design screens"

    def test_plan_requires_steps(self):
        """Test that plan requires at least one step."""
        with pytest.raises(ValidationError):
            PlanContent(
                goal="Some goal",
                steps=[],  # Empty list should fail
                timeline="1 week",
                dependencies=[],
            )


class TestOutcomeContent:
    """Tests for OutcomeContent canonical type."""

    def test_valid_outcome(self):
        """Test creating a valid outcome."""
        outcome = OutcomeContent(
            expected_outcome="Reduce churn by 15%",
            actual_outcome="Churn reduced by 22%",
            delta="Exceeded target by 7 points",
            lessons_learned=["Proactive outreach works", "Need automation"],
        )
        assert len(outcome.lessons_learned) == 2

    def test_outcome_requires_lessons(self):
        """Test that outcome requires at least one lesson learned."""
        with pytest.raises(ValidationError):
            OutcomeContent(
                expected_outcome="Some expectation",
                actual_outcome="Some outcome",
                delta="Some delta",
                lessons_learned=[],  # Empty list should fail
            )


class TestCanonicalValidation:
    """Tests for canonical type validation utilities."""

    def test_validate_canonical_content_success(self):
        """Test successful validation of canonical content."""
        content = {
            "assumption": "Customers will pay",
            "confidence": 0.6,
            "risk_if_wrong": "Revenue fails",
        }
        validated = validate_canonical_content("assumption", content)
        assert isinstance(validated, AssumptionContent)

    def test_validate_canonical_content_invalid_type(self):
        """Test validation fails for non-canonical type."""
        with pytest.raises(ValueError, match="not a canonical type"):
            validate_canonical_content("invalid_type", {})

    def test_validate_canonical_content_invalid_content(self):
        """Test validation fails for invalid content."""
        with pytest.raises(ValueError, match="Content validation failed"):
            validate_canonical_content("assumption", {"invalid": "data"})

    def test_is_canonical_type(self):
        """Test canonical type checking."""
        assert is_canonical_type("idea") is True
        assert is_canonical_type("decision") is True
        assert is_canonical_type("invalid") is False

    def test_get_required_fields(self):
        """Test getting required fields for a type."""
        fields = get_required_fields("idea")
        assert "problem_statement" in fields
        assert "proposed_solution" in fields
        assert "target_user" in fields
        assert "claimed_advantage" in fields
        assert "confidence" in fields

    def test_canonical_type_map(self):
        """Test that CANONICAL_TYPE_MAP contains all 6 types."""
        assert len(CANONICAL_TYPE_MAP) == 6
        assert "idea" in CANONICAL_TYPE_MAP
        assert "decision" in CANONICAL_TYPE_MAP
        assert "assumption" in CANONICAL_TYPE_MAP
        assert "evidence" in CANONICAL_TYPE_MAP
        assert "plan" in CANONICAL_TYPE_MAP
        assert "outcome" in CANONICAL_TYPE_MAP
