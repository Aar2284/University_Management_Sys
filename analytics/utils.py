import os
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(pdf_file_path):
    """Extract text content from a PDF file."""
    try:
        reader = PdfReader(pdf_file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
        return text.strip()
    except Exception:
        return ""


def compute_similarity(text_a, text_b):
    """Compute cosine similarity between two texts using TF-IDF."""
    if not text_a or not text_b:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    try:
        tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return round(float(similarity[0][0]) * 100, 2)
    except Exception:
        return 0.0
