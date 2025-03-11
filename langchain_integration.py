# langchain_integration.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()

# Set up the LLM with Google's Generative AI
#os.environ["GOOGLE_API_KEY"] = ""  # Replace with your actual API key
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# Define a LangChain template for generating travel recommendations
template = """
You are a travel expert. Plan a trip to {destination} on {dates} with a budget of ${budget}.
Provide a detailed itinerary including:
1. Best time to visit
2. Transportation options
3. Accommodation recommendations
4. Must-see attractions
5. Local cuisine to try
6. Estimated costs for each category
"""

prompt = PromptTemplate(
    input_variables=["destination", "dates", "budget"],
    template=template,
)

# Create an LLM chain for generating travel recommendations
travel_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
)

def generate_travel_plan(destination, dates, budget):
    """Generate a travel plan using LangChain."""
    return travel_chain.run(destination=destination, dates=dates, budget=budget)