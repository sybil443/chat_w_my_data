# Data Chat Interface

A Flask-based web application that allows users to query data using natural language processing. The application uses OpenAI's GPT model to interpret questions and generate appropriate pandas queries to filter and analyze data.

## Features

- Natural language query processing
- Interactive chat interface
- Dynamic data table display
- Automated pandas query generation
- Comprehensive logging system
- Question type classification (filtering vs explanation)
- Secure query execution system

## Prerequisites

- Python 3.8+
- OpenAI API key
- Flask
- Pandas

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sybil443/chat_w_my_data.git
cd chat_w_my_data
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following:
```env
OPENAI_API_KEY=your_api_key_here
MODEL=gpt-4
CSV_FILE_PATH=path/to/your/data.csv
FLASK_DEBUG=True
```

## Project Structure

```
project_folder/
├── src/
│   ├── __init__.py
│   ├── query_system.py
│   └── logger_config.py
├── static/
│   ├── user-avatar.png
│   └── assistant-avatar.png
├── templates/
│   └── index.html
├── logs/
│   └── application_[timestamp].log
├── app.py
├── config.py
├── requirements.txt
└── README.md
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Enter questions in the chat interface. Example questions:
   - "What is this dataset about?"
   - "Show me everything about Google"
   - "What's the revenue of Tesla?"
   - "Compare the market capitalization of different companies"

## Features in Detail

### Natural Language Processing
- Uses OpenAI's GPT model to understand user queries
- Classifies questions as either requiring data filtering or general explanation
- Generates appropriate pandas queries based on user questions

### Data Display
- Dynamic table generation
- Consistent column ordering (Question first)
- Clean and responsive interface
- Error handling for data display

### Logging System
- Comprehensive logging of all operations
- Separate logging for application and query system
- Log rotation to manage file sizes
- Debug and info level logging

### Security
- Safe query execution system
- Protection against harmful operations
- Input validation
- Restricted pandas operations

## Configuration

The application can be configured through `config.py`:
```python
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = os.getenv("MODEL", "gpt-4")
    CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
```

## Logging

Logs are stored in the `logs` directory with the following format:
```
application_YYYYMMDD_HHMMSS.log
```

Log levels:
- DEBUG: Detailed information (file only)
- INFO: General flow (console and file)
- ERROR: Error messages with stack traces

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

[Your chosen license]

## Contact

Your Name - sybilshi@gmail.com
Project Link: https://github.com/sybil443/chat_w_my_data.git
