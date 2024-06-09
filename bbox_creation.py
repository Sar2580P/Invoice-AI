from pdf2image import convert_from_path
import os
from tqdm import tqdm


def pdf_to_png(pdf_path, output_folder, dpi=300):
    """
    Convert a single-page PDF to PNG.

    Args:
        pdf_path (str): Path to the input PDF file.
        output_folder (str): Folder where the output PNG file will be saved.
        dpi (int, optional): DPI (dots per inch) setting for the output image. Default is 300.
    """
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=dpi)
    
    # Check if the PDF has at least one page
    if not images:
        print(f"No pages found in the PDF: {pdf_path}")
        return
    
    # Use the first page (assuming the PDF has only one page)
    image = images[0]
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Define the output file path
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(output_folder, f"{base_name}.png")
    
    # Save the image as PNG
    image.save(output_path, 'PNG')
    print(f"Image saved to {output_path}")

#___________________________________________________________________________________________________________________________

import cv2
import json

def get_contours(img_file_name):
    # Load the image
    image = cv2.imread(f'output_images/{img_file_name}.png')

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to get a binary image
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize a list to store contour information
    contour_info = []

    # Iterate over contours
    for i, contour in tqdm(enumerate(contours), desc='Processing Contours'):
        # Calculate the bounding box coordinates
        x, y, w, h = cv2.boundingRect(contour)
        
        # Calculate the center point
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Append contour information to the list
        contour_info.append({
            'contour_index': i,
            'left_bottom': (x, y + h),  # Add height to y-coordinate to get bottom
            'top_right': (x + w, y),
            'center': (center_x, center_y),
            'bbox': (x, y, w, h)
        })
    basename = os.path.splitext(os.path.basename(img_file_name))[0]
    with open(f'bbox_data/original_contours/{basename}.json', 'w') as json_file:
        json.dump(contour_info, json_file, indent=4)

#___________________________________________________________________________________________________________________________
# Function to merge two bounding boxes
def merge_bboxes(bbox1, bbox2):
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2
    x = min(x1, x2)
    y = min(y1, y2)
    w = max(x1 + w1, x2 + w2) - x
    h = max(y1 + h1, y2 + h2) - y
    return (x, y, w, h)

#___________________________________________________________________________________________________________________________
def group_horizontal_contours(file_name):
    with open(f'bbox_data/original_contours/{file_name}.json', 'r') as json_file:
        contour_info = json.load(json_file)
    groups = {}
    group_count = 0

    # Assign groups to bounding boxes based on y-coordinate differences
    for i, contour in tqdm(enumerate(contour_info), desc='Grouping Contours to form words'):
        assigned = False
        for group in groups:
            for idx in groups[group]:
                other_contour = contour_info[idx]
                # Check y-coordinate difference
                if abs(contour['center'][1] - other_contour['center'][1]) < 30:
                    groups[group].append(i)
                    assigned = True
                    break
            if assigned:
                break
        if not assigned:
            group_count += 1
            groups[group_count] = [i]

    # Sort the values for each key based on the x-coordinate of the center of each bounding box
    for group in groups:
        groups[group].sort(key=lambda idx: contour_info[idx]['center'][0])

    # Save group information to a JSON file
    with open(f'bbox_data/grouped_contours/{file_name}.json', 'w') as json_file:
        json.dump(groups, json_file, indent=4)

    print("Group information saved to 'groups.json'.")

#___________________________________________________________________________________________________________________________  
def merge_contours(file_name):
    with open(f'bbox_data/original_contours/{file_name}.json', 'r') as json_file:
        contour_info = json.load(json_file)
    with open(f'bbox_data/grouped_contours/{file_name}.json', 'r') as json_file:
        groups = json.load(json_file)
    
    # Function to merge two bounding boxes
    def merge_bboxes(bbox1, bbox2):
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        x = min(x1, x2)
        y = min(y1, y2)
        w = max(x1 + w1, x2 + w2) - x
        h = max(y1 + h1, y2 + h2) - y
        return (x, y, w, h)
    
    # Padding size
    padding = 7
    
    # Initialize a list to store merged bounding boxes
    merged_bboxes = []

    # Merge bounding boxes for each group based on x-coordinate distance
    for group in tqdm(groups, desc = 'Merging and padding bbox'):
        indices = groups[group]
        if not indices:
            continue
        # Start with the first bounding box in the group
        current_bbox = contour_info[indices[0]]['bbox']
        for i in range(1, len(indices)):
            next_bbox = contour_info[indices[i]]['bbox']
            # Check the distance between the right x-coordinate of the current bbox and the left x-coordinate of the next bbox
            if next_bbox[0] - (current_bbox[0] + current_bbox[2]) < 40:
                # Merge the bounding boxes
                current_bbox = merge_bboxes(current_bbox, next_bbox)
            else:
                # Pad the current merged bbox before appending
                current_bbox = (current_bbox[0] - padding, current_bbox[1] - padding, current_bbox[2] + 2 * padding, current_bbox[3] + 2 * padding)
                # Append the current merged bbox and move to the next
                merged_bboxes.append(current_bbox)
                current_bbox = next_bbox
        # Pad the last merged bbox before appending
        current_bbox = (current_bbox[0] - padding, current_bbox[1] - padding, current_bbox[2] + 2 * padding, current_bbox[3] + 2 * padding)
        # Append the last bbox
        merged_bboxes.append(current_bbox)

    # Save merged bounding box information to a JSON file
    merged_bboxes_info = [{'bbox': bbox} for bbox in merged_bboxes]
    with open(f'bbox_data/merged_contours/{file_name}.json', 'w') as json_file:
        json.dump(merged_bboxes_info, json_file, indent=4)

    print("Merged bounding box information saved to 'merged_bboxes.json'.")

#___________________________________________________________________________________________________________________________
import cv2
import matplotlib.pyplot as plt

def plot_bboxes(file_name, save_path='images_with_bbox/'):
    """
    Plot bounding boxes on the image.

    Args:
        image_path (str): Path to the input image.
        bboxes (list of dict): List of bounding boxes. Each bounding box is a dictionary with 'bbox' key.
        save_path (str, optional): Path to save the image with bounding boxes. If None, the image will not be saved.
    """
    
    with open(f'bbox_data/merged_contours/{file_name}.json', 'r') as json_file:
        bboxes = json.load(json_file)
    # Load the image
    image_path = f'output_images/{file_name}.png'
    image = cv2.imread(image_path)
    
    # Check if the image was loaded successfully
    if image is None:
        print(f"Failed to load image at {image_path}")
        return
    
    # Draw bounding boxes on the image
    for bbox_info in tqdm(bboxes, desc='Drawing Bounding Boxes'):
        x, y, w, h = bbox_info['bbox']
        # Draw rectangle on the image
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # Convert image to RGB for displaying with matplotlib
    # image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # # Display the image with bounding boxes
    # plt.figure(figsize=(10, 10))
    # plt.imshow(image_rgb)
    # plt.axis('off')
    # plt.show()
    
    # Save the image with bounding boxes if save_path is provided
    if save_path:
        cv2.imwrite(f'{save_path}/{file_name}.png', image)
        print(f"Image with bounding boxes saved at {save_path}")
        
#___________________________________________________________________________________________________________________________
def create_clusters(details_content , bbox_coordinates):
    for i in range(len(details_content)):
        bbox_x_coord = bbox_coordinates[details_content[i][0]]['bbox'][0]
        bbox_y_coord = bbox_coordinates[details_content[i][0]]['bbox'][1]
        details_content[i].append(bbox_x_coord)
        details_content[i].append(bbox_y_coord)
    
    details_content.sort(key = lambda x : x[-2])

    # combine all the details with same x coordinate
    clusters = []
    cluster = []
    cluster.append(details_content[0])
    prev_bbox_x_coord = details_content[0][-2]
    for i in tqdm(range(1, len(details_content)) , desc='Doing Spatial Clustering of Bboxes'):
        if abs(details_content[i][-2] - prev_bbox_x_coord)<50:
            cluster.append(details_content[i])
        else:
            cluster.sort(key = lambda x : x[-1])
            clusters.append(cluster)
            cluster = [details_content[i]]
        prev_bbox_x_coord = details_content[i][-2]
    
    cluster.sort(key = lambda x : x[-1])
    clusters.append(cluster)
    return clusters

#___________________________________________________________________________________________________________________________