"""JSON file-based storage for Knowledge Transfer Hub.

Uses a single JSON file to persist all project and document data.
No database required — suitable for lightweight deployment.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path("kt_data")
DATA_FILE = DATA_DIR / "projects.json"
UPLOAD_DIR = DATA_DIR / "uploads"


def _ensure_dirs() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    UPLOAD_DIR.mkdir(exist_ok=True)


def _load() -> dict[str, Any]:
    _ensure_dirs()
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"projects": {}}


def _save(data: dict[str, Any]) -> None:
    _ensure_dirs()
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Project CRUD ──────────────────────────────────────────────


def list_projects() -> list[dict[str, Any]]:
    data = _load()
    projects = list(data["projects"].values())
    projects.sort(key=lambda p: p.get("updated_at", ""), reverse=True)
    return projects


def get_project(project_id: str) -> dict[str, Any] | None:
    data = _load()
    return data["projects"].get(project_id)


def create_project(
    name: str,
    description: str,
    therapeutic_area: str,
    phase: str,
    owner: str,
    status: str = "进行中",
) -> dict[str, Any]:
    data = _load()
    pid = uuid.uuid4().hex[:12]
    now = _now_iso()
    project: dict[str, Any] = {
        "id": pid,
        "name": name,
        "description": description,
        "therapeutic_area": therapeutic_area,
        "phase": phase,
        "owner": owner,
        "status": status,
        "created_at": now,
        "updated_at": now,
        "documents": {},
        "checklist": _default_checklist(),
    }
    data["projects"][pid] = project
    _save(data)
    return project


def update_project(project_id: str, **fields: Any) -> dict[str, Any] | None:
    data = _load()
    project = data["projects"].get(project_id)
    if not project:
        return None
    for k, v in fields.items():
        if k in project and k not in ("id", "created_at", "documents", "checklist"):
            project[k] = v
    project["updated_at"] = _now_iso()
    _save(data)
    return project


def delete_project(project_id: str) -> bool:
    data = _load()
    if project_id in data["projects"]:
        del data["projects"][project_id]
        _save(data)
        return True
    return False


# ── Document CRUD ─────────────────────────────────────────────


DOCUMENT_CATEGORIES = [
    "项目概览",
    "团队与联系人",
    "技术文档",
    "流程与SOP",
    "风险与问题",
    "会议纪要",
    "培训材料",
    "数据与报告",
    "合规与法规",
    "其他",
]


def add_document(
    project_id: str,
    title: str,
    category: str,
    content: str,
    author: str,
    tags: list[str] | None = None,
    file_name: str | None = None,
) -> dict[str, Any] | None:
    data = _load()
    project = data["projects"].get(project_id)
    if not project:
        return None
    did = uuid.uuid4().hex[:12]
    now = _now_iso()
    doc: dict[str, Any] = {
        "id": did,
        "title": title,
        "category": category,
        "content": content,
        "author": author,
        "tags": tags or [],
        "file_name": file_name,
        "created_at": now,
        "updated_at": now,
    }
    project["documents"][did] = doc
    project["updated_at"] = now
    _save(data)
    return doc


def update_document(
    project_id: str, doc_id: str, **fields: Any
) -> dict[str, Any] | None:
    data = _load()
    project = data["projects"].get(project_id)
    if not project:
        return None
    doc = project["documents"].get(doc_id)
    if not doc:
        return None
    for k, v in fields.items():
        if k in doc and k not in ("id", "created_at"):
            doc[k] = v
    doc["updated_at"] = _now_iso()
    project["updated_at"] = doc["updated_at"]
    _save(data)
    return doc


def delete_document(project_id: str, doc_id: str) -> bool:
    data = _load()
    project = data["projects"].get(project_id)
    if not project:
        return False
    if doc_id in project["documents"]:
        del project["documents"][doc_id]
        project["updated_at"] = _now_iso()
        _save(data)
        return True
    return False


def get_document(project_id: str, doc_id: str) -> dict[str, Any] | None:
    data = _load()
    project = data["projects"].get(project_id)
    if not project:
        return None
    return project["documents"].get(doc_id)


def list_documents(
    project_id: str, category: str | None = None
) -> list[dict[str, Any]]:
    data = _load()
    project = data["projects"].get(project_id)
    if not project:
        return []
    docs = list(project["documents"].values())
    if category:
        docs = [d for d in docs if d["category"] == category]
    docs.sort(key=lambda d: d.get("updated_at", ""), reverse=True)
    return docs


# ── Checklist ─────────────────────────────────────────────────


def _default_checklist() -> list[dict[str, Any]]:
    items = [
        "项目背景与目标已记录",
        "关键联系人清单已更新",
        "技术架构文档已归档",
        "SOP/流程文档已整理",
        "未解决问题清单已列出",
        "数据访问权限已交接",
        "培训材料已准备",
        "风险登记册已更新",
        "合规文件已确认",
        "交接会议已安排",
    ]
    return [{"item": item, "done": False} for item in items]


def update_checklist(
    project_id: str, checklist: list[dict[str, Any]]
) -> list[dict[str, Any]] | None:
    data = _load()
    project = data["projects"].get(project_id)
    if not project:
        return None
    project["checklist"] = checklist
    project["updated_at"] = _now_iso()
    _save(data)
    return checklist


# ── Search ────────────────────────────────────────────────────


def search_all(query: str) -> list[dict[str, Any]]:
    """Search across all projects and documents."""
    if not query.strip():
        return []
    q = query.lower()
    results: list[dict[str, Any]] = []
    data = _load()
    for project in data["projects"].values():
        # Match project-level fields
        project_match = q in project["name"].lower() or q in project.get(
            "description", ""
        ).lower()
        for doc in project["documents"].values():
            doc_match = (
                q in doc["title"].lower()
                or q in doc.get("content", "").lower()
                or any(q in t.lower() for t in doc.get("tags", []))
            )
            if project_match or doc_match:
                results.append(
                    {
                        "project_id": project["id"],
                        "project_name": project["name"],
                        "doc_id": doc["id"],
                        "doc_title": doc["title"],
                        "category": doc["category"],
                        "snippet": doc.get("content", "")[:200],
                    }
                )
    return results
