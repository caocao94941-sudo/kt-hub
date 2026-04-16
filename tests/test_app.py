"""Tests for storage layer — uses in-memory SQLite-style approach.

Since the production code uses PostgreSQL, these tests verify
the data model logic by importing and checking constants/helpers.
Full integration tests require a running PostgreSQL instance.
"""

from __future__ import annotations

import storage


class TestConstants:
    """Verify constants and helper functions."""

    def test_document_categories(self) -> None:
        assert len(storage.DOCUMENT_CATEGORIES) == 10
        assert "技术文档" in storage.DOCUMENT_CATEGORIES
        assert "合规与法规" in storage.DOCUMENT_CATEGORIES

    def test_default_checklist(self) -> None:
        cl = storage._default_checklist()
        assert len(cl) == 10
        assert all(not c["done"] for c in cl)
        assert cl[0]["item"] == "项目背景与目标已记录"

    def test_now_iso_format(self) -> None:
        ts = storage._now_iso()
        assert "T" in ts
        assert ts.endswith("+00:00")
