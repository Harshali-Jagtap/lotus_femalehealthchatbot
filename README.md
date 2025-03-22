# lotus_femalehealthchatbot
Lotus - Female Health Chatbot 

🔐 Environment Variables Setup (.env)
To run this project, you need to create a .env file in the root of your project with the following contents:

```text 
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
```
ℹ️ Details:
SECRET_KEY: Used by Flask to manage sessions securely. You can generate one using:

```text
python -c "import secrets; print(secrets.token_hex(16))"
OPENAI_API_KEY: This is required for the chatbot’s integration with OpenAI.
```

👉 You can generate your own API key by logging into https://platform.openai.com/account/api-keys

⚠️ Do not share your .env file publicly. Instead, include a .env.example file in your repo for guidance.

## 🧠 Model Setup Instructions

This project uses the following pre-trained models from Hugging Face:

- BioBERT: [dmis-lab/biobert-base-cased-v1.1](https://huggingface.co/dmis-lab/biobert-base-cased-v1.1)
- ClinicalBERT: [emilyalsentzer/Bio_ClinicalBERT](https://huggingface.co/emilyalsentzer/Bio_ClinicalBERT)

To download them automatically, the code uses:

```python
from transformers import AutoModel, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
model = AutoModel.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
```

Run the following commands in a separate Python script:

```python
from transformers import AutoModelForQuestionAnswering, AutoTokenizer

model_path = "models_cache/biobert"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForQuestionAnswering.from_pretrained(model_path)
print("✅ BioBERT Model Loaded Successfully!")

model_path = "models_cache/clinicalbert"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForQuestionAnswering.from_pretrained(model_path)
print("✅ ClinicalBERT Model Loaded Successfully!")
```

If it throws an error, download the correct models:
# Run this in terminal or command prompt

```bash
mkdir -p models_cache
cd models_cache
git clone https://huggingface.co/dmis-lab/biobert-base-cased-v1.1 biobert
git clone https://huggingface.co/emilyalsentzer/Bio_ClinicalBERT clinicalbert
```
This ensures you have the right models.
These files will be saved in models_cache folder.
