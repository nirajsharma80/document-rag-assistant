from __future__ import annotations

import os

import streamlit as st

from rag import answer_question, build_index

st.set_page_config(page_title="Papertrail | PDF assistant", page_icon="📄", layout="wide")
st.title("Papertrail")
st.caption("Ask questions across your PDFs. Answers include citations to the source file and page.")


def _configured_secret(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


with st.sidebar:
    st.header("Workspace")
    provider = st.selectbox("Answer model", ["Google Gemini", "OpenAI"])
    secret_name = "GOOGLE_API_KEY" if provider == "Google Gemini" else "OPENAI_API_KEY"
    default_model = "gemini-2.5-flash" if provider == "Google Gemini" else "gpt-4o-mini"
    model = st.text_input("Model", value=default_model)
    configured_key = _configured_secret(secret_name)
    session_key = st.text_input(
        f"{secret_name} (optional session key)",
        type="password",
        help="Used only for this app session. Or configure it in .streamlit/secrets.toml.",
    ).strip()
    api_key = session_key or configured_key
    st.caption(f"{secret_name}: {'ready' if api_key else 'not configured'}")
    uploads = st.file_uploader(
        "Add PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        help="Selectable text PDFs up to 25 MB each. Scanned PDFs need OCR first.",
    )
    if st.button("Index documents", type="primary", disabled=not uploads):
        with st.spinner("Extracting pages and building the local search index..."):
            try:
                index, filenames = build_index(uploads)
            except ValueError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Could not index the PDFs: {exc}")
            else:
                st.session_state.rag_index = index
                st.session_state.file_names = filenames
                st.session_state.messages = []
                st.success(f"Indexed {len(filenames)} document(s), {len(index.passages)} searchable passage(s).")

st.info(
    "PDF parsing and search run locally. When you ask a question, only the retrieved text excerpts "
    "and your question are sent to the selected model provider."
)

if st.session_state.get("file_names"):
    st.caption("Indexed: " + " · ".join(st.session_state.file_names))
    for message in st.session_state.get("messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("Sources"):
                    for source in message["sources"]:
                        st.markdown(f"**{source['file']}**, page {source['page']} · {source['preview']}")

question = st.chat_input("Ask a question grounded in your indexed PDFs")
if question:
    if not st.session_state.get("rag_index"):
        st.warning("Upload and index at least one PDF first.")
    elif not api_key:
        st.error(f"Configure {secret_name} in the sidebar or in .streamlit/secrets.toml before asking.")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching your PDFs and generating an answer..."):
                try:
                    response, sources = answer_question(
                        st.session_state.rag_index, question, provider, model, api_key
                    )
                except Exception as exc:
                    st.error(f"Answer generation failed: {exc}")
                else:
                    st.markdown(response)
                    with st.expander("Sources"):
                        for source in sources:
                            st.markdown(f"**{source['file']}**, page {source['page']} · {source['preview']}")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response, "sources": sources}
                    )
