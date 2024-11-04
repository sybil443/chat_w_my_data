from flask import Flask, render_template, request, jsonify
from src.query_system import ExcelQuerySystem
from src.logger_config import setup_logging
from config import Config
from datetime import datetime

# Initialize Flask application
app = Flask(__name__, static_folder='static')

# Load configuration
app.config.from_object(Config)

# Set up logging using common configuration
logger = setup_logging('FlaskApp')

# Initialize the ExcelQuerySystem
logger.info("Initializing ExcelQuerySystem")
try:
    query_system = ExcelQuerySystem(
        Config.MODEL,
        Config.CSV_FILE_PATH,
        Config.OPENAI_API_KEY
    )
    logger.info("ExcelQuerySystem initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ExcelQuerySystem: {str(e)}", exc_info=True)
    raise

@app.route('/')
def home():
    """Render the main page"""
    logger.info("Serving home page")
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def handle_query():
    """Handle the query request and return results"""
    # Log request
    request_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    logger.info(f"Request ID {request_id}: Received query request")
    
    # Get question from request
    user_question = request.json.get('question')
    logger.info(f"Request ID {request_id}: Question: {user_question}")
    
    try:
        # Get both the DataFrame result and natural language explanation
        logger.debug(f"Request ID {request_id}: Processing query through ExcelQuerySystem")
        result_df, explanation = query_system.query(user_question)
        
        if result_df is not None:
            # Log successful data query
            logger.info(f"Request ID {request_id}: Query successful with data")
            logger.debug(f"Request ID {request_id}: DataFrame shape: {result_df.shape}")
            
            # Convert DataFrame to dictionary for JSON response
            table_data = result_df.to_dict('records') if not result_df.empty else None
            
            response_data = {
                'success': True,
                'answer': explanation,
                'table_data': table_data
            }
            logger.debug(f"Request ID {request_id}: Sending response with table data")
            logger.debug(f"Request ID {request_id}: Response data: {response_data}")
            
        else:
            # Log explanation-only response
            logger.info(f"Request ID {request_id}: Query returned explanation only")
            response_data = {
                'success': True,
                'answer': explanation,
                'table_data': None
            }
            
        logger.info(f"Request ID {request_id}: Request completed successfully")
        return jsonify(response_data)
            
    except Exception as error:
        # Log error
        logger.error(
            f"Request ID {request_id}: Error processing query: {str(error)}", 
            exc_info=True
        )
        return jsonify({
            'success': False,
            'error': str(error)
        })

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 Error: {request.url}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {str(error)}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info(f"Starting Flask application in {Config.DEBUG and 'DEBUG' or 'PRODUCTION'} mode")
    app.run(debug=Config.DEBUG)