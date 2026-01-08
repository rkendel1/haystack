# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Context management models.

This module defines the data models for context objects and onboarding sessions.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class CompanyInfo(BaseModel):
    """Model for company information during onboarding."""
    name: str = Field(..., description="Company name")
    website: Optional[str] = Field(None, description="Company website")
    industry: Optional[str] = Field(None, description="Industry sector")


class ContextObjectCreate(BaseModel):
    """Model for creating a new context object."""
    type: str = Field(..., description="Type of context (idea, decision, assumption, etc.)")
    content: Dict[str, Any] = Field(..., description="Content specific to the context type")
    source: str = Field(default="inferred", description="Source of the context (external, inferred, user)")
    confidence: Optional[float] = Field(default=None, description="Confidence score (0.0-1.0)")
    status: str = Field(default="pending", description="Status (pending, confirmed, rejected)")
    evidence_refs: Optional[List[str]] = Field(default=None, description="References to supporting evidence")


class ContextObject(BaseModel):
    """Model for a context object with database fields."""
    id: UUID = Field(..., description="Unique identifier")
    type: str = Field(..., description="Type of context")
    content: Dict[str, Any] = Field(..., description="Content specific to the context type")
    source: str = Field(..., description="Source of the context")
    confidence: Optional[float] = Field(None, description="Confidence score")
    status: str = Field(..., description="Status of the context")
    evidence_refs: Optional[List[str]] = Field(None, description="References to supporting evidence")
    version: int = Field(default=1, description="Version number for optimistic locking")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(None, description="Soft delete timestamp")

    class Config:
        from_attributes = True


class ContextObjectUpdate(BaseModel):
    """Model for updating a context object."""
    content: Optional[Dict[str, Any]] = Field(None, description="Updated content")
    status: Optional[str] = Field(None, description="Updated status")
    confidence: Optional[float] = Field(None, description="Updated confidence score")
    evidence_refs: Optional[List[str]] = Field(None, description="Updated evidence references")


class OnboardingSessionCreate(BaseModel):
    """Model for creating a new onboarding session."""
    user_id: str = Field(..., description="User identifier")
    company_name: str = Field(..., description="Company name")
    company_website: Optional[str] = Field(None, description="Company website")
    industry: Optional[str] = Field(None, description="Industry sector")


class OnboardingSession(BaseModel):
    """Model for an onboarding session."""
    id: UUID = Field(..., description="Unique identifier")
    user_id: str = Field(..., description="User identifier")
    company_name: str = Field(..., description="Company name")
    company_website: Optional[str] = Field(None, description="Company website")
    industry: Optional[str] = Field(None, description="Industry sector")
    current_step: str = Field(default="started", description="Current step in onboarding process")
    status: str = Field(default="active", description="Session status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class OnboardingSessionUpdate(BaseModel):
    """Model for updating an onboarding session."""
    current_step: Optional[str] = Field(None, description="Updated current step")
    status: Optional[str] = Field(None, description="Updated status")


class OnboardingContextResponse(BaseModel):
    """Response model for onboarding context discovery."""
    session_id: UUID = Field(..., description="Onboarding session ID")
    contexts: List[ContextObject] = Field(..., description="Discovered context objects")
    progress: Dict[str, Any] = Field(..., description="Progress information")
