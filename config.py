import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # OpenAI API configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = os.getenv("MODEL", "gpt-4o-mini")
    # CSV file configuration
    CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "./TechCompanyInsights - Sheet1.csv")
    
    # Flask configuration
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    # Add other configuration variables as needed