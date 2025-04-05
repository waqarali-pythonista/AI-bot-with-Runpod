# RunPod Chat Interface

A Streamlit-based chat interface for RunPod's AI models, featuring real-time streaming responses and detailed statistics tracking.

## Features

- 🤖 Real-time streaming responses from RunPod AI models
- 📊 Live statistics tracking (tokens, execution time)
- 💬 Chat history persistence
- 🔄 Automatic token counting
- 🎯 Support for custom system prompts
- 🚀 Easy-to-use interface

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/runpod-chat-interface.git
cd runpod-chat-interface
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your RunPod credentials:
```env
RUNPOD_TOKEN=your_runpod_token_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
MODEL_NAME=meta-llama/Llama-3.1-8B
```

Note: Your RunPod token should start with either `rp_` (for API tokens) or `rpa_` (for client tokens).

## Running the Application

Start the Streamlit app:
```bash
streamlit run app1.py
```

The interface will be available at `http://localhost:8501`

## Environment Variables

- `RUNPOD_TOKEN`: Your RunPod API token (starts with `rp_` or `rpa_`)
- `RUNPOD_ENDPOINT_ID`: Your RunPod endpoint ID
- `MODEL_NAME`: The name of the model to use (e.g., `meta-llama/Llama-3.1-8B`)

## Usage

1. Enter your question in the chat input
2. Watch as the AI streams its response in real-time
3. View statistics in the sidebar:
   - Execution time
   - Token usage (prompt, completion, total)
   - Model information
   - Debug information

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security Notes

- Never commit your `.env` file or expose your RunPod credentials
- Keep your API tokens secure and rotate them regularly
- Monitor your API usage through the RunPod dashboard

## License

This project is licensed under the MIT License - see the LICENSE file for details. 