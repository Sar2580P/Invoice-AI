FIND_TABLE_COLS = '''
You are provided with the list of word/sentences seperated... They are extracted from invoice or other similar documents.


List of words/sentences:
{extracted_data}


INSTRUCTIONS : 
You need to return the word whose name is similar to amount for given quantity and price.

ANSWER : 
'''

#=========================================================================================================

PRODUCT_DETAILS = '''
You have been provided with data extracted from invoice tables. 

EXTRACTED DATA :
{extracted_data}

---------------------------------------------------
INSTRUCTIONS : 
- Return list of dictionaries for each product in the table
- Each dictionaries with keys as (description/product_name) , (quantity) , (unit_price) , (amount_for_quantity) and corresponding values as value of dict...
- Maintain the currency signs if present

- The bill/ total amount should also be included in the list along with taxes if present.
    For example :     [{{"Total" : "value"}} , {{"Taxes" : "value"}}]

ANSWER : 
'''

#=========================================================================================================

INVOICE_DETAILS = '''
You are given the data related to invoice... It could be related to seller, buyer, invoice number, date etc.

EXTRACTED DATA :
{extracted_data}

------------------------------------------------------
INSTRUCTIONS :
- Return a dictionary list of dictionaries 
- For each dictionary in the list, (keys and values) should be extracted from above extracted data.
- If extracted data has no information regarding key... Use logical assumptions to get the key for the data.
        # For example : "02.02.2022" can be assumed as date
        # Don't create keys for which value is not present in the extracted data.
        
- Return a dictionary with a key describing the list content in short and value as the list of dictionaries.
- Don't put the tag ---> ```python , while returning the answer.
ANSWER :
'''