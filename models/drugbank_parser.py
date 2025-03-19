import pandas as pd
import os


class DrugBankParser:
    def __init__(self, filepath="data/drugbank.json"):
        """Load the DrugBank dataset"""
        self.data = None
        self.drugbank_file = os.path.join("data", "drugbank.json")
        self.drug_data = self.load_drugbank_data()
        try:
            self.data = pd.read_csv(filepath, sep='\t')
        except Exception as e:
            print(f"❌ Error loading DrugBank data: {e}")

            self.data = None

    def load_drugbank_data(self):
        """Read DrugBank TSV file into a pandas DataFrame"""
        try:
            df = pd.read_csv(self.drugbank_file, sep="\t")
            return df
        except Exception as e:
            print(f"❌ Error loading DrugBank data: {e}")
            return None

    # Search for a drug in the dataset
    def search_drug_info(self, drug_name):
        if self.drug_data is None:
            return "DrugBank data not available."

        result = self.drug_data[self.drug_data["name"].str.contains(drug_name, case=False, na=False)]
        if not result.empty:
            return result.to_dict(orient="records")
        return None

    def get_drug_details(self, drug_name):
        """CORRECTED VERSION WITHOUT SIMPLIFIER"""
        if self.drug_data is None:
            return "DrugBank data not available."

        try:
            result = self.drug_data[self.drug_data["name"].str.contains(drug_name, case=False, na=False)]
            if result.empty:
                return None

            drug_info = result.iloc[0]
            return f"{drug_name}: {drug_info.get('description', 'No description')}. Side effects: {drug_info.get('side_effects', 'None listed')}"

        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def get_side_effects(self, drug_name):
            """Fetch side effects (if available)"""
            if self.drug_data is None:
                return "DrugBank data is not loaded."

            drug_info = self.drug_data[self.drug_data["name"].str.contains(drug_name, case=False, na=False)]
            if not drug_info.empty:
                result = drug_info.iloc[0]
                return f"Side effects of {drug_name}: {result.get('side_effects', 'No side effects listed.')}"
            else:
                return f"No side effects found for {drug_name}."
