from flask import Flask, request, jsonify, render_template
from google import genai
from dotenv import load_dotenv
import PyPDF2
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

chat_history = []
pdf_text = ""

def extract_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    global pdf_text, chat_history
    file = request.files["pdf"]
    pdf_text = extract_text(file)
    chat_history = []
    return jsonify({"message": "PDF loaded successfully!"})

@app.route("/ask", methods=["POST"])

def ask():
    global chat_history
    try:
        data = request.json
        question = data["question"]

        history = "\n".join([f"Q: {q}\nA: {a}" for q, a in chat_history])
        prompt = f"""
        Answer based ONLY on this PDF content.
        If answer not found say "I couldn't find that in the PDF."
        
        PDF: {pdf_text[:5000]}
        
        Previous conversation:
        {history}
        
        Question: {question}
        """
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        answer = response.text
        chat_history.append((question, answer))
        return jsonify({"answer": answer})
    
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"}), 200
    
if __name__ == "__main__":
    app.run(debug=True, port=5001,use_reloader=False)