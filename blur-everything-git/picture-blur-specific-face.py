from flask import Flask, request, send_file, jsonify
import cv2
import numpy as np
import os
import zipfile
import shutil
import logging
import face_recognition

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

def extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    except Exception as e:
        logging.error(f"An error occurred while extracting the zip file: {str(e)}")
        raise

def load_face_encodings(image_folder):
    try:
        encodings = []
        for file_name in os.listdir(image_folder):
            if file_name.endswith(('jpg', 'jpeg', 'png')):
                image_path = os.path.join(image_folder, file_name)
                image = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(image)
                if encoding:
                    encodings.append(encoding[0])
        return encodings
    except Exception as e:
        logging.error(f"An error occurred while loading face encodings: {str(e)}")
        raise

def detect_and_blur_specific_person(image_path, output_path, known_encodings):
    try:
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            if True in matches:
                face = image[top:bottom, left:right]
                face = cv2.GaussianBlur(face, (99, 99), 30)
                image[top:bottom, left:right] = face

        cv2.imwrite(output_path, image[:, :, ::-1])
    except Exception as e:
        logging.error(f"An error occurred while detecting and blurring the specific person: {str(e)}")
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

@app.route('/blur-specific-person-in-pictures', methods=['POST'])
def blur_specific_person_in_pictures():
    try:
        reference_zip_file = request.files.get('reference_zip_file')
        target_zip_file = request.files.get('target_zip_file')

        if not reference_zip_file or not target_zip_file:
            return jsonify({"error": "Both reference and target zip files are required"}), 400

        downloads_dir = 'downloads'
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        reference_zip_path = os.path.join(downloads_dir, 'reference_images.zip')
        target_zip_path = os.path.join(downloads_dir, 'target_images.zip')
        reference_folder = os.path.join(downloads_dir, 'reference_images')
        target_folder = os.path.join(downloads_dir, 'target_images')
        output_folder = os.path.join(downloads_dir, 'blurred_images')
        output_zip = os.path.join(downloads_dir, 'blurred_images.zip')

        reference_zip_file.save(reference_zip_path)
        target_zip_file.save(target_zip_path)
        extract_zip(reference_zip_path, reference_folder)
        extract_zip(target_zip_path, target_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        known_encodings = load_face_encodings(reference_folder)

        for file_name in os.listdir(target_folder):
            if file_name.endswith(('jpg', 'jpeg', 'png')):
                image_path = os.path.join(target_folder, file_name)
                name, ext = os.path.splitext(file_name)
                output_path = os.path.join(output_folder, f"{name}_blur{ext}")
                detect_and_blur_specific_person(image_path, output_path, known_encodings)

        zip_files(output_folder, output_zip)

        shutil.rmtree(reference_folder)
        shutil.rmtree(target_folder)
        shutil.rmtree(output_folder)
        os.remove(reference_zip_path)
        os.remove(target_zip_path)

        return send_file(output_zip, as_attachment=True, download_name='blurred_images.zip')

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
