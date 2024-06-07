# blur.com  - Privacy Tool Application

The Privacy Tool application is designed to provide users with a range of privacy-related features such as blurring faces and eyes in images and videos, and redacting sensitive information in PDFs. This project comprises two main components: the frontend and the backend. Uses computer vision and custom made models in the backend

## Table of Contents

- [Frontend](#frontend)
  - [Features](#frontend-features)
  - [Installation](#frontend-installation)
  - [Usage](#frontend-usage)
  - [Technology Stack](#frontend-technology-stack)
  - [Project Structure](#frontend-project-structure)
  - [Contributing](#frontend-contributing)
  - [License](#frontend-license)
- [Backend](#backend)
  - [Features](#backend-features)
  - [Installation](#backend-installation)
  - [Usage](#backend-usage)
  - [API Endpoints](#api-endpoints)
  - [Technology Stack](#backend-technology-stack)
  - [Project Structure](#backend-project-structure)
  - [Contributing](#backend-contributing)
  - [License](#backend-license)
- [Face Detection and Blurring Model](#face-detection-and-blurring-model)
  - [Overview](#model-overview)
  - [Data Collection](#model-data-collection)
  - [Model Architecture](#model-architecture)
  - [Data Preprocessing](#model-data-preprocessing)
  - [Training](#model-training)
  - [Face Detection and Blurring](#model-face-detection-and-blurring)
  - [Evaluation](#model-evaluation)
  - [Model Conversion to Caffe](#model-conversion-to-caffe)

## Frontend

### Features

- Home page with a description of the application
- Multiple feature pages:
  - Blur Eyes in Video
  - Blur Faces in Video
  - Blur Specific Faces in Video
  - Redact PDF
  - Blur Eyes in Pictures
  - Blur Faces in Pictures
  - Blur Specific Faces in Pictures
- Technology overview page
- Responsive design using Bootstrap

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/privacy-tool-frontend.git
    cd privacy-tool-frontend
    ```

2. **Install dependencies:**

    ```bash
    npm install
    ```

3. **Start the development server:**

    ```bash
    npm start
    ```

    The application will be available at `http://localhost:3000`.

### Usage

- Navigate to different feature pages using the navbar.
- Upload files or provide links as required by each feature.
- Click the submit button to process the file.
- Download and preview the processed files.

### Technology Stack

- **React:** A JavaScript library for building user interfaces.
- **React Router:** A standard library for routing in React.
- **Bootstrap:** A CSS framework for responsive design.
- **Axios:** A promise-based HTTP client for making API requests.

### Project Structure

```plaintext
src/
├── components/
│   ├── Navbar.js
│   ├── Home.js
│   ├── EyesInVideo.js
│   ├── FacesInVideo.js
│   ├── SpecificFacesInVideo.js
│   ├── RedactPdf.js
│   ├── EyesInPics.js
│   ├── FacesInPics.js
│   ├── SpecificFacesInPics.js
│   ├── TechnologyPage.js
├── App.js
├── App.css
├── index.js
```

### Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Backend

### Features

- Blur Eyes in Video
- Blur Faces in Video
- Blur Specific Faces in Video
- Redact PDF
- Blur Eyes in Pictures
- Blur Faces in Pictures
- Blur Specific Faces in Pictures

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/privacy-tool-backend.git
    cd privacy-tool-backend
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Flask application:**

    ```bash
    flask run
    ```

    The application will be available at `http://localhost:5000`.

### Usage

- Send requests to the API endpoints using tools like Postman or the frontend application.
- Upload files or provide links as required by each feature.
- Receive the processed files as a response.

### API Endpoints

- **POST /blur-eyes-in-pictures**: Blur eyes in pictures.
- **POST /blur-faces-in-pictures**: Blur faces in pictures.
- **POST /blur-specific-person-in-pictures**: Blur specific faces in pictures using reference images.
- **POST /redact-pdf**: Redact sensitive information in PDFs.
- **POST /blur-eyes**: Blur eyes in videos.
- **POST /blur-faces**: Blur faces in videos.
- **POST /blur-person**: Blur specific faces in videos using reference images.

### Technology Stack

- **Flask:** A lightweight WSGI web application framework in Python.
- **OpenCV:** An open-source computer vision and machine learning software library.
- **spaCy:** An open-source library for advanced natural language processing in Python.
- **PyTube:** A lightweight, dependency-free Python library for downloading YouTube videos.
- **Requests:** A simple, yet elegant HTTP library for Python.

### Project Structure

```plaintext
privacy-tool-backend/
├── app.py
├── requirements.txt
├── venv/
├── static/
├── templates/
```

### Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Face Detection and Blurring Model

### Overview

This project involves building a custom Convolutional Neural Network (CNN) model for detecting and blurring faces in images, without using pretrained models.

### Data Collection

We use the [WIDER FACE dataset](http://shuoyang1213.me/WIDERFACE/) for training and validation.

### Model Architecture

A CNN is designed for face detection. The architecture includes convolutional layers, max-pooling layers, and fully connected layers. The output layer provides the coordinates of the detected face bounding boxes.

```python
import tensorflow as tf
from tensorflow.keras import layers, models

def create_face_detection_model(input_shape=(128, 128, 3)):
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(128, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dense(4))  # [x, y, width, height] for bounding box
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

model = create_face_detection_model()
model.summary()
```

### Data Preprocessing

Images are resized to 128x128 pixels, and labels are converted to bounding box coordinates.

### Training

The model is trained using the WIDER FACE dataset with mean squared error loss and the Adam optimizer. 

### Face Detection and Blurring

Detected faces are blurred by applying a Gaussian blur to the regions defined by the bounding boxes.

### Evaluation

The model is evaluated using precision, recall, and F1 score metrics on the validation set.

### Model Conversion to Caffe

To deploy the model in a production environment that requires Caffe, it is converted using a model conversion tool like MMdnn.
