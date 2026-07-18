from langchain_groq import  ChatGroq
from dotenv import load_dotenv

from prompts import *
from state import *

load_dotenv()


llm = ChatGroq(model="llama-3.3-70b-versatile")




user_prompt   = "Create a simple calculator web application"



prompt = prompt(user_prompt)



response = llm.with_structured_output(Plan).invoke(prompt)

print(response.model_dump())


