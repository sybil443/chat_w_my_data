# Import the necessary functions from app.py
from app import get_llm_response, prepare_data_context
import pandas as pd

def test_openai_integration():
    """Test OpenAI API integration with sample questions"""
    
    # List of test questions
    test_questions = [
        "How many teams are in the data?",
        "What's the average score?",
        "Show me all teams",
        "What's in this dataset?"
    ]
    
    print("\n=== Testing OpenAI Integration ===\n")
    
    # Print data context for reference
    data_info = prepare_data_context()
    print("Data Context:")
    print("Columns:", data_info['column_names'])
    print("Row Count:", data_info['row_count'])
    print("\nSample Data:")
    print(data_info['sample_data'])
    print("\n" + "="*50 + "\n")
    
    # Test each question
    for question in test_questions:
        print(f"\nTest Question: {question}")
        print("-" * 40)
        
        try:
            response = get_llm_response(question)
            print("Response:", response['answer'])
            
            if response.get('data'):
                print("\nTable Data:")
                print(pd.DataFrame(response['data']))
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    test_openai_integration()
