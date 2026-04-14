import uuid
import random
from datetime import datetime, timedelta
from db import SessionLocal
from models import Campaign, CampaignMetric, Lead, User

def seed_mock_data():
    db = SessionLocal()
    try:
        # 1. Get a user to assign data to
        user = db.query(User).first()
        if not user:
            print("No user found. Run db_init first.")
            return
            
        # 2. Find or Create an active campaign
        campaign = db.query(Campaign).filter(Campaign.status == "active").first()
        if not campaign:
            campaign = Campaign(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name="Pilot Growth Campaign",
                status="active",
                platform="both",
                objective="leads",
                total_budget=5000.0,
            )
            db.add(campaign)
            db.commit()
            db.refresh(campaign)

        # 3. Generate 30 days of metrics
        print(f"Seeding 30 days of metrics for Campaign: {campaign.name}")
        base_date = datetime.utcnow() - timedelta(days=30)
        
        for i in range(31):
            day = base_date + timedelta(days=i)
            # Random performance oscillation
            spend = random.uniform(50.0, 150.0)
            impressions = int(spend * random.uniform(50, 100))
            clicks = int(impressions * random.uniform(0.01, 0.05))
            conversions = int(clicks * random.uniform(0.05, 0.15))
            
            metric = CampaignMetric(
                id=str(uuid.uuid4()),
                campaign_id=campaign.id,
                day=day,
                platform="meta" if i % 2 == 0 else "google",
                spend=spend,
                impressions=impressions,
                clicks=clicks,
                conversions=conversions
            )
            db.add(metric)
            
            # Generate mock leads for conversions
            for _ in range(conversions):
                lead = Lead(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    campaign_id=campaign.id,
                    full_name=f"Lead {uuid.uuid4().hex[:6]}",
                    email=f"lead_{uuid.uuid4().hex[:4]}@example.com",
                    status="new",
                    score=random.randint(40, 95)
                )
                db.add(lead)
                
        db.commit()
        print("Mock analytics data seeded successfully.")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_mock_data()
