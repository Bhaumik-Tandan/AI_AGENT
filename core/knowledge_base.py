from typing import List, Dict, Any, Optional
import sqlite3
import json
from openai import OpenAI

client = OpenAI()
from config.settings import EMBEDDING_MODEL, VECTOR_SIMILARITY_THRESHOLD

class KnowledgeBase:
    def __init__(self, db_path: str = 'knowledge.db'):
        self.conn = sqlite3.connect(db_path)
        self.setup_database()

    def setup_database(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS collected_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                value TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    def add_knowledge(self, category: str, content: str, metadata: Optional[Dict] = None) -> int:
        embedding = self._generate_embedding(content)
        cursor = self.conn.execute(
            "INSERT INTO knowledge_entries (category, content, embedding, metadata) VALUES (?, ?, ?, ?)",
            (category, content, json.dumps(embedding), json.dumps(metadata or {}))
        )
        self.conn.commit()
        return cursor.lastrowid

    def query_knowledge(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        query_embedding = self._generate_embedding(query)

        sql = """
            SELECT category, content, metadata 
            FROM knowledge_entries 
            WHERE category = COALESCE(?, category)
        """

        cursor = self.conn.execute(sql, (category,))
        results = []

        for row in cursor.fetchall():
            stored_embedding = json.loads(row[2])
            similarity = self._calculate_similarity(query_embedding, stored_embedding)

            if similarity >= VECTOR_SIMILARITY_THRESHOLD:
                results.append({
                    "category": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[3]),
                    "relevance": similarity
                })

        return sorted(results, key=lambda x: x["relevance"], reverse=True)

    def save_collected_data(self, user_id: str, field_name: str, value: str, agent_id: str):
        self.conn.execute(
            "INSERT INTO collected_data (user_id, field_name, value, agent_id) VALUES (?, ?, ?, ?)",
            (user_id, field_name, value, agent_id)
        )
        self.conn.commit()

    def get_collected_data(self, user_id: str, agent_id: str) -> Dict[str, str]:
        cursor = self.conn.execute(
            "SELECT field_name, value FROM collected_data WHERE user_id = ? AND agent_id = ?",
            (user_id, agent_id)
        )
        return {row[0]: row[1] for row in cursor.fetchall()}

    def _generate_embedding(self, text: str) -> List[float]:
        response = client.embeddings.create(input=text,
        model=EMBEDDING_MODEL)
        return response.data[0].embedding

    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        # Implement cosine similarity calculation
        # This is a simplified version - you might want to use numpy for better performance
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5
        return dot_product / (magnitude1 * magnitude2)

    def close(self):
        self.conn.close()