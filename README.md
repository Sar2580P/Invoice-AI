# Invoice-AI

## **Problem Statement :** 
- Provided with pdf format invoices in English and German, located at [test data](test_data).
- Extract Text from invoices as .txt files for down-stream LLM applications.

For whole-some view of code with interactive shells, pls view [py notebook](explore.ipynb) 
## **Algorithmic Solution :** 

### [**Step-1 :**](bbox_creation.py) 
- converted pdf to png.
- Extract contours using **open-cv** to create bounding boxes around letters. The bounding boxes can be of varying sizes depending on font-size and case of letter.
- Then grouped and merged the contours/ bounding boxes to cover the entire word with single bounding box.
- While merging, padding was done to improve performance of OCR in extracting text from image.

 ![Image after step-1](images_with_bbox/sample%204.png)

### **Step-2 :**
- Now cropped for each bounding box and [extracted text using ocr](text_extraction.py#L96)
- Used 3 models from Tesseract-OCR, namely : 
    - deu (for German) 
    - eng (for English)
    - digits (difficulty in reading digits by other 2 models)
- Applied various image enhancement techniques like [increasing img resolution](text_extraction.py#L5)
- Maintained the [aspect ratio](text_extraction.py#L23) of cropped images, else difficult for OCR to recognise text.
- For very large and bold font size text, OCR could not read. So [zoomed them out](text_extraction.py#L49)... which increased the OCR readability.
- Texts are extracted from right->left and bottom->top.


### **Step-3 :**
- Recognised that amount for price and quantity is always the last column in all invoices or billings.
- As per text arrangement : 
    - all text above amount for price and quantity contains the entire table.
    - all text below amount for price and quantity contains track realted info like date, customer-info, seller-info.
- Used LLM [(Gemini)](llm_utils.py#L8) for finding word similar in meaning to amount for price and quantity, in given text data
- Then used LLM to [prompt](templates.py#L17) it to create list of products mentioned in table.
- Then [clustered the bounding boxes](bbox_creation.py#L225) on text above table on basis of spatial clustering. 
- Then passed these clusters seperately to LLM through [prompt](templates.py#L37) asking it to return a valid list of dictionaries with appropriate key-value.

### **[Final Output](extracted_invoices/sample%204.json)**


# Environment Setup 
- create virtual env.
- [pip install -r requirements.txt](requirements.txt)
- The [process_invoice_data function](main.py#L8) handling every thing end-to-end in main.py
- Stream_lit demo run : [st run main.py](main.py#L59)
- Set up API key in .env file to use Gemini LLM