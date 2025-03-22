# lotus_femalehealthchatbot
Lotus - Female Health Chatbot 

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
These files will be saved in models_cache folder.