import os
import streamlit as st
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5001")


def initialize_session():
    """Initialize a new session and store the session_id in session_state."""
    if "session_id" not in st.session_state:
        try:
            response = requests.post(f"{BACKEND_URL}/create_session")
            result = response.json()
            st.session_state.session_id = result.get("session_id")
        except Exception as e:
            st.error(f"Failed to initialize session: {e}")
            st.session_state.session_id = None


def main():
    st.title("YouTube Summarizer")

    initialize_session()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! Link a YouTube URL to get started!",
            }
        ]

    # Display existing messages in a chat UI
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    # Chat input box at the bottom
    if prompt := st.chat_input("Ask about the video or provide a YouTube URL"):
        # Add the user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display the user message immediately
        with st.chat_message("user"):
            st.write(prompt)

        # Here you decide how to handle the request
        # For example, detect if it’s a URL or a question:
        if "youtube.com" in prompt:
            # Summarize the video if it's a YouTube URL
            with st.chat_message("assistant"):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/summarize",
                        json={
                            "youtube_url": prompt,
                            "session_id": st.session_state.session_id,
                        },
                    )
                    result = response.json()
                    if response.status_code == 200:
                        if "response" in result:
                            summary = result["response"]
                            st.write(summary)
                            st.session_state.messages.append(
                                {"role": "assistant", "content": summary}
                            )
                    else:
                        st.error(f"Error: {result['detail']}")
                except Exception as e:
                    st.write(f"Error: {e}")
        else:
            # Otherwise, treat it as a Q&A
            with st.chat_message("assistant"):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/qa",
                        json={
                            "user_question": prompt,
                            "session_id": st.session_state.session_id,
                        },
                    )
                    result = response.json()
                    if response.status_code == 200:
                        answer = response.json().get("response")
                        st.write(answer)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )
                    else:
                        st.error(f"Error: {result['detail']}")
                except Exception as e:
                    st.write(f"Error: {e}")


if __name__ == "__main__":
    main()
