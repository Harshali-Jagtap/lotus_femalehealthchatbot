from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import torch
import logging

# Suppress transformers warnings
logging.getLogger("transformers").setLevel(logging.ERROR)
class ClinicalBERT:
    def __init__(self):
        model_path = "models_cache/clinicalbert"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        self.qa_pipeline = pipeline(
            "question-answering",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )

    def analyze_symptoms(self, symptoms):
        context = """
        Symptom management guide:
        - Dizziness: Sit down immediately, drink water, avoid sudden movements
        - Headache: Rest in dark room, use cold compress, take painkillers
        - Fever: Stay hydrated, use fever reducers, monitor temperature
        - Muscle aches: Gentle stretching, warm compress, over-the-counter pain relief
        """
        result = self.qa_pipeline(
            question=symptoms,
            context=context,
            max_answer_len=150  # Increased from 100
        )
        return result["answer"]

if __name__ == "__main__":
    clin = ClinicalBERT()
    text = "Patient reports fever, cough, and muscle aches."
    context = "Flu symptoms include fever, cough, sore throat, muscle aches, headaches, and fatigue."
    answer = clin.analyze_symptoms(text, context)
    print(f"ClinicalBERT Output: {answer}")
