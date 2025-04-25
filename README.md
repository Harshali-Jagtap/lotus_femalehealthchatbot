
# 🌸 Lotus – Female Health Chatbot

## 📖 Overview
Lotus is an AI-powered, privacy-first health chatbot built to support women’s healthcare needs, offering personalized medical advice, mental health support, and symptom checking.  
It leverages cutting-edge NLP models such as BioBERT, ClinicalBERT, T5 Summarizer, and BART Classifier, while ensuring strong privacy protection and a user-friendly experience.

## 🚀 Key Features
- ✅ Medical Query Understanding via BioBERT and ClinicalBERT
- ✅ Symptom Checker with immediate, research-backed advice
- ✅ Mental Health Support: breathing exercises, mindfulness routines, affirmations
- ✅ Mood Tracker with daily mood analysis and visual dashboards
- ✅ Fallback System: DrugBank → MedQuad → BERT models → OpenAI GPT
- ✅ Dynamic Follow-Up Prevention for non-medical queries
- ✅ Secure Authentication (JWT-based login and reset via Mailtrap)
- ✅ GDPR-Compliant Data Privacy

## 🏗️ System Structure
| Directory/Component | Purpose |
|----------------------|---------|
| /datat/           | Json Files (DrugBank, MedQuad, Mental Health, Prompt Responses) |
| /models/           | AI Models (BioBERT, ClinicalBERT, BART Classifier, T5 Summarizer) |
| /routes/           | Flask routes (auth, chatbot, dashboard, mental health) |
| /security/        | Database connection |
| /templates/        | Frontend HTML pages |
| /static/           | CSS and JavaScript assets |
| main.py            | Flask application runner |
| .env               | Environment variables for configuration |

## 🛠 Installation Guide
1. Clone the repository:
   ```bash
   git clone https://github.com/Harshali-Jagtap/lotus_femalehealthchatbot.git
   cd lotus-female-health-chatbot
   ```
   Or Simply download it!

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # (Mac/Linux)
   venv\Scripts\activate     # (Windows)
   ```

3. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   - Create a `.env` file and set:
     ```
     FLASK_APP=main.py
     FLASK_ENV=development
     SECRET_KEY=your_secret_key
     OPENAI_API_KEY=your_openai_key
     DATABASE_NAME=your_databasename
     MAIL_USERNAME=your_mailtrap_username
     MAIL_PASSWORD=your_mailtrap_password
     MAIL_SERVER=smtp.mailtrap.io
     MAIL_PORT=2525
     MAIL_USE_TLS=True
     MAIL_DEFAULT_SENDER=mailtrap_email@inbox.mailtrap.io
     ```

5. Run the application:
   ```bash
   flask run
   ```

## ⚙️ Configuration Notes
- Create your own Mailtrap account for SMTP testing.
- Setup MongoDB Atlas for secure cloud database hosting.

## ⚠️ Common Errors & Solutions

### ❌ ImportError: cannot import name 'ExpiredSignatureError' from 'jwt'
**Solution:**
```python
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
```
Ensure PyJWT is updated:
```bash
pip install --upgrade PyJWT
```

### ❌ ImportError: T5Tokenizer requires the SentencePiece library
**Solution:**
```bash
pip install sentencepiece
```

## 🔐 Security Features
- JWT Authentication
- MongoDB Encryption
- GDPR-compliant data handling
- Secure API key management

## 🧪 Testing
- Unit, Integration, and UAT Testing completed.
- Security vulnerabilities mitigated.
- Load testing with concurrent user sessions successful.

## 📈 Future Enhancements
- Multilingual support (Spanish, Hindi, Arabic)
- Real-time voice input (Speech-to-Text)
- Telehealth appointment scheduling

## 🙏 Acknowledgements
- Supervisor: Oliver Hyde (TUS)
- Libraries Used: Huggingface Transformers, Flask, MongoDB Atlas, Chart.js

---

# 🚀 Thank You for Exploring Lotus!

## Copyright (c) 2025 Harshali Jagtap
