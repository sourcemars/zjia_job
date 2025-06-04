import json
import sqlite3

def examine_job_data():
    """Examine the structure of scraped job data and database status"""
    
    print("=== SCRAPED JOB DATA ANALYSIS ===")
    try:
        with open('jobonline_internship_positions_20250529_005328.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 JSON File Analysis:")
        print(f"  - Total companies: {len(data)}")
        
        total_positions = 0
        for i, company in enumerate(data):
            positions = company.get('internship_positions', [])
            total_positions += len(positions)
            
            print(f"\n🏢 Company {i+1}: {company.get('company_name', 'Unknown')}")
            print(f"  - Industry: {company.get('company_industry', 'N/A')}")
            print(f"  - Size: {company.get('company_size', 'N/A')}")
            print(f"  - Internship positions: {len(positions)}")
            
            if positions:
                for j, pos in enumerate(positions[:2]):  # Show first 2 positions
                    print(f"    Position {j+1}:")
                    for key, value in pos.items():
                        if isinstance(value, str) and len(value) > 60:
                            print(f"      {key}: {value[:60]}...")
                        else:
                            print(f"      {key}: {value}")
                if len(positions) > 2:
                    print(f"    ... and {len(positions) - 2} more positions")
        
        print(f"\n📈 Summary:")
        print(f"  - Total companies: {len(data)}")
        print(f"  - Total internship positions: {total_positions}")
        
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
    
    print("\n=== DATABASE STATUS ===")
    try:
        conn = sqlite3.connect('zjia_job.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"📋 Available tables: {tables}")
        
        for table in tables:
            if 'job' in table.lower():
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"  - {table}: {count} records")
                
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 1;")
                    sample = cursor.fetchone()
                    cursor.execute(f"PRAGMA table_info({table});")
                    columns = [col[1] for col in cursor.fetchall()]
                    print(f"    Sample record: {dict(zip(columns, sample)) if sample else 'None'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    
    print("\n=== STORAGE STATUS ===")
    print("🔍 Checking if job data has been processed and stored...")
    
    import os
    processed_files = [f for f in os.listdir('.') if 'processed' in f and f.endswith('.json')]
    if processed_files:
        print(f"📁 Found processed files: {processed_files}")
    else:
        print("📁 No processed job files found")
    
    if os.path.exists('store_job_data.py'):
        print("✅ Storage script exists: store_job_data.py")
        print("💡 To store the scraped data, run:")
        print("   python store_job_data.py --input jobonline_internship_positions_20250529_005328.json --source jobonline")
    else:
        print("❌ Storage script not found")

if __name__ == "__main__":
    examine_job_data()
