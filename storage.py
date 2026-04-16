"""SQLite storage layer for Knowledge Transfer Hub.

Uses a local SQLite file (kt_hub.db). No external database needed.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent / "kt_hub.db"

# ── Connection ────────────────────────────────────────────────


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    conn = _get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                therapeutic_area TEXT DEFAULT '',
                phase TEXT DEFAULT '',
                owner TEXT DEFAULT '',
                status TEXT DEFAULT '进行中',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                checklist TEXT DEFAULT '[]',
                links TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                category TEXT DEFAULT '',
                content TEXT DEFAULT '',
                author TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                file_name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT NOT NULL,
                username TEXT DEFAULT '',
                action TEXT NOT NULL,
                detail TEXT DEFAULT ''
            );
        """)
        conn.commit()
    finally:
        conn.close()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    # Parse JSON fields
    for key in ("checklist", "links", "tags"):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                d[key] = [] if key in ("checklist", "tags") else {}
    return d


# ── Project CRUD ──────────────────────────────────────────────

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


def list_projects() -> list[dict[str, Any]]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM projects ORDER BY updated_at DESC"
        ).fetchall()
        result = []
        for r in rows:
            d = _row_to_dict(r)
            cnt = conn.execute(
                "SELECT COUNT(*) FROM documents WHERE project_id = ?",
                (d["id"],),
            ).fetchone()[0]
            d["doc_count"] = cnt
            result.append(d)
        return result
    finally:
        conn.close()


def get_project(project_id: str) -> dict[str, Any] | None:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def create_project(
    name: str,
    description: str,
    phase: str,
    owner: str,
    status: str = "进行中",
    links: dict | None = None,
) -> dict[str, Any]:
    pid = uuid.uuid4().hex[:12]
    now = _now_iso()
    checklist = _default_checklist()
    conn = _get_conn()
    try:
        conn.execute(
            """INSERT INTO projects
               (id, name, description, therapeutic_area, phase, owner,
                status, created_at, updated_at, checklist, links)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                pid, name, description, "", phase, owner,
                status, now, now,
                json.dumps(checklist, ensure_ascii=False),
                json.dumps(links or {}, ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return {
        "id": pid, "name": name, "description": description,
        "therapeutic_area": "", "phase": phase, "owner": owner,
        "status": status, "created_at": now, "updated_at": now,
        "checklist": checklist, "links": links or {},
    }


def update_project(project_id: str, **fields: Any) -> dict[str, Any] | None:
    allowed = {"name", "description", "phase", "owner", "status"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return get_project(project_id)
    now = _now_iso()
    sets = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [now, project_id]
    conn = _get_conn()
    try:
        conn.execute(
            f"UPDATE projects SET {sets}, updated_at = ? WHERE id = ?",
            vals,
        )
        conn.commit()
    finally:
        conn.close()
    return get_project(project_id)


def delete_project(project_id: str) -> bool:
    conn = _get_conn()
    try:
        cur = conn.execute(
            "DELETE FROM projects WHERE id = ?", (project_id,)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ── Document CRUD ─────────────────────────────────────────────


def add_document(
    project_id: str,
    title: str,
    category: str,
    content: str,
    author: str,
    tags: list[str] | None = None,
    file_name: str | None = None,
) -> dict[str, Any] | None:
    if not get_project(project_id):
        return None
    did = uuid.uuid4().hex[:12]
    now = _now_iso()
    conn = _get_conn()
    try:
        conn.execute(
            """INSERT INTO documents
               (id, project_id, title, category, content, author,
                tags, file_name, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                did, project_id, title, category, content, author,
                json.dumps(tags or [], ensure_ascii=False),
                file_name, now, now,
            ),
        )
        conn.execute(
            "UPDATE projects SET updated_at = ? WHERE id = ?",
            (now, project_id),
        )
        conn.commit()
    finally:
        conn.close()
    return {
        "id": did, "title": title, "category": category,
        "content": content, "author": author, "tags": tags or [],
        "file_name": file_name, "created_at": now, "updated_at": now,
    }


def list_documents(
    project_id: str, category: str | None = None
) -> list[dict[str, Any]]:
    conn = _get_conn()
    try:
        if category:
            rows = conn.execute(
                "SELECT * FROM documents WHERE project_id = ? AND category = ? ORDER BY updated_at DESC",
                (project_id, category),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM documents WHERE project_id = ? ORDER BY updated_at DESC",
                (project_id,),
            ).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_document(project_id: str, doc_id: str) -> dict[str, Any] | None:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ? AND project_id = ?",
            (doc_id, project_id),
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def update_document(
    project_id: str, doc_id: str, **fields: Any
) -> dict[str, Any] | None:
    allowed = {"title", "category", "content", "author", "tags"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return get_document(project_id, doc_id)
    if "tags" in updates:
        updates["tags"] = json.dumps(updates["tags"], ensure_ascii=False)
    now = _now_iso()
    sets = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [now, doc_id, project_id]
    conn = _get_conn()
    try:
        conn.execute(
            f"UPDATE documents SET {sets}, updated_at = ? WHERE id = ? AND project_id = ?",
            vals,
        )
        conn.execute(
            "UPDATE projects SET updated_at = ? WHERE id = ?",
            (now, project_id),
        )
        conn.commit()
    finally:
        conn.close()
    return get_document(project_id, doc_id)


def delete_document(project_id: str, doc_id: str) -> bool:
    conn = _get_conn()
    try:
        cur = conn.execute(
            "DELETE FROM documents WHERE id = ? AND project_id = ?",
            (doc_id, project_id),
        )
        if cur.rowcount > 0:
            conn.execute(
                "UPDATE projects SET updated_at = ? WHERE id = ?",
                (_now_iso(), project_id),
            )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ── Checklist ─────────────────────────────────────────────────


def update_checklist(
    project_id: str, checklist: list[dict[str, Any]]
) -> list[dict[str, Any]] | None:
    now = _now_iso()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "UPDATE projects SET checklist = ?, updated_at = ? WHERE id = ?",
            (json.dumps(checklist, ensure_ascii=False), now, project_id),
        )
        conn.commit()
        return checklist if cur.rowcount > 0 else None
    finally:
        conn.close()


# ── Links ─────────────────────────────────────────────────────


def update_links(
    project_id: str, links: dict[str, str]
) -> dict[str, str] | None:
    now = _now_iso()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "UPDATE projects SET links = ?, updated_at = ? WHERE id = ?",
            (json.dumps(links, ensure_ascii=False), now, project_id),
        )
        conn.commit()
        return links if cur.rowcount > 0 else None
    finally:
        conn.close()


# ── Audit Log ─────────────────────────────────────────────────


def add_log(username: str, action: str, detail: str) -> None:
    now = _now_iso()
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO audit_logs (time, username, action, detail) VALUES (?,?,?,?)",
            (now, username, action, detail),
        )
        conn.commit()
    finally:
        conn.close()


def list_logs(limit: int = 500) -> list[dict[str, Any]]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT time, username, action, detail FROM audit_logs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Search ────────────────────────────────────────────────────


def search_all(query: str) -> list[dict[str, Any]]:
    if not query.strip():
        return []
    q = f"%{query.lower()}%"
    conn = _get_conn()
    try:
        rows = conn.execute(
            """SELECT d.id as doc_id, d.title as doc_title, d.category,
                      d.content, p.id as project_id, p.name as project_name
               FROM documents d
               JOIN projects p ON d.project_id = p.id
               WHERE LOWER(d.title) LIKE ?
                  OR LOWER(d.content) LIKE ?
                  OR LOWER(p.name) LIKE ?
                  OR LOWER(p.description) LIKE ?
               ORDER BY d.updated_at DESC
               LIMIT 50""",
            (q, q, q, q),
        ).fetchall()
        return [
            {
                "project_id": r["project_id"],
                "project_name": r["project_name"],
                "doc_id": r["doc_id"],
                "doc_title": r["doc_title"],
                "category": r["category"],
                "snippet": (r["content"] or "")[:200],
            }
            for r in rows
        ]
    finally:
        conn.close()


# ── Seed Data ─────────────────────────────────────────────────


def seed_projects() -> None:
    """Insert initial projects if the database is empty."""
    conn = _get_conn()
    try:
        count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    finally:
        conn.close()
    if count > 0:
        return

    seed = [
        # ── 一、药物安全与不良反应管理 ──
        {
            "name": "AE Identification (WuKong)",
            "description": (
                "【LSMV SaaS系统】利用大语言模型（AI）从社交媒体、医院及PDF文档（杂志期刊）中提取AE（药物不良反应）报道，"
                "抽取后由PV团队人工审核修改，并向Global监管机构申报。\n\n"
                "BPO: Berry Luan | 供应商对接人: 商汤-朱文力\n\n"
                "【权限配置】QA权限需在CIDM申请组别 PDChinaAEIdentification-QAAdmin。"
                "服务器LAAM账号: GLOLAAM_CHINA-AEIS-Admin-USR\n\n"
                "【待办/痛点】\n"
                "• 需找Marc确认存放在LAAM上的服务器系统密码\n"
                "• CR1: 需考虑整合SSO CIDM登录\n"
                "• CR2: 计划将AI底层从商汤切换为罗氏内部太极(Taichi)平台"
                "（已有Portkey Request: RITM6205283），或通义千问、Deepseek"
            ),
            "phase": "上市后", "owner": "Jenny Qu",
            "links": {
                "project_url": "QA: https://wukong-test.roche.com\nProd: https://wukong.roche.com",
                "gdrive_url": "https://drive.google.com/drive/folders/1GbszjD",
                "veeva_url": "China AE Identification",
                "server_laam": "LAAM账号: GLOLAAM_CHINA-AEIS-Admin-USR\nCIDM组: PDChinaAEIdentification-QAAdmin",
                "vendor": "商汤-朱文力",
            },
        },
        {
            "name": "China Digital Safety Case Submission (RPA)",
            "description": (
                "【GXP国际规范项目】RPA机器人直接登录全局LSMV系统查看产品信息，自动判断AE Case是否需递交监管部门，"
                "并填写患者年龄、身高、体重、人种等信息，最终由人工校验提交。\n\n"
                "BPO: Yue Tang | 供应商: Juexin Malf Ma\n\n"
                "【待办/痛点】\n"
                "• LSMV系统每年多次更新药品名称，或遇病人同时服用多种药物等复杂分类情况，RPA极易失效\n"
                "• 目前机器人填写准确率80%，剩余20%需人工校验\n"
                "• RPA部署由Global RPA团队统一上传至GitHub和Windows Server/瑞士发布控制中心\n"
                "• 遇问题需向UiPath/OSP发Ticket找Lengfeng或Juexing处理\n\n"
                "【环境信息】\n"
                "DEV服务器 VM: rbamv952866, 账号: RXTCASU0\n"
                "QA和Prod环境归Global管理，需确认UiPath和LAAM Safe组权限"
            ),
            "phase": "上市后", "owner": "Jenny Qu",
            "links": {
                "project_url": "N/A（无Web界面，RPA直接登录LSMV系统）",
                "gdrive_url": "https://drive.google.com/drive/folders/17c_a4G",
                "veeva_url": "China Digitized Safety Case Submission",
                "server_laam": "DEV: VM rbamv952866 / 账号 RXTCASU0\nQA/Prod: Global管理，需确认UiPath和LAAM Safe组权限",
                "vendor": "Juexin - Malf Ma",
            },
        },
        {
            "name": "China Safety Aggregated Report",
            "description": (
                "【含WebApp和Visual Dashboard】用于新药上市及连带安全市场、Global不良事件的申报。"
                "系统Job通过模板解析元数据，利用预设逻辑（PDS）自动从Global系统拉取AE药品数据填充至系统。\n\n"
                "供应商对接人: Juexin 江涛(Jiangtao Di)\n\n"
                "【界面逻辑】绿色=系统自动填充，黄色=需业务手动填写，右侧标注具体计算逻辑。共3套环境。\n\n"
                "【权限配置】LAAM无保险箱。Dashboard QA权限需在CIDM申请 "
                "TC-APAC-Aggregated_Report_Visual_Dashboard-Consumers"
            ),
            "phase": "上市后", "owner": "Jenny Qu",
            "links": {
                "project_url": "QA: https://apsar-test.roche.com/digital/export\nProd: https://apsar.roche.com/digital/export",
                "gdrive_url": "https://drive.google.com/drive/folders/111lJEN",
                "veeva_url": "China Safety Aggregated Report-WebApp\nChina Safety Aggregated Report-Visual Dashboard",
                "server_laam": "LAAM无保险箱\nCIDM组: TC-APAC-Aggregated_Report_Visual_Dashboard-Consumers",
                "vendor": "Juexin - 江涛 (Jiangtao Di)",
            },
        },
        {
            "name": "China RMP",
            "description": (
                "【风险管理计划系统】用于提交Risk Management Plan。\n\n"
                "【权限配置】QA权限及问题沟通需直接联系供应商 sun.chen@roche.com，LAAM权限已在CIDM上申请。"
            ),
            "phase": "上市后", "owner": "Jenny Qu",
            "links": {
                "project_url": "QA: https://chinarmp-test.roche.com\nProd: https://chinarmp.roche.com",
                "gdrive_url": "https://drive.google.com/drive/folders/1ckbeo",
                "veeva_url": "China RMP System",
                "server_laam": "LAAM权限已在CIDM申请",
                "vendor": "sun.chen@roche.com",
            },
        },
        # ── 二、临床运营与项目管理 ──
        {
            "name": "MPR / MPR AI (Monthly Portfolio Reporting)",
            "description": (
                "【PD产品组合项目管理和追溯的可视化系统】On-Premise环境，需SX账号登录。\n\n"
                "BPO: Simon Wang | 日常操作用户: Yijing Zhu\n\n"
                "【功能】项目经理(PM)维护自己的Program，记录药品Milestone并查验每月药品整治数据；"
                "用户确认当月数据后可复制继续编辑下月。\n\n"
                "【PDPM数据报表】包含9张报表，数据从MPR读取，每天通过PDS同步2次。"
                "报表查看权限在CIDM申请组别: Tableau PD_China_MPR_Report_Project Black Belt access on CCAS"
            ),
            "phase": "上市后", "owner": "Jenny Qu",
            "links": {
                "project_url": "Web: https://pdalmcn-test.roche.com/mpr/programmanagement",
                "gdrive_url": "",
                "veeva_url": "",
                "server_laam": "On-Premise环境，需SX账号登录\nCIDM组: Tableau PD_China_MPR_Report_Project Black Belt access on CCAS",
                "vendor": "",
            },
        },
        {
            "name": "Mediplan",
            "description": (
                "【临床实验药物计划与提醒系统】服务罗氏及其他机构医院，用于在其他系统建立Study研究编号。\n\n"
                "【待办/痛点】\n"
                "• 供应商德勤(Deloitte)即将被替换，需尽快收回其权限\n"
                "• 亟待补充缺失的系统用户名单、CIDM server、DB以及确切的LAAM信息"
            ),
            "phase": "上市后", "owner": "",
            "links": {
                "project_url": "QA: https://mediplan-test.roche.com/index\nProd: https://mediplan.roche.com/index",
                "gdrive_url": "https://drive.google.com/drive/folders/1rt5kH1",
                "veeva_url": "MediPlan",
                "server_laam": "待补充CIDM server、DB及LAAM信息",
                "vendor": "Deloitte / Juexin（德勤即将被替换）",
            },
        },
        {
            "name": "Site Monitoring Follow Up Letter",
            "description": (
                "【Tableau Dashboard】展示罗氏合作临床试验站点的指标评分。\n\n"
                "BPO: Mandy Wu | 供应商: Juexin 江涛\n\n"
                "【功能】收集拜访医院报告，通过数仓提取数据进行Site Monitoring及PDG研究中心能力分析。\n\n"
                "【权限配置】数据来源权限由CIDM组配置，Jiangtao和Jimmy有权限配置。"
            ),
            "phase": "上市后", "owner": "Jenny Qu",
            "links": {
                "project_url": "QA: https://tableau-tst.ccas.roche.com/#/projects/46\nProd: https://tableau.ccas.roche.com/#/workbooks/84/views",
                "gdrive_url": "https://drive.google.com/drive/folders/1hbk1Y",
                "veeva_url": "Site Monitoring Follow Up Letter",
                "server_laam": "N/A\n权限配置: Jiangtao和Jimmy",
                "vendor": "Juexin - 江涛",
            },
        },
        # ── 三、其他辅助RPA、财务与基础架构 ──
        {
            "name": "HGRAC / SUSAR RPA",
            "description": (
                "【统筹与部署】服务器由Global RPA Team统管。密码存放在UiPath的Assets中。"
                "Lefeng负责在Google Chat处理用户反馈，目前仅Lefeng能在开发环境自行发布，QA和Prod需找Global团队。\n\n"
                "【HGRAC】包含Pharma和DIA两套环境，临床后交接给IRIS，"
                "向\"人类遗传资源服务系统\"填报出境生物遗传信息申请。BPO: Zhihui Cheng。\n"
                "痛点: 需通过Google访问，UI变化时需修改QA/PROD代码；机器人授权器需用户每年定期授权一次。\n\n"
                "【SUSAR】GXP项目，处理非遗传严重不良反应。BPO: Elza Li。"
                "外部Vendor将文档上传至BOX，RPA通过GDrive分析、翻译后返回BOX，并具备下载模板发邮件给医院的功能。"
            ),
            "phase": "上市后", "owner": "Iris Cai",
            "links": {
                "project_url": "N/A",
                "gdrive_url": "HGRAC: https://drive.google.com/drive/folders/1dMvM6dC6YOU3kG5bohTKkVeyVlONZo4p\nSUSAR: https://drive.google.com/drive/folders/1DyR_FplrCRI89ITuWosZky_NT25o7xsh",
                "veeva_url": "PRJ0220489 - China PD Automation Project",
                "server_laam": "Global RPA Team统管\n密码存放在UiPath Assets中\nLefeng负责开发环境发布",
                "vendor": "Juexin - Malf Ma",
            },
        },
        {
            "name": "China MailGuard (Python)",
            "description": (
                "【Python机器人系统】On Premise环境，需SX账号登录。"
                "监控公共邮箱并处理附件，根据邮件标题等映射关系生成记录(track)，"
                "通过调用罗氏接口或第三方进行翻译分析后回复医院及供应商。\n\n"
                "BPO: Yue Tang\n\n"
                "【环境配置】LAAM上维护了1个通用公共账号(generic)和2个做本地翻译用的secret账号。包含QA与Prod修改环境。\n\n"
                "【待办/痛点】\n"
                "• 原翻译工具接口下线，需应对翻译接口变化的Task\n"
                "• 记录中疑似缺少2台服务器(QA/Prod)的具体信息，有待核实"
            ),
            "phase": "上市后", "owner": "Jenny Qu",
            "links": {
                "project_url": "N/A（On Premise，需SX账号登录）",
                "gdrive_url": "https://drive.google.com/drive/folders/1DulEvo",
                "veeva_url": "China MailGuard",
                "server_laam": "LAAM: 1个generic公共账号 + 2个翻译secret账号\nQA/Prod服务器信息待核实",
                "vendor": "Juexin - Malf Ma",
            },
        },
        {
            "name": "Financial Report",
            "description": (
                "【RPA财务报告处理系统】处理用户发到公邮的工单PDF文件（约200-300页/份）。"
                "RPA下载附件，按页拆分成文件，提取关键词、重命名，上传至GDrive指定路径"
                "（包含成本中心和URL路径两列信息），最后发送邮件通知用户。执行频率约Weekly。\n\n"
                "【环境配置】共3套环境（开发和UAT服务器不同，但账号一致）。需使用SX账号登录服务器。\n\n"
                "【待办/痛点】\n"
                "• Client secret (Google认证) 频繁过期，联系人 Yuki Zhou\n"
                "• 需查看Marc的KT文档，了解如何申请为期3个月的SX账号服务器访问权限"
            ),
            "phase": "上市后", "owner": "",
            "links": {
                "project_url": "N/A（RPA系统，无Web界面）",
                "gdrive_url": "",
                "veeva_url": "",
                "server_laam": "3套环境（开发和UAT服务器不同，账号一致）\n需SX账号登录\nGoogle认证联系人: Yuki Zhou",
                "vendor": "",
            },
        },
    ]

    for s in seed:
        create_project(
            name=s["name"],
            description=s["description"],
            phase=s["phase"],
            owner=s["owner"],
            links=s["links"],
        )
