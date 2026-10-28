import os
import streamlit as st
from rag import build_index, answer_question

st.set_page_config(page_title="Papertrail | PDF assistant", page_icon="⌕", layout="wide")
st.title("⌕ Papertrail")
st.caption("Ask questions across your PDFs. Answers include page-level citations from the uploaded documents.")
with st.sidebar:
    st.header("Workspace")
    provider=st.selectbox("Answer model",["Google Gemini","OpenAI"] )
    model=st.text_input("Model",value="gemini-2.5-flash" if provider=="Google Gemini" else "gpt-4o-mini")
    secret_name="GOOGLE_API_KEY" if provider=="Google Gemini" else "OPENAI_API_KEY"
    try:
        configured_key=os.getenv(secret_name) or st.secrets.get(secret_name)
    except Exception:
        configured_key=os.getenv(secret_name)
    has_key=bool(configured_key)
    st.caption(f"{secret_name}: {'configured' if has_key else 'not configured'}")
    uploads=st.file_uploader("Add PDF documents",type=["pdf"],accept_multiple_files=True)
    if st.button("Index documents",type="primary",disabled=not uploads):
        with st.spinner("Extracting, chunking, and embedding pages..."):
            st.session_state.vectorstore, st.session_state.file_names=build_index(uploads)
        st.success(f"Indexed {len(st.session_state.file_names)} document(s).")
if st.session_state.get("file_names"):
    st.caption("Indexed: " + " · ".join(st.session_state.file_names))
question=st.chat_input("Ask a question grounded in your uploaded PDFs")
if question:
    if not st.session_state.get("vectorstore"):
        st.warning("Upload and index at least one PDF first.")
    elif not has_key:
        st.error(f"Add {secret_name} to your environment or .streamlit/secrets.toml to generate answers.")
    else:
        with st.chat_message("user"): st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Retrieving relevant passages..."):
                response,sources=answer_question(st.session_state.vectorstore,question,provider,model,configured_key)
            st.markdown(response)
            with st.expander("Sources"):
                for source in sources: st.markdown(f"**{source['file']}**, page {source['page']} · {source['preview']}")
