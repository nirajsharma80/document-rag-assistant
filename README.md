# Papertrail — PDF RAG Assistant

Papertrail is a Streamlit app for asking questions about selectable-text PDFs. It extracts PDF text locally, retrieves relevant page-level passages using a lightweight local BM25 search index, and sends only those excerpts and the question to Google Gemini or OpenAI to draft an answer with source citations.

## Features

- Upload and index multiple PDFs in the browser.
- Local retrieval with BM25; no FAISS, PyTorch, model download, or GPU required.
- Gemini and OpenAI answer providers.
- Source filename, page number, and retrieved passage previews.
- API keys can be entered as masked session-only values or configured in Streamlit secrets.
- Scanned/image-only PDFs are detected and reported; OCR is not included.

## Run on Windows with VS Code

Open this folder in VS Code, then run `run.bat` from File Explorer, or open a PowerShell terminal in the project folder and run:

```powershell
.\run.ps1
```

The launcher creates `.venv`, installs `requirements.txt`, and starts Papertrail. The batch launcher invokes PowerShell with a process-only execution policy so you do not have to change your saved Windows policy. Open the local URL Streamlit prints (normally `http://localhost:8501`). The project also supports running manually:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

`run.ps1` prefers the Python executable used in this environment (`%LOCALAPPDATA%\Python\pythoncore-3.15-64\python.exe`) when present, and otherwise uses `python` from PATH. If an installed Python version cannot install one of the requirements, install Python 3.14 or 3.13 from python.org, select it in VS Code, and rerun the script.

## Configure a model key

Choose Gemini or OpenAI in the sidebar and enter that provider's key in the masked session field. The value stays in the current Streamlit session. For repeated use, create `.streamlit/secrets.toml` from `.streamlit/secrets.toml.example` and add your key there. Never commit real API keys.

Without a model key, PDF text extraction and local search can still be used, but generated answers require a provider key.

## Data handling and limitations

- Uploaded PDFs are parsed and indexed in memory by this app and are not saved to disk.
- When you ask a question, retrieved excerpts and the question are sent to the selected provider. Avoid using confidential documents unless your data policy allows it.
- The index and chat are held in Streamlit session state and disappear when that session ends or the page is refreshed.
- Retrieval is lexical BM25 search. It does not understand semantic similarity as a neural embedding model would; inspect the cited passages.
- Scanned PDFs need OCR before indexing.
- Model answers can be wrong. Citations help you check the source but do not guarantee correctness.

## Troubleshooting

- **PowerShell blocks `run.ps1`:** run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal, then retry. This only applies to the current PowerShell process.
- **Key not configured:** enter the masked key in the sidebar or set it in `.streamlit/secrets.toml` and restart.
- **No text extracted:** the PDF may be scanned/image-only or password-protected.
- **Port already in use:** stop the existing Streamlit app with `Ctrl+C`, or run `.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502`.

## Stack

Python · Streamlit · pypdf · local BM25 retrieval · Google Gen AI SDK · OpenAI Python SDK

## License

MIT. See [LICENSE](LICENSE).
