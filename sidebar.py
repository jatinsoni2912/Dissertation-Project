import streamlit as st

from conversations import (
    get_all_users, create_user,
    new_conversation, get_all_conversations,
    load_conversation, delete_conversation, get_user_stats,
)

def render_sidebar() -> None:
    
    with st.sidebar:
        st.markdown("## 🗺️ GeoQuery")

        existing = get_all_users()
        opts = ["— select user —"] + existing + ["➕ New user…"]
        sel_user = st.selectbox("User", opts, index=0, label_visibility="collapsed")

        
        if sel_user == "➕ New user…":
            name = st.text_input("Username",
                                     placeholder="e.g. participant_01",
                                     key="new_username_input")
            
            if st.button("Create", use_container_width=True, key="create_user_btn"):
                if name.strip():
                    create_user(name.strip())
                    st.session_state.current_user    = name.strip()
                    st.session_state.current_conv_id = None
                    st.session_state.current_conv    = None
                    st.rerun()

        elif sel_user != "— select user —":
            if st.session_state.current_user != sel_user:
                st.session_state.current_user    = sel_user
                st.session_state.current_conv_id = None
                st.session_state.current_conv    = None
                st.rerun()
        
        

