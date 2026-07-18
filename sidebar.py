import streamlit as st

from conversations import (
    get_all_users, create_user,
    new_conversation, get_all_conversations,
    load_conversation, delete_conversation, get_user_stats,
)

def handle_user_selection():
    existing = get_all_users()
    opts = ["— select user —"] + existing + ["➕ New user…"]

    sel = st.selectbox("User", opts, index=0, label_visibility="collapsed")

    if sel == "➕ New user…":
        create_new_user_flow()
        return

    if sel != "— select user —":
        switch_user_if_needed(sel)

def create_new_user_flow():
    name = st.text_input("Username", placeholder="e.g. participant_01", key="new_username_input")
    
    if st.button("Create", use_container_width=True, key="create_user_btn"):
        if name.strip():
            create_user(name.strip())
            st.session_state.current_user = name.strip()
            st.session_state.current_conv_id = None
            st.session_state.current_conv = None
            st.rerun()

def switch_user_if_needed(sel):
    if st.session_state.current_user != sel:
        st.session_state.current_user = sel
        st.session_state.current_conv_id = None
        st.session_state.current_conv = None
        st.rerun()

def render_chat_controls():
    col_new, col_del = st.columns([3, 1])

    with col_new:
        if st.button("✏️ New chat", use_container_width=True, key="new_chat_btn"):
            conv = new_conversation(st.session_state.current_user)
            st.session_state.current_conv_id = conv["id"]
            st.session_state.current_conv = conv
            st.session_state.selected_example = ""
            st.rerun()

    with col_del:
        if st.session_state.current_conv_id and st.button("🗑️", key="del_chat_btn", help="Delete this conversation"):
            delete_conversation(st.session_state.current_user, st.session_state.current_conv_id)

            st.session_state.current_conv_id = None
            st.session_state.current_conv = None
            st.rerun()        

def render_conversation_list():
    all_convs = get_all_conversations(st.session_state.current_user)

    if not all_convs:
        st.caption("No conversations yet — click ✏️ New chat to start.")
        return

    for cv in all_convs:
        render_conversation_button(cv)

def render_conversation_button(cv):
    active = cv["id"] == st.session_state.current_conv_id
    ts = cv["updated_at"][:10] if cv["updated_at"] else ""
    label = f"{'▶ ' if active else ''}{cv['title']}"

    if st.button(label, key=f"conv_{cv['id']}", use_container_width=True, help=f"{ts} · {cv['msg_count']} message(s)", type="primary" if active else "secondary"):
        st.session_state.current_conv_id = cv["id"]
        st.session_state.current_conv = load_conversation(st.session_state.current_user, cv["id"])
        st.rerun()

def render_user_stats():
    st.markdown("---")
    stats = get_user_stats(st.session_state.current_user)

    st.caption(f"**{st.session_state.current_user}**  ·  "
        f"{stats['conversations']} chats  ·  "
        f"{stats['total_queries']} queries  ·  "
        f"🎤 {stats['voice_queries']}")
        
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🗺️ GeoQuery")

        handle_user_selection()

        if not st.session_state.current_user:
            return

        st.markdown("---")
        render_chat_controls()
        render_conversation_list()
        render_user_stats()





