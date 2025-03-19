from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import torch
import logging

# Suppress transformers warnings
logging.getLogger("transformers").setLevel(logging.ERROR)

class BioBERT:
    def __init__(self):
        model_path = "models_cache/biobert"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        self.qa_pipeline = pipeline(
            "question-answering",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )

    def answer_question(self, question):
        context = """
        Simplified medical facts:
        - Hypertension: High blood pressure. Normal: <120/80 mmHg. Treat with diet/exercise/medication
        - Antibiotics: Fight bacterial infections. Common side effects: nausea, diarrhea, rash
        - Paracetamol: Pain/fever relief. Max dose: 4000mg/day. Avoid alcohol
        - COVID-19: Spreads through air. Prevention: masks, vaccination, hand hygiene
        """
        result = self.qa_pipeline(
            question=question,
            context=context,
            max_answer_len=150  # Increased from 100
        )
        return result["answer"]


if __name__ == "__main__":
    bio = BioBERT()
    question = "How does COVID-19 spread?"
    context = "COVID-19 spreads through respiratory droplets from infected individuals."
    answer = bio.answer_question(question, context)
    print(f"BioBERT Output: {answer}")
