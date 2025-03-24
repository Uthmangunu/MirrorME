import streamlit as st
import sys
import os
sys.path.append(os.path.abspath("."))

from firebase_client import get_all_docs, get_doc, save_doc

st.set_page_config(page_title="🌍 Mirror Feed", page_icon="🧠")
st.title("🌍 Explore Public Mirrors")

mirrors = get_all_docs("public_mirrors")

if not mirrors:
    st.info("No public mirrors yet. Encourage others to share their minds!")
else:
    for mirror in mirrors:
        user_id = mirror.get("user_id")
        st.markdown("---")
        st.markdown(f"## {mirror.get('emoji', '')} {mirror.get('archetype', '')}")
        st.caption(mirror.get("desc", ""))

        st.markdown("**Trait Snapshot:**")
        for trait, score in mirror.get("traits", {}).items():
            st.progress(score / 100.0, text=f"{trait.title()}: {score}")

        if st.button(f"🗣 Talk to this Mirror", key=f"talk_{user_id}"):
            st.session_state["sandbox_target"] = user_id
            st.switch_page("Sandbox.py")

        with st.expander("💬 Leave a Comment"):
            comments = get_doc("mirror_comments", user_id).get("comments", [])
            for c in comments:
                st.markdown(f"- {c}")

            new_comment = st.text_input("Add your thoughts:", key=f"comment_input_{user_id}")
            if st.button("Submit Comment", key=f"submit_comment_{user_id}") and new_comment:
                comments.append(new_comment)
                save_doc("mirror_comments", user_id, {"comments": comments})
                st.experimental_rerun()
