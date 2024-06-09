from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt

# Function to preprocess the image
def preprocess_image_high_resolution(image):
    # Increase resolution
    high_res_image = image.resize((image.width * 3, image.height * 3), Image.Resampling.LANCZOS)
    # Apply Gaussian Blur to smooth edges
    blurred_image = high_res_image.filter(ImageFilter.GaussianBlur(radius=1))
    # Convert to grayscale
    grayscale_image = blurred_image.convert("L")
    # Increase contrast
    enhancer = ImageEnhance.Contrast(grayscale_image)
    enhanced_image = enhancer.enhance(3)
    # Apply binarization
    binary_image = enhanced_image.point(lambda x: 0 if x < 128 else 255, '1')
    # Apply sharpening filter
    sharpened_image = binary_image.filter(ImageFilter.SHARPEN)
    return sharpened_image

#___________________________________________________________________________________________________________________________

def resize_with_aspect_ratio(image, target_width):
    """
    Resize an image while preserving its aspect ratio.

    Args:
        image (PIL.Image.Image): Input image.
        target_width (int): Target width for resizing.

    Returns:
        PIL.Image.Image: Resized image.
    """
    # Get the original width and height
    original_width, original_height = image.size
    
    # Calculate the scaling factor based on the target width
    scaling_factor = target_width / original_width
    
    # Calculate the new dimensions with the preserved aspect ratio
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)
    
    # Resize the image
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return resized_image
#___________________________________________________________________________________________________________________________
def zoom_out(image, zoom_out_level=2):

    # Get the original image dimensions
    original_width, original_height = image.size
    # print(image.size)
    # Calculate new dimensions for zoomed-out image
    zoomed_out_width = original_width * zoom_out_level
    zoomed_out_height = original_height * zoom_out_level

    # Create a new image with white background for zooming out
    zoomed_out_image = Image.new(image.mode, (zoomed_out_width, zoomed_out_height), color='white')

    # Calculate the position to paste the original image centered
    paste_x = (zoomed_out_width - original_width) // 2
    paste_y = (zoomed_out_height - original_height) // 2

    # Paste the original image onto the zoomed-out image
    zoomed_out_image.paste(image, (paste_x, paste_y))

    # Resize back to the original dimensions
    resized_image = resize_with_aspect_ratio(zoomed_out_image, 300)

    # Save or display the resized image
    # resized_image.show()  # Display the image
    # resized_image.save('resized_image.png')  # Save the image
    # print(resized_image.size)
    return resized_image

# # Example usage
# zoom_out('output.png', zoom_out_level=5)
#___________________________________________________________________________________________________________________________
import pytesseract
import re 

def only_special_characters(text):
    # Define a regular expression pattern to match special characters
    pattern = re.compile(r'^[!@#$%^&*(),.?":{}|<>[\]\\;\'/`~\-_=+’]+$')
    
    # Check if the entire text matches the pattern
    if pattern.fullmatch(text):
        return True
    else:
        return False

#___________________________________________________________________________________________________________________________

# Function to extract text from a bounding box
def extract_text_from_bbox(image:Image, bbox , lang='eng'):
    x, y, w, h = bbox
    cropped_image = image.crop((x, y, x + w, y + h))
    text = pytesseract.image_to_string(cropped_image, lang=lang).strip()
    if text == '' or only_special_characters(text):
        cropped_image = preprocess_image_high_resolution(cropped_image)
        text = pytesseract.image_to_string(cropped_image, lang=lang).strip()

    if text=='' or only_special_characters(text):
        cropped_image = zoom_out(cropped_image, zoom_out_level=3)
        text = pytesseract.image_to_string(cropped_image, lang=lang).strip()
        if text=='' or only_special_characters(text):
            custom_config = r'--oem 3 --psm 6 outputbase digits'
            cropped_image = zoom_out(cropped_image, zoom_out_level=3)
            text = pytesseract.image_to_string(cropped_image, config=custom_config).strip()
            if text=='':
                plt.figure(figsize=(10, 10))
                plt.imshow(cropped_image)
                plt.axis('off')
                plt.show()
    return text.strip()

#___________________________________________________________________________________________________________________________