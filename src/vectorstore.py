from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter


def split_transcript(chapter_transcript):
    # Larger chunk_size and chunk_overlap better higher level context preservation
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    all_splits = []
    for chapter in chapter_transcript:
        all_splits.extend(text_splitter.split_text(" ".join(chapter.transcript)))
    return all_splits


def get_vectorstore(all_splits):

    # Store the document into a vector store with a specific embedding model
    vectorstore = FAISS.from_texts(
        all_splits,
        HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"),
    )
    return vectorstore


def get_retriever(meta_data, chapter_transcript):
    all_splits = [
        f"video title: {meta_data.title}",
        f"youtube channel name: {meta_data.channel_name}",
        f"video publish date: {meta_data.publish_date}",
    ]
    transcript_splits = split_transcript(chapter_transcript)
    all_splits.extend(transcript_splits)
    vectorstore = get_vectorstore(all_splits)
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 10})

    return retriever
