"""
X (Twitter) API Integration via Tweepy.

Requires:
- X_CONSUMER_KEY
- X_CONSUMER_SECRET
- X_ACCESS_TOKEN
- X_ACCESS_TOKEN_SECRET
- X_BEARER_TOKEN (optional)
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class XApiError(RuntimeError):
    pass

def post_tweet(text: str) -> dict:
    """
    Posts a single tweet to X.
    If MOCK_X_API=1, generates a fake success response.
    """
    if os.getenv("MOCK_X_API") == "1":
        logger.info("[MOCK X API] Posting tweet: %s", text)
        return {"provider": "x", "status": "mock_success", "tweet_id": "mock_1234567890", "mock": True}

    try:
        import tweepy
        
        consumer_key = os.getenv("X_CONSUMER_KEY")
        consumer_secret = os.getenv("X_CONSUMER_SECRET")
        access_token = os.getenv("X_ACCESS_TOKEN")
        access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise XApiError("Missing X API credentials (CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)")

        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        response = client.create_tweet(text=text)
        
        logger.info("Social post successfully live on X. Tweet ID: %s", response.data['id'])
        return {
            "provider": "x",
            "status": "success",
            "tweet_id": response.data['id'],
            "text": text
        }
        
    except ImportError:
        logger.error("tweepy library not installed")
        raise XApiError("tweepy library is missing. Run pip install tweepy")
    except Exception as e:
        logger.exception("X API post failed")
        raise XApiError(str(e))
