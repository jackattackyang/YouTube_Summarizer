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
- Heroku account for deployment (if deploying with Heroku)

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

## Deployment

### Backend Deployment (Heroku)

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) and login:
```bash
heroku login
```

2. Create a new Heroku app:
```bash
heroku create your-app-name
```

3. Set the environment variables in Heroku:
```bash
heroku config:set YOUTUBE_API_KEY=your_youtube_api_key
heroku config:set REPLICATE_API_TOKEN=your_replicate_api_token
```

4. Deploy to Heroku:
```bash
git push heroku main
```

The backend API will be available at `https://your-app-name.herokuapp.com`

### Frontend Deployment (Streamlit Cloud)

1. Push your code to a GitHub repository

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)

3. Click "New app" and select your repository

4. Set the following:
   - Main file path: `ui/streamlit_qa.py`
   - Python version: 3.10
   - Add the following secrets in the Streamlit Cloud dashboard:
     - BACKEND_URL: Your Heroku backend URL (e.g., https://your-app-name.herokuapp.com)

The frontend will be available at your Streamlit Cloud URL.

## Local Development

### Running Locally

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

### Local Docker Deployment
The project includes Docker support for deploying the backend service locally:

```bash
docker-compose up
```
This will start the FastAPI backend service at http://localhost:5001

## Project Structure

```
youtube_summarizer/
├── api/
│   ├── app.py              # FastAPI backend
│   └── replicate_api.py    # LLaMA API
├── data/
│   ├── get_youtube_data.py # YouTube data fetching
│   └── preprocess.py       # Data preprocessing
├── ui/
│   └── streamlit_qa.py     # Streamlit frontend
├── src/
│   ├── vectorstore.py      # FAISS vector store for RAG
│   └── chat.py             # Chat functionality
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