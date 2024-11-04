import pandas as pd
from openai import OpenAI
from .logger_config import setup_logging
import os
from datetime import datetime

class ExcelQuerySystem:
    def __init__(self, model, csv_path, api_key):
        """
        Initialize the query system with an Excel file and OpenAI API key
        
        Args:
            excel_path (str): Path to the Excel file
            api_key (str): OpenAI API key
        """
        # Set up logging using common configuration
        self.logger = setup_logging('ExcelQuerySystem')
        
        self.logger.info("Initializing ExcelQuerySystem")
        
        self.logger.info(f"Loading CSV file from: {csv_path}")
        
        self.df = pd.read_csv(csv_path)
        self.client = OpenAI(api_key=api_key)
        self.model = model

        # Create a schema description of the dataframe
        self.schema = self._create_schema_description()
        self.logger.info("Initialization complete")
    
    

    def _create_schema_description(self):
        """Create a description of the dataframe schema for the LLM"""
        self.logger.info("Creating schema description")
        
        columns = self.df.columns.tolist()
        dtypes = self.df.dtypes.to_dict()
        
        schema = "DataFrame Schema:\n"
        schema += f"Total rows: {len(self.df)}\n"
        schema += "Columns:\n"
        for col in columns:
            schema += f"- {col} (Type: {dtypes[col]})\n"
        
        # Add sample values for each column
        schema += "\nSample values for each column:\n"
        for col in columns:
            sample_values = self.df[col].dropna().unique()[:3]
            schema += f"- {col}: {', '.join(map(str, sample_values))}\n"
        
        self.logger.debug(f"Generated schema:\n{schema}")
        return schema

    def _determine_question_type(self, question):
        """Determine if the question requires data filtering or just explanation"""
        self.logger.info(f"Determining question type for: {question}")
        
        prompt = f"""
Analyze the following question and determine if it requires filtering/querying data from the DataFrame or just needs a general explanation.

DataFrame Context:
{self.schema}

Question: {question}

Classify this question as either:
1. 'filter' - if it requires searching, filtering, or analyzing specific data from the DataFrame
2. 'explain' - if it's asking for general explanation, terminology, or questions not requiring specific data filtering

Return ONLY one of these exactly: 'filter' or 'explain'
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at classifying questions. Respond only with 'filter' or 'explain'."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        question_type = response.choices[0].message.content.strip().lower()
        self.logger.info(f"Question type determined: {question_type}")
        return question_type

    def _generate_query_code(self, user_question):
        """Generate pandas code to answer the user's question"""
        self.logger.info("Generating query code")
        
        prompt = f"""
You are an expert in pandas and data analysis. Given the following DataFrame schema and user question, 
generate ONLY the python code (without any explanation) that would answer the question.
The code should return a pandas DataFrame with the filtered results.

{self.schema}

User Question: {user_question}

Important: Only use these pandas operations:
- Basic indexing and selection: df[...], df.loc[...], df.iloc[...]
- Filtering: df[df['column'] condition]
- Grouping: df.groupby()
- Aggregation: .count(), .sum(), .mean(), .min(), .max()
- Sorting: .sort_values()
- Basic arithmetic: +, -, *, /
- Comparisons: >, <, >=, <=, ==, !=
- String operations: .str.contains(), .str.startswith(), .str.endswith()

Return only the python code that starts with 'df' and uses proper python syntax. 
The code should NOT be wrapped in any other code or comments.
When the code is executed using eval(), it should return a pandas DataFrame with the filtered results.
Don't include any explanations or print statements.

Here are some examples of how to interepret user questions:

1. "Show me everything about Apple" -> df = df['Apple']
2. "Show me the revenue of Tesla" -> df[df['Company'] == 'Tesla']['Revenue']
3. "What is the market capitalization of Alphabet" -> df[df['Company'] == 'Alphabet']['Market Capitalization']
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a data analysis expert. Generate only pandas code without any explanation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        query_code = response.choices[0].message.content.strip()
        self.logger.debug(f"Generated query code:\n{query_code}")
        return query_code
    
    def _safe_execute_query(self, query_code, df):
        """Safely execute the generated pandas query"""
        self.logger.info("Safely executing query code")
        
        # Dictionary of allowed functions and their implementations
        allowed_operations = {
            'groupby': df.groupby,
            'sort_values': df.sort_values,
            'mean': df.mean,
            'sum': df.sum,
            'count': df.count,
            'max': df.max,
            'min': df.min,
        }
        
        try:
            # Basic safety checks
            if not query_code.startswith('df'):
                raise ValueError("Query must start with 'df'")
            
            # Remove any potentially dangerous operations
            dangerous_ops = ['eval', 'exec', 'import', 'open', 'read', 'write', 'delete', 'remove', 'system']
            if any(op in query_code.lower() for op in dangerous_ops):
                raise ValueError("Query contains unauthorized operations")

            # Create a local namespace with only the DataFrame and allowed operations
            local_namespace = {
                'df': df,
                'pd': pd,  # needed for some pandas operations
                **allowed_operations
            }
            
            # Handle different types of queries
            if '=' in query_code:
                # For assignment operations, split into parts
                parts = query_code.split('=')
                if len(parts) != 2:
                    raise ValueError("Invalid assignment operation")
                
                # Execute the right side of the assignment
                right_side = parts[1].strip()
                result = eval(right_side, {"__builtins__": {}}, local_namespace)
                
                # Update the local namespace
                local_namespace['df'] = result
                self.logger.debug(f"Assignment operation completed. New shape: {result.shape}")
            else:
                # For direct queries
                result = eval(query_code, {"__builtins__": {}}, local_namespace)
            
            # Get the final result from the namespace
            final_result = local_namespace['df']
            
            # Ensure the result is a DataFrame
            if not isinstance(final_result, pd.DataFrame):
                if isinstance(final_result, pd.Series):
                    final_result = final_result.to_frame()
                else:
                    final_result = pd.DataFrame(final_result)
            
            self.logger.info(f"Query executed successfully. Result shape: {result.shape}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing query: {str(e)}", exc_info=True)
            raise ValueError(f"Error executing query: {str(e)}")
        
    def generate_explanation(self, question):
        """Generate a general explanation for questions that don't require data filtering"""
        self.logger.info("Generating general explanation")
        
        prompt = f"""
Provide a clear and informative answer to the following question. Consider the context of our DataFrame but focus on giving a general explanation.

DataFrame Context:
{self.schema}

Question: {question}

Provide a clear, comprehensive explanation in 2-3 sentences.
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful data analyst providing clear explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        explanation = response.choices[0].message.content.strip()
        self.logger.debug(f"Generated explanation:\n{explanation}")
        return explanation
    
    def generate_natural_language_response(self, question, result_df):
        """Generate a natural language explanation of the filtered data results"""
        prompt = f"""
Given the following question and the resulting data, provide a natural language explanation of the findings.
Keep the explanation clear and concise.

Question: {question}

Data Summary:
{result_df.to_string() if len(result_df) < 10 else result_df.head().to_string() + "[...more rows...]"}

Explain what we can learn from this data in 2-3 sentences.
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a data analyst providing clear, concise explanations of data findings."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content.strip()
    
    def query(self, question):
        """Process user question and return appropriate response"""
        self.logger.info(f"\n{'='*50}\nProcessing new query: {question}\n{'='*50}")
        
        try:
            # Determine question type
            question_type = self._determine_question_type(question)
            self.logger.info(f"Question type: {question_type}")
            
            if question_type == 'explain':
                # For questions that don't require data filtering
                self.logger.info("Generating explanation for general question")
                explanation = self.generate_explanation(question)
                self.logger.info("Explanation generated successfully")
                self.logger.debug(f"Explanation content:\n{explanation}")
                return None, explanation
            else:
                # For questions that require data filtering
                self.logger.info("Processing data filtering question")
                
                # Generate the pandas code
                query_code = self._generate_query_code(question)
                self.logger.info("Query code generated")
                self.logger.debug(f"Query code:\n{query_code}")
                
                # Create a local copy of the dataframe named 'df'
                df = self.df
                self.logger.debug(f"Working with DataFrame of shape: {df.shape}")
                self.logger.debug(f"Working with DataFrame: \n{df}")

                # Safely execute the query
                result = self._safe_execute_query(query_code, self.df)
                self.logger.info(f"Query executed. Result shape: {result.shape}")
                self.logger.debug(f"Query result preview:\n{result.head() if not result.empty else 'Empty DataFrame'}")
                
                # Generate natural language explanation
                self.logger.info("Generating explanation for query results")
                explanation = self.generate_natural_language_response(question, result)
                self.logger.debug(f"Generated explanation:\n{explanation}")
                
                self.logger.info("Query processing completed successfully")
                return result, explanation
        
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return None, f"Error processing question: {str(e)}"