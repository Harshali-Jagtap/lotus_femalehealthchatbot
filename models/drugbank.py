# ===== Drug Bank Dataset (Json file) =====
import json
import os


class DrugBank:
    """
    Initialize DrugBank handler.

    :param simplifier: Optional simplifier (e.g., T5) to make drug descriptions easier to understand
    :param data_dir: Directory where drugbank.json is stored
    """

    def __init__(self, simplifier=None, data_dir="data"):
        self.data = None
        self.simplifier = simplifier  # T5Simplifier instance
        self.json_path = os.path.join(data_dir, "drugbank.json")
        self.drug_data = self.load_drugbank_data()

    def load_drugbank_data(self):
        """
        Load DrugBank data from JSON file
        :return: List of drug records or None on failure
        """
        try:
            with open(self.json_path, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading DrugBank data: {e}")
            return None

    def search_drug_info(self, drug_name):
        """
        Search for partial matches of a drug name and optionally simplify descriptions.

        :param drug_name: Drug name or partial term to look for
        :return: List of matching drugs with simplified descriptions
        """

        if not self.drug_data:
            return "DrugBank data not available."

        matches = [drug for drug in self.drug_data if drug_name.lower() in drug["name"].lower()]

        if not matches:
            return None

        # Simplify descriptions
        for drug in matches:
            if self.simplifier and drug["description"]:
                drug["simple_desc"] = self.simplifier.simplify(drug["description"])
            else:
                drug["simple_desc"] = drug["description"]

        return matches

    def get_drug_details(self, drug_name):
        """
        Return a formatted string of a drug's purpose and category, with optional simplification.

        Filters out clearly invalid/multi-word terms.

        :param drug_name: Exact name of the drug
        :return: Cleaned string response or None if not found
        """

        if not self.drug_data:
            return "DrugBank data not available."

        # Strict filtering: reject multi-word queries that are clearly not a drug name
        if len(drug_name.strip().split()) > 2 or any(term in drug_name.lower() for term in [
            "for", "to", "help", "medicine", "relief", "symptom", "pain", "treatment", "how", "what"
        ]):
            return None

        # Try to match drug name exactly
        drug = next((d for d in self.drug_data if d["name"].lower() == drug_name.lower()), None)
        if not drug:
            return None

        simplified = self.simplifier.simplify(drug["description"]) if self.simplifier else drug["description"]

        return (
            f"{drug['name']}:\n"
            f"- Purpose: {simplified}\n"
            f"- Categories: {drug['categories'] if drug['categories'] else 'Not specified'}"
        )