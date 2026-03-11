import os
import sys

def verify_environment():
    """
    Checks if all required environment variables are present before starting
    the FastAPI backend. Exits with a clear error if any are missing.
    """
    
    required_vars = [
        "GEMINI_API_KEY",
        "TMDB_API_KEY",
        "DATABASE_URL"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            
    if missing_vars:
        print("\n" + "="*60)
        print("❌ CRITICAL STARTUP ERROR: Missing Environment Variables")
        print("="*60)
        print("The following required environment variables were not found:\n")
        
        for var in missing_vars:
            print(f"  - {var}")
            
        print("\nPlease ensure they are defined in your .env file or exported")
        print("in your system environment before starting the server.")
        print("="*60 + "\n")
        
        # Exit with error code 1
        sys.exit(1)
        
    print("✅ Environment verification passed. All required variables are present.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    verify_environment()
