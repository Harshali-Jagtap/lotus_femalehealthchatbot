from transformers import T5ForConditionalGeneration, T5Tokenizer

class T5Simplifier:
    def __init__(self):
        model_name = "t5-small"
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

    def simplify(self, text):
        input_text = text  # Better prompt
        input_ids = self.tokenizer.encode(
            input_text,
            return_tensors="pt",
            max_length=1000,
            truncation=True
        )
        simplified_ids = self.model.generate(
            input_ids,
            max_length=1000,  # Increased from 150
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=2  # Prevent repetitive phrases
        )
        return self.tokenizer.decode(simplified_ids[0], skip_special_tokens=True)


if __name__ == "__main__":
    simplifier = T5Simplifier()
    test_text = "Hypertension is a cardiovascular condition characterized by elevated blood pressure."
    print(simplifier.simplify(test_text))  # Output: "High blood pressure is when your blood pushes too hard against your blood vessels."