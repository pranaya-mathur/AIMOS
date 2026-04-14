from typing import List, Optional
from services.integrations.openai_service import generate_json

def score_lead_intent(conversation_history: List[dict]) -> dict:
    """
    Analyzes conversation history to determine lead intent, sentiment, and score.
    Returns: { "score": int, "intent": str, "sentiment": str, "reasoning": str }
    """
    prompt = f"""
    You are an AI Lead Qualification Agent for AIMOS Enterprise.
    Analyze the following conversation history and qualify the lead.
    
    Intent Categories: 
    - awareness (asking general questions)
    - interest (asking about features/benefits)
    - decision (asking about pricing/comparison)
    - action (ready to buy/book)
    
    Conversation:
    {conversation_history}
    
    Return a JSON object:
    {{
      "score": 0-100 (where 100 is extremely high intent/action),
      "intent": "awareness" | "interest" | "decision" | "action",
      "sentiment": "positive" | "neutral" | "negative",
      "reasoning": "Brief explanation of the score"
    }}
    """
    
    try:
        result = generate_json(prompt)
        return result
    except Exception:
        return {
            "score": 50,
            "intent": "awareness",
            "sentiment": "neutral",
            "reasoning": "Fallback score due to agent error"
        }
