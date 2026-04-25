import httpx
import logging
from typing import List, Dict, Any, Optional
from core.config import get_settings

logger = logging.getLogger(__name__)

class SearchService:
    @staticmethod
    def search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        settings = get_settings()
        api_key = settings.tavily_api_key

        if not api_key:
            logger.warning("TAVILY_API_KEY missing. Returning mock search results.")
            return SearchService._mock_search(query)

        try:
            # Using Tavily API via httpx
            # Documentation: https://docs.tavily.com/docs/tavily-api/introduction
            response = httpx.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "smart",
                    "max_results": max_results
                },
                timeout=20.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error(f"Tavily search failed for query '{query}': {e}")
            return SearchService._mock_search(query)

    @staticmethod
    def _mock_search(query: str) -> List[Dict[str, Any]]:
        """Fallback for local dev without API keys."""
        return [
            {
                "title": f"Mock Competitor for {query}",
                "url": "https://example-competitor.com",
                "content": "This is a simulated search result for testing purposes. In a production environment with a valid API key, real-time market data would be fetched here.",
                "score": 0.99
            }
        ]
