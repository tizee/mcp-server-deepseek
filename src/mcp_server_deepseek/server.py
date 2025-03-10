import os
import logging
from dotenv import load_dotenv

import anyio
from openai import AsyncOpenAI
from mcp.server.fastmcp import Context, FastMCP

load_dotenv()

DEFAULT_MODEL_NAME = os.environ.get("MCP_SERVER_DEEPSEEK_MODEL_NAME", "deepseek-reasoner")
DEFAULT_BASE_URL = os.environ.get("MCP_SERVER_DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")

API_KEY = os.environ.get("MCP_SERVER_DEEPSEEK_API_KEY", "")

DEFAULT_LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
log_level = getattr(logging, DEFAULT_LOG_LEVEL, logging.INFO)
CACHE_DIR = os.path.expanduser("~/.cache/mcp-server-deepseek")
# Create the cache directory if it doesn't exist
os.makedirs(CACHE_DIR, exist_ok=True)
log_file = os.path.join(CACHE_DIR, "server.log")

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode="w"),
        logging.StreamHandler()
    ]
)

# --- deepseek code ---
class DeepSeek:
    def __init__(self, model_name: str, base_url: str, key: str):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = key
        # Increase the OpenAI client timeout and retries
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=3600,
            max_retries=5
        )

    async def get_reasoning_content(self, prompt: str, context: Context = None) -> str:
        """Get reasoning content with improved error handling and progress reporting"""
        reasoning_content = ""
        try:
            # Report progress to client if context is available
            if context:
                await context.info("Starting DeepSeek API call...")

            # Create a timeout for the API call
            with anyio.move_on_after(3600):
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    max_tokens=1,
                    messages=[{"role": "user", "content": prompt}],
                    stream=False
                )

                if hasattr(response.choices[0].message, 'reasoning_content') and response.choices[0].message.reasoning_content:
                    logging.debug(f"{response.choices[0].message.reasoning_content}")
                    reasoning_content = response.choices[0].message.reasoning_content

                if context:
                    await context.info("DeepSeek API call completed")

            if not reasoning_content:
                return "No reasoning content available or request timed out."

            return reasoning_content
        except Exception as e:
            error_message = f"Error getting reasoning content: {str(e)}"
            logging.error(error_message)
            return error_message

# --- Server code ---
mcp = FastMCP("mcp-server-deepseek",
              log_level=DEFAULT_LOG_LEVEL)

@mcp.prompt()
def ask_deepseek(prompt:str)-> str:
    return f"""
    Ask deepseek-r1 with user's prompt:
    {prompt}
    """

@mcp.tool()
async def think_with_deepseek_r1(prompt: str, context: Context) -> str:
    """
    Ask deepseek-R1 for user's prompt

    Arg:
        prompt: user's full prompt (full text)
    Return:
        Enhanced thinking
    """
    ds = DeepSeek(DEFAULT_MODEL_NAME,
                  DEFAULT_BASE_URL, API_KEY)

    try:
        # Set a timeout for the entire operation
        with anyio.fail_after(3600):  # Slightly less than the MCP protocol timeout
            reasoning_content = await ds.get_reasoning_content(prompt, context)

            # Return the result
            return f"""
            <thinking>
            {reasoning_content}
            </thinking>
            """
    except TimeoutError:
        return """
        <thinking>
        The reasoning process timed out. Please try again with a simpler prompt.
        </thinking>
        """
    except Exception as e:
        logging.exception("Error in think_with_deepseek_r1")
        return f"""
        <thinking>
        Error while processing: {str(e)}
        </thinking>
        """

def main():
    mcp.run()

test_prompt="""
Create a single HTML file containing CSS and JavaScript to generate an animated weather card. The card should visually represent the following weather conditions with distinct animations: Wind: (e.g., moving clouds, swaying trees, or wind lines) Rain: (e.g., falling raindrops, puddles forming) Sun: (e.g., shining rays, bright background) Snow: (e.g., falling snowflakes, snow accumulating) Show all the weather card side by side The card should have a dark background. Provide all the HTML, CSS, and JavaScript code within this single file. The JavaScript should include a way to switch between the different weather conditions (e.g., a function or a set of buttons) to demonstrate the animations for each.
"""
async def test():
    ds = DeepSeek(DEFAULT_MODEL_NAME,
                  DEFAULT_BASE_URL, API_KEY)
    print(f"{DEFAULT_BASE_URL}")
    print(f"{DEFAULT_MODEL_NAME}")
    reasoning_content = await ds.get_reasoning_content(test_prompt)
    print(f"reasoning: {reasoning_content}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(test())
