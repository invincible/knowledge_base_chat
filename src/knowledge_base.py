import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class KnowledgeBase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.vectorizer = TfidfVectorizer()
        self.keywords = []
        self.X = None
        self.connect()
        self.initialize()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def initialize(self):
        try:
            keywords = self.cursor.execute("SELECT keyword FROM keywords").fetchall()
            self.keywords = [k[0].lower() for k in keywords]
            self.X = self.vectorizer.fit_transform(self.keywords)
        except sqlite3.Error as e:
            print(f"An error occurred during initialization: {e}")

    def find_similar(self, query, threshold=0.4, top_n=4):
        query_vec = self.vectorizer.transform([query.lower()])
        similarities = cosine_similarity(query_vec, self.X).flatten()
        results = []

        for idx in np.argsort(similarities)[-top_n:][::-1]:
            similarity_percentage = similarities[idx] * 100
            if similarity_percentage >= threshold * 100:
                try:
                    node_id = self.cursor.execute("SELECT node_id FROM keywords WHERE LOWER(keyword)=?", (self.keywords[idx],)).fetchone()[0]
                    node = self.cursor.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
                    results.append({
                        "node_id": node[0],
                        "name": node[1],
                        "response": node[3],
                        "similarity": f"{similarity_percentage:.2f}%"
                    })
                except sqlite3.Error as e:
                    print(f"An error occurred while fetching similar nodes: {e}")

        return results

    def get_transitions(self, node_id):
        try:
            transitions = self.cursor.execute("""
                SELECT t.to_node_id, COALESCE(t.button_text, n.name) as button_text
                FROM transitions t
                LEFT JOIN nodes n ON t.to_node_id = n.id
                WHERE t.from_node_id = ?
            """, (node_id,)).fetchall()
            return transitions
        except sqlite3.Error as e:
            print(f"An error occurred while fetching transitions: {e}")
            return []

    def get_node(self, node_id):
        try:
            return self.cursor.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
        except sqlite3.Error as e:
            print(f"An error occurred while fetching node: {e}")
            return None

    def get_parent_id(self, node_id):
        try:
            parent = self.cursor.execute("SELECT parent_id FROM nodes WHERE id=?", (node_id,)).fetchone()
            return parent[0] if parent else None
        except sqlite3.Error as e:
            print(f"An error occurred while fetching parent id: {e}")
            return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()