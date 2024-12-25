from langchain.chains import ConversationalRetrievalChain
from langchain_community.llms import Replicate


def get_chat_chain(retriever):
    llm = Replicate(
        model="meta/meta-llama-3-8b-instruct",
        model_kwargs={"temperature": 0.0, "top_p": 1, "max_new_tokens": 500},
    )

    chat_chain = ConversationalRetrievalChain.from_llm(
        llm, retriever, return_source_documents=True
    )
    return chat_chain


def chat(query, chat_chain, chat_history):
    response = chat_chain({"question": query, "chat_history": chat_history})
    # Update chat history
    chat_history.append((query, response["answer"]))
    return response, chat_history
