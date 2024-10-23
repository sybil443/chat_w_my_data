# Import necessary libraries
import os
# import openai # for azure openai api
from openai import OpenAI #for openai api
import pandas as pd
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Initialize Flask application with static folder configuration
app = Flask(__name__, static_folder='static')

# Load environment variables and configure OpenAI
load_dotenv()
# openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
# openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
# openai.api_type = 'azure'
# openai.api_version = '2024-02-01'
# deployment_name = "gpt-4o-mini"
## Set the API key and model name
MODEL="gpt-4o-mini"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Load the CSV data globally to avoid reloading for each query
data_frame = pd.read_csv('test_data - Sheet1.csv')

def prepare_data_context():
    """Prepare a concise summary of the data for the LLM"""
    data_info = {
        'column_names': list(data_frame.columns),
        'row_count': len(data_frame),
        'sample_data': data_frame.head(5).to_string(),
        'data_types': data_frame.dtypes.to_string()
    }
    return data_info

def get_llm_response(user_question):
    """Get response from LLM based on the data and user question"""
    data_info = prepare_data_context()
    
    system_prompt = f"""You are a data analyst assistant. You have access to a DataFrame with the following information:
    
Columns: {data_info['column_names']}
Number of rows: {data_info['row_count']}
Data types: \n{data_info['data_types']}

Here's a sample of the data:
{data_info['sample_data']}

Important Instructions:
1. If the user asks for data that can be displayed in a table format, return your response in two parts:
   - Your explanation as normal text
   - The data formatted as a table prefixed with [TABLE_DATA] and suffixed with [/TABLE_DATA]
2. If no table data is needed, just provide your normal response.
3. Keep explanations clear and concise.
4. If calculations are needed, explain them briefly."""

    try:
        # response = openai.ChatCompletion.create(
        #     engine=deployment_name,
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": user_question}
        #     ],
        #     max_tokens=500,
        #     temperature=0
        # )
        response = client.chat.completions.create(
            model=MODEL,  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
                ],
            max_tokens=500,
            temperature=0
        )
        
        # answer = response['choices'][0]['message']['content'].strip() # for azure openai api
        answer = response.choices[0].message.content # for openai 
        
        # Split response into text and table data if table data exists
        table_data = None
        if '[TABLE_DATA]' in answer:
            parts = answer.split('[TABLE_DATA]')
            text_response = parts[0].strip()
            table_data = parts[1].split('[/TABLE_DATA]')[0].strip()
        else:
            text_response = answer
            
        return {
            'answer': text_response,
            'table_data': table_data
        }
    except Exception as error:
        return {
            'answer': f"Error processing your question: {str(error)}",
            'table_data': None
        }

@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    """Handle the query request and return results"""
    user_question = request.json.get('question')
    try:
        response_data = get_llm_response(user_question)
        return jsonify({
            'success': True,
            'answer': response_data['answer'],
            'table_data': response_data['table_data']
        })
    except Exception as error:
        return jsonify({
            'success': False,
            'error': str(error)
        })

if __name__ == '__main__':
    app.run(debug=True)