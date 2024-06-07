// src/components/EyesInPics.js
import React, { useState } from 'react';
import axios from 'axios';
import '../App.css';

const EyesInPics = () => {
  const [file, setFile] = useState(null);
  const [outputFileName, setOutputFileName] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleOutputFileNameChange = (e) => {
    setOutputFileName(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    if (file) formData.append('zip_file', file);
    formData.append('output_filename', outputFileName);

    try {
      const response = await axios.post("http://localhost:5000/blur-eyes-in-pictures", formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });

      const blob = new Blob([response.data], { type: response.data.type });
      const downloadUrl = URL.createObjectURL(blob);
      setPreviewUrl(downloadUrl);

      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = outputFileName || 'output.zip';
      a.click();
    } catch (error) {
      console.error('Error processing the file', error);
    }
  };

  return (
    <div className="gradient-background">
      <div className="container">
        <h2>Blur Eyes in Pictures</h2>
        <p>
          This tool uses advanced computer vision techniques to detect and blur eyes in images. By leveraging
          deep learning models and OpenCV, we ensure precise and effective eye detection and blurring to protect
          privacy.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="file-upload" className="file-input-wrapper">
              Choose File
            </label>
            <input id="file-upload" type="file" onChange={handleFileChange} />
          </div>
          <div className="form-group">
            <label>Output File Name:</label>
            <input type="text" value={outputFileName} onChange={handleOutputFileNameChange} />
          </div>
          <div className="form-group">
            <button type="submit">Blur Eyes</button>
          </div>
        </form>
        {previewUrl && (
          <div className="preview">
            <h3>Preview:</h3>
            <iframe src={previewUrl} width="600" height="400" title="Preview"></iframe>
          </div>
        )}
      </div>
    </div>
  );
};

export default EyesInPics;
