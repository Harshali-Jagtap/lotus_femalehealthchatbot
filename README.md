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

## Common Errors & How to Fix Them

### ImportError: cannot import name 'ExpiredSignatureError' from 'jwt'

**Problem:**  
This error occurs if you try to import `ExpiredSignatureError` or `InvalidTokenError` directly from `jwt`.

**Cause:**  
In PyJWT v2+, exceptions like `ExpiredSignatureError` are located in the `jwt.exceptions` submodule, not in the root
`jwt` module.

** Solution:**

1. Replace incorrect import:

    ```text
    # Wrong
    from jwt import ExpiredSignatureError, InvalidTokenError
    ```

2. Use the correct import:

    ```text
    # Correct
    from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
    ```

3. Ensure PyJWT is up to date:

    ```bash
    pip install --upgrade PyJWT
    ```

---

### ImportError: T5Tokenizer requires the SentencePiece library

**Problem:**  
When using `T5Tokenizer`, you might get an error saying the `sentencepiece` library is missing.

** Solution:**

Install the required package:

```bash
pip install sentencepiece
```

** Pro Tip **

```bash
pip freeze > requirements.txt
```
