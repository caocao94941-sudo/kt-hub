"""Knowledge Transfer Hub — 项目交接知识管理平台.

Streamlit application for collecting, organizing, and transferring
project knowledge across teams. Uses JSON file storage.
"""

from __future__ import annotations

import streamlit as st

import storage
from styles import CUSTOM_CSS

# ── Page config ───────────────────────────────────────────────

st.set_page_config(
    page_title="KT Hub · 项目交接知识管理",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────

if "current_project" not in st.session_state:
    st.session_state.current_project = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"


# ── Sidebar navigation ───────────────────────────────────────


def _sidebar() -> None:
    with st.sidebar:
        st.markdown("## 📋 KT Hub")
        st.markdown("*项目交接知识管理平台*")
        st.markdown("---")

        page = st.radio(
            "导航",
            ["仪表盘", "新建项目", "搜索"],
            label_visibility="collapsed",
            key="nav_radio",
        )
        page_map = {"仪表盘": "dashboard", "新建项目": "new_project", "搜索": "search"}
        st.session_state.page = page_map.get(page, "dashboard")

        st.markdown("---")

        # Project quick-select
        projects = storage.list_projects()
        if projects:
            st.markdown("### 项目列表")
            for p in projects:
                status_icon = {"进行中": "🟢", "已完成": "🔵", "暂停": "🟡"}.get(
                    p["status"], "⚪"
                )
                if st.button(
                    f"{status_icon} {p['name']}",
                    key=f"sidebar_{p['id']}",
                    use_container_width=True,
                ):
                    st.session_state.current_project = p["id"]
                    st.session_state.page = "project_detail"
                    st.rerun()

        st.markdown("---")
        st.markdown(
            '<div class="kt-footer">KT Hub v1.0<br>AI-assisted</div>',
            unsafe_allow_html=True,
        )


_sidebar()

# ── Helper functions ──────────────────────────────────────────


def _render_hero() -> None:
    st.markdown(
        """
        <div class="kt-hero">
            <h1>📋 Knowledge Transfer Hub</h1>
            <p>集中管理项目交接文档，确保知识无缝传递</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _status_badge(status: str) -> str:
    cls = {"进行中": "active", "已完成": "completed", "暂停": "paused"}.get(
        status, "active"
    )
    return f'<span class="kt-badge kt-badge-{cls}">{status}</span>'


def _progress_bar(pct: int) -> str:
    return f"""
    <div class="kt-progress-bar">
        <div class="kt-progress-fill" style="width: {pct}%"></div>
    </div>
    """


def _checklist_progress(checklist: list[dict]) -> int:
    if not checklist:
        return 0
    done = sum(1 for c in checklist if c.get("done"))
    return int(done / len(checklist) * 100)


# ── Dashboard page ────────────────────────────────────────────


def page_dashboard() -> None:
    _render_hero()

    projects = storage.list_projects()

    # Metrics row
    total = len(projects)
    active = sum(1 for p in projects if p["status"] == "进行中")
    completed = sum(1 for p in projects if p["status"] == "已完成")
    total_docs = sum(len(p.get("documents", {})) for p in projects)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("项目总数", total)
    c2.metric("进行中", active)
    c3.metric("已完成", completed)
    c4.metric("文档总数", total_docs)

    st.markdown("---")

    if not projects:
        st.info("还没有项目。点击左侧「新建项目」开始创建。")
        return

    st.markdown("## 项目概览")

    for p in projects:
        pct = _checklist_progress(p.get("checklist", []))
        doc_count = len(p.get("documents", {}))

        tags_html = f'<span class="tag">{p.get("therapeutic_area", "")}</span>'
        if p.get("phase"):
            tags_html += f'<span class="tag">{p["phase"]}</span>'

        st.markdown(
            f"""
            <div class="kt-card">
                <div style="display:flex; justify-content:space-between;
                            align-items:flex-start;">
                    <div>
                        <h4>{p['name']}</h4>
                        <div class="meta">{p.get('description', '')[:120]}</div>
                    </div>
                    <div style="text-align:right;">
                        {_status_badge(p['status'])}
                    </div>
                </div>
                <div style="margin-top:0.8rem;">
                    {tags_html}
                </div>
                <div style="margin-top:0.8rem;">
                    <div class="meta">
                        交接进度 {pct}% · {doc_count} 份文档 ·
                        负责人: {p.get('owner', '-')}
                    </div>
                    {_progress_bar(pct)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_open, col_del = st.columns([6, 1])
        with col_open:
            if st.button("打开项目 →", key=f"open_{p['id']}"):
                st.session_state.current_project = p["id"]
                st.session_state.page = "project_detail"
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{p['id']}", help="删除项目"):
                storage.delete_project(p["id"])
                st.rerun()


# ── New project page ──────────────────────────────────────────


def page_new_project() -> None:
    st.markdown("## 新建交接项目")

    with st.form("new_project_form"):
        name = st.text_input("项目名称 *", placeholder="例：XX药物III期临床试验")
        description = st.text_area(
            "项目描述", placeholder="简要描述项目背景、目标和当前状态"
        )

        c1, c2 = st.columns(2)
        with c1:
            therapeutic_area = st.selectbox(
                "治疗领域",
                [
                    "肿瘤学",
                    "免疫学",
                    "神经科学",
                    "心血管",
                    "罕见病",
                    "感染性疾病",
                    "眼科",
                    "呼吸系统",
                    "其他",
                ],
            )
        with c2:
            phase = st.selectbox(
                "项目阶段",
                [
                    "临床前",
                    "I期",
                    "II期",
                    "III期",
                    "注册申报",
                    "上市后",
                    "非临床项目",
                ],
            )

        c3, c4 = st.columns(2)
        with c3:
            owner = st.text_input("当前负责人 *", placeholder="姓名")
        with c4:
            status = st.selectbox("项目状态", ["进行中", "已完成", "暂停"])

        submitted = st.form_submit_button("创建项目", use_container_width=True)

        if submitted:
            if not name or not owner:
                st.error("请填写项目名称和负责人。")
            else:
                project = storage.create_project(
                    name=name,
                    description=description,
                    therapeutic_area=therapeutic_area or "",
                    phase=phase or "",
                    owner=owner,
                    status=status or "进行中",
                )
                st.success(f"项目「{project['name']}」创建成功！")
                st.session_state.current_project = project["id"]
                st.session_state.page = "project_detail"
                st.rerun()


# ── Project detail page ──────────────────────────────────────


def page_project_detail() -> None:
    pid = st.session_state.current_project
    if not pid:
        st.warning("请先选择一个项目。")
        return

    project = storage.get_project(pid)
    if not project:
        st.error("项目不存在。")
        return

    # Header
    st.markdown(
        f"""
        <div class="kt-hero">
            <h1>{project['name']}</h1>
            <p>{project.get('description', '')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Project meta
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("治疗领域", project.get("therapeutic_area", "-"))
    mc2.metric("项目阶段", project.get("phase", "-"))
    mc3.metric("负责人", project.get("owner", "-"))
    pct = _checklist_progress(project.get("checklist", []))
    mc4.metric("交接进度", f"{pct}%")

    # Tabs
    tab_docs, tab_add, tab_checklist, tab_settings = st.tabs(
        ["📄 文档列表", "➕ 添加文档", "✅ 交接清单", "⚙️ 项目设置"]
    )

    # ── Documents tab ──
    with tab_docs:
        _render_documents_tab(pid)

    # ── Add document tab ──
    with tab_add:
        _render_add_document_tab(pid)

    # ── Checklist tab ──
    with tab_checklist:
        _render_checklist_tab(pid, project)

    # ── Settings tab ──
    with tab_settings:
        _render_settings_tab(pid, project)


def _render_documents_tab(pid: str) -> None:
    cat_filter = st.selectbox(
        "按类别筛选",
        ["全部"] + storage.DOCUMENT_CATEGORIES,
        key="doc_cat_filter",
    )

    category = None if cat_filter == "全部" else cat_filter
    docs = storage.list_documents(pid, category=category)

    if not docs:
        st.info("该类别下暂无文档。请在「添加文档」标签页中创建。")
        return

    for doc in docs:
        tags_html = "".join(
            f'<span class="tag">{t}</span>' for t in doc.get("tags", [])
        )
        created = doc.get("created_at", "")[:10]

        st.markdown(
            f"""
            <div class="kt-card">
                <div style="display:flex; justify-content:space-between;">
                    <h4>{doc['title']}</h4>
                    <span class="tag">{doc['category']}</span>
                </div>
                <div class="meta">
                    作者: {doc.get('author', '-')} · 创建: {created}
                    {' · 附件: ' + doc['file_name']
                     if doc.get('file_name') else ''}
                </div>
                {f'<div style="margin-top:0.4rem;">{tags_html}</div>'
                 if tags_html else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("查看详情", expanded=False):
            st.markdown(doc.get("content", ""))

            ec1, ec2 = st.columns([4, 1])
            with ec2:
                if st.button("删除文档", key=f"deldoc_{doc['id']}"):
                    storage.delete_document(pid, doc["id"])
                    st.rerun()


def _render_add_document_tab(pid: str) -> None:
    with st.form("add_doc_form"):
        title = st.text_input("文档标题 *", placeholder="例：项目架构说明")
        category = st.selectbox("文档类别 *", storage.DOCUMENT_CATEGORIES)
        author = st.text_input("作者", placeholder="姓名")
        content = st.text_area(
            "文档内容 *",
            placeholder=(
                "支持 Markdown 格式。\n\n可以包含：\n"
                "- 项目背景\n- 关键决策\n- 技术细节\n- 注意事项"
            ),
            height=300,
        )
        tags_input = st.text_input(
            "标签（逗号分隔）", placeholder="例：关键, 待确认, Q1"
        )

        uploaded = st.file_uploader(
            "附件（可选）",
            type=["pdf", "docx", "xlsx", "pptx", "txt", "csv", "md"],
        )

        submitted = st.form_submit_button("保存文档", use_container_width=True)

        if submitted:
            if not title or not content:
                st.error("请填写文档标题和内容。")
            else:
                tags = (
                    [t.strip() for t in tags_input.split(",") if t.strip()]
                    if tags_input
                    else []
                )
                file_name = None
                if uploaded:
                    file_path = storage.UPLOAD_DIR / uploaded.name
                    file_path.write_bytes(uploaded.getvalue())
                    file_name = uploaded.name

                storage.add_document(
                    project_id=pid,
                    title=title,
                    category=category or "",
                    content=content,
                    author=author,
                    tags=tags,
                    file_name=file_name,
                )
                st.success(f"文档「{title}」已保存！")
                st.rerun()


def _render_checklist_tab(pid: str, project: dict) -> None:
    st.markdown("### 交接检查清单")
    st.markdown("跟踪交接进度，确保所有关键事项都已完成。")

    checklist = project.get("checklist", [])
    pct = _checklist_progress(checklist)

    st.markdown(
        f"""
        <div style="margin: 1rem 0;">
            <div class="meta">完成进度: {pct}%</div>
            {_progress_bar(pct)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    updated = False
    for i, item in enumerate(checklist):
        new_val = st.checkbox(
            item["item"],
            value=item.get("done", False),
            key=f"check_{pid}_{i}",
        )
        if new_val != item.get("done", False):
            checklist[i]["done"] = new_val
            updated = True

    if updated:
        storage.update_checklist(pid, checklist)
        st.rerun()


def _render_settings_tab(pid: str, project: dict) -> None:
    st.markdown("### 项目设置")

    with st.form("edit_project_form"):
        name = st.text_input("项目名称", value=project["name"])
        description = st.text_area(
            "项目描述", value=project.get("description", "")
        )

        c1, c2 = st.columns(2)
        with c1:
            areas = [
                "肿瘤学",
                "免疫学",
                "神经科学",
                "心血管",
                "罕见病",
                "感染性疾病",
                "眼科",
                "呼吸系统",
                "其他",
            ]
            current_area = project.get("therapeutic_area", "其他")
            area_idx = (
                areas.index(current_area) if current_area in areas else 0
            )
            therapeutic_area = st.selectbox(
                "治疗领域", areas, index=area_idx
            )
        with c2:
            phases = [
                "临床前",
                "I期",
                "II期",
                "III期",
                "注册申报",
                "上市后",
                "非临床项目",
            ]
            current_phase = project.get("phase", "临床前")
            phase_idx = (
                phases.index(current_phase)
                if current_phase in phases
                else 0
            )
            phase = st.selectbox("项目阶段", phases, index=phase_idx)

        c3, c4 = st.columns(2)
        with c3:
            owner = st.text_input(
                "负责人", value=project.get("owner", "")
            )
        with c4:
            statuses = ["进行中", "已完成", "暂停"]
            current_status = project.get("status", "进行中")
            status_idx = (
                statuses.index(current_status)
                if current_status in statuses
                else 0
            )
            status = st.selectbox("状态", statuses, index=status_idx)

        if st.form_submit_button("保存修改", use_container_width=True):
            storage.update_project(
                pid,
                name=name,
                description=description,
                therapeutic_area=therapeutic_area,
                phase=phase,
                owner=owner,
                status=status,
            )
            st.success("项目信息已更新！")
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚠️ 危险操作")
    if st.button("删除此项目", type="secondary"):
        storage.delete_project(pid)
        st.session_state.current_project = None
        st.session_state.page = "dashboard"
        st.rerun()


# ── Search page ───────────────────────────────────────────────


def page_search() -> None:
    st.markdown("## 🔍 全局搜索")
    st.markdown("在所有项目和文档中搜索关键词。")

    query = st.text_input(
        "搜索关键词",
        placeholder="输入项目名、文档标题、内容或标签...",
        key="search_query",
    )

    if query:
        results = storage.search_all(query)
        if results:
            st.markdown(f"找到 **{len(results)}** 条结果：")
            for r in results:
                st.markdown(
                    f"""
                    <div class="kt-card">
                        <h4>{r['doc_title']}</h4>
                        <div class="meta">
                            项目: {r['project_name']} ·
                            类别: {r['category']}
                        </div>
                        <div style="margin-top:0.5rem;
                                    color: var(--slate-600);
                                    font-size:0.9rem;">
                            {r['snippet']}...
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "打开项目",
                    key=f"search_open_{r['project_id']}_{r['doc_id']}",
                ):
                    st.session_state.current_project = r["project_id"]
                    st.session_state.page = "project_detail"
                    st.rerun()
        else:
            st.info("未找到匹配结果。")


# ── Router ────────────────────────────────────────────────────

page_map = {
    "dashboard": page_dashboard,
    "new_project": page_new_project,
    "project_detail": page_project_detail,
    "search": page_search,
}

current_page = st.session_state.get("page", "dashboard")
page_fn = page_map.get(current_page, page_dashboard)
page_fn()
