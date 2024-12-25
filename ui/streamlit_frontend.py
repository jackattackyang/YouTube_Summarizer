import streamlit as st
import requests

# Flask backend URL
BACKEND_URL = "http://127.0.0.1:5001/"


def main():
    st.title("YouTube Summarizer")
    st.write("Enter a YouTube URL to get a summary by Llama 3B")

    # initialize submitted state
    if "submitted_url" not in st.session_state:
        st.session_state.submitted_url = False

    def submit_url():
        st.session_state.submitted_url = True

    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        on_change=submit_url,
        label_visibility="collapsed",
    )

    # Submit button
    if st.session_state.submitted_url:
        if youtube_url.strip():
            # Send POST request to Flask backend
            try:
                st.write("Running...")
                response = requests.post(BACKEND_URL, json={"youtube_url": youtube_url})
                result = response.json()

                if "response" in result:
                    st.success("Response from API:")
                    st.write(result["response"])
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a YouTube URL.")

    # Q&A Section
    st.divider()
    if "submitted_qa" not in st.session_state:
        st.session_state.submitted_qa = False
        st.session_state.conversation = []

    def submit_qa():
        st.session_state.submitted_qa = True

    user_question = st.text_input(
        "Ask a question about the video:",
        on_change=submit_qa,
        placeholder="Type your question here...",
    )
    if st.session_state.submitted_qa:

        if user_question.strip():
            st.session_state.conversation.append(
                {"role": "user", "content": user_question}
            )
            for msg in st.session_state.conversation:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
            try:
                # Send entire conversation (or just user_question) to the server
                response = requests.post(
                    f"{BACKEND_URL}/qa",
                    json={"user_question": user_question},
                )
                answer = response.json()["response"]
                # Add assistant message to conversation
                st.session_state.conversation.append(
                    {"role": "assistant", "content": answer}
                )
                st.markdown(f"**Assistant:** {answer}")
                st.success("Assistant answered above.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a question.")


if __name__ == "__main__":
    main()
