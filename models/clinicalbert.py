# ===== ClinicalBERT Symptom Analysis Module =====
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import torch
import logging

# Suppress warnings
logging.getLogger("transformers").setLevel(logging.ERROR)


class ClinicalBERT:
    """
    Load the ClinicalBERT model for medical question-answering.
    Uses GPU if available, otherwise falls back to CPU.
    """

    def __init__(self):
        model_path = "emilyalsentzer/Bio_ClinicalBERT"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        self.qa_pipeline = pipeline("question-answering", model=self.model, tokenizer=self.tokenizer,
                                    device=0 if torch.cuda.is_available() else -1)

    def analyze_symptoms(self, symptoms):
        """
        Given a symptom description (question), return advice using a built-in clinical context.

        :param symptoms: user symptom query (string)
        :return: relevant answer string
        """
        context = """
        - Headache: Rest in a quiet, dark room. Use a cold compress on your forehead and take pain relievers like ibuprofen or paracetamol.
        - Fever: Stay hydrated, rest, and take fever-reducing medicine like paracetamol.
        - Muscle pain: Gentle stretching, warm compress, or over-the-counter pain relievers.
        - Nausea: Eat light meals, sip water or ginger tea, avoid strong smells.
        - Dizziness: Sit down immediately, breathe slowly, and drink water.
        """

        result = self.qa_pipeline(question=symptoms, context=context)
        return result["answer"]


# ===== Standalone Test Mode =====
if __name__ == "__main__":
    clin = ClinicalBERT()
    text = "Patient reports fever, cough, and muscle aches."
    context = "Flu symptoms include fever, cough, sore throat, muscle aches, headaches, and fatigue."
    answer = clin.analyze_symptoms(text, context)
    print(f"ClinicalBERT Output: {answer}")
