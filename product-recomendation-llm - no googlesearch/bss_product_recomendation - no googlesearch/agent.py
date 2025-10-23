from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from dotenv import load_dotenv
load_dotenv()

from . import prompt

product_recomendator = LlmAgent(
    name="bank_sampoerna_product_recomendation",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about Bank Sampoerna's products."
    ),
    instruction=prompt.PROMPT,
    tools=[google_search]
)

root_agent = product_recomendator
