from flask import Flask, request, send_file, jsonify
import cv2
import numpy as np
import os
import zipfile
import shutil
import logging
import face_recognition
import fitz
import spacy
from pytube import YouTube
import requests
from urllib.error import HTTPError

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
nlp = spacy.load("en_core_web_sm")

# Utility functions
def extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    except Exception as e:
        logging.error(f"An error occurred while extracting the zip file: {str(e)}")
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

# Eye detection and blurring in pictures
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

@app.route('/blur-eyes-in-pictures', methods=['POST'])
def blur_eyes_in_pictures():
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

# Face detection and blurring in pictures
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

# Specific person detection and blurring in pictures
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

# PDF text redaction
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += page.get_text()
    return text

def redact_text_in_pdf(pdf_path, output_path, redaction_list):
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            for redaction in redaction_list:
                text_instances = page.search_for(redaction)
                for inst in text_instances:
                    page.add_redact_annot(inst, text=" ", fill=(0, 0, 0))
            page.apply_redactions()
        doc.save(output_path)
    except Exception as e:
        raise RuntimeError(f"An error occurred while redacting the PDF: {str(e)}")

def identify_redaction_targets(text, instruction):
    doc = nlp(text)
    redaction_targets = []

    if "project" in instruction.lower():
        for ent in doc.ents:
            if ent.label_ in ["ORG", "WORK_OF_ART", "PRODUCT", "EVENT"]:
                redaction_targets.append(ent.text)

    if "person" in instruction.lower():
        for ent in doc.ents:
            if ent.label_ in ["PERSON"]:
                redaction_targets.append(ent.text)

    if "everything" in instruction.lower():
        redaction_targets.extend([ent.text for ent in doc.ents])

    return list(set(redaction_targets))

@app.route('/redact-pdf', methods=['POST'])
def redact_pdf():
    try:
        pdf_file = request.files.get('pdf_file')
        instruction = request.form.get('instruction')

        if not pdf_file or not instruction:
            return jsonify({"error": "PDF file and instruction are required"}), 400

        uploads_dir = 'uploads'
        downloads_dir = 'downloads'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        pdf_path = os.path.join(uploads_dir, pdf_file.filename)
        redacted_pdf_path = os.path.join(downloads_dir, f"redacted_{pdf_file.filename}")

        pdf_file.save(pdf_path)

        text = extract_text_from_pdf(pdf_path)

        redaction_list = identify_redaction_targets(text, instruction)

        redact_text_in_pdf(pdf_path, redacted_pdf_path, redaction_list)

        os.remove(pdf_path)

        return send_file(redacted_pdf_path, as_attachment=True, download_name=f"redacted_{pdf_file.filename}")

    except Exception as e:
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

# Video processing
def download_youtube_video(url, filename):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(file_extension='mp4').first()
        if not stream:
            raise Exception("No valid video stream found.")
        stream.download(filename=filename)
    except HTTPError as e:
        logging.error(f"HTTP Error: {e.code} - {e.reason}")
        raise
    except Exception as e:
        logging.error(f"An error occurred while downloading the video: {str(e)}")
        raise

def download_vimeo_video(url, filename):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download Vimeo video")
        with open(filename, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        logging.error(f"An error occurred while downloading the Vimeo video: {str(e)}")
        raise

def extract_frames(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"Failed to open video file: {video_path}")
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        return frames
    except Exception as e:
        logging.error(f"An error occurred while extracting frames: {str(e)}")
        raise

def reassemble_video(frames, output_path, fps=30):
    try:
        height, width, _ = frames[0].shape
        video_out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
        for frame in frames:
            video_out.write(frame)
        video_out.release()
    except Exception as e:
        logging.error(f"An error occurred while reassembling video: {str(e)}")
        raise

@app.route('/blur-eyes', methods=['POST'])
def blur_eyes_in_video():
    try:
        data = request.get_json()
        source_type = data.get('type')
        path_or_url = data.get('path/url')
        output_filename = data.get('output_filename', 'blurred_eyes_video.mp4')
        if not source_type or not path_or_url:
            return jsonify({"error": "No source type or path/URL provided"}), 400

        downloads_dir = 'downloads'
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        video_path = os.path.join(downloads_dir, 'video.mp4')
        output_path = os.path.join(downloads_dir, output_filename)

        if source_type == 'youtube':
            logging.info(f"Downloading YouTube video from URL: {path_or_url}")
            download_youtube_video(path_or_url, video_path)
        elif source_type == 'vimeo':
            logging.info(f"Downloading Vimeo video from URL: {path_or_url}")
            download_vimeo_video(path_or_url, video_path)
        elif source_type == 'local':
            logging.info(f"Using local video file: {path_or_url}")
            if not os.path.exists(path_or_url):
                return jsonify({"error": "Local file not found"}), 400
            video_path = path_or_url
        else:
            return jsonify({"error": "Invalid source type"}), 400

        logging.info("Video downloaded successfully")

        logging.info("Extracting frames from video")
        frames = extract_frames(video_path)
        eye_cascade = load_eye_detector()
        logging.info("Loaded eye detector model")
        logging.info("Detecting and blurring eyes in frames")
        blurred_frames = [detect_and_blur_eyes(eye_cascade, frame) for frame in frames]
        logging.info("Reassembling video from blurred frames")
        reassemble_video(blurred_frames, output_path)

        if source_type in ['youtube', 'vimeo']:
            os.remove(video_path)
        logging.info("Video processed successfully")
        return jsonify({"message": "Video processed successfully", "output_file": output_path}), 200

    except HTTPError as e:
        logging.error(f"HTTP Error: {e.code} - {e.reason}")
        return jsonify({"error": f"HTTP Error: {e.code} - {e.reason}"}), 500
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

@app.route('/blur-faces', methods=['POST'])
def blur_faces_in_video():
    try:
        data = request.get_json()
        source_type = data.get('type')
        path_or_url = data.get('path/url')
        output_filename = data.get('output_filename', 'blurred_video.mp4')
        if not source_type or not path_or_url:
            return jsonify({"error": "No source type or path/URL provided"}), 400

        downloads_dir = 'downloads'
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        video_path = os.path.join(downloads_dir, 'video.mp4')
        output_path = os.path.join(downloads_dir, output_filename)

        if source_type == 'youtube':
            logging.info(f"Downloading YouTube video from URL: {path_or_url}")
            download_youtube_video(path_or_url, video_path)
        elif source_type == 'vimeo':
            logging.info(f"Downloading Vimeo video from URL: {path_or_url}")
            download_vimeo_video(path_or_url, video_path)
        elif source_type == 'local':
            logging.info(f"Using local video file: {path_or_url}")
            if not os.path.exists(path_or_url):
                return jsonify({"error": "Local file not found"}), 400
            video_path = path_or_url
        else:
            return jsonify({"error": "Invalid source type"}), 400

        logging.info("Video downloaded successfully")

        logging.info("Extracting frames from video")
        frames = extract_frames(video_path)
        net = load_face_detector()
        logging.info("Loaded face detector model")
        logging.info("Detecting and blurring faces in frames")
        blurred_frames = [detect_and_blur_faces(net, frame) for frame in frames]
        logging.info("Reassembling video from blurred frames")
        reassemble_video(blurred_frames, output_path)

        if source_type in ['youtube', 'vimeo']:
            os.remove(video_path)
        logging.info("Video processed successfully")
        return jsonify({"message": "Video processed successfully", "output_file": output_path}), 200

    except HTTPError as e:
        logging.error(f"HTTP Error: {e.code} - {e.reason}")
        return jsonify({"error": f"HTTP Error: {e.code} - {e.reason}"}), 500
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

@app.route('/blur-person', methods=['POST'])
def blur_specific_person_in_video():
    try:
        source_type = request.form.get('type')
        path_or_url = request.form.get('path/url')
        output_filename = request.form.get('output_filename', 'blurred_person_video.mp4')
        zip_file = request.files.get('zip_file')

        if not source_type or not path_or_url or not zip_file:
            return jsonify({"error": "Missing source type, path/URL, or zip file"}), 400

        downloads_dir = 'downloads'
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        video_path = os.path.join(downloads_dir, 'video.mp4')
        output_path = os.path.join(downloads_dir, output_filename)
        zip_path = os.path.join(downloads_dir, 'images.zip')
        image_folder = os.path.join(downloads_dir, 'extracted_images')

        zip_file.save(zip_path)
        extract_zip(zip_path, image_folder)
        known_encodings = load_face_encodings(image_folder)

        if source_type == 'youtube':
            logging.info(f"Downloading YouTube video from URL: {path_or_url}")
            download_youtube_video(path_or_url, video_path)
        elif source_type == 'vimeo':
            logging.info(f"Downloading Vimeo video from URL: {path_or_url}")
            download_vimeo_video(path_or_url, video_path)
        elif source_type == 'local':
            logging.info(f"Using local video file: {path_or_url}")
            if not os.path.exists(path_or_url):
                return jsonify({"error": "Local file not found"}), 400
            video_path = path_or_url
        else:
            return jsonify({"error": "Invalid source type"}), 400

        logging.info("Video downloaded successfully")

        logging.info("Extracting frames from video")
        frames = extract_frames(video_path)
        logging.info("Detecting and blurring the specific person in frames")
        blurred_frames = [detect_and_blur_specific_person(frame, known_encodings) for frame in frames]
        logging.info("Reassembling video from blurred frames")
        reassemble_video(blurred_frames, output_path)

        if source_type in ['youtube', 'vimeo']:
            os.remove(video_path)
        logging.info("Video processed successfully")
        return jsonify({"message": "Video processed successfully", "output_file": output_path}), 200

    except HTTPError as e:
        logging.error(f"HTTP Error: {e.code} - {e.reason}")
        return jsonify({"error": f"HTTP Error: {e.code} - {e.reason}"}), 500
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)