import os, json
from text_extraction import extract_text_from_bbox, Image
from ask_llm import get_total_col_of_table, get_table_data, get_granular_invoice_details
from bbox_creation import pdf_to_png, get_contours, group_horizontal_contours, merge_contours, plot_bboxes, create_clusters
from tqdm import tqdm
import streamlit as st

async def process_invoice_data(file_name, lang = 'eng' , plot_bbox = True):
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    if file_name.endswith('.pdf'):
        pdf_path = f'test_data/{file_name}'
        output_folder = 'output_images'
        pdf_to_png(pdf_path, output_folder)

    get_contours(base_name)
    group_horizontal_contours(base_name)
    merge_contours(base_name)
    if plot_bbox:
        plot_bboxes(base_name)
        
    # Reading Text from Image
    # Extract text from each bounding box and store in a list
    extracted_texts = []

    with open(f'bbox_data/merged_contours/{base_name}.json' , 'r')  as json_file:
        bbox_coordinates = json.load(json_file)

    image = Image.open(f'output_images/{base_name}.png')

    for i ,bbox in tqdm(enumerate(bbox_coordinates), desc='Extracting Text from Boxes'):
        bbox = bbox["bbox"]
        text = extract_text_from_bbox(image, bbox, lang=lang)
        extracted_texts.append([i, text])

    # # Print the extracted texts
    # for text in extracted_texts:
    #     print(text)
    
    table_content , details_content = get_total_col_of_table(extracted_texts)
    
    product_details = get_table_data(table_content)
    # print(product_details)
    
    clusters = create_clusters(details_content, bbox_coordinates)    

    li = await get_granular_invoice_details(clusters)

    with open(f'extracted_invoices/{base_name}.json', 'w') as json_file:
        dict_ = {
        'invoice_details' : li , 
        'product_details' : product_details
        }
        # print(dict_)
        json.dump(dict_, json_file, indent=4)
        
    return dict_

# process_invoice_data('sample 3.pdf', lang = 'deu')
async def main():
    st.set_page_config(page_title="Invoice Processor", page_icon="📄", layout="wide")

    st.title("📄 Invoice Processing Application")
    st.markdown("Welcome to the Invoice Processing Application. Please upload your invoice and specify the language of the file to proceed.")

    # Input section
    file_name = st.text_input("Enter file name:")
    lang = st.text_input("Enter language of file:")
    
    if st.button("Process"):
        with st.spinner("Processing..."):
            await process_invoice_data(file_name, lang)
            base_name = os.path.splitext(os.path.basename(file_name))[0]
            with open(f'extracted_invoices/{base_name}.json', 'r') as json_file:
                data = json.load(json_file)
            image = Image.open(f'images_with_bbox/{base_name}.png')

        # Layout: Create two columns for image and result
        col1, col2 = st.columns(2)

        with col1:
            st.image(image, caption='Text Localization', use_column_width=True)

        with col2:
            st.header("Result")
            st.json(data)
    else:
        st.error("Please provide valid inputs and click the process button.")

    # Adding some custom styling
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #4CAF50; /* Green */
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            transition-duration: 0.4s;
        }
        .stButton>button:hover {
            background-color: white;
            color: black;
            border: 2px solid #4CAF50;
        }
        </style>
        """, unsafe_allow_html=True)

import asyncio
if __name__ == "__main__":
    asyncio.run(main())