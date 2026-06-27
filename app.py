import os
import json
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# --------------------------------------------------
# FLASK APP
# --------------------------------------------------
app = Flask(__name__, static_url_path='/static')
CORS(app)

# --------------------------------------------------
# GEMINI API KEY
# --------------------------------------------------
API_KEY = "enter your gemini ap here"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

# --------------------------------------------------
# UNSPLASH API KEY
# --------------------------------------------------
UNSPLASH_ACCESS_KEY = "entrt your unplash api hear"


def get_car_image_url(query: str) -> str:
    """
    Fetch car image directly from Unsplash web search.
    Falls back to placeholder if not found.
    """
    name = (query or "").strip()
    print("🔍 [get_car_image_url] Searching image for:", name)

    if not UNSPLASH_ACCESS_KEY:
        print("⚠️ No Unsplash key configured, using placeholder.")
        return "https://via.placeholder.com/800x400?text=Car+Image"

    try:
        res = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": f"{name} car",
                "per_page": 1,
                "orientation": "landscape"
            },
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        )

        print("🌐 Unsplash status code:", res.status_code)

        if res.status_code != 200:
            print("⚠️ Unsplash error:", res.text)
            return "https://via.placeholder.com/800x400?text=Car+Image"

        data = res.json()
        results = data.get("results", [])

        if results:
            url = results[0]["urls"]["regular"]
            print("✅ Got Unsplash image URL:", url)
            return url
        else:
            print("⚠️ No results from Unsplash, using placeholder.")
            return "https://via.placeholder.com/800x400?text=Car+Image"

    except Exception as e:
        print("❌ Image fetch error:", e)
        return "https://via.placeholder.com/800x400?text=Car+Image"


# --------------------------------------------------
# JSON extraction helper
# --------------------------------------------------
def extract_json(text):
    text = text.strip()
    try:
        return json.loads(text)
    except:
        pass

    stack = []
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if start is None:
                start = i
            stack.append("{")
        elif ch == "}" and stack:
            stack.pop()
            if not stack:
                try:
                    return json.loads(text[start:i+1])
                except:
                    start = None
    raise ValueError("No valid JSON found")


# --------------------------------------------------
# Serve index.html
# --------------------------------------------------
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


# --------------------------------------------------
# Single Car Info Endpoint
# --------------------------------------------------
@app.route('/get_car_info', methods=['GET'])
def get_car_info():
    car_name = request.args.get('car', '').strip()
    if not car_name:
        return jsonify({"status": "error", "message": "Please provide a car name."})

    prompt = f"""
    Give detailed information about {car_name} (Indian market if applicable).
    Return ONLY valid JSON.
    Keys:
    - "model": string
    - "engine": string
    - "price": {{"variant": "₹xx"}}
    - "features": array of strings
    - "mileage": string
    - "comfort": string
    If unknown, return {{"error": "No information available"}}.
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        try:
            car_data = json.loads(text)
        except:
            car_data = extract_json(text)

        if "error" in car_data:
            return jsonify({"status": "error", "message": car_data["error"]})

        model_name_for_image = car_data.get("model", car_name)
        car_data["image_url"] = get_car_image_url(model_name_for_image)

        return jsonify({"status": "success", "data": car_data})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# --------------------------------------------------
# Cars by Budget Endpoint
# --------------------------------------------------
@app.route('/cars_by_budget', methods=['GET'])
def cars_by_budget():
    max_price = request.args.get('max_price', '').strip()

    if not max_price:
        return jsonify({"status": "error", "message": "Please provide max_price in rupees (e.g. 500000)."})

    try:
        max_price_int = int(max_price.replace(",", ""))
    except ValueError:
        return jsonify({"status": "error", "message": "max_price must be a number like 500000."})

    prompt = f"""
    You are an Indian car expert.

    List popular NEW cars available in India with approx on-road price UNDER ₹{max_price_int}.
    Focus on entry-level hatchbacks, compact SUVs and budget-friendly models.

    Return ONLY valid JSON in this exact format:

    {{
      "cars": [
        {{
          "model": "string (car name with variant if relevant)",
          "price": "string (approx on-road price like '₹4.8 lakh')",
          "segment": "Hatchback | Sedan | SUV | MUV | Other",
          "fuel_type": "Petrol | Diesel | CNG | EV | Hybrid",
          "transmission": "Manual | Automatic | AMT | CVT | DCT",
          "mileage": "string like '18 kmpl (ARAI)'",
          "key_features": [
            "feature 1",
            "feature 2",
            "feature 3"
          ]
        }}
      ]
    }}

    Rules:
    - Maximum 10 cars.
    - All cars must be under ₹{max_price_int} on-road (approx in 2025).
    - If no suitable cars, return:
      {{"error": "No cars found under this budget"}}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        try:
            result = json.loads(text)
        except:
            result = extract_json(text)

        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]})

        if "cars" not in result or not isinstance(result["cars"], list):
            return jsonify({"status": "error", "message": "Invalid data format from model."})

        for car in result["cars"]:
            model_name = car.get("model", "")
            if model_name:
                car["image_url"] = get_car_image_url(model_name)
            else:
                car["image_url"] = ""

        return jsonify({"status": "success", "data": result})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# --------------------------------------------------
# Compare Two Cars
# --------------------------------------------------
@app.route('/compare_cars', methods=['GET'])
def compare_cars_get():
    car1 = request.args.get('car1', '').strip()
    car2 = request.args.get('car2', '').strip()

    if not car1 or not car2:
        return jsonify({"status": "error", "message": "Please provide both car1 and car2."})

    return compare_logic(car1, car2)


@app.route('/compare_cars', methods=['POST'])
def compare_cars_post():
    data = request.get_json(force=True)
    car1 = data.get("car1", "").strip()
    car2 = data.get("car2", "").strip()

    if not car1 or not car2:
        return jsonify({"status": "error", "message": "Both car1 and car2 required."})

    return compare_logic(car1, car2)


# --------------------------------------------------
# COMPARISON CORE FUNCTION
# --------------------------------------------------
def compare_logic(car1, car2):

    prompt = f"""
    Compare the following two cars and return ONLY valid JSON.
    The JSON MUST follow this format:

    {{
      "car1": {{
        "model": string,
        "engine": string,
        "price": object,
        "features": array,
        "mileage": string,
        "comfort": string
      }},
      "car2": {{
        "model": string,
        "engine": string,
        "price": object,
        "features": array,
        "mileage": string,
        "comfort": string
      }},
      "comparison": {{
        "better_overall": "car1" | "car2" | "tie",
        "advantages": {{
            "car1": [string],
            "car2": [string]
        }},
        "summary": string,
        "recommendation": string
      }}
    }}

    Car 1 = {car1}
    Car 2 = {car2}

    If information is missing for any car, fill with:
    "Information not available"
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        try:
            result = json.loads(text)
        except:
            result = extract_json(text)

        c1 = result.get("car1", {})
        c2 = result.get("car2", {})

        name1 = c1.get("model", car1) or car1
        name2 = c2.get("model", car2) or car2

        c1["image_url"] = get_car_image_url(name1)
        c2["image_url"] = get_car_image_url(name2)

        result["car1"] = c1
        result["car2"] = c2

        return jsonify({"status": "success", "data": result})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# --------------------------------------------------
# Run Server
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)