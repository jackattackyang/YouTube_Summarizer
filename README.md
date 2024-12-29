# YouTube Video Summarizer

An AI-powered application that summarizes YouTube videos and provides an interactive Q&A interface using the video's content. The project uses LLaMA 3 for generating summaries and answering questions, with a FastAPI backend and Streamlit frontend.

## Features

- **Video Summarization**: Generate concise summaries of YouTube videos
- **Interactive Q&A**: Ask questions about the video content
- **Session Management**: Maintains conversation history for contextual responses
- **Modern UI**: Clean and intuitive Streamlit interface

## Architecture

### Backend (FastAPI)
- Fetches YouTube video metadata and transcripts
- Processes and chunks video content
- Integrates with LLaMA 3 via Replicate API
- Implements RAG (Retrieval Augmented Generation) for accurate responses
- Manages user sessions and conversation history

### Frontend (Streamlit)
- Simple and intuitive user interface
- Real-time interaction with the backend
- Displays video summaries and Q&A responses
- Maintains chat history

## Prerequisites

- Python 3.10+
- YouTube Data API key
- Replicate API token

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd youtube_summarizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
YOUTUBE_API_KEY=your_youtube_api_key
REPLICATE_API_TOKEN=your_replicate_api_token
```

## Running Locally

1. Start the FastAPI backend:
```bash
python api/app.py
```
The backend will be available at `http://localhost:5001`

2. In a new terminal, start the Streamlit frontend:
```bash
streamlit run ui/streamlit_qa.py
```
The UI will be available at `http://localhost:8501`

## Docker Deployment

The project includes Docker support for easy deployment:

```bash
docker-compose up
```

This will start both the backend and frontend services.

## Project Structure

```
youtube_summarizer/
├── api/
│   ├── app.py              # FastAPI backend
│   └── replicate_api.py    # LLaMA integration
├── data/
│   ├── get_youtube_data.py # YouTube data fetching
│   └── preprocess.py       # Data preprocessing
├── ui/
│   └── streamlit_qa.py     # Streamlit frontend
├── src/
│   ├── vectorstore.py      # Vector storage for RAG
│   └── chat.py            # Chat functionality
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

## Environment Variables

- `YOUTUBE_API_KEY`: Required for fetching video metadata
- `REPLICATE_API_TOKEN`: Required for LLaMA model access
- `PORT`: Optional, defaults to 5001 for the backend server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]