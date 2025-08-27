# scripts/setup_project.py
#!/usr/bin/env python3
"""
Setup script for the Airtable Contractor System
Helps users configure their environment properly
"""

from decouple import config, UndefinedValueError
import os
import sys

def setup_environment():
    """Guide user through environment setup"""
    print("🔧 Airtable Contractor System Setup")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Creating .env file...")
        create_env_file()
    else:
        print(".env file found")
    
    # Check for required API keys
    check_required_keys()
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Run 'make create-base' to create your Airtable base")
    print("2. Run 'make install-dev' to install dependencies")
    print("3. Run 'make test' to verify everything works")

def create_env_file():
    """Create a new .env file with template"""
    env_content = """# Airtable Configuration
# Get your API key from: https://airtable.com/account
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=

# LLM Configuration (Optional)
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=
GEMINI_API_KEY=

# Shortlisting Criteria
TIER_1_COMPANIES=Google,Meta,OpenAI,Microsoft,Apple,Amazon,Netflix
ELIGIBLE_LOCATIONS=US,USA,United States,Canada,UK,United Kingdom,Germany,India
MAX_HOURLY_RATE=100
MIN_AVAILABILITY=20
MIN_EXPERIENCE=4

# API Settings
MAX_RETRIES=3
RETRY_BACKOFF=2

# Debug
DEBUG=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(".env file created. Please edit it with your API keys.")

def check_required_keys():
    """Check if required API keys are set"""
    print("\nChecking required API keys...")
    
    try:
        airtable_key = config('AIRTABLE_API_KEY')
        if airtable_key == 'your_airtable_api_key_here':
            print("Please update AIRTABLE_API_KEY in your .env file")
            print("   Get it from: https://airtable.com/account")
            return False
        else:
            print("AIRTABLE_API_KEY is set")
    except UndefinedValueError:
        print("AIRTABLE_API_KEY is not set in .env file")
        return False
    
    return True

def main():
    """Main setup function"""
    try:
        setup_environment()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()