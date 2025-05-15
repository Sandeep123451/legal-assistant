from flask import Flask, request, jsonify, render_template, send_file
import requests
from io import BytesIO
from fpdf import FPDF
import html
import json

app = Flask(__name__)

# Your API keys
KANOON_API_KEY = "14d7de0f5d86db0d5ca7fcd965a7058774d31d6b"
GROQ_API_KEY = "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"

# Indian Kanoon API Base URL
KANOON_API_URL = "https://api.indiankanoon.org/search/"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Function for searching data from Indian Kanoon
def search_kanoon(query):
    headers = {
        "Authorization": f"Token {KANOON_API_KEY}"
    }
    params = {
        "query": query,   
        "num": 1
    }
    response = requests.get(KANOON_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json()
        if results.get("results"):
            return results["results"][0].get("snippet", "No snippet found.")
        return "No results found."
    return "Error fetching data from Indian Kanoon."

# Function for generating explanation using Groq
def get_groq_explanation(user_question, kanoon_data):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a legal assistant. Explain legal content in simple terms."},
            {"role": "user", "content": f"User asked: {user_question}\nRelevant legal info: {kanoon_data}\nPlease explain."}
        ],
        "temperature": 0.7
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return "Sorry, couldn't get an explanation from Groq."

# Sample legal dictionary (this can be expanded)
legal_dict = {
    "tort": "A tort is a civil wrong that causes harm or loss to someone, and for which the law provides a remedy.",
    "contract": "A contract is an agreement between two or more parties that is enforceable by law.",
    "statute": "A statute is a written law passed by a legislative body.",
    "plaintiff": "A plaintiff is a person who brings a case against another in a court of law.",
    "defendant": "A defendant is a person who is being accused or sued in a court of law."
}

@app.route('/legal_dictionary_search', methods=['POST'])
def legal_dictionary_search():
    term = request.json.get('term')

    if not term:
        return jsonify({"response": "Please enter a legal term."}), 400

    definition = legal_dict.get(term.lower())

    if definition:
        return jsonify({"response": definition})
    else:
        # Fallback to Groq explanation if not in static dictionary
        explanation = get_groq_explanation(term, "")

        return jsonify({"response": explanation})



# Route for the home page
@app.route("/")
def index():
    return render_template("index.html")

# Route for the chatbot page
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

# Route to render the Document Drafting Page
@app.route('/document_drafting', methods=['GET', 'POST'])
def document_drafting():
    if request.method == 'POST':
        # Get the form data
        document_type = request.form.get('documentType')
        if document_type == 'nda':
            party_one = request.form.get('partyOne')
            party_two = request.form.get('partyTwo')
            confidentiality_terms = request.form.get('confidentialityTerms')
            # Generate the NDA content
            document_content = f"""
                <h3>Non-Disclosure Agreement (NDA)</h3>
                <p><strong>Party One:</strong> {party_one}</p>
                <p><strong>Party Two:</strong> {party_two}</p>
                <p><strong>Confidentiality Terms:</strong> {confidentiality_terms}</p>
            """
        elif document_type == 'contract':
            party_a = request.form.get('partyA')
            party_b = request.form.get('partyB')
            contract_terms = request.form.get('contractTerms')
            # Generate the Contract content
            document_content = f"""
                <h3>Contract Agreement</h3>
                <p><strong>Party A:</strong> {party_a}</p>
                <p><strong>Party B:</strong> {party_b}</p>
                <p><strong>Contract Terms:</strong> {contract_terms}</p>
            """
        # Add more document types as needed

        # Return the generated document as a response (or render a new template with the preview)
        return render_template('document_preview.html', document_content=document_content)
    
    return render_template('document_drafting.html')  # Display the document drafting form page

def generate_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

@app.route("/download_document", methods=["POST"])
def download_document():
    content = request.form.get("documentContent")
    pdf_output = generate_pdf(content)
    return send_file(pdf_output, as_attachment=True, download_name="document.pdf", mimetype="application/pdf")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")  # Get the user's message
    if not user_message:
        return jsonify({"response": "Please send a message."}), 400

    explanation = get_groq_explanation(user_message, "")


    # Return the response as JSON
    return jsonify({"response": explanation})


@app.route("/legal_aid_checker")
def legal_aid_checker():
    return render_template("legal_aid_checker.html")

@app.route("/legal_dictionary")
def legal_dictionary():
    return render_template("legal_dictionary.html")
@app.route("/case_law_finder")
def case_law_finder():
    return render_template("case_law_finder.html")

@app.route("/search_case_law", methods=["POST"])
def search_case_law():
    user_query = request.json.get('query')

    if not user_query:
        return jsonify({"response": "Please enter a case law query."}), 400

    # # Search case law using Indian Kanoon API or Groq AI
    kanoon_data = search_kanoon(user_query)  # This is where you call the search from Indian Kanoon API

    # Get an explanation using Groq API (Optional)
    explanation = get_groq_explanation(user_query, kanoon_data)

    return jsonify({"response": explanation})






# Find relevant Supreme Court case laws related to the Right to Education under Article 21A of the Indian Constitution.






@app.route("/legal_compliance_checker")
def legal_compliance_checker():
    return render_template("legal_compliance_checker.html")
# Simulate a compliance check function

def check_compliance(query):
    # Example logic for checking compliance (This should be your actual business logic)
    if "tax" in query.lower():
        return {
            "status": "Compliant",
            "details": "Your tax filings are up-to-date.",
            "recommendations": [
                "File your tax returns by April 15th.",
                "Consult with a tax advisor for deductions."
            ]
        }
    else:
        return {
            "status": "Non-Compliant",
            "details": "Compliance check failed. Further action required.",
            "recommendations": [
                "Review applicable laws and regulations.",
                "Contact a legal advisor."
            ]
        }

@app.route('/legal_compliance_check', methods=['POST'])
def legal_compliance_check():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    result = check_compliance(query)
    return jsonify(result)

@app.route('/generate_compliance_report', methods=['POST'])
def generate_compliance_report():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # For demonstration purposes, return a mock PDF
    # You can replace this with code to generate an actual PDF report
    return app.send_static_file('mock_report.pdf')

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
