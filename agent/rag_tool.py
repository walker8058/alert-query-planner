import os
from uuid import uuid4
from dotenv import load_dotenv
from langchain_google_vertexai import VertexAIEmbeddings, VertexAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from config import MODEL, CHROMA_PERSIST_DIRECTORY
from plans import a1, b1

# 載入 .env 設定
load_dotenv()

# 初始化 Embeddings 與 LLM
embeddings = VertexAIEmbeddings(model_name="gemini-embedding-001")
llm = VertexAI(
    model_name=MODEL,
    temperature=0.0,
    max_output_tokens=512,
)

# 初始化 Chroma 向量庫
vector_store = Chroma(
    collection_name="rag_collection",
    embedding_function=embeddings,
    persist_directory=CHROMA_PERSIST_DIRECTORY,
)

# 若向量庫為空，可初始化一些測試文件（正式環境請移除或改為動態管理）
if not vector_store.get()["ids"]:
    docs = [
        Document(page_content=a1, metadata={"source": "plans", "id":1}),
        Document(page_content=b1, metadata={"source": "plans", "id":2}),
    ]
    uuids = [str(uuid4()) for _ in docs]
    vector_store.add_documents(documents=docs, ids=uuids)

# 建立 Retriever
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 1}
)

# 建立 RAG Chain
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
)

def plans_knowledge_base(query: str) -> str:
    """取得查詢計劃
    說明:
        根據輸入訊息的種類，從RAG知識庫檢索符合該種類的計劃。
    """
    print("開始檢索計劃知識庫")
    print(f"查詢：{query}")
    result = rag_chain.invoke(query)
    answer = result.get("source_documents", [])
    sources = [
        f"- ({doc.metadata.get('source', '')}) {doc.page_content}"
        for doc in result.get("source_documents", [])
    ]
    sources_str = "\n".join(sources)
    print(f"回答：{answer}\n\n來源文件：\n{sources_str}")
    return answer