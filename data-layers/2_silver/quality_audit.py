import logging
from database import get_connection

logging.basicConfig(level=logging.INFO)

def run_quality_audit():
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Calculate Success Rate
    cur.execute("SELECT COUNT(*) FROM silver_social_posts;")
    silver_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM silver_quarantine;")
    quarantine_count = cur.fetchone()[0]
    
    total = silver_count + quarantine_count
    success_rate = (silver_count / total * 100) if total > 0 else 0
    
    # 2. Identify Top Error Reasons in Quarantine
    cur.execute("""
        SELECT error_reason, COUNT(*) 
        FROM silver_quarantine 
        GROUP BY error_reason 
        ORDER BY 2 DESC LIMIT 5;
    """)
    top_errors = cur.fetchall()

    # 3. Print the Health Report
    print("--- 📊 SILVER LAYER HEALTH REPORT ---")
    print(f"✅ Healthy Records: {silver_count}")
    print(f"⚠️ Quarantined Records: {quarantine_count}")
    print(f"📈 Pipeline Success Rate: {success_rate:.2f}%")
    print("\n--- 🚩 TOP 5 REASONS FOR FAILURE ---")
    for reason, count in top_errors:
        print(f"- {reason}: {count} records")
    
    # 4. Critical Warning (Circuit Breaker logic)
    if success_rate < 90 and total > 100:
        logging.warning("🚨 CRITICAL: Success rate is below 90%! Manual inspection of Quarantine required.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    run_quality_audit()
