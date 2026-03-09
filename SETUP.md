# AI Financial Advisor — Setup & Run Guide

## Prerequisites
- Python 3.9 or higher
- A Groq API key (free at https://console.groq.com)
- pip package manager

## Step 1: Clone / Download the Project
If you have git:
```bash
git clone <your-repo-url>
cd ai-financial-advisor
```
Or extract the ZIP and navigate to the folder.

## Step 2: Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables
```bash
cp .env.example .env
```
Open `.env` in a text editor and set:
```
GROQ_API_KEY=gsk_your_actual_key_here
```
Get your free API key at: https://console.groq.com/keys

## Step 5: Run the Application
```bash
streamlit run app.py
```
The app will open automatically at: http://localhost:8501

## Usage Guide
1. Fill in your financial details in the left sidebar
2. Optionally expand "Add Expense Categories" for a detailed breakdown
3. Click **"🔍 Analyze My Finances"**
4. Browse the 4 tabs:
   - **Dashboard** — Visual overview of your financial health
   - **AI Advice** — Personalized AI-generated recommendations
   - **Projections** — Future savings and debt payoff charts
   - **Ask Advisor** — Chat with AI for follow-up questions

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `GROQ_API_KEY not found` | Ensure `.env` file exists with valid key |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| App doesn't open | Visit http://localhost:8501 manually |
| API errors | Check your Groq API key and internet connection |
| Streamlit version error | Run `pip install --upgrade streamlit` |

## Project Structure
```
ai-financial-advisor/
├── .env.example          # Environment variable template
├── .gitignore
├── requirements.txt      # Python dependencies
├── app.py                # Main Streamlit app
├── config/
│   └── settings.py       # Config loader
├── modules/
│   ├── financial_analyzer.py  # Financial calculations
│   ├── prompt_builder.py      # Groq prompt construction
│   ├── groq_client.py         # Groq API wrapper
│   └── visualizer.py          # Plotly charts
├── utils/
│   └── formatters.py          # Formatting utilities
└── SETUP.md              # This file
```

## Model Information
- **Provider**: Groq (https://groq.com)
- **Model**: llama-3.3-70b-versatile
- **Speed**: ~500 tokens/second (extremely fast inference)
- **Context**: 128K tokens
- **Cost**: Free tier available

## Customization
- To change the LLM model: edit `GROQ_MODEL` in `.env`
- To add new chart types: extend `modules/visualizer.py`
- To modify AI behavior: edit prompts in `modules/prompt_builder.py`
- To add authentication: integrate `streamlit-authenticator` package
