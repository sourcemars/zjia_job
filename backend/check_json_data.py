import json
import os
from datetime import datetime

def check_json_files():
    """Check available JSON files with job data"""
    json_files = []
    
    for file in os.listdir('.'):
        if file.endswith('.json'):
            json_files.append(file)
    
    print(f"Found {len(json_files)} JSON files:")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"\n📄 {json_file}:")
            print(f"  - File size: {os.path.getsize(json_file)} bytes")
            print(f"  - Data type: {type(data)}")
            
            if isinstance(data, list):
                print(f"  - Number of records: {len(data)}")
                if len(data) > 0:
                    sample = data[0]
                    print(f"  - Sample record keys: {list(sample.keys()) if isinstance(sample, dict) else 'Not a dict'}")
                    if isinstance(sample, dict):
                        for key in ['title', 'company', 'location', 'salary']:
                            if key in sample:
                                value = sample[key]
                                if isinstance(value, str) and len(value) > 50:
                                    print(f"    - {key}: {value[:50]}...")
                                else:
                                    print(f"    - {key}: {value}")
            elif isinstance(data, dict):
                print(f"  - Dictionary keys: {list(data.keys())}")
            
        except Exception as e:
            print(f"  - Error reading {json_file}: {e}")

if __name__ == "__main__":
    check_json_files()
