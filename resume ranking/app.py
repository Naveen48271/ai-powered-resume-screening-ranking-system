import os
import pdfplumber
import nltk
import numpy as np
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("stopwords")
nltk.download("punkt")
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app = Flask(__name__)

UPLOAD_FOLDER = "resumes"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to extract text from PDFs
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + " "
    return text.lower()

# Function to preprocess text
def preprocess_text(text):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text)
    return " ".join([word for word in words if word.isalnum() and word not in stop_words])

@app.route("/rank", methods=["POST"])
def rank_resumes():
    job_description = request.form.get("job_description")
    if not job_description:
        return jsonify({"error": "Job description is required"}), 400

    job_description = preprocess_text(job_description)

    resumes = []
    resume_names = []

    # Save uploaded resumes and process
    if "resumes" not in request.files:
        return jsonify({"error": "No resumes uploaded"}), 400

    files = request.files.getlist("resumes")
    for file in files:
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            text = extract_text_from_pdf(filepath)
            processed_text = preprocess_text(text)

            resumes.append(processed_text)
            resume_names.append(filename)

    if not resumes:
        return jsonify({"error": "No valid resumes processed"}), 400

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer()
    documents = [job_description] + resumes
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Compute similarity scores
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    ranked_resumes = sorted(zip(resume_names, similarities), key=lambda x: x[1], reverse=True)

    return jsonify({"ranked_resumes": ranked_resumes})

if __name__ == "__main__":
    app.run(debug=True)
