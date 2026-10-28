# Papertrail — PDF RAG Assistant

A focused PDF question-answering app built around LangChain, local sentence-transformer embeddings, FAISS similarity search, and Gemini or OpenAI generation. Each answer is grounded in retrieved text and accompanied by filename/page references.

## What it does

1. Extracts selectable text from uploaded PDFs.
2. Splits pages into overlapping chunks and embeds them locally.
3. Retrieves the most relevant passages for a question.
4. Asks the chosen chat model to answer from those passages and show citations.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Add `GOOGLE_API_KEY` or `OPENAI_API_KEY` to your environment. Alternatively copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in the key. The secrets file is ignored by Git. The first indexing run downloads the embedding model to the local Hugging Face cache.

## Design notes

- Embeddings and FAISS retrieval run locally; selected text excerpts are sent to the configured model provider to generate answers.
- The index lives in Streamlit session state and is cleared when the session ends.
- Scanned/image-only PDFs require an OCR step and currently produce no searchable text.
- Similarity retrieval can miss relevant content; check the source passages before relying on an answer.
- Never upload confidential documents to a model provider unless your data-handling policy permits it.

## Stack

Python · Streamlit · LangChain · FAISS · sentence-transformers · pypdf · Gemini/OpenAI

## License

MIT. See [LICENSE](LICENSE).
