import fitz
import os

def extract_images(pdf_path, output_folder="extracted_images"):

    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)

    images = []

    for page_index in range(len(doc)):

        page = doc[page_index]
        image_list = page.get_images()

        for img in image_list:

            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            img_name = f"img_{page_index}_{xref}.png"
            img_path = os.path.join(output_folder, img_name)

            pix.save(img_path)

            images.append(img_path)

    return images