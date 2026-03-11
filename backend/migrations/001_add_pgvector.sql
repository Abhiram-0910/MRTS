-- pgvector Migration Script
-- Run this ONCE against your PostgreSQL database as a superuser.
-- The application's init_db() will also attempt to run the first two
-- statements automatically on startup (non-superuser requires pg_extension
-- privileges granted by a DBA first).

-- ── 1. Install the pgvector extension ────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;

-- ── 2. Create media_embeddings table ─────────────────────────────────────────
-- Dimension must match the embedding model:
--   384  →  paraphrase-multilingual-MiniLM-L12-v2  (HuggingFace, default)
--   768  →  models/embedding-001                   (Gemini, if GEMINI_API_KEY set)
--
-- Set VECTOR_DIM env var before running init_db() to choose the dimension.
-- Changing the dimension later requires: DROP TABLE media_embeddings; then re-ingest.

CREATE TABLE IF NOT EXISTS media_embeddings (
    id          SERIAL       PRIMARY KEY,
    tmdb_id     INTEGER      NOT NULL,
    media_type  VARCHAR(16)  NOT NULL,      -- 'movie' | 'tv'
    embedding   vector(384),                -- change 384 → 768 for Gemini embeddings
    CONSTRAINT uq_media_embedding UNIQUE (tmdb_id, media_type)
);

-- ── 3. IVFFlat index for fast approximate nearest-neighbour search ────────────
-- lists = 100 is appropriate for up to ~1 million rows.
-- Rebuild this index (REINDEX) after bulk ingestion completes.
-- For datasets > 1M rows consider HNSW: CREATE INDEX ... USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_media_embeddings_ivfflat
    ON media_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ── 4. Verify installation ───────────────────────────────────────────────────
-- Run these to confirm the extension and table are ready:
--
--   SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
--   \d media_embeddings
--   EXPLAIN SELECT tmdb_id FROM media_embeddings ORDER BY embedding <=> '[0,0,...,0]' LIMIT 5;
