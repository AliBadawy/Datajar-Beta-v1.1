# DataJar Chat

A ChatGPT-like interface built with Streamlit and OpenAI's API.

## Features

- Clean, modern UI inspired by ChatGPT
- Real-time, word-by-word response streaming
- Conversation memory across chat sessions
- Direct integration with OpenAI API

## Getting Started

### Prerequisites

- Python 3.7+
- An OpenAI API key

### Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/datajar-chat.git
cd datajar-chat
```

2. Install the required packages:
```bash
pip install streamlit openai
```

3. Create a `secret.py` file in the project root with your OpenAI API key:
```python
# secret.py
OPENAI_API_KEY = "your-openai-api-key-here"
```

### Running the App

Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

The app will be available at http://localhost:8501

## Project Structure

- `streamlit_app.py`: Main Streamlit application
- `openai_handler.py`: OpenAI API integration
- `style.css`: Custom styling for ChatGPT-like interface
- `secret.py`: Contains your OpenAI API key (not included in repository)

## License

MIT

## Acknowledgments

- [OpenAI](https://openai.com/) for the powerful AI models
- [Streamlit](https://streamlit.io/) for the easy-to-use app framework
