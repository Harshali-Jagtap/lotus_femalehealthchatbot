# ===== BART Zero-Shot Classifier =====
from transformers import pipeline


class BARTClassifier:
    """
    Initialize the zero-shot classification pipeline using BART (MNLI model).
    """

    def __init__(self):
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        # Common keywords for quick early classification
        self.medical_terms = [
            "symptom", "pain", "fever", "cough", "medication",
            "treatment", "diagnosis", "disease", "infection",
            "medicine", "drug", "medical", "health",
            "pain", "illness", "vaccine", "doctor", "hospital", "treatment",
            "cold", "flu", "virus", "infection",
            "prescription", "dose", "blood", "heart", "cancer"
        ]

    def is_medical_query(self, text):
        """
        Determine if a user query is medical in nature.

        - First does a keyword check.
        - Then use BART zero-shot classification for ambiguous inputs.

        :param text: user query string
        :return: True if classified as medical inquiry
        """
        if any(term in text.lower() for term in self.medical_terms):
            return True

        # For uncertain cases, rely on a language model
        candidate_labels = ["medical inquiry", "general conversation"]
        result = self.classifier(text, candidate_labels)

        # Return True only if confidence is strong enough
        return result['labels'][0] == "medical inquiry" and result['scores'][0] > 0.65
