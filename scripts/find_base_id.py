# scripts/find_base_id.py
import requests
from decouple import config

def find_base_id():
    """Help user find their Airtable Base ID"""
    api_key = config('AIRTABLE_API_KEY', default='')
    
    if not api_key:
        print("Please set AIRTABLE_API_KEY in your .env file first")
        return
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get list of bases
        response = requests.get(
            'https://api.airtable.com/v0/meta/bases',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            bases = response.json().get('bases', [])
            
            if not bases:
                print("No bases found for this API key")
                return
            
            print("Your Airtable Bases:")
            print("=" * 50)
            for base in bases:
                print(f"Name: {base['name']}")
                print(f"ID: {base['id']}")
                print(f"Permission Level: {base.get('permissionLevel', 'Unknown')}")
                print("-" * 30)
                
            print("\nCopy the ID of your 'Contractor Application System' base")
            print("and add it to your .env file as AIRTABLE_BASE_ID")
            
        else:
            print(f"Failed to fetch bases: {response.status_code}")
            if response.status_code == 403:
                print("Your API key may not have permission to list bases")
                
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    find_base_id()