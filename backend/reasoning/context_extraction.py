# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Context extraction pipelines for onboarding.

These pipelines infer business context from minimal input.
All outputs are provisional and require user review.
"""

import json
import os
from typing import Any, Dict, List, Optional

from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator


class CompanyContextExtractor:
    """Extract company context from website and basic info."""

    def __init__(self):
        self.generator = OpenAIGenerator(model="gpt-4o-mini")

    def extract(self, company_name: str, website: str, industry: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract company context.

        Returns provisional company profile based on public information.
        """
        prompt = f"""Analyze the following company information and provide a structured business context.

Company Name: {company_name}
Website: {website}
Industry: {industry or 'Unknown'}

Provide a JSON response with the following structure:
{{
    "description": "Brief business description",
    "business_model": "B2B, B2C, B2B2C, Marketplace, etc.",
    "geography": ["Primary geographic markets"],
    "size_estimate": "startup | small | medium | large | enterprise",
    "founded_year": "Estimated or null",
    "key_products": ["Main products or services"],
    "confidence_notes": "What information is certain vs. inferred"
}}

Be conservative and mark uncertain information clearly. Only include what can be reasonably inferred.
If information is not available, use null values.

Respond with only the JSON object, no other text."""

        result = self.generator.run(prompt=prompt)
        response_text = result["replies"][0] if result.get("replies") else "{}"

        try:
            # Extract JSON from potential markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            company_data = json.loads(response_text)
            return {
                "type": "company",
                "content": company_data,
                "source": "inferred",
                "confidence": 0.6,
                "evidence_refs": [website],
            }
        except json.JSONDecodeError:
            # Fallback to basic info
            return {
                "type": "company",
                "content": {
                    "description": f"{company_name} - information pending",
                    "business_model": "Unknown",
                    "geography": [],
                    "size_estimate": None,
                },
                "source": "inferred",
                "confidence": 0.3,
                "evidence_refs": [website],
            }


class IndustryRegulationMapper:
    """Map industry to likely applicable regulations."""

    def __init__(self):
        self.generator = OpenAIGenerator(model="gpt-4o-mini")

    def map_regulations(self, industry: str, geography: List[str]) -> List[Dict[str, Any]]:
        """
        Map industry and geography to likely regulations.

        Returns provisional regulatory framework list.
        """
        geo_str = ", ".join(geography) if geography else "Global"
        prompt = f"""List the most likely regulatory frameworks that apply to companies in the following context:

Industry: {industry}
Geography: {geo_str}

Provide a JSON array of regulatory frameworks with this structure:
[
    {{
        "name": "Regulation name or framework",
        "jurisdiction": "US Federal | EU | California | UK | etc.",
        "category": "privacy | security | financial | health | labor | environmental | etc.",
        "relevance_reason": "Why this likely applies",
        "confidence": 0.0-1.0
    }}
]

Only include regulations that are highly likely to apply. Be conservative.
Limit to 5-8 most relevant frameworks.

Respond with only the JSON array, no other text."""

        result = self.generator.run(prompt=prompt)
        response_text = result["replies"][0] if result.get("replies") else "[]"

        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            regulations_data = json.loads(response_text)
            return [
                {
                    "type": "regulation",
                    "content": reg,
                    "source": "inferred",
                    "confidence": reg.get("confidence", 0.5),
                    "evidence_refs": [],
                }
                for reg in regulations_data
            ]
        except json.JSONDecodeError:
            return []


class CompetitiveLandscapeExtractor:
    """Extract competitive landscape information."""

    def __init__(self):
        self.generator = OpenAIGenerator(model="gpt-4o-mini")

    def extract_competitors(self, company_name: str, industry: str, business_model: str) -> List[Dict[str, Any]]:
        """
        Identify likely competitors and market position.

        Returns provisional competitive landscape.
        """
        prompt = f"""Identify likely competitors and market adjacencies for the following company:

Company: {company_name}
Industry: {industry}
Business Model: {business_model}

Provide a JSON array of competitors/adjacent companies:
[
    {{
        "name": "Competitor or adjacent company name",
        "relationship": "direct_competitor | indirect_competitor | adjacent_market | potential_partner",
        "similarity_reason": "Why this company is relevant",
        "confidence": 0.0-1.0
    }}
]

Only include well-known companies that are clearly relevant.
Limit to 5-7 most significant entries.

Respond with only the JSON array, no other text."""

        result = self.generator.run(prompt=prompt)
        response_text = result["replies"][0] if result.get("replies") else "[]"

        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            competitors_data = json.loads(response_text)
            return [
                {
                    "type": "competitor",
                    "content": comp,
                    "source": "inferred",
                    "confidence": comp.get("confidence", 0.5),
                    "evidence_refs": [],
                }
                for comp in competitors_data
            ]
        except json.JSONDecodeError:
            return []


class PersonaGenerator:
    """Generate constraint-based customer personas."""

    def __init__(self):
        self.generator = OpenAIGenerator(model="gpt-4o-mini")

    def generate_personas(self, company_name: str, industry: str, business_model: str) -> List[Dict[str, Any]]:
        """
        Generate customer personas based on business constraints.

        These are archetypes, NOT fictional individuals with demographics.
        """
        prompt = f"""Generate customer personas (archetypes) for a company with these characteristics:

Company: {company_name}
Industry: {industry}
Business Model: {business_model}

Provide a JSON array of personas as ROLES/ARCHETYPES (not individuals):
[
    {{
        "archetype_name": "Role or job title",
        "needs": ["Key needs this persona has"],
        "constraints": ["Budget, compliance, tech constraints"],
        "decision_criteria": ["What matters in vendor selection"],
        "typical_concerns": ["Common objections or risks"],
        "confidence": 0.0-1.0
    }}
]

Focus on ROLES and NEEDS, not demographics or fictional details.
Limit to 3-4 most important customer archetypes.

Respond with only the JSON array, no other text."""

        result = self.generator.run(prompt=prompt)
        response_text = result["replies"][0] if result.get("replies") else "[]"

        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            personas_data = json.loads(response_text)
            return [
                {
                    "type": "persona",
                    "content": persona,
                    "source": "inferred",
                    "confidence": persona.get("confidence", 0.5),
                    "evidence_refs": [],
                }
                for persona in personas_data
            ]
        except json.JSONDecodeError:
            return []


class OnboardingPipeline:
    """Orchestrate all context extraction during onboarding."""

    def __init__(self):
        self.company_extractor = CompanyContextExtractor()
        self.regulation_mapper = IndustryRegulationMapper()
        self.competitor_extractor = CompetitiveLandscapeExtractor()
        self.persona_generator = PersonaGenerator()

    def run(self, company_name: str, website: str, industry: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Run the full onboarding pipeline.

        Returns a list of context objects to be stored.
        """
        all_contexts = []

        # 1. Extract company context
        company_context = self.company_extractor.extract(company_name, website, industry)
        all_contexts.append(company_context)

        # Extract data from company context for subsequent pipelines
        company_data = company_context.get("content", {})
        detected_industry = industry or company_data.get("industry", "Technology")
        business_model = company_data.get("business_model", "Unknown")
        geography = company_data.get("geography", [])

        # 2. Map regulations
        regulations = self.regulation_mapper.map_regulations(detected_industry, geography)
        all_contexts.extend(regulations)

        # 3. Extract competitive landscape
        competitors = self.competitor_extractor.extract_competitors(company_name, detected_industry, business_model)
        all_contexts.extend(competitors)

        # 4. Generate customer personas
        personas = self.persona_generator.generate_personas(company_name, detected_industry, business_model)
        all_contexts.extend(personas)

        # 5. Add baseline assumptions
        assumptions = self._generate_baseline_assumptions(company_data)
        all_contexts.extend(assumptions)

        return all_contexts

    def _generate_baseline_assumptions(self, company_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate baseline assumptions about the business context."""
        assumptions = []

        # Assumption about data handling
        assumptions.append(
            {
                "type": "assumption",
                "content": {
                    "category": "data_handling",
                    "assumption": "Company collects and processes customer data",
                    "rationale": "Most modern businesses handle some customer information",
                },
                "source": "inferred",
                "confidence": 0.7,
                "evidence_refs": [],
            }
        )

        # Assumption about vendor relationships
        assumptions.append(
            {
                "type": "assumption",
                "content": {
                    "category": "vendor_usage",
                    "assumption": "Company uses third-party vendors for operations",
                    "rationale": "Standard business practice for SaaS, cloud, and support services",
                },
                "source": "inferred",
                "confidence": 0.8,
                "evidence_refs": [],
            }
        )

        # Assumption about compliance needs
        assumptions.append(
            {
                "type": "assumption",
                "content": {
                    "category": "compliance",
                    "assumption": "Company needs to maintain compliance documentation",
                    "rationale": "Required for most regulated industries and B2B sales",
                },
                "source": "inferred",
                "confidence": 0.7,
                "evidence_refs": [],
            }
        )

        return assumptions
