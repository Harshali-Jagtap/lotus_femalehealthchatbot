# ===== MedQuad Dataset (Json File) =====

import json
import os, re
from sklearn.feature_extraction.text import TfidfVectorizer


class MedQuAD:
    def __init__(self):
        """ Initialize MedQuAD with an internal TF-IDF vectorizer and load data. """

        self.medquad_data = []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.load_medquad_data()

    def load_medquad_data(self):
        """
        Load and preprocess MedQuAD data from JSON.
        Each entry includes a 'question' and 'answer' field.
        """

        medquad_file = os.path.join("data", "medquad.json")
        with open(medquad_file, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
        self.medquad_data = [{
            "question": entry["question"].strip(),
            "answer": " ".join(entry["answer"].split())  # Remove newlines
        } for entry in raw_data if entry.get("answer")]

    def search_medquad(self, question):
        """
        Search for a semantically relevant MedQuAD Q&A based on keyword overlap and answer matching.

        :param question: user input
        :return: best matching answer or None
        """
        if not self.medquad_data:
            return None

        question_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', question.lower()))
        best_match = None
        max_overlap = 0

        for entry in self.medquad_data:
            q_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', entry["question"].lower()))
            overlap = len(question_words & q_words)

            if overlap > max_overlap:
                max_overlap = overlap
                best_match = entry

        if best_match and max_overlap >= 2:
            stop_words = {
                "what", "are", "the", "and", "with", "that", "have", "you", "for", "from",
                "how", "does", "why", "can", "will", "which", "in", "on", "to", "of", "is", "a", "an"
            }
            topic_terms = [word for word in question.lower().split() if word not in stop_words]

            answer_text = best_match["answer"].lower()
            question_text = best_match["question"].lower()

            match_count = sum(1 for word in topic_terms if word in answer_text or word in question_text)

            if match_count >= max(1, len(topic_terms) // 2):
                # Extra strict: if a user asks about "medicine" or "drug", answer must mention common treatments
                if any(term in question.lower() for term in ["medicine", "medication", "drug", "treatment"]):
                    if not any(kw in answer_text for kw in
                               ["paracetamol", "ibuprofen", "acetaminophen", "antibiotic", "pain reliever", "NSAID"]):
                        print("MedQuAD: no real medicine mentioned despite medical question. Skipping.")
                        return None
                return best_match["answer"]
            else:
                print("MedQuAD: topic terms not found in answer. Skipping.")
                return None

        return None


# ===== Standalone Test =====
if __name__ == "__main__":
    medquad = MedQuAD()
    test_question = "ibuprofen"  # Testing with a general keyword
    found = False

    for entry in medquad.medquad_data:
        if test_question.lower() in entry["question"].lower():
            print(f"Match Found: {entry['question']}")
            print(f"Answer: {entry['answer']}")
            found = True
            break

    if not found:
        print(f"No match found for '{test_question}' in MedQuAD.")