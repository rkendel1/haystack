# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Supabase Document Store wrapper for backend services.

This module provides a convenient wrapper around the Haystack SupabaseDocumentStore
for use in backend applications.
"""

import os

from haystack.document_stores.supabase import SupabaseDocumentStore


def get_supabase_store(db_url: str = None) -> SupabaseDocumentStore:
    """
    Get or create a SupabaseDocumentStore instance.

    :param db_url: PostgreSQL connection URL. If not provided, reads from DATABASE_URL
        environment variable.
    :returns: SupabaseDocumentStore instance.
    """
    if db_url is None:
        db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")

    return SupabaseDocumentStore(db_url=db_url)
