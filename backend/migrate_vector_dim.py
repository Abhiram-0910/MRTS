"""
migrate_vector_dim.py — Upgrade embedding column from vector(384) → vector(768)

Context
-------
When we switched the embedding model from HuggingFace paraphrase-MiniLM-L12-v2
(384 dimensions) to Google Gemini text-embedding-004 (768 dimensions), the
rag_engine.py added a zero-padding shim as a short-term fix.

This script performs the proper schema migration:
    ALTER TABLE media_embeddings ALTER COLUMN embedding TYPE vector(768)

Run once, then remove the zero-padding shim from rag_engine.py.

Usage
-----
    cd backend/
    python migrate_vector_dim.py            # dry-run preview
    python migrate_vector_dim.py --execute  # actually run the migration

Prerequisites
-------------
    DATABASE_URL set in .env  (e.g. postgresql://user:pass@localhost/dbname)
    pip install psycopg2-binary python-dotenv
"""

import argparse
import sys
from textwrap import dedent

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# ── Config ────────────────────────────────────────────────────────────────────

TARGET_TABLE  = "media_embeddings"
TARGET_COLUMN = "embedding"
OLD_DIM       = 384
NEW_DIM       = 768

# ── Helpers ───────────────────────────────────────────────────────────────────

def _connect(database_url: str):
    """Open a raw psycopg2 connection with autocommit OFF (we manage tx)."""
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        return conn
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Cannot connect to database: {e}")
        sys.exit(1)


def check_pgvector(cur) -> bool:
    """Return True if the pgvector extension is installed in this database."""
    cur.execute(
        "SELECT 1 FROM pg_extension WHERE extname = 'vector';"
    )
    return cur.fetchone() is not None


def check_table_exists(cur, table: str) -> bool:
    """Return True if *table* exists in the public schema."""
    cur.execute(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name   = %s;
        """,
        (table,),
    )
    return cur.fetchone() is not None


def get_current_dim(cur, table: str, column: str) -> int | None:
    """
    Return the current vector dimension of *column* in *table*, or None if the
    column does not exist or is not a vector type.
    """
    # pg_attribute stores atttypmod which encodes the dimension for vector types.
    # For pgvector: atttypmod = dimension + 4  (the +4 is a pg internal offset).
    cur.execute(
        """
        SELECT atttypmod
        FROM   pg_attribute
        JOIN   pg_class  ON pg_class.oid  = pg_attribute.attrelid
        JOIN   pg_type   ON pg_type.oid   = pg_attribute.atttypid
        WHERE  pg_class.relname  = %s
          AND  pg_attribute.attname = %s
          AND  pg_type.typname   = 'vector'
          AND  pg_attribute.attnum > 0
          AND  NOT pg_attribute.attisdropped;
        """,
        (table, column),
    )
    row = cur.fetchone()
    if row is None:
        return None
    atttypmod = row[0]
    # atttypmod == -1 means no modifier (shouldn't happen for vector)
    return (atttypmod - 4) if atttypmod > 0 else None


def get_dependent_indexes(cur, table: str, column: str) -> list[dict]:
    """
    Return all indexes on *table* that reference *column*.
    pgvector HNSW/IVFFlat indexes on the embedding column must be dropped before
    ALTER TABLE can change the type — Postgres will refuse otherwise.
    """
    cur.execute(
        """
        SELECT
            i.relname  AS index_name,
            ix.indisprimary AS is_primary,
            pg_get_indexdef(ix.indexrelid) AS index_def
        FROM
            pg_index ix
            JOIN pg_class t  ON t.oid  = ix.indrelid
            JOIN pg_class i  ON i.oid  = ix.indexrelid
            JOIN pg_attribute a ON a.attrelid = t.oid
                                AND a.attnum = ANY(ix.indkey)
        WHERE
            t.relname   = %s
            AND a.attname = %s
            AND NOT ix.indisprimary;
        """,
        (table, column),
    )
    return [
        {"name": row[0], "is_primary": row[1], "def": row[2]}
        for row in cur.fetchall()
    ]


# ── Main migration logic ───────────────────────────────────────────────────────

def run_migration(database_url: str, execute: bool) -> None:
    mode = "EXECUTE" if execute else "DRY-RUN"
    print(f"\n{'='*60}")
    print(f"  Vector dimension migration  [{mode}]")
    print(f"  {TARGET_TABLE}.{TARGET_COLUMN}: vector({OLD_DIM}) → vector({NEW_DIM})")
    print(f"{'='*60}\n")

    conn = _connect(database_url)
    cur  = conn.cursor()

    try:
        # ── Pre-flight checks ─────────────────────────────────────────────────

        print("[ 1/5 ] Checking pgvector extension …")
        if not check_pgvector(cur):
            print(
                "[ERROR] pgvector extension is NOT installed.\n"
                "        Run:  CREATE EXTENSION IF NOT EXISTS vector;\n"
                "        then retry this script."
            )
            sys.exit(1)
        print("        ✓ pgvector is installed.\n")

        print(f"[ 2/5 ] Checking table '{TARGET_TABLE}' exists …")
        if not check_table_exists(cur, TARGET_TABLE):
            print(
                f"[ERROR] Table '{TARGET_TABLE}' does not exist.\n"
                f"        Has the initial schema migration been run?\n"
                f"        Check backend/migrations/001_add_pgvector.sql"
            )
            sys.exit(1)
        print(f"        ✓ Table '{TARGET_TABLE}' found.\n")

        print(f"[ 3/5 ] Reading current column dimension …")
        current_dim = get_current_dim(cur, TARGET_TABLE, TARGET_COLUMN)

        if current_dim is None:
            print(
                f"[ERROR] Column '{TARGET_COLUMN}' does not exist in '{TARGET_TABLE}' "
                f"or is not a vector type.\n"
                f"        Check your schema."
            )
            sys.exit(1)

        print(f"        Current dim = {current_dim}")

        if current_dim == NEW_DIM:
            print(
                f"\n[INFO ] Column is already vector({NEW_DIM}). No migration needed.\n"
                f"        Exiting without changes."
            )
            sys.exit(0)

        if current_dim != OLD_DIM:
            print(
                f"\n[WARN ] Expected current dim={OLD_DIM} but found {current_dim}.\n"
                f"        Proceeding anyway — the ALTER TABLE will upgrade to {NEW_DIM}.\n"
            )
        else:
            print(f"        ✓ Confirmed vector({OLD_DIM}) — ready to migrate.\n")

        # ── Dependent index handling ───────────────────────────────────────────

        print(f"[ 4/5 ] Checking for indexes on '{TARGET_COLUMN}' to drop first …")
        indexes = get_dependent_indexes(cur, TARGET_TABLE, TARGET_COLUMN)

        drop_statements   = []
        create_statements = []

        if indexes:
            for idx in indexes:
                print(f"        Found: {idx['name']}")
                print(f"        Def  : {idx['def']}")
                drop_statements.append(
                    f"DROP INDEX IF EXISTS {idx['name']};"
                )
                # We'll recreate with the same definition but updated dimension:
                # The user should rebuild HNSW/IVFFlat indexes manually because the
                # optimal ef_construction/m parameters may differ at 768 dims.
                create_statements.append(
                    f"-- Regenerate: {idx['def']}  (adjust params for 768 dims)"
                )
            print(
                f"\n[WARN ] {len(indexes)} dependent index(es) will be DROPPED and must be\n"
                f"        recreated after migration. See 'Recreate indexes' section below.\n"
            )
        else:
            print("        ✓ No dependent vector indexes found.\n")

        # ── Print plan ────────────────────────────────────────────────────────

        print("[ 5/5 ] Migration SQL plan:\n")
        all_sql = []
        all_sql.extend(drop_statements)
        all_sql.append(
            f"ALTER TABLE {TARGET_TABLE} "
            f"ALTER COLUMN {TARGET_COLUMN} TYPE vector({NEW_DIM});"
        )
        for stmt in all_sql:
            print(f"        {stmt}")

        if create_statements:
            print("\n        -- Recreate indexes (run manually after verifying embeddings):\"")
            for stmt in create_statements:
                print(f"        {stmt}")

        print()

        if not execute:
            print(
                "[DRY-RUN] No changes made. Re-run with --execute to apply.\n"
            )
            return

        # ── Execute ───────────────────────────────────────────────────────────

        print("[EXECUTE] Applying migration inside a transaction …\n")

        for stmt in all_sql:
            print(f"  → {stmt}")
            cur.execute(stmt)

        conn.commit()
        print(
            f"\n[SUCCESS] Column '{TARGET_TABLE}.{TARGET_COLUMN}' is now vector({NEW_DIM}).\n"
        )

        if create_statements:
            print(
                "  ⚠  Remember to rebuild your HNSW/IVFFlat indexes.\n"
                "     Example for HNSW (adjust m and ef_construction for your dataset):\n\n"
                f"     CREATE INDEX ON {TARGET_TABLE}\n"
                f"     USING hnsw ({TARGET_COLUMN} vector_cosine_ops)\n"
                f"     WITH (m = 16, ef_construction = 64);\n"
            )

        print(
            "  Next step: remove the zero-padding shim in rag_engine.py once all\n"
            "  existing rows have been re-embedded with the Gemini 768-dim model.\n"
        )

    except psycopg2.Error as db_err:
        conn.rollback()
        print(f"\n[DB ERROR] Transaction rolled back.\n  {db_err}")
        sys.exit(1)
    except KeyboardInterrupt:
        conn.rollback()
        print("\n[ABORTED] Rolled back — no changes were made.")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description=dedent("""\
            Migrate media_embeddings.embedding from vector(384) to vector(768).
            Runs a dry-run by default; pass --execute to apply changes.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Actually execute the migration (default: dry-run only).",
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Override DATABASE_URL from the environment / .env file.",
    )
    args = parser.parse_args()

    database_url = args.database_url or os.getenv("DATABASE_URL")
    if not database_url:
        print(
            "[ERROR] DATABASE_URL is not set.\n"
            "        Add it to your .env file or pass --database-url <url>."
        )
        sys.exit(1)

    run_migration(database_url, execute=args.execute)


if __name__ == "__main__":
    main()
