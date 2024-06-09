from llama_index.core import PromptTemplate
from templates import FIND_TABLE_COLS, PRODUCT_DETAILS, INVOICE_DETAILS
from llm_utils import use_llm
import re , ast

def contains_numbers(text):
    # Regular expression to match any digit
    pattern = r'\d+'
    
    # Search for the pattern in the text
    if re.search(pattern, text):
        return True
    else:
        return False

#___________________________________________________________________________________________________________________________
def get_total_col_of_table(extracted_texts:list):
    cols = []
    for x in extracted_texts:
        value = x[1]
        
        if len(value.split())<3 and not contains_numbers(value):
            cols.append(value)
    
    extracted = '\n-'.join(cols)
    prompt = PromptTemplate(FIND_TABLE_COLS).format(extracted_data = extracted) 
    response , _ = use_llm(prompt)
    
    print(response)
    split_index = len(extracted_texts)-1
    while split_index>=0:
        val = extracted_texts[split_index][1]
        if val.strip() == response.strip():
            break
        split_index-=1
        
    table_content , details_content = extracted_texts[:split_index+1] , extracted_texts[split_index+1:]
    return table_content , details_content

#___________________________________________________________________________________________________________________________
def get_table_data(table_content):
    extracted_data = ''
    for i in range(len(table_content)):
        extracted_data+=f"- {table_content[i][1]}\n"
    prompt = PromptTemplate(PRODUCT_DETAILS).format(extracted_data = extracted_data)
    response, _ = use_llm(prompt)
    # print(response)
    return ast.literal_eval(response)
    
#___________________________________________________________________________________________________________________________


import asyncio
import ast

async def get_granular_invoice_details(clusters):
    async def process_cluster(cluster):
        cluster_text = ''
        for x in cluster:
            cluster_text += f"- {x[1]}\n"
        prompt = PromptTemplate(INVOICE_DETAILS).format(extracted_data=cluster_text)
        response, _ =  use_llm(prompt)
        try:
            response = ast.literal_eval(response)
            return response
        except:
            print(f'Response of llm : {response} for cluster : {cluster_text}', '-' * 100)
            return None

    tasks = [process_cluster(cluster) for cluster in clusters]
    results = await asyncio.gather(*tasks)
    return [result for result in results if result is not None]
