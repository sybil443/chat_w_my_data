from src.query_system import ExcelQuerySystem
from config import Config
import pandas as pd

def test_openai_integration():
    """Test OpenAI API integration with sample questions"""
    
    # Initialize the query system
    query_system = ExcelQuerySystem(Config.MODEL, Config.CSV_FILE_PATH, Config.OPENAI_API_KEY)
    
    # List of test questions - mix of filtering and explanation questions
    test_questions = [
        # Data filtering questions
        "How many teams are in the data?",
        "What's the average score?",
        "Show me all teams",
        # General explanation questions
        "What's in this dataset?",
        "Can you explain what segments mean in this context?",
        "What's the purpose of this analysis?",
        # Mixed questions
        "Compare the responses between segment A and B",
        "What are the key findings about pricing?"
    ]
    
    print("\n=== Testing OpenAI Integration ===\n")
    
    # Print data context for reference
    print("Data Context:")
    print(query_system.schema)
    print("\n" + "="*50 + "\n")
    
    # Test each question
    for question in test_questions:
        print(f"\nTest Question: {question}")
        print("-" * 40)
        
        try:
            # Get both DataFrame result and explanation
            result_df, explanation = query_system.query(question)
            
            print("Explanation:", explanation)
            
            if result_df is not None:
                print("\nTable Data:")
                print(result_df)
                print(f"\nNumber of rows in result: {len(result_df)}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "="*50)

def interactive_test():
    """Interactive testing mode"""
    query_system = ExcelQuerySystem(Config.MODEL, Config.CSV_FILE_PATH, Config.OPENAI_API_KEY)
    
    print("\n=== Interactive Testing Mode ===")
    print("Type 'exit' to quit\n")
    
    while True:
        question = input("\nEnter your question: ").strip()
        
        if question.lower() == 'exit':
            break
        
        try:
            result_df, explanation = query_system.query(question)
            
            print("\nExplanation:", explanation)
            
            if result_df is not None:
                print("\nTable Data:")
                print(result_df)
                print(f"\nNumber of rows in result: {len(result_df)}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    # Ask user which mode they want to use
    print("Choose test mode:")
    print("1. Run all test questions")
    print("2. Interactive mode")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        test_openai_integration()
    elif choice == "2":
        interactive_test()
    else:
        print("Invalid choice. Please run again and select 1 or 2.")