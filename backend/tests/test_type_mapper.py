# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for type mapper and migration utilities.
"""

import pytest
from datetime import date

from backend.reasoning.type_mapper import (
    infer_canonical_type,
    migrate_legacy_to_canonical,
    _migrate_to_assumption,
    _migrate_to_evidence,
)


class TestTypeInference:
    """Tests for canonical type inference."""

    def test_infer_assumption(self):
        """Test inferring assumption type."""
        content = {
            "assumption": "Customers will pay",
            "risk_if_wrong": "Revenue fails",
        }
        assert infer_canonical_type("unknown", content) == "assumption"

    def test_infer_decision(self):
        """Test inferring decision type."""
        content = {
            "decision": "Use PostgreSQL",
            "options_considered": ["MongoDB", "PostgreSQL"],
        }
        assert infer_canonical_type("unknown", content) == "decision"

    def test_infer_outcome(self):
        """Test inferring outcome type."""
        content = {
            "expected_outcome": "Reduce churn by 15%",
            "actual_outcome": "Reduced by 22%",
        }
        assert infer_canonical_type("unknown", content) == "outcome"

    def test_infer_plan(self):
        """Test inferring plan type."""
        content = {
            "goal": "Launch feature",
            "steps": ["Design", "Build", "Test"],
        }
        assert infer_canonical_type("unknown", content) == "plan"

    def test_infer_evidence(self):
        """Test inferring evidence type."""
        content = {
            "source": "Report 2024",
            "claim_supported_or_refuted": "Market is growing",
        }
        assert infer_canonical_type("unknown", content) == "evidence"

    def test_direct_mapping(self):
        """Test direct type mappings."""
        assert infer_canonical_type("assumption", {}) == "assumption"
        assert infer_canonical_type("decision", {}) == "decision"
        assert infer_canonical_type("retrospective", {}) == "outcome"

    def test_legacy_types_to_evidence(self):
        """Test that legacy types default to evidence."""
        assert infer_canonical_type("company", {}) == "evidence"
        assert infer_canonical_type("competitor", {}) == "evidence"
        assert infer_canonical_type("regulation", {}) == "evidence"


class TestLegacyMigration:
    """Tests for migrating legacy content to canonical format."""

    def test_migrate_assumption_with_all_fields(self):
        """Test migrating a well-formed assumption."""
        legacy = {
            "assumption": "Users will adopt new UI",
            "confidence": 0.7,
            "risk_if_wrong": "Poor user experience",
            "category": "product",
        }
        result = migrate_legacy_to_canonical("assumption", legacy)

        assert result["type"] == "assumption"
        assert result["content"]["assumption"] == "Users will adopt new UI"
        assert result["content"]["confidence"] == 0.7
        assert result["content"]["risk_if_wrong"] == "Poor user experience"

    def test_migrate_legacy_assumption_minimal(self):
        """Test migrating assumption with minimal fields."""
        legacy = {
            "category": "compliance",
            "assumption": "GDPR applies",
            "rationale": "We handle EU data",
        }
        result = migrate_legacy_to_canonical("assumption", legacy)

        assert result["type"] == "assumption"
        assert result["content"]["assumption"] == "GDPR applies"
        assert "risk_if_wrong" in result["content"]

    def test_migrate_company_to_evidence(self):
        """Test migrating company context to evidence."""
        legacy = {
            "name": "Acme Corp",
            "description": "B2B SaaS company",
            "business_model": "Subscription",
        }
        result = migrate_legacy_to_canonical("company", legacy)

        assert result["type"] == "evidence"
        assert "source" in result["content"]
        assert "claim_supported_or_refuted" in result["content"]
        assert "Acme Corp" in result["content"]["claim_supported_or_refuted"]

    def test_migrate_regulation_to_evidence(self):
        """Test migrating regulation to evidence."""
        legacy = {
            "name": "GDPR",
            "jurisdiction": "EU",
            "relevance_reason": "We handle EU customer data",
        }
        result = migrate_legacy_to_canonical("regulation", legacy)

        assert result["type"] == "evidence"
        assert "GDPR" in result["content"]["claim_supported_or_refuted"]

    def test_migrate_competitor_to_evidence(self):
        """Test migrating competitor to evidence."""
        legacy = {
            "name": "CompetitorX",
            "relationship": "direct_competitor",
            "similarity_reason": "Same market segment",
        }
        result = migrate_legacy_to_canonical("competitor", legacy)

        assert result["type"] == "evidence"
        assert "CompetitorX" in result["content"]["claim_supported_or_refuted"]

    def test_migrate_preserves_metadata(self):
        """Test that migration preserves important metadata."""
        legacy = {
            "assumption": "Users prefer simple UI",
            "confidence": 0.8,
        }
        metadata = {"source": "user_research", "date": "2024-01-01"}
        result = migrate_legacy_to_canonical("assumption", legacy, metadata)

        # The metadata should inform the migration
        assert result["type"] == "assumption"
        assert result["content"]["confidence"] == 0.8

    def test_migrate_handles_nested_assumption(self):
        """Test handling nested assumption structures."""
        legacy = {
            "category": "technical",
            "assumption": {
                "assumption": "API can handle 1000 RPS",
            },
        }
        result = _migrate_to_assumption(legacy, {})

        assert result["type"] == "assumption"
        # Should extract the nested assumption text
        assert "assumption" in result["content"]


class TestMigrationEdgeCases:
    """Tests for edge cases in migration."""

    def test_migrate_empty_content(self):
        """Test migrating empty content."""
        result = migrate_legacy_to_canonical("unknown", {})
        assert result["type"] == "evidence"

    def test_migrate_malformed_content(self):
        """Test migrating malformed content gracefully."""
        legacy = {
            "random_field": "random_value",
            "another_field": 123,
        }
        result = migrate_legacy_to_canonical("unknown", legacy)

        # Should default to evidence
        assert result["type"] == "evidence"
        assert "content" in result

    def test_migrate_already_canonical(self):
        """Test that already canonical content passes through."""
        canonical = {
            "assumption": "Market will grow",
            "confidence": 0.7,
            "risk_if_wrong": "Investment fails",
        }
        result = migrate_legacy_to_canonical("assumption", canonical)

        assert result["type"] == "assumption"
        assert result["content"]["assumption"] == "Market will grow"
