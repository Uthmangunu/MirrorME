import streamlit as st
from firebase_client import get_doc, save_doc, get_all_docs
from datetime import datetime

st.set_page_config(page_title="🌍 Mirror Feed", page_icon="🧠")
st.title("🌍 Explore Public Mirrors")

mirrors = get_all_docs("public_mirrors")
current_user = st.session_state.get("user", {}).get("localId")

if not mirrors:
    st.info("No public mirrors yet. Encourage others to share their minds!")
else:
    for mirror in mirrors:
        user_id = mirror.get("user_id")
        if not user_id:
            continue

        st.markdown("---")
        st.markdown(f"## {mirror.get('emoji', '')} {mirror.get('archetype', '')}")
        st.caption(mirror.get("desc", ""))

        st.markdown("**Trait Snapshot:**")
        for trait, score in mirror.get("traits", {}).items():
            st.progress(score / 100.0, text=f"{trait.title()}: {score}")

        with st.expander("💬 Comments"):
            comment_path = f"comments/{user_id}"
            comment_doc = get_doc("comments", user_id) or {}
            comments = comment_doc.get("entries", [])

            for c in comments[-5:]:
                st.markdown(f"**{c['author']}** said:")
                st.markdown(f"\> {c['text']}")
                st.caption(c['timestamp'])

            st.markdown("---")
            comment_key = f"comment_input_{user_id}"
            if comment_key not in st.session_state:
                st.session_state[comment_key] = ""

            new_comment = st.text_input("Write a comment...", key=comment_key)
            if st.button("Post", key=f"comment_btn_{user_id}") and new_comment.strip():
                new_entry = {
                    "author": current_user or "Anonymous",
                    "text": new_comment.strip(),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                comments.append(new_entry)
                save_doc("comments", user_id, {"entries": comments})
                st.success("Comment posted!")
                st.session_state[comment_key] = ""

        if st.button(f"🗣 Talk to this Mirror", key=f"talk_{user_id}"):
            st.session_state["sandbox_target"] = user_id
            st.switch_page("pages/Sandbox.py")
