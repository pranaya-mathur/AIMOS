import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import get_db
from models import Lead, ConversationMessage, LandingPage, Brand
from services.agents.sales_agent_agent import run as run_sales_agent

router = APIRouter()

class ChatMessageBody(BaseModel):
    lead_id: Optional[str] = None
    slug: str  # Landing page slug to get brand context
    message: str

@router.post("/message")
def chat_with_agent(
    body: ChatMessageBody,
    db: Session = Depends(get_db)
):
    """Live site chatbot endpoint using the Sales Agent."""
    
    # 1. Resolve Context (Brand Brain)
    page = db.query(LandingPage).filter(LandingPage.slug == body.slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page context not found")
        
    brand = db.query(Brand).filter(Brand.id == page.brand_id).first()
    brand_kit = brand.ai_generated_kit if brand else {}

    # 2. Get or Create Lead
    lead = None
    if body.lead_id:
        lead = db.query(Lead).filter(Lead.id == body.lead_id).first()
    
    if not lead:
        lead = Lead(
            id=str(uuid.uuid4()),
            phone=f"anon-{str(uuid.uuid4())[:8]}", # Temporary unique identifier
            user_id=page.user_id,
            organization_id=page.organization_id,
            landing_page_id=page.id,
            source="chatbot",
            status="new"
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

    # 3. Persist Inbound Message
    inbound = ConversationMessage(
        id=str(uuid.uuid4()),
        lead_id=lead.id,
        direction="inbound",
        content=body.message
    )
    db.add(inbound)

    # 4. Fetch History for Agent
    history = db.query(ConversationMessage).filter(ConversationMessage.lead_id == lead.id).order_by(ConversationMessage.created_at.asc()).all()
    history_serial = [{"role": "user" if m.direction == "inbound" else "assistant", "content": m.content} for m in history]

    # 5. Run Sales Agent
    agent_state = {
        "input": {
            "brand_name": brand.name if brand else "Our Brand",
            "industry": brand.industry if brand else "General",
            "message": body.message
        },
        "agent_outputs": {
            "history": history_serial,
            "brand_kit": brand_kit
        }
    }
    
    result = run_sales_agent(agent_state)
    response_text = result.get("sales_agent", {}).get("response", "Thank you for your message. How can I help?")

    # 6. Persist Outbound Message
    outbound = ConversationMessage(
        id=str(uuid.uuid4()),
        lead_id=lead.id,
        direction="outbound",
        content=response_text
    )
    db.add(outbound)
    
    # 7. Update Lead Intelligence (Intent/Score)
    if "intent" in result.get("sales_agent", {}):
        lead.intent = result["sales_agent"]["intent"]
    if "lead_score" in result.get("sales_agent", {}):
        lead.score = result["sales_agent"]["lead_score"]

    db.commit()

    return {
        "lead_id": lead.id,
        "response": response_text
    }
