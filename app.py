from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pdfminer.high_level import extract_text
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Download required NLTK data
try:
    nltk.download('punkt_tab')  # Add this line
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
except Exception as e:
    print(f"Error downloading NLTK resources: {e}")

def extract_resume_text(file):
    if file.filename.endswith('.pdf'):
        # Save the uploaded file temporarily
        temp_path = os.path.join('/tmp', file.filename)
        file.save(temp_path)
        try:
            # Extract text from PDF
            text = extract_text(temp_path)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        # Assume file is a plain text file
        text = file.read().decode('utf-8')
    return text

def calculate_ats_score(resume_text, job_description):
    # Tokenize and clean the text
    stop_words = set(stopwords.words('english'))
    resume_tokens = word_tokenize(resume_text.lower())
    job_tokens = word_tokenize(job_description.lower())

    # Remove stop words and non-alphabetical tokens
    resume_keywords = [word for word in resume_tokens if word.isalpha() and word not in stop_words]
    job_keywords = [word for word in job_tokens if word.isalpha() and word not in stop_words]

    # Match keywords
    matched_keywords = set(resume_keywords).intersection(set(job_keywords))
    score = (len(matched_keywords) / len(set(job_keywords))) * 100
    return round(score, 2)

@app.route('/ats-score', methods=['POST'])
def check_ats_score():
    # Check if resume file is in the request
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400
    
    # Get the resume file and job description
    resume_file = request.files['resume']
    job_description = request.form.get('jobDescription')
    
    if resume_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not job_description:
        return jsonify({'error': 'No job description provided'}), 400
    
    # Process the file and calculate score
    try:
        resume_text = extract_resume_text(resume_file)
        score = calculate_ats_score(resume_text, job_description)
        return jsonify({'score': score}), 200
    except Exception as e:
        print(f"Error processing request: {str(e)}")  # For debugging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)