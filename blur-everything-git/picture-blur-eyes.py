from flask import Flask, request, send_file, jsonify
import cv2
import numpy as np
import os
import zipfile
import shutil
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

def extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    except Exception as e:
        logging.error(f"An error occurred while extracting the zip file: {str(e)}")
        raise

def load_eye_detector():
    try:
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        return eye_cascade
    except Exception as e:
        logging.error(f"Error loading eye detector model: {str(e)}")
        raise

def detect_and_blur_eyes(eye_cascade, image_path, output_path):
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        eyes = eye_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in eyes:
            eye = image[y:y+h, x:x+w]
            eye = cv2.GaussianBlur(eye, (99, 99), 30)
            image[y:y+h, x:x+w] = eye

        cv2.imwrite(output_path, image)
    except Exception as e:
        logging.error(f"An error occurred while detecting and blurring eyes: {str(e)}")
        raise

def zip_files(input_folder, output_zip):
    try:
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            for root, dirs, files in os.walk(input_folder):
                for file in files:
                    zipf.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file),
                                               os.path.join(input_folder, '..')))
    except Exception as e:
        logging.error(f"An error occurred while zipping files: {str(e)}")
        raise

@app.route('/blur-eyes-in-pictures', methods=['POST'])
def blur_eyes_in_pictures():
    try:
        zip_file = request.files.get('zip_file')
        if not zip_file:
            return jsonify({"error": "No zip file provided"}), 400

        # Ensure the downloads directory exists
        downloads_dir = 'downloads'
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        zip_path = os.path.join(downloads_dir, 'input_images.zip')
        extract_folder = os.path.join(downloads_dir, 'extracted_images')
        output_folder = os.path.join(downloads_dir, 'blurred_images')
        output_zip = os.path.join(downloads_dir, 'blurred_images.zip')

        # Save and extract the zip file
        zip_file.save(zip_path)
        extract_zip(zip_path, extract_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        eye_cascade = load_eye_detector()

        for file_name in os.listdir(extract_folder):
            if file_name.endswith(('jpg', 'jpeg', 'png')):
                image_path = os.path.join(extract_folder, file_name)
                name, ext = os.path.splitext(file_name)
                output_path = os.path.join(output_folder, f"{name}_blur{ext}")
                detect_and_blur_eyes(eye_cascade, image_path, output_path)

        zip_files(output_folder, output_zip)

        shutil.rmtree(extract_folder)
        shutil.rmtree(output_folder)
        os.remove(zip_path)

        return send_file(output_zip, as_attachment=True, download_name='blurred_images.zip')

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
