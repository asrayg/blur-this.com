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

def load_face_detector():
    try:
        net = cv2.dnn.readNetFromCaffe('custom_deploy.prototxt', 'face-detecting-model.caffemodel')
        return net
    except Exception as e:
        logging.error(f"Error loading face detector model: {str(e)}")
        raise

def detect_and_blur_faces(net, image_path, output_path):
    try:
        image = cv2.imread(image_path)
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                face = image[startY:endY, startX:endX]
                face = cv2.GaussianBlur(face, (99, 99), 30)
                image[startY:endY, startX:endX] = face

        cv2.imwrite(output_path, image)
    except Exception as e:
        logging.error(f"An error occurred while detecting and blurring faces: {str(e)}")
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

@app.route('/blur-faces-in-pictures', methods=['POST'])
def blur_faces_in_pictures():
    try:
        zip_file = request.files.get('zip_file')
        if not zip_file:
            return jsonify({"error": "No zip file provided"}), 400

        downloads_dir = 'downloads'
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        zip_path = os.path.join(downloads_dir, 'input_images.zip')
        extract_folder = os.path.join(downloads_dir, 'extracted_images')
        output_folder = os.path.join(downloads_dir, 'blurred_images')
        output_zip = os.path.join(downloads_dir, 'blurred_images.zip')

        zip_file.save(zip_path)
        extract_zip(zip_path, extract_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        net = load_face_detector()

        for file_name in os.listdir(extract_folder):
            if file_name.endswith(('jpg', 'jpeg', 'png')):
                image_path = os.path.join(extract_folder, file_name)
                name, ext = os.path.splitext(file_name)
                output_path = os.path.join(output_folder, f"{name}_blur{ext}")
                detect_and_blur_faces(net, image_path, output_path)

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
