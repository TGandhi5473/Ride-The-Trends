import logging
from database import get_connection, release_connection

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_quality_audit():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # 1. Single-trip Health Metrics
        cur.execute("""
            SELECT 
                (SELECT COUNT(*) FROM silver_social_posts) as silver_count,
                (SELECT COUNT(*) FROM silver_quarantine) as quarantine_count;
        """)
        silver_count, quarantine_count = cur.fetchone()
        
        total = silver_count + quarantine_count
        success_rate = (silver_count / total * 100) if total > 0 else 0
        
        # 2. Identify Top Error Reasons
        cur.execute("""
            SELECT error_reason, COUNT(*) 
            FROM silver_quarantine 
            GROUP BY error_reason 
            ORDER BY 2 DESC LIMIT 5;
        """)
        top_errors = cur.fetchall()

        # 3. "Niche Discovery" Check (The 'OTHER' Label)
        cur.execute("SELECT COUNT(*) FROM silver_social_posts WHERE predicted_category = 'OTHER';")
        other_count = cur.fetchone()[0]

        # 4. Print the Health Report
        print("\n" + "="*40)
        print("📊 SILVER LAYER HEALTH REPORT")
        print("="*40)
        print(f"✅ Healthy Records:      {silver_count}")
        print(f"⚠️ Quarantined Records:  {quarantine_count}")
        print(f"📈 Pipeline Success:     {success_rate:.2f}%")
        print(f"🔍 Niche/Other Labels:   {other_count} (Candidates for retraining)")
        
        if top_errors:
            print("\n--- 🚩 TOP REASONS FOR FAILURE ---")
            for reason, count in top_errors:
                print(f"- {reason}: {count} records")
        
        # 5. Circuit Breaker Logic
        if success_rate < 90 and total > 50:
            logging.warning("🚨 ALERT: Low success rate! Check for API schema changes or BERT drift.")

    except Exception as e:
        logging.error(f"Audit failed: {e}")
    finally:
        cur.close()
        release_connection(conn) # Return to pool instead of closing

if __name__ == "__main__":
    run_quality_audit()
