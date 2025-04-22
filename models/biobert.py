# ===== BioBERT Medical Question Answering Wrapper =====
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import torch
import logging

# Suppress transformer loading warnings
logging.getLogger("transformers").setLevel(logging.ERROR)


class BioBERT:
    """
    Load BioBERT pretrained on PubMed and fine-tuned on SQuAD2.0.
    Sets up a QA pipeline with GPU support if available.
    """

    def __init__(self):
        model_path = "ktrapeznikov/biobert_v1.1_pubmed_squad_v2"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        self.qa_pipeline = pipeline("question-answering", model=self.model, tokenizer=self.tokenizer,
                                    device=0 if torch.cuda.is_available() else -1)

    def answer_question(self, question):
        """
        Answer a medical question using a built-in simplified context.

        :param question: user input question
        :return: answer string extracted from context
        """
        context = """

        - Hypertension: High blood pressure. Treat with diet/exercise.
        - Diabetes: High blood sugar. Managed by insulin, exercise.
        - Paracetamol: Pain reliever. Max 4g/day. Avoid alcohol.
        - Antibiotics: Treat bacterial infections. Side effects: nausea, diarrhea.
        - COVID-19: Spreads by air. Prevent with masks, vaccines, handwashing.
        """
        result = self.qa_pipeline(question=question, context=context)
        return result["answer"]


# ===== Standalone Test Mode =====
if __name__ == "__main__":
    bio = BioBERT()
    question = "How does COVID-19 spread?"
    context = "COVID-19 spreads through respiratory droplets from infected individuals."
    answer = bio.answer_question(question, context)
    print(f"BioBERT Output: {answer}")
