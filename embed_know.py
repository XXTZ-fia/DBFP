import os
import torch
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

INDEX_PATH = "rag/faiss_index"

embedding = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'},
    encode_kwargs={
        'normalize_embeddings': True,
        'batch_size': 32
    }
)

# 2. 如果向量库已存在，直接加载
if os.path.exists(INDEX_PATH):
    print("加载已有向量库...")
    vectorstore = FAISS.load_local(INDEX_PATH, embedding, allow_dangerous_deserialization=True)

else:
    print("未找到向量库，开始构建...")
    # 文本切分
    medical_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=100,
        length_function=len
    )

    medical_text = ""
    file_name_list = [
        "akshare_doc.txt"
    ]
    for file_name in file_name_list:
        with open(file_name, "r", encoding="utf-8") as f:
            medical_text += f.read()

    docs = medical_text_splitter.create_documents([medical_text])
    texts = [d.page_content for d in docs]

    # 分批 embedding（带进度条）
    batch_size = 32
    all_embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Embedding progress"):
        batch = texts[i:i+batch_size]
        emb = embedding.embed_documents(batch)
        all_embeddings.extend(emb)

    # 创建向量库（注意 from_embeddings 参数格式）
    text_embeddings = list(zip(texts, all_embeddings))
    vectorstore = FAISS.from_embeddings(text_embeddings, embedding)

    # 保存向量库
    vectorstore.save_local(INDEX_PATH)
    print("向量库已保存到", INDEX_PATH)

# 3. 获取检索器
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})