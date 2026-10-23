"""Knowledge base retrieval engine with keyword & semantic matching."""

import json
from pathlib import Path
from typing import Any, Dict, List

class KnowledgeBaseEngine:
    """Manages searching and retrieving approved corporate knowledge articles."""

    def __init__(self, kb_path: str = None):
        if not kb_path:
            kb_path = str(Path(__file__).parent / "articles.json")
        self.kb_path = kb_path
        self.articles = self._load_articles()

    def _load_articles(self) -> List[Dict[str, Any]]:
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def search(self, query: str, category: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Finds most relevant knowledge base articles matching the inquiry."""
        tokens = set(query.lower().split())
        scored: List[tuple[int, Dict[str, Any]]] = []

        for article in self.articles:
            score = 0
            if category and article.get("category") == category:
                score += 5

            for kw in article.get("keywords", []):
                if kw.lower() in query.lower():
                    score += 4

            article_tokens = set(f"{article['title']} {article['content']}".lower().split())
            overlap = len(tokens.intersection(article_tokens))
            score += overlap

            if score > 0:
                scored.append((score, article))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]
