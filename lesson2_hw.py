# from langchain_openai import ChatOpenAI
# import os 
# from secret_key import openai_key
# os.environ["OPENAI_API_KEY"]=openai_key 
# from langchain_core.prompts import ChatPromptTemplate
# model = ChatOpenAI(temperature=2)
# prompt = ChatPromptTemplate.from_messages(["human","What is the capital of {country}?"])
# final_prompt= prompt.format_messages(country="Israel")
# print(model.invoke(final_prompt).content) 

#h.w lesson2
from secret_key import openai_key
import os   
os.environ["OPENAI_API_KEY"] = openai_key
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate


def getnerate_code_test_from_prompt(prompt):
 model = ChatOpenAI(temperature=1)
 code_prompt_template = PromptTemplate(
      input_variables=["prompt"],
         template="Generate a python code for the following task: {prompt}")
 code_prompt=code_prompt_template.format(prompt=prompt)
 test_prompt_template = PromptTemplate(
      input_variables=["code"],  
         template="Generate a test in python the following code: {code}")   
 code_chain = code_prompt_template |  model | StrOutputParser()
 test_chain =test_prompt_template | model | StrOutputParser()
 full_chain = code_chain | {"code": code_chain, "test": test_chain}
 response = full_chain.invoke({"prompt": prompt})
 return response

response =getnerate_code_test_from_prompt("Create a function that returns the sum of two numbers") 
print("Generated Code:\n", response['code'])
print("Generated Test:\n", response['test'])
