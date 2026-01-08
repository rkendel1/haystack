#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Migration script to convert existing context objects to canonical format.

This script:
1. Connects to the database
2. Fetches all existing context objects
3. Infers canonical types
4. Migrates content to canonical format
5. Updates the database

Usage:
    python migrate_to_canonical.py [--dry-run] [--limit N]
"""

import argparse
import os
import sys
from typing import List, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.reasoning.type_mapper import infer_canonical_type, migrate_legacy_to_canonical
from backend.models.canonical_types import validate_canonical_content, is_canonical_type


def get_db_connection(db_url: str = None):
    """Get database connection."""
    if db_url is None:
        db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")
    return psycopg2.connect(db_url)


def fetch_legacy_contexts(conn, limit: int = None) -> List[dict]:
    """Fetch context objects that may need migration."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = """
            SELECT id, type, content, source, confidence, evidence_refs, version, created_at
            FROM context_objects
            WHERE deleted_at IS NULL
        """
        if limit:
            query += f" LIMIT {limit}"

        cur.execute(query)
        return [dict(row) for row in cur.fetchall()]


def analyze_context(context: dict) -> Tuple[str, bool, str]:
    """
    Analyze a context object and determine if migration is needed.

    Returns:
        (canonical_type, needs_migration, reason)
    """
    context_type = context["type"]
    content = context["content"]

    # Check if already canonical
    if is_canonical_type(context_type):
        try:
            # Validate if content already matches canonical format
            validate_canonical_content(context_type, content)
            return (context_type, False, "Already in canonical format")
        except ValueError as e:
            return (context_type, True, f"Type is canonical but content needs fixing: {str(e)}")

    # Infer canonical type
    canonical_type = infer_canonical_type(context_type, content)
    return (canonical_type, True, f"Legacy type '{context_type}' → canonical '{canonical_type}'")


def migrate_context(context: dict, dry_run: bool = True) -> dict:
    """
    Migrate a single context object to canonical format.

    Returns:
        Updated context dict with canonical type and content
    """
    canonical_type, needs_migration, reason = analyze_context(context)

    if not needs_migration:
        return {
            "id": context["id"],
            "action": "skip",
            "reason": reason,
            "old_type": context["type"],
            "new_type": canonical_type,
        }

    # Perform migration
    migrated = migrate_legacy_to_canonical(
        legacy_type=context["type"],
        content=context["content"],
        metadata={
            "source": context["source"],
            "confidence": context["confidence"],
            "evidence_refs": context["evidence_refs"],
        },
    )

    # Validate the migrated content
    try:
        validate_canonical_content(migrated["type"], migrated["content"])
        validation_status = "valid"
    except ValueError as e:
        validation_status = f"invalid: {str(e)}"

    return {
        "id": context["id"],
        "action": "migrate" if not dry_run else "would_migrate",
        "reason": reason,
        "old_type": context["type"],
        "new_type": migrated["type"],
        "new_content": migrated["content"],
        "validation": validation_status,
    }


def apply_migration(conn, context_id: str, new_type: str, new_content: dict):
    """Apply migration to database."""
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE context_objects
            SET type = %s, content = %s, version = version + 1
            WHERE id = %s
            """,
            (new_type, psycopg2.extras.Json(new_content), context_id),
        )
    conn.commit()


def main():
    """Main migration script."""
    parser = argparse.ArgumentParser(description="Migrate context objects to canonical format")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without applying changes")
    parser.add_argument("--limit", type=int, help="Limit number of contexts to process")
    parser.add_argument("--db-url", help="Database URL (defaults to DATABASE_URL env var)")
    args = parser.parse_args()

    print("=" * 80)
    print("Context Canonicalization Migration")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE MIGRATION'}")
    print()

    # Connect to database
    try:
        conn = get_db_connection(args.db_url)
        print(f"✓ Connected to database")
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        return 1

    # Fetch contexts
    try:
        contexts = fetch_legacy_contexts(conn, args.limit)
        print(f"✓ Found {len(contexts)} context objects")
        print()
    except Exception as e:
        print(f"✗ Failed to fetch contexts: {e}")
        return 1

    # Analyze and migrate
    results = {
        "skip": 0,
        "migrate": 0,
        "would_migrate": 0,
        "errors": 0,
    }

    for i, context in enumerate(contexts, 1):
        try:
            result = migrate_context(context, dry_run=args.dry_run)

            # Print progress
            print(f"[{i}/{len(contexts)}] {result['old_type']} → {result['new_type']}: {result['action']}")
            if result["action"] in ["migrate", "would_migrate"] and result.get("validation") != "valid":
                print(f"    ⚠ Validation: {result['validation']}")

            # Apply migration if not dry run
            if not args.dry_run and result["action"] == "migrate" and result.get("validation") == "valid":
                apply_migration(conn, result["id"], result["new_type"], result["new_content"])

            # Update stats
            results[result["action"]] = results.get(result["action"], 0) + 1

        except Exception as e:
            print(f"    ✗ Error: {e}")
            results["errors"] += 1

    # Summary
    print()
    print("=" * 80)
    print("Migration Summary")
    print("=" * 80)
    print(f"Total contexts:    {len(contexts)}")
    print(f"Skipped:           {results['skip']}")
    if args.dry_run:
        print(f"Would migrate:     {results['would_migrate']}")
    else:
        print(f"Migrated:          {results['migrate']}")
    print(f"Errors:            {results['errors']}")

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
