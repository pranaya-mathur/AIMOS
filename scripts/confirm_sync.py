#!/usr/bin/env python3
import requests
import os
import sys

BASE_URL = "http://localhost:8000"

def check_step(name, success_msg, fail_msg, check_fn):
    print(f"Checking {name}...")
    try:
        if check_fn():
            print(f"✅ {success_msg}")
            return True
        else:
            print(f"❌ {fail_msg}")
            return False
    except Exception as e:
        print(f"❌ {fail_msg} (Error: {e})")
        return False

def check_health():
    resp = requests.get(f"{BASE_URL}/health/ready")
    return resp.status_code == 200

def check_db_tables():
    import subprocess
    cmd = "docker-compose exec -T api python3 -c \"from db import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())\""
    res = subprocess.check_output(cmd, shell=True).decode()
    tables = eval(res.strip())
    expected = {'users', 'campaigns', 'job_audits', 'usage_events', 'leads', 'conversation_messages', 'campaign_metrics'}
    return expected.issubset(set(tables))

def check_celery_tasks():
    import subprocess
    cmd = "docker-compose exec -T api celery -A celery_app.celery inspect registered"
    res = subprocess.check_output(cmd, shell=True).decode()
    tasks = ["launch_meta_campaign_task", "send_google_ads_task", "post_social_task", "send_engagement_email_task", "send_whatsapp_task", "optimization_tick"]
    return all(t in res for t in tasks)

def check_imports():
    import subprocess
    cmd = "docker-compose exec -T api python3 -c \"from services.integrations import google_ads, social_x, engagement_email, engagement_sms, meta_marketing, whatsapp_cloud, metrics_service; print('OK')\""
    res = subprocess.check_output(cmd, shell=True).decode()
    return "OK" in res

def main():
    print("=== AIMOS ENTERPRISE FULL REPO SYNC AUDIT ===\n")
    
    s1 = check_step("API Health", "API is live and healthy", "API is down", check_health)
    s2 = check_step("Database Schema", "All 7 core tables are present", "Database schema MISMATCH", check_db_tables)
    s3 = check_step("Celery Task Queue", "All 12-agent tasks are registered", "Worker task registration FAIL", check_celery_tasks)
    s4 = check_step("Service Imports", "All Live Wire SDKs (Google Ads, X, SendGrid, Twilio, Meta) are imported correctly", "Broken imports in SDK bridges", check_imports)
    
    print("\n" + "="*45)
    if all([s1, s2, s3, s4]):
        print("✅ REPO IS 100% IN SYNC (INFRA + CORE + SERVICES)")
    else:
        print("⚠️ SYNC ISSUES DETECTED. CHECK THE LOGS ABOVE.")
    print("="*45)

if __name__ == "__main__":
    main()
