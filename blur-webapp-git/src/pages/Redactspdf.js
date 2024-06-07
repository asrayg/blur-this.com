// src/components/RedactPdf.js
import React, { useState } from 'react';
import axios from 'axios';
import '../App.css';

const RedactPdf = () => {
  const [file, setFile] = useState(null);
  const [instruction, setInstruction] = useState('');
  const [outputFileName, setOutputFileName] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleInstructionChange = (e) => {
    setInstruction(e.target.value);
  };

  const handleOutputFileNameChange = (e) => {
    setOutputFileName(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    if (file) formData.append('pdf_file', file);
    formData.append('instruction', instruction);
    formData.append('output_filename', outputFileName);

    try {
      const response = await axios.post("http://localhost:5000/redact-pdf", formData, {
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
      a.download = outputFileName || 'redacted_output.pdf';
      a.click();
    } catch (error) {
      console.error('Error processing the file', error);
    }
  };

  return (
    <div className="gradient-background">
      <div className="container">
        <h2>Redact PDF</h2>
        <p>
          This tool uses advanced natural language processing techniques to redact sensitive information from PDF files. By leveraging
          models such as spaCy, we ensure precise and effective redaction to protect your privacy.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="file-upload" className="file-input-wrapper">
              Choose File
            </label>
            <input id="file-upload" type="file" onChange={handleFileChange} />
          </div>
          <div className="form-group">
            <label>Redaction Instructions:</label>
            <input type="text" value={instruction} onChange={handleInstructionChange} placeholder="e.g., redact all names" />
          </div>
          <div className="form-group">
            <label>Output File Name:</label>
            <input type="text" value={outputFileName} onChange={handleOutputFileNameChange} />
          </div>
          <div className="form-group">
            <button type="submit">Redact PDF</button>
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

export default RedactPdf;
