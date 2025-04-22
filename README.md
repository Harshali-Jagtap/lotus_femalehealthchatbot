### 🚀 Project Setup Instructions


#### 1. Set Up Python Interpreter
Make sure you have **Python 3.8+** installed.

You can create a virtual environment (recommended):

```bash
python -m venv venv
```

Activate it:
- On **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- On **Mac/Linux**:
  ```bash
  source venv/bin/activate
  ```

#### 2. Install Required Dependencies
Install all necessary Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This will install Flask, OpenAI, transformers, and other required libraries.

#### 3. Configure Environment
Create a `.env` file in the project root (see template above) and add your secret keys.

#### 4. Run the Flask App
```bash
python main.py
```

Or if using Flask CLI:
```bash
export FLASK_APP=main.py       # On Linux/macOS
set FLASK_APP=main.py          # On Windows

flask run
```

The chatbot should now be accessible at:  
🌐 `http://127.0.0.1:5000/`