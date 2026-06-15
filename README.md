# 🚨 Post-Incident RCA Drafter

AI-powered tool that automatically generates structured Root Cause Analysis (RCA) reports from incident timelines, error logs, and Git diffs — powered by Groq.

## ✨ Features
- 📋 Web form to input incident details
- 📁 Upload error logs and Git diffs
- 🤖 AI generates full RCA in seconds (Groq)
- 📊 History of all past incidents
- 🖨️ Print / Save as PDF

## 🚀 Quick Start (3 Steps)

### Step 1 — Install Python packages
```bash
cd rca-drafter
pip install -r requirements.txt
```

### Step 2 — Add your Groq API key
Open the `.env` file and replace `PASTE_YOUR_KEY_HERE` with your key from https://ai.google.dev

### Step 3 — Run the app
```bash
python backend/app.py
```

Then open your browser and go to: **http://localhost:5000**

## 📁 Project Structure
```
rca-drafter/
├── backend/
│   ├── app.py                  ← Main Flask server
│   ├── database.py             ← SQLite database
│   └── services/
│       ├── ai_service.py       ← Gemini API
│       ├── log_parser.py       ← Parse error logs
│       ├── diff_parser.py      ← Parse git diffs
│       └── prompt_builder.py   ← Build AI prompt
├── frontend/
│   ├── index.html              ← Submit incident form
│   ├── report.html             ← View RCA report
│   ├── history.html            ← All past incidents
│   ├── css/style.css
│   └── js/
├── sample_data/                ← Test with these files
└── requirements.txt
```

## 🧪 Testing with Sample Data
1. Open http://localhost:5000
2. Fill in the form with a test incident title
3. Upload `sample_data/sample_logs.txt` as Error Logs
4. Upload `sample_data/sample.diff` as Git Diff
5. Use this timeline:
   ```
   02:15 – PagerDuty alert: Payment API health check failing
   02:18 – On-call engineer acknowledged
   02:22 – Confirmed 100% error rate on payment endpoint
   02:35 – Root cause identified: timeout config changed
   02:47 – Hotfix deployed
   03:00 – Full recovery confirmed
   ```
6. Click "Generate RCA Report"

## 👥 Team
Built by a 4-member team.

## 🔒 Security Note
Never commit your `.env` file. The `.gitignore` already protects it.

Watch Demo video:
https://www.loom.com/share/75f737fcf1984aa39259efa1ff594434


Sample Data:
https://github.com/asmahumera520-wq/RootCauseAnalysis/tree/main/sample_data

Sample Testcases:
https://github.com/asmahumera520-wq/RootCauseAnalysis/tree/main/Test_cases

