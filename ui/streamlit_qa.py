import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5001"


def main():
    st.title("YouTube Summarizer")

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
        if prompt.startswith("http"):
            # Summarize the video if it's a YouTube URL
            with st.chat_message("assistant"):
                try:
                    response = requests.post(BACKEND_URL, json={"youtube_url": prompt})
                    result = response.json()

                    if "response" in result:
                        summary = result["response"]
                        st.write(summary)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": summary}
                        )
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.write(f"Error: {e}")
        else:
            # Otherwise, treat it as a Q&A
            with st.chat_message("assistant"):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/qa", json={"user_question": prompt}
                    )
                    answer = response.json().get("response", "No answer.")
                    st.write(answer)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                except Exception as e:
                    st.write(f"Error: {e}")


if __name__ == "__main__":
    main()
