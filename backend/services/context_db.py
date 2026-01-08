# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Database service layer for context management.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import psycopg2
from psycopg2.extras import RealDictCursor

from backend.models.context import (
    ContextObject,
    ContextObjectCreate,
    ContextObjectUpdate,
    OnboardingSession,
    OnboardingSessionCreate,
    OnboardingSessionUpdate,
)


class ContextDatabaseService:
    """Service for managing context objects in the database."""

    def __init__(self, db_url: Optional[str] = None):
        """Initialize the database service."""
        if db_url is None:
            db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")
        self.db_url = db_url

    def _get_connection(self):
        """Get a database connection."""
        return psycopg2.connect(self.db_url)

    # Context Object CRUD operations

    def create_context_object(self, context: ContextObjectCreate) -> ContextObject:
        """Create a new context object."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO context_objects (type, content, source, confidence, status, evidence_refs)
                    VALUES (%(type)s, %(content)s, %(source)s, %(confidence)s, %(status)s, %(evidence_refs)s)
                    RETURNING *
                    """,
                    {
                        "type": context.type,
                        "content": psycopg2.extras.Json(context.content),
                        "source": context.source,
                        "confidence": context.confidence,
                        "status": context.status,
                        "evidence_refs": psycopg2.extras.Json(context.evidence_refs),
                    },
                )
                row = cur.fetchone()
                conn.commit()
                return ContextObject(**row)

    def get_context_object(self, context_id: UUID) -> Optional[ContextObject]:
        """Get a context object by ID."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT * FROM context_objects
                    WHERE id = %s AND deleted_at IS NULL
                    """,
                    (str(context_id),),
                )
                row = cur.fetchone()
                if row:
                    return ContextObject(**row)
                return None

    def list_context_objects(
        self,
        context_type: Optional[str] = None,
        status: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ContextObject]:
        """List context objects with optional filters."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conditions = ["deleted_at IS NULL"]
                params = []

                if context_type:
                    conditions.append("type = %s")
                    params.append(context_type)
                if status:
                    conditions.append("status = %s")
                    params.append(status)
                if source:
                    conditions.append("source = %s")
                    params.append(source)

                where_clause = " AND ".join(conditions)
                params.extend([limit, offset])

                cur.execute(
                    f"""
                    SELECT * FROM context_objects
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()
                return [ContextObject(**row) for row in rows]

    def update_context_object(self, context_id: UUID, update: ContextObjectUpdate) -> Optional[ContextObject]:
        """Update a context object."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build update fields
                set_clauses = []
                params = {}

                if update.content is not None:
                    set_clauses.append("content = %(content)s")
                    params["content"] = psycopg2.extras.Json(update.content)
                if update.status is not None:
                    set_clauses.append("status = %(status)s")
                    params["status"] = update.status
                if update.confidence is not None:
                    set_clauses.append("confidence = %(confidence)s")
                    params["confidence"] = update.confidence
                if update.evidence_refs is not None:
                    set_clauses.append("evidence_refs = %(evidence_refs)s")
                    params["evidence_refs"] = psycopg2.extras.Json(update.evidence_refs)

                if not set_clauses:
                    return self.get_context_object(context_id)

                set_clauses.append("version = version + 1")
                params["context_id"] = str(context_id)

                cur.execute(
                    f"""
                    UPDATE context_objects
                    SET {', '.join(set_clauses)}
                    WHERE id = %(context_id)s AND deleted_at IS NULL
                    RETURNING *
                    """,
                    params,
                )
                row = cur.fetchone()
                conn.commit()
                if row:
                    return ContextObject(**row)
                return None

    def delete_context_object(self, context_id: UUID) -> bool:
        """Soft delete a context object."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE context_objects
                    SET deleted_at = now()
                    WHERE id = %s AND deleted_at IS NULL
                    RETURNING id
                    """,
                    (str(context_id),),
                )
                result = cur.fetchone()
                conn.commit()
                return result is not None

    def confirm_context_object(self, context_id: UUID) -> Optional[ContextObject]:
        """Confirm a context object."""
        return self.update_context_object(context_id, ContextObjectUpdate(status="confirmed"))

    def reject_context_object(self, context_id: UUID) -> Optional[ContextObject]:
        """Reject a context object."""
        return self.update_context_object(context_id, ContextObjectUpdate(status="rejected"))

    # Onboarding Session CRUD operations

    def create_onboarding_session(self, session: OnboardingSessionCreate) -> OnboardingSession:
        """Create a new onboarding session."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO onboarding_sessions (user_id, company_name, company_website, industry)
                    VALUES (%(user_id)s, %(company_name)s, %(company_website)s, %(industry)s)
                    RETURNING *
                    """,
                    {
                        "user_id": session.user_id,
                        "company_name": session.company_name,
                        "company_website": session.company_website,
                        "industry": session.industry,
                    },
                )
                row = cur.fetchone()
                conn.commit()
                return OnboardingSession(**row)

    def get_onboarding_session(self, session_id: UUID) -> Optional[OnboardingSession]:
        """Get an onboarding session by ID."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT * FROM onboarding_sessions
                    WHERE id = %s
                    """,
                    (str(session_id),),
                )
                row = cur.fetchone()
                if row:
                    return OnboardingSession(**row)
                return None

    def update_onboarding_session(self, session_id: UUID, update: OnboardingSessionUpdate) -> Optional[OnboardingSession]:
        """Update an onboarding session."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build update fields
                set_clauses = []
                params = {}

                if update.company_name is not None:
                    set_clauses.append("company_name = %(company_name)s")
                    params["company_name"] = update.company_name
                if update.company_website is not None:
                    set_clauses.append("company_website = %(company_website)s")
                    params["company_website"] = update.company_website
                if update.industry is not None:
                    set_clauses.append("industry = %(industry)s")
                    params["industry"] = update.industry
                if update.current_step is not None:
                    set_clauses.append("current_step = %(current_step)s")
                    params["current_step"] = update.current_step
                if update.status is not None:
                    set_clauses.append("status = %(status)s")
                    params["status"] = update.status
                    if update.status == "completed":
                        set_clauses.append("completed_at = now()")
                if update.metadata is not None:
                    set_clauses.append("metadata = %(metadata)s")
                    params["metadata"] = psycopg2.extras.Json(update.metadata)

                if not set_clauses:
                    return self.get_onboarding_session(session_id)

                params["session_id"] = str(session_id)

                cur.execute(
                    f"""
                    UPDATE onboarding_sessions
                    SET {', '.join(set_clauses)}
                    WHERE id = %(session_id)s
                    RETURNING *
                    """,
                    params,
                )
                row = cur.fetchone()
                conn.commit()
                if row:
                    return OnboardingSession(**row)
                return None

    def bulk_create_context_objects(self, contexts: List[ContextObjectCreate]) -> List[ContextObject]:
        """Bulk create context objects."""
        created = []
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for context in contexts:
                    cur.execute(
                        """
                        INSERT INTO context_objects (type, content, source, confidence, status, evidence_refs)
                        VALUES (%(type)s, %(content)s, %(source)s, %(confidence)s, %(status)s, %(evidence_refs)s)
                        RETURNING *
                        """,
                        {
                            "type": context.type,
                            "content": psycopg2.extras.Json(context.content),
                            "source": context.source,
                            "confidence": context.confidence,
                            "status": context.status,
                            "evidence_refs": psycopg2.extras.Json(context.evidence_refs),
                        },
                    )
                    row = cur.fetchone()
                    created.append(ContextObject(**row))
                conn.commit()
        return created

    # Context Relationship operations

    def create_relationship(
        self, from_context_id: UUID, to_context_id: UUID, relationship_type: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a relationship between two context objects."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO context_links (from_context_id, to_context_id, relationship_type, metadata)
                    VALUES (%(from_context_id)s, %(to_context_id)s, %(relationship_type)s, %(metadata)s)
                    ON CONFLICT (from_context_id, to_context_id, relationship_type) DO NOTHING
                    RETURNING *
                    """,
                    {
                        "from_context_id": str(from_context_id),
                        "to_context_id": str(to_context_id),
                        "relationship_type": relationship_type,
                        "metadata": psycopg2.extras.Json(metadata or {}),
                    },
                )
                row = cur.fetchone()
                conn.commit()
                return dict(row) if row else None

    def get_relationships(self, context_id: UUID, direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get relationships for a context object.

        Args:
            context_id: The context object ID
            direction: 'outgoing', 'incoming', or 'both'
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if direction == "outgoing":
                    cur.execute(
                        """
                        SELECT * FROM context_links
                        WHERE from_context_id = %s
                        ORDER BY created_at DESC
                        """,
                        (str(context_id),),
                    )
                elif direction == "incoming":
                    cur.execute(
                        """
                        SELECT * FROM context_links
                        WHERE to_context_id = %s
                        ORDER BY created_at DESC
                        """,
                        (str(context_id),),
                    )
                else:  # both
                    cur.execute(
                        """
                        SELECT * FROM context_links
                        WHERE from_context_id = %s OR to_context_id = %s
                        ORDER BY created_at DESC
                        """,
                        (str(context_id), str(context_id)),
                    )
                rows = cur.fetchall()
                return [dict(row) for row in rows]

    def delete_relationship(self, from_context_id: UUID, to_context_id: UUID, relationship_type: str) -> bool:
        """Delete a specific relationship."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM context_links
                    WHERE from_context_id = %s AND to_context_id = %s AND relationship_type = %s
                    RETURNING id
                    """,
                    (str(from_context_id), str(to_context_id), relationship_type),
                )
                result = cur.fetchone()
                conn.commit()
                return result is not None

    def get_related_contexts(
        self, context_id: UUID, relationship_type: Optional[str] = None, direction: str = "outgoing"
    ) -> List[ContextObject]:
        """
        Get context objects related to a given context.

        Args:
            context_id: The source context object ID
            relationship_type: Optional filter by relationship type
            direction: 'outgoing' or 'incoming'
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if direction == "outgoing":
                    query = """
                        SELECT co.* FROM context_objects co
                        JOIN context_links cl ON co.id = cl.to_context_id
                        WHERE cl.from_context_id = %s AND co.deleted_at IS NULL
                    """
                    params = [str(context_id)]
                else:  # incoming
                    query = """
                        SELECT co.* FROM context_objects co
                        JOIN context_links cl ON co.id = cl.from_context_id
                        WHERE cl.to_context_id = %s AND co.deleted_at IS NULL
                    """
                    params = [str(context_id)]

                if relationship_type:
                    query += " AND cl.relationship_type = %s"
                    params.append(relationship_type)

                query += " ORDER BY co.created_at DESC"

                cur.execute(query, params)
                rows = cur.fetchall()
                return [ContextObject(**row) for row in rows]
