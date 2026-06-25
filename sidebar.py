import streamlit as st

def render_sidebar() -> None:
    if "known_users" not in st.session_state:
        st.session_state.known_users = []
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    
    with st.sidebar:
        st.markdown("## 🗺️ GeoQuery")

        user_opts = ["— select user —"] + st.session_state.known_users + ["➕ New user…"]
        sel_user = st.selectbox("User", user_opts, index=0,
                                label_visibility="collapsed")

        if sel_user == "➕ New user…":
            new_name = st.text_input("Username",
                                     placeholder="e.g. participant_01",
                                     key="new_username_input")
            if st.button("Create", use_container_width=True, key="create_user_btn"):
                if new_name.strip() and new_name.strip() not in st.session_state.known_users:
                    st.session_state.known_users.append(new_name.strip())
                    st.session_state.current_user = new_name.strip()
                    st.rerun()

        elif sel_user != "— select user —":
            if st.session_state.current_user != sel_user:
                st.session_state.current_user = sel_user
                st.rerun()

        if st.session_state.current_user:
            st.markdown("---")
            st.caption(f"**{st.session_state.current_user}** is selected. ")
    

