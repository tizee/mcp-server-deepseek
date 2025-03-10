# mcp-server-deepseek

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that provides access to DeepSeek-R1's reasoning capabilities, allowing non-reasoning models to generate better responses with enhanced thinking.

- read [R1+Sonnet set SOTA on aider’s polyglot benchmark](https://aider.chat/2025/01/24/r1-sonnet.html)

## Overview

This server acts as a bridge between LLM applications and DeepSeek's reasoning capabilities. It exposes DeepSeek-R1's reasoning content through an MCP tool, which can be used by any MCP-compatible client.

The server is particularly useful for:

- Enhancing responses from models without native reasoning capabilities
- Accessing DeepSeek-R1's thinking process for complex problem solving
- Adding structured reasoning to Claude or other LLMs that support MCP

## Features

- **Access to DeepSeek-R1**: Connects to DeepSeek's API to leverage their reasoning model
- **Structured Thinking**: Returns reasoning in a structured `<thinking>` format
- **Integration with MCP**: Fully compatible with the Model Context Protocol
- **Error Handling**: Robust error handling with detailed logging

## Installation

### Prerequisites

- Python 3.13 or higher
- An API key for DeepSeek

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-server-deepseek.git
   cd mcp-server-deepseek
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

4. Create a `.env` file with your DeepSeek API credentials:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your API key and model details:
   ```
   MCP_SERVER_DEEPSEEK_MODEL_NAME=deepseek-reasoner
   MCP_SERVER_DEEPSEEK_API_KEY=your_api_key_here
   MCP_SERVER_DEEPSEEK_API_BASE_URL=https://api.deepseek.com
   ```

## Usage

### Running the Server

You can run the server directly:

```bash
mcp-server-deepseek
```

Or use the development mode with the MCP Inspector:

```bash
make dev
```

### MCP Tool

The server exposes a single tool:

#### `think_with_deepseek_r1`

This tool sends a prompt to DeepSeek-R1 and returns its reasoning content.

**Arguments:**
- `prompt` (string): The full user prompt to process

**Returns:**
- String containing DeepSeek-R1's reasoning wrapped in `<thinking>` tags

### Example Usage

When used with Claude or another LLM that supports MCP, you can trigger the thinking process by calling the tool:

```
Please use the think_with_deepseek_r1 tool with the following prompt:
"How can I optimize a neural network for time series forecasting?"
```

## Development

### Testing

For development and testing, use the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv run mcp-server-deepseek
```

### Logging

Logs are stored in `~/.cache/mcp-server-deepseek/server.log`

The log level can be configured using the `LOG_LEVEL` environment variable (defaults to `DEBUG`).

## Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your DeepSeek API key is correctly set in the `.env` file
- **Timeout Errors**: Complex prompts may cause timeouts. Try simplifying your prompt
- **Missing Reasoning**: Some queries might not generate reasoning content. Try rephrasing

### Error Logs

Check the logs for detailed error messages:

```bash
cat ~/.cache/mcp-server-deepseek/server.log
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- Thanks to the DeepSeek team for their powerful reasoning model
- Built with the [Model Context Protocol](https://modelcontextprotocol.io) framework
