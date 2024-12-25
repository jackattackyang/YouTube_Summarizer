from flask import Flask, request, jsonify

from data.get_youtube_data import YouTubeDataFetcher
from data.preprocess import merge_chapter_transcript, get_prompt
from api.replicate_api import llama3_8b, llama3_70b

from src.vectorstore import get_retriever
from src.chat import chat, get_chat_chain


# video_url = "https://www.youtube.com/watch?v=QlUcyaXiXPE&ab_channel=MorningBrewDaily"

app = Flask(__name__)
youtube = YouTubeDataFetcher()

session_data = {}
chat_history = []  # Global store for chat_history between user and llm


@app.route("/", methods=["POST"])
def summarize():
    global session_data

    data = request.json
    youtube_url = data.get("youtube_url")
    if "youtube.com" not in youtube_url:
        return jsonify({"error": "No YouTube URL provided"}), 400

    try:
        meta_data = youtube.get_meta_data(youtube_url)
        session_data["meta_data"] = meta_data

        chapter_transcript = merge_chapter_transcript(meta_data)
        prompt = get_prompt(meta_data, chapter_transcript)
        response = llama3_8b(prompt)
        output = response

        retriever = get_retriever(meta_data, chapter_transcript)
        chat_chain = get_chat_chain(retriever)

        session_data["chapter_transcript"] = chapter_transcript
        session_data["retriever"] = retriever
        session_data["chat_chain"] = chat_chain

        return jsonify({"response": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/qa", methods=["POST"])
def question_answer():
    global chat_history, session_data

    data = request.json
    user_question = data.get("user_question")

    if not session_data.get("chat_chain"):
        return (
            jsonify({"error": "Please link a YouTube video first"}),
            400,
        )

    chat_chain = session_data["chat_chain"]
    response, chat_history = chat(user_question, chat_chain, chat_history)
    return jsonify({"response": response["answer"]})


if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Run on a separate port for backend
