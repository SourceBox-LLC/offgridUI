# AI Chatbot Assistant

A beautiful and feature-rich AI chatbot assistant built with Streamlit and powered by OpenAI's API.

## Features

- 🎯 Modern and responsive UI
- 🔑 Secure API key management
- 💬 Full chat history with user and AI messages
- 🖼️ Image upload and display capability
- 🔄 Error handling and retries
- 🧹 Chat history clearing

## Setup Instructions

### Prerequisites

- Python 3.7 or newer
- OpenAI API key

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

4. The application will open in your default web browser. If it doesn't, navigate to the URL shown in the terminal (typically `http://localhost:8501`).

### Using the Chatbot

1. Enter your OpenAI API key in the sidebar
2. Type your message in the chat input field
3. Optionally upload an image to include with your message
4. View the AI's response
5. Use the "Clear Chat History" button in the sidebar to start a fresh conversation

## Configuration

The chatbot uses OpenAI's `o3-mini` model by default, with a medium reasoning effort. You can modify these settings in the `llm.py` file.

## License

[MIT License](LICENSE)

## Acknowledgements

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI](https://openai.com/)
