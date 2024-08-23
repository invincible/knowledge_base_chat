import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from flask import g

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('../data/dialog.db')
    return db

class KnowledgeBase:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.initialize()

    def initialize(self):
        with get_db() as conn:
            cursor = conn.cursor()
            keywords = cursor.execute("SELECT keyword FROM keywords").fetchall()
        self.keywords = [k[0].lower() for k in keywords]
        self.X = self.vectorizer.fit_transform(self.keywords)

    def find_similar(self, query, threshold=0.4, top_n=4):
        query_vec = self.vectorizer.transform([query.lower()])
        similarities = cosine_similarity(query_vec, self.X).flatten()
        results = []

        for idx in np.argsort(similarities)[-top_n:][::-1]:
            similarity_percentage = similarities[idx] * 100
            if similarity_percentage >= threshold * 100:
                with get_db() as conn:
                    cursor = conn.cursor()
                    node_id = cursor.execute("SELECT node_id FROM keywords WHERE LOWER(keyword)=?", (self.keywords[idx],)).fetchone()[0]
                    node = cursor.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
                results.append({
                    "node_id": node[0],
                    "name": node[1],
                    "response": node[3],
                    "similarity": f"{similarity_percentage:.2f}%"
                })

        return results

    def get_transitions(self, node_id):
        with get_db() as conn:
            cursor = conn.cursor()
            transitions = cursor.execute("""
                SELECT t.to_node_id, COALESCE(t.button_text, n.name) as button_text
                FROM transitions t
                LEFT JOIN nodes n ON t.to_node_id = n.id
                WHERE t.from_node_id = ?
            """, (node_id,)).fetchall()
        return transitions

    def get_node(self, node_id):
        with get_db() as conn:
            cursor = conn.cursor()
            return cursor.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()

    def get_all_nodes(self):
        with get_db() as conn:
            cursor = conn.cursor()
            nodes = cursor.execute("SELECT id, name, parent_id, response FROM nodes").fetchall()
        return [{'id': node[0], 'name': node[1], 'parent_id': node[2], 'response': node[3]} for node in nodes]

    def update_node(self, node_id, new_data):
        with get_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE nodes SET name = ?, response = ? WHERE id = ?",
                               (new_data['name'], new_data['response'], node_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error updating node: {e}")
                return False

    def get_parent_id(self, node_id):
        with get_db() as conn:
            cursor = conn.cursor()
            parent = cursor.execute("SELECT parent_id FROM nodes WHERE id=?", (node_id,)).fetchone()
        return parent[0] if parent else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()