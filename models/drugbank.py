import json
import os
import pandas as pd
from models.t5_summarizer import T5Simplifier


class DrugBank:
    def __init__(self, simplifier=None, data_dir="data"):
        self.data = None
        self.simplifier = simplifier  # T5Simplifier instance
        self.json_path = os.path.join(data_dir, "drugbank.json")
        self.drug_data = self.load_drugbank_data()

    def load_drugbank_data(self):
        """Load data from drugbank.json"""
        try:
            with open(self.json_path, "r") as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} drug entries from DrugBank.")
            return data
        except Exception as e:
            print(f"❌ Error loading DrugBank data: {e}")
            return None

    def search_drug_info(self, drug_name):
        """Search for drug and simplify its description"""
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
        """Get simplified drug details for layman"""
        if not self.drug_data:
            return "DrugBank data not available."

        drug = next((d for d in self.drug_data if d["name"].lower() == drug_name.lower()), None)

        if not drug:
            return None

        # Simplify medical jargon
        simplified = self.simplifier.simplify(drug["description"]) if self.simplifier else drug["description"]

        return (
            f"{drug['name']}:\n"
            f"- Purpose: {simplified}\n"
            f"- Categories: {drug['categories'] if drug['categories'] else 'Not specified'}"
        )