// src/components/EyesInVideo.js
import React, { useState } from 'react';
import axios from 'axios';
import '../App.css';

const EyesInVideo = () => {
  const [file, setFile] = useState(null);
  const [link, setLink] = useState('');
  const [outputFileName, setOutputFileName] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleLinkChange = (e) => {
    setLink(e.target.value);
  };

  const handleOutputFileNameChange = (e) => {
    setOutputFileName(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    if (file) formData.append('file', file);
    if (link) formData.append('link', link);
    formData.append('output_filename', outputFileName);

    try {
      const response = await axios.post("http://localhost:5000/blur-eyes", formData, {
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
      a.download = outputFileName || 'output';
      a.click();
    } catch (error) {
      console.error('Error processing the file', error);
    }
  };

  return (
    <div className="gradient-background">
      <div className="container">
        <h2>Blur Eyes in Video</h2>
        <p>
          This tool uses advanced computer vision techniques to detect and blur eyes in video files. By leveraging
          deep learning models and OpenCV, we ensure precise and effective eye detection and blurring to protect
          privacy.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Upload Video:</label>
            <input type="file" onChange={handleFileChange} />
          </div>
          <div className="form-group">
            <label>Or provide a link:</label>
            <input type="text" value={link} onChange={handleLinkChange} />
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

export default EyesInVideo;
