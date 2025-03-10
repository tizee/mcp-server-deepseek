import os
import logging
from dotenv import load_dotenv

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
    def __init__(self,model_name: str,base_url: str, key: str):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = key
        self.client = AsyncOpenAI(api_key=self.api_key,
            base_url=self.base_url,
            timeout=3600,
           max_retries=3)

    async def get_reasoning_content(self,prompt: str) -> str:
        reasoning_content = ""
        stream= await self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=1,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        async for chunk in stream:
            if hasattr(chunk.choices[0].delta,'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                logging.debug(f"{chunk.choices[0].delta.reasoning_content}")
                reasoning_content += chunk.choices[0].delta.reasoning_content
        return reasoning_content

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
async def think_with_deepseek_r1(prompt: str, context: Context)-> str:
    """
    Ask deepseek-R1 for user's prompt

    Arg:
        prompt: user's full prompt (full text)
    Return:
        Enhanced thinking
    """
    ds = DeepSeek(DEFAULT_MODEL_NAME,
                  DEFAULT_BASE_URL, API_KEY)
    import anyio
    reasoning_content = ""
    with anyio.CancelScope(shield=True):
        reasoning_content = await ds.get_reasoning_content(prompt)
    return f"""
    <thinking>
    {reasoning_content}
    </thinking>
    """

def main():
    mcp.run()

test_prompt="""
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
