"""Tests for the storage layer of Knowledge Transfer Hub."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from unittest.mock import patch

import storage


class TestProjectCRUD:
    """Test project create, read, update, delete operations."""

    def setup_method(self) -> None:
        self.tmp_file = Path("test_data.json")
        self.tmp_dir = Path("test_kt_data")
        self.tmp_upload = self.tmp_dir / "uploads"
        self._patches = [
            patch.object(storage, "DATA_FILE", self.tmp_file),
            patch.object(storage, "DATA_DIR", self.tmp_dir),
            patch.object(storage, "UPLOAD_DIR", self.tmp_upload),
        ]
        for p in self._patches:
            p.start()

    def teardown_method(self) -> None:
        for p in self._patches:
            p.stop()
        if self.tmp_file.exists():
            self.tmp_file.unlink()
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def test_create_project(self) -> None:
        project = storage.create_project(
            name="Test Project",
            description="A test",
            therapeutic_area="肿瘤学",
            phase="III期",
            owner="Alice",
        )
        assert project["name"] == "Test Project"
        assert project["therapeutic_area"] == "肿瘤学"
        assert project["status"] == "进行中"
        assert len(project["id"]) == 12
        assert "checklist" in project
        assert len(project["checklist"]) == 10

    def test_list_projects(self) -> None:
        storage.create_project("P1", "d1", "肿瘤学", "I期", "A")
        storage.create_project("P2", "d2", "免疫学", "II期", "B")
        projects = storage.list_projects()
        assert len(projects) == 2
        assert projects[0]["name"] == "P2"

    def test_get_project(self) -> None:
        p = storage.create_project("P1", "d1", "肿瘤学", "I期", "A")
        result = storage.get_project(p["id"])
        assert result is not None
        assert result["name"] == "P1"

    def test_get_project_not_found(self) -> None:
        assert storage.get_project("nonexistent") is None

    def test_update_project(self) -> None:
        p = storage.create_project("P1", "d1", "肿瘤学", "I期", "A")
        updated = storage.update_project(
            p["id"], name="P1 Updated", status="已完成"
        )
        assert updated is not None
        assert updated["name"] == "P1 Updated"
        assert updated["status"] == "已完成"

    def test_update_project_not_found(self) -> None:
        assert storage.update_project("nonexistent", name="X") is None

    def test_update_project_protected_fields(self) -> None:
        p = storage.create_project("P1", "d1", "肿瘤学", "I期", "A")
        original_id = p["id"]
        updated = storage.update_project(p["id"], id="hacked")
        assert updated is not None
        assert updated["id"] == original_id

    def test_delete_project(self) -> None:
        p = storage.create_project("P1", "d1", "肿瘤学", "I期", "A")
        assert storage.delete_project(p["id"]) is True
        assert storage.get_project(p["id"]) is None

    def test_delete_project_not_found(self) -> None:
        assert storage.delete_project("nonexistent") is False


class TestDocumentCRUD:
    """Test document operations within a project."""

    def setup_method(self) -> None:
        self.tmp_file = Path("test_data_docs.json")
        self.tmp_dir = Path("test_kt_data_docs")
        self.tmp_upload = self.tmp_dir / "uploads"
        self._patches = [
            patch.object(storage, "DATA_FILE", self.tmp_file),
            patch.object(storage, "DATA_DIR", self.tmp_dir),
            patch.object(storage, "UPLOAD_DIR", self.tmp_upload),
        ]
        for p in self._patches:
            p.start()
        self.project = storage.create_project(
            "P1", "d1", "肿瘤学", "I期", "A"
        )

    def teardown_method(self) -> None:
        for p in self._patches:
            p.stop()
        if self.tmp_file.exists():
            self.tmp_file.unlink()
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def test_add_document(self) -> None:
        doc = storage.add_document(
            self.project["id"],
            title="Architecture Doc",
            category="技术文档",
            content="# Architecture\nDetails here.",
            author="Bob",
            tags=["关键", "v1"],
        )
        assert doc is not None
        assert doc["title"] == "Architecture Doc"
        assert doc["category"] == "技术文档"
        assert doc["tags"] == ["关键", "v1"]

    def test_add_document_invalid_project(self) -> None:
        result = storage.add_document(
            "bad_id", "t", "c", "content", "a"
        )
        assert result is None

    def test_list_documents(self) -> None:
        storage.add_document(
            self.project["id"], "D1", "技术文档", "c1", "A"
        )
        storage.add_document(
            self.project["id"], "D2", "会议纪要", "c2", "B"
        )
        docs = storage.list_documents(self.project["id"])
        assert len(docs) == 2

    def test_list_documents_by_category(self) -> None:
        storage.add_document(
            self.project["id"], "D1", "技术文档", "c1", "A"
        )
        storage.add_document(
            self.project["id"], "D2", "会议纪要", "c2", "B"
        )
        docs = storage.list_documents(
            self.project["id"], category="技术文档"
        )
        assert len(docs) == 1
        assert docs[0]["title"] == "D1"

    def test_get_document(self) -> None:
        doc = storage.add_document(
            self.project["id"], "D1", "技术文档", "c1", "A"
        )
        assert doc is not None
        result = storage.get_document(self.project["id"], doc["id"])
        assert result is not None
        assert result["title"] == "D1"

    def test_update_document(self) -> None:
        doc = storage.add_document(
            self.project["id"], "D1", "技术文档", "c1", "A"
        )
        assert doc is not None
        updated = storage.update_document(
            self.project["id"], doc["id"], title="D1 Updated"
        )
        assert updated is not None
        assert updated["title"] == "D1 Updated"

    def test_delete_document(self) -> None:
        doc = storage.add_document(
            self.project["id"], "D1", "技术文档", "c1", "A"
        )
        assert doc is not None
        assert (
            storage.delete_document(self.project["id"], doc["id"]) is True
        )
        assert (
            storage.get_document(self.project["id"], doc["id"]) is None
        )


class TestChecklist:
    """Test checklist operations."""

    def setup_method(self) -> None:
        self.tmp_file = Path("test_data_cl.json")
        self.tmp_dir = Path("test_kt_data_cl")
        self.tmp_upload = self.tmp_dir / "uploads"
        self._patches = [
            patch.object(storage, "DATA_FILE", self.tmp_file),
            patch.object(storage, "DATA_DIR", self.tmp_dir),
            patch.object(storage, "UPLOAD_DIR", self.tmp_upload),
        ]
        for p in self._patches:
            p.start()
        self.project = storage.create_project(
            "P1", "d1", "肿瘤学", "I期", "A"
        )

    def teardown_method(self) -> None:
        for p in self._patches:
            p.stop()
        if self.tmp_file.exists():
            self.tmp_file.unlink()
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def test_default_checklist(self) -> None:
        p = storage.get_project(self.project["id"])
        assert p is not None
        assert len(p["checklist"]) == 10
        assert all(not c["done"] for c in p["checklist"])

    def test_update_checklist(self) -> None:
        p = storage.get_project(self.project["id"])
        assert p is not None
        checklist = p["checklist"]
        checklist[0]["done"] = True
        checklist[1]["done"] = True
        result = storage.update_checklist(self.project["id"], checklist)
        assert result is not None
        assert result[0]["done"] is True
        assert result[1]["done"] is True
        assert result[2]["done"] is False


class TestSearch:
    """Test search functionality."""

    def setup_method(self) -> None:
        self.tmp_file = Path("test_data_search.json")
        self.tmp_dir = Path("test_kt_data_search")
        self.tmp_upload = self.tmp_dir / "uploads"
        self._patches = [
            patch.object(storage, "DATA_FILE", self.tmp_file),
            patch.object(storage, "DATA_DIR", self.tmp_dir),
            patch.object(storage, "UPLOAD_DIR", self.tmp_upload),
        ]
        for p in self._patches:
            p.start()

    def teardown_method(self) -> None:
        for p in self._patches:
            p.stop()
        if self.tmp_file.exists():
            self.tmp_file.unlink()
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def test_search_by_title(self) -> None:
        p = storage.create_project(
            "Oncology Trial", "desc", "肿瘤学", "III期", "A"
        )
        storage.add_document(
            p["id"], "Protocol Design", "技术文档", "content", "B"
        )
        results = storage.search_all("Protocol")
        assert len(results) == 1
        assert results[0]["doc_title"] == "Protocol Design"

    def test_search_by_content(self) -> None:
        p = storage.create_project("P1", "desc", "肿瘤学", "I期", "A")
        storage.add_document(
            p["id"], "Doc1", "技术文档", "Contains biomarker data", "B"
        )
        results = storage.search_all("biomarker")
        assert len(results) == 1

    def test_search_by_tag(self) -> None:
        p = storage.create_project("P1", "desc", "肿瘤学", "I期", "A")
        storage.add_document(
            p["id"],
            "Doc1",
            "技术文档",
            "content",
            "B",
            tags=["urgent"],
        )
        results = storage.search_all("urgent")
        assert len(results) == 1

    def test_search_empty_query(self) -> None:
        assert storage.search_all("") == []
        assert storage.search_all("   ") == []

    def test_search_no_results(self) -> None:
        p = storage.create_project("P1", "desc", "肿瘤学", "I期", "A")
        storage.add_document(
            p["id"], "Doc1", "技术文档", "content", "B"
        )
        results = storage.search_all("nonexistent_xyz")
        assert len(results) == 0


class TestDataPersistence:
    """Test that data persists correctly to JSON file."""

    def setup_method(self) -> None:
        self.tmp_file = Path("test_data_persist.json")
        self.tmp_dir = Path("test_kt_data_persist")
        self.tmp_upload = self.tmp_dir / "uploads"
        self._patches = [
            patch.object(storage, "DATA_FILE", self.tmp_file),
            patch.object(storage, "DATA_DIR", self.tmp_dir),
            patch.object(storage, "UPLOAD_DIR", self.tmp_upload),
        ]
        for p in self._patches:
            p.start()

    def teardown_method(self) -> None:
        for p in self._patches:
            p.stop()
        if self.tmp_file.exists():
            self.tmp_file.unlink()
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def test_data_persists_to_file(self) -> None:
        storage.create_project("P1", "d1", "肿瘤学", "I期", "A")
        assert self.tmp_file.exists()
        data = json.loads(self.tmp_file.read_text(encoding="utf-8"))
        assert len(data["projects"]) == 1

    def test_data_survives_reload(self) -> None:
        p = storage.create_project("P1", "d1", "肿瘤学", "I期", "A")
        projects = storage.list_projects()
        assert len(projects) == 1
        assert projects[0]["id"] == p["id"]
