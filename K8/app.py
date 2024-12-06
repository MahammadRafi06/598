import os
from flask import Flask, request, render_template, jsonify
import urllib.request
import json
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
def allowSelfSignedHttps(allowed):
    # Bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

patient = {}
@app.route('/analyze', methods=['POST'])
def analyze():
    allowSelfSignedHttps(True)
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
            [request.form.get("age"), request.form.get("sex"), request.form.get("chestPainType"), request.form.get("restingBP"),request.form.get("cholesterol"),
              request.form.get("fastingBS"),request.form.get("restingECG"), request.form.get("maxHR"), request.form.get("exerciseAngina"), request.form.get("stDepression"),
             request.form.get("stSlope"), request.form.get("majorVessels"),request.form.get("thal")]
        ]
    }
    }
    body = str.encode(json.dumps(data))
    url = 'https://z89project-cidci.canadacentral.inference.ml.azure.com/score'
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

    patient[request.form.get("patientID")] = {
        "patientName": request.form.get("patientName"),
        "dob": request.form.get("dob"),
        "HealthPlan": request.form.get("healthPlan"),
    }
    patient_details = f"""
    Name: {request.form.get("patientName")}
    Date of Birth: {request.form.get("dob")}
    Health Plan: {request.form.get("healthPlan")}
    """
    if result_json ==[0]:
        analysis_summary = """Based on the provided patient data, our analysis indicates no significant risk of heart attack. 
                              However, we recommend routine follow-ups and monitoring to ensure continued health.
                           """
    else:
         analysis_summary = """ Based on the provided patient data, our analysis indicates a potential risk of heart attack. 
                                We recommend clinical verification and correlation with additional diagnostic findings for accurate assessment.
                            """


    return render_template('result.html', 
                           patient_details=patient_details, 
                           analysis_summary=analysis_summary)







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)























