# OffGrid UI

OffGrid AI is a private, local, and secure AI assistant application built with Streamlit and the Ollama AI model. It allows you to have natural language conversations with an AI model running locally on your machine, ensuring your data stays private and offline.

## Introduction

OffGrid AI is designed to provide a user-friendly interface for interacting with the Ollama AI model, a powerful language model trained by Anthropic. The application allows you to have conversations with the AI assistant, send and receive images, and manage multiple chat sessions. The key feature of OffGrid AI is that it runs the AI model locally, ensuring your data never leaves your machine, providing maximum privacy and security.

## Features

- **Private and Secure**: OffGrid AI runs the AI model locally, ensuring your data never leaves your machine.
- **Natural Language Conversations**: Engage in natural language conversations with the AI assistant.
- **Image Support**: Send and receive images during your conversations.
- **Multiple Chat Sessions**: Manage multiple chat sessions and switch between them easily.
- **Customizable Model**: Choose from different Ollama AI models or use your own custom model.
- **Local Server**: Launch the Ollama server locally with a single click.

## Installation

To run OffGrid AI on your machine, you'll need to follow these steps:

1. **Install Python**: Make sure you have Python 3.7 or later installed on your system.

2. **Clone the Repository**: Clone the OffGrid AI repository to your local machine using the following command:

   ```
   git clone https://github.com/your-username/offgrid-ai.git
   ```

3. **Install Dependencies**: Navigate to the project directory and install the required Python packages using pip:

   ```
   cd offgrid-ai
   pip install -r requirements.txt
   ```

4. **Download Ollama Model**: Download the Ollama AI model from the official Anthropic repository. You can find the instructions and download links on the [Ollama GitHub page](https://github.com/anthropics/ollama).

5. **Launch Ollama Server**: After downloading the Ollama model, you'll need to launch the Ollama server. OffGrid AI provides a convenient button to launch the server locally. Alternatively, you can launch the server manually by running the following command:

   ```
   ollama serve
   ```

   Make sure the Ollama server is running before starting the OffGrid AI application.

## Usage

To start the OffGrid AI application, run the following command in the project directory:

```
streamlit run app.py
```

This will open the OffGrid AI interface in your default web browser. You can now start having conversations with the AI assistant.

### Key Features

- **Chat Interface**: The main interface allows you to send messages to the AI assistant and receive responses. You can also attach images to your messages.
- **Chat Sessions**: On the sidebar, you can view all your chat sessions, create new ones, rename existing sessions, and delete sessions you no longer need.
- **Model Selection**: In the sidebar, you can choose which Ollama AI model to use for your conversations.
- **Launch Local Server**: If the Ollama server is not running, you can launch it directly from the OffGrid AI interface using the "Launch Local Server" button.

## Contributing

Contributions to OffGrid AI are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/your-username/offgrid-ai).

When contributing, please follow the standard GitHub workflow:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with descriptive commit messages
4. Push your changes to your forked repository
5. Submit a pull request to the main repository

Please ensure that your code follows the existing coding style and conventions used in the project.

## License

OffGrid AI is released under the [MIT License](LICENSE).

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing Python library for building data apps.
- [Anthropic](https://www.anthropic.com/) for developing the Ollama AI model and making it open-source.
- [SQLAlchemy](https://www.sqlalchemy.org/) for the Python SQL toolkit and Object-Relational Mapper.
