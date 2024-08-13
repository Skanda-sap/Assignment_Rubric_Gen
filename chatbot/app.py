from flask import Flask, request, render_template
import pdfplumber
import docx
import nltk

app = Flask(__name__)

# Ensure necessary NLTK resources are downloaded
nltk.download('punkt')

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return '\n'.join(page.extract_text() for page in pdf.pages)

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return '\n'.join(para.text for para in doc.paragraphs)

def generate_rubric_and_grade(text):
    rubric = []
    total_score = 0
    max_score = 10  # Assuming a total of 10 points

    # Check for introduction and thesis - more flexible detection
    intro_score = 0
    if any(keyword in text.lower() for keyword in ['introduction', 'beginning', 'start']):
        rubric.append("Introduction & Thesis: Clarity and Relevance")
        intro_score = 2  # Assign 2 points for a good introduction and thesis
    else:
        rubric.append("Introduction & Thesis: Needs Improvement")
        intro_score = 1  # Assign 1 point for a weak or missing introduction and thesis
    total_score += intro_score

    # Check for coherence and transition - broader detection
    body_score = 0
    if any(phrase in text.lower() for phrase in ['transition', 'next', 'following', 'coherence']):
        rubric.append("Body Paragraphs: Coherence and Transition")
        body_score = 2  # Assign 2 points for well-structured body paragraphs
    else:
        rubric.append("Body Paragraphs: Needs Better Coherence and Transition")
        body_score = 1  # Assign 1 point for weak coherence and transitions
    total_score += body_score

    # Check for conclusion - broader detection
    conclusion_score = 0
    if any(keyword in text.lower() for keyword in ['conclusion', 'summary', 'closing']):
        rubric.append("Conclusion: Summarization and Closure")
        conclusion_score = 2  # Assign 2 points for a strong conclusion
    else:
        rubric.append("Conclusion: Needs Improvement")
        conclusion_score = 1  # Assign 1 point for a weak or missing conclusion
    total_score += conclusion_score

    # Grammar and style check - provide base score
    grammar_score = 2  # Assume good grammar and style unless major issues are detected
    rubric.append("Grammar and Style: Sentence Structure and Word Choice")
    total_score += grammar_score

    # Argument and Analysis - broader detection
    argument_score = 2  # Base score for strong argument and analysis
    rubric.append("Argument & Analysis: Depth and Critical Thinking")
    total_score += argument_score

    # Normalize the score to fit within 10 points
    final_score = total_score / max_score * 10  # If total_score is out of 10 points, no normalization needed

    return rubric, final_score

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.filename.endswith('.docx'):
            text = extract_text_from_docx(uploaded_file)
        else:
            text = "Unsupported file format"
            rubric, grade = [], 0  # No grading for unsupported formats
        rubric, grade = generate_rubric_and_grade(text)
        return render_template('index.html', text=text, rubric=rubric, grade=grade)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
