1. **Blur Eyes in Pictures:**

```sh
curl -X POST http://localhost:5000/blur-eyes-in-pictures \
  -F "zip_file=@/path/to/your/input_images.zip"
```

2. **Blur Faces in Pictures:**

```sh
curl -X POST http://localhost:5000/blur-faces-in-pictures \
  -F "zip_file=@/path/to/your/input_images.zip"
```

3. **Blur Specific Person in Pictures:**

```sh
curl -X POST http://localhost:5000/blur-specific-person-in-pictures \
  -F "reference_zip_file=@/path/to/your/reference_images.zip" \
  -F "target_zip_file=@/path/to/your/target_images.zip"
```

4. **Redact PDF:**

```sh
curl -X POST http://localhost:5000/redact-pdf \
  -F "pdf_file=@/path/to/your/document.pdf" \
  -F "instruction=redact everything or redact info about XXX" 
```

5. **Blur Eyes in Video:**

```sh
curl -X POST http://localhost:5000/blur-eyes \
  -H "Content-Type: application/json" \
  -d '{"type": "youtube", "path/url": "https://www.youtube.com/watch?v=example", "output_filename": "blurred_eyes_video.mp4"}'
```

6. **Blur Faces in Video:**

```sh
curl -X POST http://localhost:5000/blur-faces \
  -H "Content-Type: application/json" \
  -d '{"type": "youtube", "path/url": "https://www.youtube.com/watch?v=example", "output_filename": "blurred_video.mp4"}'
```

7. **Blur Specific Person in Video:**

```sh
curl -X POST http://localhost:5000/blur-person \
  -F "type=youtube" \
  -F "path/url=https://www.youtube.com/watch?v=example" \
  -F "output_filename=blurred_person_video.mp4" \
  -F "zip_file=@/path/to/your/images.zip"
```