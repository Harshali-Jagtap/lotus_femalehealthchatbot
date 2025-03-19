import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MedQuAD:
    def __init__(self):
        self.medquad_data = []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.load_medquad_data()

    def load_medquad_data(self):
        medquad_file = os.path.join("data", "medquad.json")
        with open(medquad_file, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
        self.medquad_data = [{
            "question": entry["question"].strip(),
            "answer": " ".join(entry["answer"].split())  # Remove newlines
        } for entry in raw_data if entry.get("answer")]

    def search_medquad(self, question):
        questions = [entry["question"] for entry in self.medquad_data]
        tfidf_matrix = self.vectorizer.fit_transform(questions)
        user_vec = self.vectorizer.transform([question])
        similarities = cosine_similarity(user_vec, tfidf_matrix)
        max_idx = similarities.argmax()
        return self.medquad_data[max_idx]["answer"] if similarities[0, max_idx] > 0.2 else None  # Changed to 0.2


# ✅ Test the updated MedQuAD
if __name__ == "__main__":
    medquad = MedQuAD()
    test_question = "ibuprofen"  # Testing with a general keyword
    found = False

    for entry in medquad.medquad_data:
        if test_question.lower() in entry["question"].lower():
            print(f"✅ Match Found: {entry['question']}")
            print(f"💡 Answer: {entry['answer']}")
            found = True
            break

    if not found:
        print(f"❌ No match found for '{test_question}' in MedQuAD.")
