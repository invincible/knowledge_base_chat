import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class KnowledgeBase:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.vectorizer = TfidfVectorizer()
        self.initialize()

    def initialize(self):
        keywords = self.cursor.execute("SELECT keyword FROM keywords").fetchall()
        self.keywords = [k[0] for k in keywords]
        self.X = self.vectorizer.fit_transform(self.keywords)

    def find_similar(self, query, threshold=0.7, top_n=3):
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.X).flatten()
        results = []

        for idx in np.argsort(similarities)[-top_n:][::-1]:
            similarity_percentage = similarities[idx] * 100
            if similarity_percentage >= threshold * 100:
                node_id = self.cursor.execute("SELECT node_id FROM keywords WHERE keyword=?", (self.keywords[idx],)).fetchone()[0]
                node = self.cursor.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
                results.append({
                    "node_id": node[0],
                    "name": node[1],
                    "response": node[3],
                    "similarity": f"{similarity_percentage:.2f}%"
                })

        return results

    def get_transitions(self, node_id):
        transitions = self.cursor.execute("""
            SELECT t.to_node_id, COALESCE(t.button_text, n.name) as button_text
            FROM transitions t
            LEFT JOIN nodes n ON t.to_node_id = n.id
            WHERE t.from_node_id = ?
        """, (node_id,)).fetchall()
        return transitions

    def get_node(self, node_id):
        return self.cursor.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()