-- SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
--
-- SPDX-License-Identifier: Apache-2.0

-- Enable required PostgreSQL extensions for vector search and text search

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
