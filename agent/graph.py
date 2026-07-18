from langchain_groq import  ChatGroq
from dotenv import load_dotenv

load_dotenv()


llm = ChatGroq(model="openai/gpt-oss-120b")


response = llm.invoke("who invented yoga")

print(response.content)