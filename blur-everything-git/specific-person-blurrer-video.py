from flask import Flask, request, jsonify
import cv2
import numpy as np
import os
import logging
import zipfile
import face_recognition
from pytube import YouTube
import requests
from urllib.error import HTTPError

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

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

def detect_and_blur_specific_person(frame, known_encodings):
    try:
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            if True in matches:
                face = frame[top:bottom, left:right]
                face = cv2.GaussianBlur(face, (99, 99), 30)
                frame[top:bottom, left:right] = face
        return frame
    except Exception as e:
        logging.error(f"An error occurred while detecting and blurring the specific person: {str(e)}")
        raise

@app.route('/blur-person', methods=['POST'])
def blur_specific_person_in_video():
    try:
        source_type = request.form.get('type')
        path_or_url = request.form.get('path/url')
        output_filename = request.form.get('output_filename', 'blurred_person_video.mp4')
        zip_file = request.files.get('zip_file')

        if not source_type or not path_or_url or not zip_file:
            return jsonify({"error": "Missing source type, path/URL, or zip file"}), 400

        # Ensure the downloads directory exists
        downloads_dir = 'downloads'
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        video_path = os.path.join(downloads_dir, 'video.mp4')
        output_path = os.path.join(downloads_dir, output_filename)
        zip_path = os.path.join(downloads_dir, 'images.zip')
        image_folder = os.path.join(downloads_dir, 'extracted_images')

        # Save and extract the zip file
        zip_file.save(zip_path)
        extract_zip(zip_path, image_folder)
        known_encodings = load_face_encodings(image_folder)

        # Download video
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
