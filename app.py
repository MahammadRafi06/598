import os
from flask import Flask, request, render_template, jsonify, send_file, Response
import urllib.request
import json
import ssl
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

app = Flask(__name__)
def allowSelfSignedHttps(allowed):
    # Bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    allowSelfSignedHttps(True)
    patient_df = pd.read_csv('data/Patient.csv')
    transactions_df = pd.read_csv('data/Transactions.csv')
    patient_details = {}
    transaction ={}
    trans = transactions_df[transactions_df['Transaction_ID']==int(request.form.get("transactionId"))].to_dict(orient='records')
    for tran in trans:
        for key, val in tran.items():
            transaction[key] = val
    try:
        pats = patient_df[patient_df['Patient_ID']==transaction['Patient_ID']].to_dict(orient='records')
        for pat in pats:
            for key, val in pat.items():
                patient_details[key] = val
    except Exception as KeyError:
        return render_template('error.html'), 404

    data = {
            "input_data": {
                "columns": [
                    "age",
                    "sex",
                    "cp",
                    "trestbps",
                    "chol",
                    "fbs",
                    "restecg",
                    "thalach",
                    "exang",
                    "oldpeak",
                    "slope",
                    "ca",
                    "thal"
                ],
                "data": [
                    [transaction['age'], transaction['sex'], transaction['cp'], transaction['trestbps'], transaction['chol'], transaction['fbs'], 
                    transaction['restecg'], transaction['thalach'], transaction['exang'], transaction['oldpeak'], transaction['slope'], 
                    transaction['ca'], transaction['thal']]
                ]
            }
    }
    if transaction['Premieum']==1:
        body = str.encode(json.dumps(data))
        url = 'https://premiumservice-endpoint-213e0007.canadacentral.inference.ml.azure.com/score'
        api_key = os.getenv("api_key")
        if not api_key:
            raise Exception("A key must be provided to invoke the endpoint")
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }

        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)
            result = response.read().decode('utf-8')
            result_json = json.loads(result)

        except urllib.error.HTTPError as error:
            print("The request failed with status code:", error.code)
            print("Error details:")
            print(error.info())
            print(error.read().decode("utf-8", 'ignore'))
            return jsonify({"error": "Request failed", "details": error.read().decode("utf-8", 'ignore')}), error.code

        if result_json ==[0]:
            analysis_summary = """Based on the provided patient data, our analysis indicates no significant risk of heart attack. 
                                However, we recommend routine follow-ups and monitoring to ensure continued health.
                            """
        else:
            analysis_summary = """ Based on the provided patient data, our analysis indicates a potential risk of heart attack. 
                                    We recommend clinical verification and correlation with additional diagnostic findings for accurate assessment.
                                """
    else:
        analysis_summary = """PREMIUM SERVICE WAS NOT REQUESTED FOR THIS TRANSACTION"""
    return render_template('report 2.html', 
                           patient_details=patient_details, 
                           analysis_summary=analysis_summary, transaction=transaction)

@app.route('/download-pdf')
def download_pdf():
    # Render the HTML template
    html = render_template('report.html')

    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')

    # Create a file-like buffer to hold the PDF data
    buffer = BytesIO()

    # Create a PDF canvas
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Patient Report")

    # Starting position for the text
    x = 50
    y = 750

    # Add Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(x, y, "Patient Report")
    y -= 30

    # Add content from parsed HTML
    pdf.setFont("Helvetica", 12)

    for section in soup.find_all('div', class_='section'):
        # Add section title
        section_title = section.find('h2').get_text()
        pdf.drawString(x, y, section_title)
        y -= 20

        # Add details in the section
        for p in section.find_all('p'):
            text = p.get_text()
            pdf.drawString(x, y, text)
            y -= 15

        # Add space after each section
        y -= 10

        # If the y-coordinate is too low, create a new page
        if y < 50:
            pdf.showPage()
            y = 750

    # Finalize the PDF
    pdf.showPage()
    pdf.save()

    # Move the buffer's cursor to the beginning
    buffer.seek(0)

    # Return the PDF as a response with appropriate headers
    response = Response(buffer, content_type='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename="Patient_Report.pdf"'
    return response

'''def download_pdf():
    # Create a file-like buffer to hold the PDF data
    buffer = io.BytesIO()

    # Create a PDF canvas
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Patient Report")

    # Add content to the PDF
    pdf.drawString(100, 750, "Patient Report")
    pdf.drawString(100, 730, "Name: Smriti Kotiyal")
    pdf.drawString(100, 710, "Date of Birth: 08/05/1994")
    pdf.drawString(100, 690, "Age: 30")
    pdf.drawString(100, 670, "Sex: Female")
    pdf.drawString(100, 650, "Patient ID: 155019939")
    pdf.drawString(100, 630, "Specimen ID: 327-535-1549-0")

    # Finalize the PDF
    pdf.showPage()
    pdf.save()

    # Move the buffer's cursor to the beginning
    buffer.seek(0)

    # Return the PDF as a response with appropriate headers
    response = Response(buffer, content_type='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename="Patient_Report.pdf"'
    return response'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)























