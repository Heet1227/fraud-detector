from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import whois
from bs4 import BeautifulSoup
from datetime import datetime
import time

app = Flask(__name__)
CORS(app)

# API Keys (Replace with your actual keys)
ABSTRACT_API_KEY = "efa5270de55b4123b32161f8cf5c295d"
OPENCELLID_API_KEY = "953aaf403aca86eb0ba988e47b444a48"
NUMVERIFY_API_KEY = "your_numverify_api_key_here"  # Replace if needed

# Function to check phone number using NumVerify API
def check_phone_number(phone):
    url = f"https://phonevalidation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&phone={phone}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if not data.get("valid"):
            return {"status": "Invalid", "message": "❌ This phone number is invalid or fake!"}

        return {
            "status": "Valid",
            "phone": phone,
            "country": data.get("country", {}).get("name", "Not Available"),
            "carrier": data.get("carrier", "Not Available"),
            "line_type": data.get("line_type", "Not Available"),
            "message": "⚠️ VoIP number detected, often used in scams!" if data.get("line_type") == "voip" else "✅ This is a standard number."
        }
    except requests.exceptions.RequestException as e:
        return {"status": "Error", "message": f"❌ API Error: {str(e)}"}

# Function to get phone location dynamically
def get_phone_location(mcc, mnc, cell_id, lac):
    url = "https://us1.unwiredlabs.com/v2/process.php"
    payload = {
        "token": OPENCELLID_API_KEY,
        "radio": "gsm",
        "mcc": mcc,
        "mnc": mnc,
        "cells": [{"lac": lac, "cid": cell_id}],
        "address": 1
    }
    
    try:
        for _ in range(3):  # Retry mechanism (3 attempts)
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "lat" in data and "lon" in data:
                    return {"latitude": data["lat"], "longitude": data["lon"], "address": data.get("address", "Unknown")}
            time.sleep(2)  # Wait before retry
        return {"error": "Location Not Found"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

# Function to get domain age using WHOIS
def get_whois_info(url):
    try:
        domain_name = url.replace("https://", "").replace("http://", "").split("/")[0]
        domain = whois.whois(domain_name)
        creation_date = domain.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            age = (datetime.now() - creation_date).days
            return f"🗓 Domain Age: {age} days"
        return "Unknown Domain Age"
    except Exception as e:
        return f"❌ WHOIS Error: {str(e)}"

# Function to fetch and analyze website content
def get_website_content(url):
    try:
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        full_url = "https://" + domain
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(full_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"❌ Error: Unable to fetch website (Status {response.status_code})"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join(soup.stripped_strings).lower()
        scam_keywords = ["lottery", "prize", "winner", "bitcoin", "investment", "free money", "claim your reward"]
        
        if any(keyword in text for keyword in scam_keywords):
            return "⚠️ Warning: Possible scam keywords found!"
        return "✅ No suspicious content detected."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Unified API Route to handle both phone numbers and websites
@app.route('/check', methods=['POST'])
def check_input():
    data = request.json
    input_data = data.get("input")
    
    if not input_data:
        return jsonify({"status": "Error", "message": "❌ No input provided!"}), 400
    
    if input_data.startswith("+") or input_data.isdigit():
        phone_info = check_phone_number(input_data)
        location_info = get_phone_location(310, 260, 5678, 1234)  # Replace with real data
        phone_info.update(location_info)
        return jsonify(phone_info)
    else:
        return jsonify({
            "domain_age": get_whois_info(input_data),
            "content_analysis": get_website_content(input_data)
        })

# Run Flask server
if __name__ == '__main__':
    app.run(debug=True)
