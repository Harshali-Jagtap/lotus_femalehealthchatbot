# ===== T5 Medical Text Simplifier =====
from transformers import T5ForConditionalGeneration, T5Tokenizer


class T5Simplifier:
    def __init__(self):
        """
        Load the T5-small model and tokenizer for text simplification tasks.
        """
        model_name = "t5-small"
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

    def simplify(self, text):
        """
        Simplify medical text using T5 for easier patient understanding.

        :param text: complex medical explanation
        :return: simplified, layman-friendly version
        """
        input_text = f"Simplify this medical text for a patient with no medical background: {text}"

        # Encode input for the model
        input_ids = self.tokenizer.encode(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )

        # Generate simplified output
        simplified_ids = self.model.generate(
            input_ids,
            max_length=200,  # Increased length
            num_beams=5,
            early_stopping=True,
            no_repeat_ngram_size=2,  # Reduced repetition
            temperature=0.7  # Added for more natural output
        )
        return self.tokenizer.decode(simplified_ids[0], skip_special_tokens=True)


# ===== Standalone Test Mode =====
if __name__ == "__main__":
    simplifier = T5Simplifier()
    test_text = "Hypertension is a cardiovascular condition characterized by elevated blood pressure."
    print(simplifier.simplify(
        test_text))