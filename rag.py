import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

def build_index(uploads):
    from pypdf import PdfReader
    docs=[]
    splitter=RecursiveCharacterTextSplitter(chunk_size=900,chunk_overlap=140,add_start_index=True)
    for upload in uploads:
        reader=PdfReader(upload)
        for page_num,page in enumerate(reader.pages,1):
            text=(page.extract_text() or "").strip()
            if text:
                for chunk in splitter.split_text(text): docs.append(Document(page_content=chunk,metadata={"source":upload.name,"page":page_num}))
    if not docs: raise ValueError("No extractable text found. Scanned PDFs need OCR before indexing.")
    embeddings=HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL,model_kwargs={"device":"cpu"},encode_kwargs={"normalize_embeddings":True})
    return FAISS.from_documents(docs,embeddings), sorted({d.metadata["source"] for d in docs})

def answer_question(vectorstore,question,provider,model_name,api_key):
    retrieved=vectorstore.similarity_search(question,k=5)
    context="\n\n".join(f"[Source: {d.metadata['source']}, page {d.metadata['page']}]\n{d.page_content}" for d in retrieved)
    prompt=("Answer only using the supplied excerpts. If the excerpts do not contain the answer, say so. "
            "Cite claims with the source filename and page number exactly as shown.\n\n"
            f"EXCERPTS:\n{context}\n\nQUESTION: {question}")
    if provider=="Google Gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm=ChatGoogleGenerativeAI(model=model_name,google_api_key=api_key,temperature=0.1)
    else:
        from langchain_openai import ChatOpenAI
        llm=ChatOpenAI(model=model_name,api_key=api_key,temperature=0.1)
    answer=llm.invoke(prompt).content
    sources=[{"file":d.metadata["source"],"page":d.metadata["page"],"preview":d.page_content[:220].replace("\n"," ")+"…"} for d in retrieved]
    return answer,sources
