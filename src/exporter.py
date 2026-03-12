import pandas as pd
import os
from typing import List, Dict

class Exporter:
    @staticmethod
    def to_csv(data: List[Dict], filename: str = "leads.csv"):
        """
        Exports list of dictionaries to a CSV file using Pandas.
        """
        if not data:
            print("[!] No data to export.")
            return
            
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"[√] Successfully exported {len(data)} leads to {filename}")

    @staticmethod
    def to_json(data: List[Dict], filename: str = "leads.json"):
        """
        Exports list of dictionaries to a JSON file.
        """
        if not data:
            return
            
        df = pd.DataFrame(data)
        df.to_json(filename, orient="records", indent=4)
        print(f"[√] Successfully exported {len(data)} leads to {filename}")
        
    @staticmethod
    def ensure_dir(path: str):
        if not os.path.exists(os.path.dirname(path)) and os.path.dirname(path):
            os.makedirs(os.path.dirname(path))
