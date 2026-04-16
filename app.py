"""Knowledge Transfer Hub — 项目交接知识管理平台.

Streamlit app with Supabase PostgreSQL backend.
"""

from __future__ import annotations

import streamlit as st

import storage
from styles import CUSTOM_CSS

ADMIN_USER = "caow2"
PHASES = ["临床前", "I期", "II期", "III期", "注册申报", "上市后", "非临床项目"]

# ── Init ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="KT Hub · 项目交接知识管理",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

storage.init_db()
storage.seed_projects()

# ── Session state ─────────────────────────────────────────────

if "current_project" not in st.session_state:
    st.session_state.current_project = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = ""


def is_admin() -> bool:
    return st.session_state.user == ADMIN_USER


# ── Login page ────────────────────────────────────────────────


def page_login() -> None:
    st.markdown(
        """<div style="display:flex;justify-content:center;padding-top:15vh">
        <div style="max-width:400px;width:100%">""",
        unsafe_allow_html=True,
    )
    st.markdown("## 📋 KT Hub 登录")
    user = st.text_input("用户名", placeholder="请输入用户名")
    if st.button("登录", use_container_width=True):
        if user.strip():
            st.session_state.user = user.strip()
            st.session_state.page = "dashboard"
            storage.add_log(user.strip(), "登录", f"用户 {user.strip()} 登录系统")
            st.rerun()
        else:
            st.error("请输入用户名")
    st.markdown("*仅授权用户可进行编辑操作*")
    st.markdown("</div></div>", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────


def _sidebar() -> None:
    with st.sidebar:
        st.markdown("## 📋 KT Hub")
        st.markdown("*项目交接知识管理平台*")
        st.markdown("---")

        page = st.radio(
            "导航",
            ["仪表盘"]
            + (["新建项目"] if is_admin() else [])
            + ["搜索"]
            + (["操作日志"] if is_admin() else []),
            label_visibility="collapsed",
        )
        page_map = {
            "仪表盘": "dashboard",
            "新建项目": "new_project",
            "搜索": "search",
            "操作日志": "logs",
        }
        st.session_state.page = page_map.get(page, "dashboard")

        st.markdown("---")

        projects = storage.list_projects()
        if projects:
            st.markdown("### 项目列表")
            for p in projects:
                icon = {"进行中": "🟢", "已完成": "🔵", "暂停": "🟡"}.get(
                    p["status"], "⚪"
                )
                if st.button(
                    f"{icon} {p['name']}",
                    key=f"sb_{p['id']}",
                    use_container_width=True,
                ):
                    st.session_state.current_project = p["id"]
                    st.session_state.page = "project_detail"
                    st.rerun()

        st.markdown("---")
        st.markdown(f"当前用户: **{st.session_state.user}**")
        if st.button("退出登录"):
            storage.add_log(
                st.session_state.user, "退出", f"用户 {st.session_state.user} 退出"
            )
            st.session_state.user = ""
            st.session_state.page = "login"
            st.rerun()


# ── Helpers ───────────────────────────────────────────────────


def _hero(title: str, sub: str = "") -> None:
    st.markdown(
        f"""<div class="kt-hero"><h1>{title}</h1>
        <p>{sub}</p></div>""",
        unsafe_allow_html=True,
    )


def _status_badge(status: str) -> str:
    cls = {"进行中": "active", "已完成": "completed", "暂停": "paused"}.get(
        status, "active"
    )
    return f'<span class="kt-badge kt-badge-{cls}">{status}</span>'


def _progress_bar(pct: int) -> str:
    return f"""<div class="kt-progress-bar">
    <div class="kt-progress-fill" style="width:{pct}%"></div></div>"""


def _checklist_pct(cl: list[dict]) -> int:
    if not cl:
        return 0
    return int(sum(1 for c in cl if c.get("done")) / len(cl) * 100)


# ── Dashboard ─────────────────────────────────────────────────


def page_dashboard() -> None:
    _hero("📋 Knowledge Transfer Hub", "集中管理项目交接文档，确保知识无缝传递")

    projects = storage.list_projects()
    total = len(projects)
    active = sum(1 for p in projects if p["status"] == "进行中")
    completed = sum(1 for p in projects if p["status"] == "已完成")
    total_docs = sum(p.get("doc_count", 0) for p in projects)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("项目总数", total)
    c2.metric("进行中", active)
    c3.metric("已完成", completed)
    c4.metric("文档总数", total_docs)

    st.markdown("---")
    if not projects:
        st.info("还没有项目。" + ("点击左侧「新建项目」开始创建。" if is_admin() else ""))
        return

    st.markdown("## 项目概览")
    for p in projects:
        pct = _checklist_pct(p.get("checklist", []))
        doc_count = p.get("doc_count", 0)
        st.markdown(
            f"""<div class="kt-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div><h4>{p['name']}</h4>
                <div class="meta">{(p.get('description') or '')[:120]}</div></div>
                <div>{_status_badge(p['status'])}</div>
            </div>
            <div style="margin-top:0.8rem"><span class="tag">{p.get('phase','')}</span></div>
            <div style="margin-top:0.8rem">
                <div class="meta">交接进度 {pct}% · {doc_count} 份文档 · 负责人: {p.get('owner','-')}</div>
                {_progress_bar(pct)}
            </div></div>""",
            unsafe_allow_html=True,
        )
        cols = st.columns([6, 1])
        with cols[0]:
            if st.button("打开项目 →", key=f"open_{p['id']}"):
                st.session_state.current_project = p["id"]
                st.session_state.page = "project_detail"
                st.rerun()
        with cols[1]:
            if is_admin() and st.button("🗑️", key=f"del_{p['id']}"):
                storage.add_log(st.session_state.user, "删除项目", p["name"])
                storage.delete_project(p["id"])
                st.rerun()


# ── New Project ───────────────────────────────────────────────


def page_new_project() -> None:
    if not is_admin():
        st.warning("仅管理员可创建项目。")
        return
    st.markdown("## 新建交接项目")
    with st.form("new_project"):
        name = st.text_input("项目名称 *", placeholder="例：XX药物III期临床试验")
        desc = st.text_area("项目描述", placeholder="简要描述项目背景、目标和当前状态")
        c1, c2 = st.columns(2)
        with c1:
            phase = st.selectbox("项目阶段", PHASES)
        with c2:
            status = st.selectbox("项目状态", ["进行中", "已完成", "暂停"])
        owner = st.text_input("当前负责人 *", placeholder="姓名")
        if st.form_submit_button("创建项目", use_container_width=True):
            if not name or not owner:
                st.error("请填写项目名称和负责人。")
            else:
                p = storage.create_project(
                    name=name, description=desc,
                    phase=phase or "", owner=owner, status=status or "进行中",
                )
                storage.add_log(st.session_state.user, "创建项目", name)
                st.session_state.current_project = p["id"]
                st.session_state.page = "project_detail"
                st.rerun()


# ── Project Detail ────────────────────────────────────────────


def page_project_detail() -> None:
    pid = st.session_state.current_project
    if not pid:
        st.warning("请先选择一个项目。")
        return
    project = storage.get_project(pid)
    if not project:
        st.error("项目不存在。")
        return

    _hero(project["name"], project.get("description", ""))

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("项目阶段", project.get("phase", "-"))
    mc2.metric("负责人", project.get("owner", "-"))
    pct = _checklist_pct(project.get("checklist", []))
    mc3.metric("交接进度", f"{pct}%")

    tab_names = ["📄 文档列表"]
    if is_admin():
        tab_names.append("➕ 添加文档")
    tab_names.append("✅ 交接清单")
    if is_admin():
        tab_names.append("⚙️ 项目设置")

    tabs = st.tabs(tab_names)
    idx = 0

    with tabs[idx]:
        _tab_docs(pid)
    idx += 1

    if is_admin():
        with tabs[idx]:
            _tab_add_doc(pid)
        idx += 1

    with tabs[idx]:
        _tab_checklist(pid, project)
    idx += 1

    if is_admin():
        with tabs[idx]:
            _tab_settings(pid, project)


def _tab_docs(pid: str) -> None:
    cat = st.selectbox(
        "按类别筛选", ["全部"] + storage.DOCUMENT_CATEGORIES, key="doc_filter"
    )
    docs = storage.list_documents(pid, category=None if cat == "全部" else cat)
    if not docs:
        st.info("暂无文档。" + ("请在「添加文档」标签页中创建。" if is_admin() else ""))
        return
    for d in docs:
        tags = "".join(f'<span class="tag">{t}</span>' for t in d.get("tags", []))
        st.markdown(
            f"""<div class="kt-card">
            <div style="display:flex;justify-content:space-between">
                <h4>{d['title']}</h4><span class="tag">{d['category']}</span>
            </div>
            <div class="meta">作者: {d.get('author','-')} · 创建: {(d.get('created_at',''))[:10]}</div>
            {f'<div style="margin-top:0.4rem">{tags}</div>' if tags else ''}
            </div>""",
            unsafe_allow_html=True,
        )
        with st.expander("查看详情"):
            st.markdown(d.get("content", ""))
            if is_admin():
                if st.button("删除文档", key=f"deldoc_{d['id']}"):
                    storage.add_log(
                        st.session_state.user, "删除文档", d["title"]
                    )
                    storage.delete_document(pid, d["id"])
                    st.rerun()


def _tab_add_doc(pid: str) -> None:
    with st.form("add_doc"):
        title = st.text_input("文档标题 *", placeholder="例：项目架构说明")
        c1, c2 = st.columns(2)
        with c1:
            category = st.selectbox("文档类别 *", storage.DOCUMENT_CATEGORIES)
        with c2:
            author = st.text_input("作者", placeholder="姓名")
        content = st.text_area("文档内容 *", height=300, placeholder="支持纯文本")
        tags_input = st.text_input("标签（逗号分隔）", placeholder="例：关键, 待确认")
        if st.form_submit_button("保存文档", use_container_width=True):
            if not title or not content:
                st.error("请填写文档标题和内容。")
            else:
                tags = (
                    [t.strip() for t in tags_input.split(",") if t.strip()]
                    if tags_input else []
                )
                storage.add_document(
                    pid, title, category or "", content, author, tags
                )
                storage.add_log(st.session_state.user, "添加文档", title)
                st.rerun()


def _tab_checklist(pid: str, project: dict) -> None:
    st.markdown("### 交接检查清单")
    checklist = project.get("checklist", [])
    pct = _checklist_pct(checklist)
    st.markdown(
        f'<div class="meta">完成进度: {pct}%</div>{_progress_bar(pct)}',
        unsafe_allow_html=True,
    )

    updated = False
    for i, item in enumerate(checklist):
        val = st.checkbox(
            item["item"],
            value=item.get("done", False),
            key=f"chk_{pid}_{i}",
            disabled=not is_admin(),
        )
        if val != item.get("done", False):
            checklist[i]["done"] = val
            updated = True

    if updated and is_admin():
        storage.update_checklist(pid, checklist)
        storage.add_log(st.session_state.user, "更新清单", project["name"])
        st.rerun()

    # ── Links section ──
    st.markdown("---")
    st.markdown("### 🔗 项目关键链接")
    links = project.get("links") or {}

    if is_admin():
        with st.form("links_form"):
            lnk_project = st.text_area(
                "Project URL", value=links.get("project_url", ""), height=68
            )
            lnk_gdrive = st.text_input(
                "Gdrive URL", value=links.get("gdrive_url", "")
            )
            lnk_veeva = st.text_area(
                "Veeva URL", value=links.get("veeva_url", ""), height=68
            )
            lnk_server = st.text_input(
                "Server / LAAM", value=links.get("server_laam", "")
            )
            lnk_vendor = st.text_input(
                "Vendor", value=links.get("vendor", "")
            )
            if st.form_submit_button("保存链接", use_container_width=True):
                new_links = {
                    "project_url": lnk_project,
                    "gdrive_url": lnk_gdrive,
                    "veeva_url": lnk_veeva,
                    "server_laam": lnk_server,
                    "vendor": lnk_vendor,
                }
                storage.update_links(pid, new_links)
                storage.add_log(
                    st.session_state.user, "更新链接", project["name"]
                )
                st.rerun()
    else:
        if any(links.values()):
            for label, key in [
                ("Project URL", "project_url"),
                ("Gdrive URL", "gdrive_url"),
                ("Veeva URL", "veeva_url"),
                ("Server / LAAM", "server_laam"),
                ("Vendor", "vendor"),
            ]:
                val = links.get(key, "")
                if val:
                    st.markdown(f"**{label}:** {val}")
        else:
            st.info("暂无链接信息。")


def _tab_settings(pid: str, project: dict) -> None:
    st.markdown("### 项目设置")
    with st.form("edit_project"):
        name = st.text_input("项目名称", value=project["name"])
        desc = st.text_area("项目描述", value=project.get("description", ""))
        c1, c2 = st.columns(2)
        with c1:
            cur_phase = project.get("phase", "临床前")
            idx = PHASES.index(cur_phase) if cur_phase in PHASES else 0
            phase = st.selectbox("项目阶段", PHASES, index=idx)
        with c2:
            statuses = ["进行中", "已完成", "暂停"]
            cur_st = project.get("status", "进行中")
            si = statuses.index(cur_st) if cur_st in statuses else 0
            status = st.selectbox("状态", statuses, index=si)
        owner = st.text_input("负责人", value=project.get("owner", ""))
        if st.form_submit_button("保存修改", use_container_width=True):
            storage.update_project(
                pid, name=name, description=desc,
                phase=phase, owner=owner, status=status,
            )
            storage.add_log(st.session_state.user, "修改项目", name)
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚠️ 危险操作")
    if st.button("删除此项目", type="secondary"):
        storage.add_log(st.session_state.user, "删除项目", project["name"])
        storage.delete_project(pid)
        st.session_state.current_project = None
        st.session_state.page = "dashboard"
        st.rerun()


# ── Search ────────────────────────────────────────────────────


def page_search() -> None:
    st.markdown("## 🔍 全局搜索")
    query = st.text_input("搜索关键词", placeholder="输入项目名、文档标题、内容...")
    if query:
        results = storage.search_all(query)
        if results:
            st.markdown(f"找到 **{len(results)}** 条结果：")
            for r in results:
                st.markdown(
                    f"""<div class="kt-card"><h4>{r['doc_title']}</h4>
                    <div class="meta">项目: {r['project_name']} · 类别: {r['category']}</div>
                    <div style="margin-top:0.5rem;font-size:0.9rem">{r['snippet']}...</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                if st.button("打开项目", key=f"sr_{r['project_id']}_{r['doc_id']}"):
                    st.session_state.current_project = r["project_id"]
                    st.session_state.page = "project_detail"
                    st.rerun()
        else:
            st.info("未找到匹配结果。")


# ── Logs ──────────────────────────────────────────────────────


def page_logs() -> None:
    if not is_admin():
        st.warning("仅管理员可查看操作日志。")
        return
    st.markdown("## 📜 操作日志")
    logs = storage.list_logs()
    if not logs:
        st.info("暂无操作记录。")
        return
    st.table(
        [
            {
                "时间": entry["time"][:19].replace("T", " "),
                "用户": entry["username"],
                "操作": entry["action"],
                "详情": entry["detail"],
            }
            for entry in logs
        ]
    )


# ── Router ────────────────────────────────────────────────────

if not st.session_state.user:
    page_login()
else:
    _sidebar()
    page_map = {
        "dashboard": page_dashboard,
        "new_project": page_new_project,
        "project_detail": page_project_detail,
        "search": page_search,
        "logs": page_logs,
    }
    fn = page_map.get(st.session_state.page, page_dashboard)
    fn()
