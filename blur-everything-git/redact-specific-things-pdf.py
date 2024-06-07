from flask import Flask, request, send_file, jsonify
import fitz  
import os
import shutil
import spacy

app = Flask(__name__)

nlp = spacy.load("en_core_web_sm")

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

if __name__ == '__main__':
    app.run(debug=True)
