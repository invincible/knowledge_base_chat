import sqlite3
import re
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
        logger.info(f"Initialized KnowledgeBase with database: {db_path}")

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY,
                node_type TEXT,
                question TEXT,
                answer TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transitions (
                id INTEGER PRIMARY KEY,
                from_node_id INTEGER,
                to_node_id INTEGER,
                condition TEXT,
                FOREIGN KEY (from_node_id) REFERENCES nodes (id),
                FOREIGN KEY (to_node_id) REFERENCES nodes (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS buttons (
                id INTEGER PRIMARY KEY,
                node_id INTEGER,
                button_text TEXT,
                FOREIGN KEY (node_id) REFERENCES nodes (id)
            )
        ''')
        self.conn.commit()

    def get_node(self, node_id):
        self.cursor.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
        return self.cursor.fetchone()

    def get_transitions(self, node_id):
        self.cursor.execute("SELECT * FROM transitions WHERE from_node_id = ?", (node_id,))
        return self.cursor.fetchall()

    def get_buttons(self, node_id):
        self.cursor.execute("SELECT button_text FROM buttons WHERE node_id = ?", (node_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def add_node(self, node_type, question, answer):
        self.cursor.execute(
            "INSERT INTO nodes (node_type, question, answer) VALUES (?, ?, ?)",
            (node_type, question, answer)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def add_transition(self, from_node_id, to_node_id, condition):
        self.cursor.execute(
            "INSERT INTO transitions (from_node_id, to_node_id, condition) VALUES (?, ?, ?)",
            (from_node_id, to_node_id, condition)
        )
        self.conn.commit()

    def add_button(self, node_id, button_text):
        self.cursor.execute(
            "INSERT INTO buttons (node_id, button_text) VALUES (?, ?)",
            (node_id, button_text)
        )
        self.conn.commit()

    def search_nodes(self, query):
        logger.debug(f"Searching for nodes with query: {query}")
        clean_query = re.sub(r'[^\w\s]', '', query.lower())
        words = clean_query.split()

        condition = " OR ".join([f"LOWER(question) LIKE ? OR LOWER(answer) LIKE ?" for _ in words])
        params = [f"%{word}%" for word in words for _ in range(2)]

        self.cursor.execute(f"""
            SELECT id, node_type, question, answer 
            FROM nodes 
            WHERE {condition}
        """, params)
        results = self.cursor.fetchall()
        logger.debug(f"Found nodes: {results}")
        return results

    def get_node_by_button(self, button_text):
        logger.debug(f"Searching for node with button text: {button_text}")
        self.cursor.execute("""
            SELECT n.id, n.node_type, n.question, n.answer
            FROM nodes n
            JOIN transitions t ON n.id = t.to_node_id
            WHERE LOWER(t.condition) = LOWER(?)
        """, (button_text,))
        result = self.cursor.fetchone()
        logger.debug(f"Found node: {result}")
        return result

    def print_all_data(self):
        logger.debug("Printing all data from the database")
        self.cursor.execute("SELECT * FROM nodes")
        logger.debug(f"Nodes: {self.cursor.fetchall()}")
        self.cursor.execute("SELECT * FROM transitions")
        logger.debug(f"Transitions: {self.cursor.fetchall()}")
        self.cursor.execute("SELECT * FROM buttons")
        logger.debug(f"Buttons: {self.cursor.fetchall()}")

    def clear_database(self):
        logger.info("Clearing the database")
        self.cursor.execute("DELETE FROM nodes")
        self.cursor.execute("DELETE FROM transitions")
        self.cursor.execute("DELETE FROM buttons")
        self.conn.commit()

    def close(self):
        self.conn.close()