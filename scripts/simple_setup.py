# scripts/simple_setup.py
#!/usr/bin/env python3
"""
Simple setup script to check environment configuration
"""

import os
import sys

def check_env_file():
    """Check if .env file exists and has basic structure"""
    if not os.path.exists('.env'):
        print(".env file not found")
        print("Creating .env file from template...")
        
        env_content = """# Airtable Configuration
# Get your API key from: https://airtable.com/account
AIRTABLE_API_KEY=your_api_key_here

# Get your Base ID from Airtable URL or API docs
# Format: https://airtable.com/{BASE_ID}/api/docs
AIRTABLE_BASE_ID=your_base_id_here

# LLM Configuration (Optional)
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=
GEMINI_API_KEY=

# Application Settings
DEBUG=True
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("Created .env file")
        print("Please edit .env with your actual API keys")
        return False
    return True

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 9:
        print("Python version is compatible")
        return True
    else:
        print("Python 3.9 or higher is required")
        return False

def main():
    """Main setup function"""
    print("Simple Environment Setup Check")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check .env file
    env_exists = check_env_file()
    
    if env_exists:
        # Try to read the .env file
        try:
            with open('.env', 'r') as f:
                content = f.read()
            
            if 'your_api_key_here' in content:
                print("Please update your .env file with actual API keys")
                print("   Get Airtable API key from: https://airtable.com/account")
            else:
                print(".env file appears to be configured")
                
        except Exception as e:
            print(f"Error reading .env file: {e}")
    else:
        print("ℹPlease configure your .env file and run this script again")
    
    print("\n Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run 'make install-pip' to install dependencies")
    print("3. Run 'make check-airtable' to test connection")

if __name__ == '__main__':
    main()