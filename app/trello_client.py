import hashlib
import os
import requests
import hashlib


class TrelloClient:
    def __init__(self):
        self.key = os.getenv("TRELLO_KEY")
        self.token = os.getenv("TRELLO_TOKEN")
        self.list_id = os.getenv("TRELLO_LIST_ID")

    @staticmethod
    def generate_trello_color(project_name):
        colors = [
            "green",
            "yellow",
            "orange",
            "red",
            "purple",
            "blue",
            "sky",
            "lime",
            "pink",
            "black"
        ]

        hash_value = int(
            hashlib.md5(project_name.encode()).hexdigest(),
            16
        )

        return colors[hash_value % len(colors)]

    def create_card(self, name: str, desc: str, label_name: str = None):
        if not self.list_id or not self.key:
            return {"id": None}
        if label_name:
            label_id = self.create_or_get_label(label_name)
        url = "https://api.trello.com/1/cards"
        params = {"key": self.key, "token": self.token, "idList": self.list_id, "idLabels": [label_id] if label_id else [], "name": name, "desc": desc}
        try:
            r = requests.post(url, params=params)
            r.raise_for_status()
            card = r.json()
            return card
        except Exception as e:
            print(f"Error creating card: {e}")
            return {"id": None}
    
    def get_board_labels(self):
        """Get all labels from the board"""
        if not self.list_id or not self.key:
            return []
        try:
            # First, get the board ID from the list
            url = f"https://api.trello.com/1/lists/{self.list_id}"
            params = {"key": self.key, "token": self.token}
            r = requests.get(url, params=params)
            r.raise_for_status()
            list_data = r.json()
            board_id = list_data.get("idBoard")
            if not board_id:
                return []
            
            # Get all labels on the board
            url = f"https://api.trello.com/1/boards/{board_id}/labels"
            r = requests.get(url, params=params)
            r.raise_for_status()
            return r.json() or []
        except Exception as e:
            print(f"Error getting board labels: {e}")
            return []
    
    def create_or_get_label(self, label_name: str, color: str = ""):
        """Create a label or get existing one with the same name"""
        if not self.list_id or not self.key:
            return None
        
        try:
            # Get existing labels on the board
            labels = self.get_board_labels()
            for label in labels:
                if label.get("name", "").lower() == label_name.lower():
                    return label.get("id")
            
            # Create new label if it doesn't exist
            url = f"https://api.trello.com/1/labels"
            list_data = requests.get(f"https://api.trello.com/1/lists/{self.list_id}", 
                                    params={"key": self.key, "token": self.token}).json()
            board_id = list_data.get("idBoard")
            
            if not board_id:
                return None
            color = self.generate_trello_color(label_name) if not color else color
            params = {"key": self.key, "token": self.token, "idBoard": board_id, 
                      "name": label_name, "color": color}
            r = requests.post(url, params=params)
            r.raise_for_status()
            label_data = r.json()
            return label_data.get("id")
        except Exception as e:
            print(f"Error creating or getting label: {e}")
            return None
    
    def add_label_to_card(self, card_id: str, label_name: str):
        """Add a label to a card by name"""
        if not card_id or not label_name:
            return None
        
        try:
            label_id = self.create_or_get_label(label_name)
            if not label_id:
                return None
            
            # Use the correct endpoint to add label to card
            url = f"https://api.trello.com/1/cards/{card_id}/labels"
            data = {"value": label_id}
            params = {"key": self.key, "token": self.token}
            r = requests.post(url, params=params, json=data)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error adding label to card: {e}")
            return None

    def attach_file(self, card_id: str, file_path: str):
        if not card_id:
            return None
        url = f"https://api.trello.com/1/cards/{card_id}/attachments"
        params = {"key": self.key, "token": self.token}
        with open(file_path, "rb") as fh:
            files = {"file": fh}
            r = requests.post(url, params=params, files=files)
            try:
                return r.json()
            except Exception:
                return None
