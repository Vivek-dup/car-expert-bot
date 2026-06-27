# 🚗 Car Expert Bot

An AI-powered car expert web app for the **Indian car market** — search car specs, compare models, and find cars within your budget.

Built with **Flask + Google Gemini AI + Unsplash API**.

---

## 📸 Features

- 🔍 **Car Info** — Search any car and get engine, mileage, price variants, comfort and features
- ⚖️ **Compare Cars** — Compare two cars side by side with AI verdict
- 💰 **Budget Finder** — Find the best cars under your budget with a slider

---

## 🛠️ Tech Stack

- **Backend** — Python, Flask
- **AI** — Google Gemini 2.5 Flash
- **Images** — Unsplash API
- **Frontend** — HTML, CSS, JavaScript

---

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/Vivek-dup/car-expert-bot.git
cd car-expert-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get your API keys

#### 🔑 Google Gemini API Key
1. Go to **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key

#### 🔑 Unsplash API Key
1. Go to **https://unsplash.com/developers**
2. Click **Register as a developer**
3. Click **New Application**
4. Fill in the details and accept terms
5. Scroll down to **Keys** section
6. Copy the **Access Key**

### 4. Add your API keys

Open `app.py` and add your keys here:

```python
API_KEY = "your_gemini_api_key_here"
UNSPLASH_ACCESS_KEY = "your_unsplash_access_key_here"
```

### 5. Run the app
```bash
python app.py
```

Open your browser and go to **http://localhost:5000**

---

## 📁 Project Structure

```
car-expert-bot/
│
├── app.py                  # Flask backend
├── index.html              # Frontend UI
├── static/
│   ├── requirements.txt    # Python dependencies
│   └── knowledge_base.json
└── README.md
```

---

## 📦 Requirements

```
flask
flask-cors
google-generativeai
requests
```

---

## ⚠️ Important Note

Never share your API keys publicly. Keep them private and never push them to GitHub.

---

## 🙌 Credits

- [Google Gemini](https://aistudio.google.com/) — AI model
- [Unsplash](https://unsplash.com/) — Car images
