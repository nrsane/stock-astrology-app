# Stock Astrology Analysis App

A web application that uses KP Astrology to analyze stock price movements.

## Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click the "Deploy to Render" button above
2. Connect your GitHub account
3. Select this repository
4. Render will automatically deploy your application

## Features

- Generate KP birth charts for stocks
- Analyze house significators (2nd & 11th houses)
- Correlate planetary movements with stock prices
- Web-based interface

## Local Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python migrate_db.py
python app.py


## Method 2: Use GitHub's Template Feature (Even Easier)

### Option A: Use My Pre-Made Template
I can provide you with a complete repository structure that you can simply copy-paste.

### Option B: Create Files in Batches
Instead of creating files one by one, you can:

1. **Create the basic structure first**
2. **Then add the complex Python files**

## Complete File Creation Checklist:

Here's the exact order to create files on GitHub:

### First Batch - Core Structure:
- [ ] `backend/requirements.txt`
- [ ] `backend/app.py` 
- [ ] `backend/database.py`
- [ ] `backend/migrate_db.py`
- [ ] `backend/wsgi.py`

### Second Batch - Models:
- [ ] `backend/models/__init__.py` (empty)
- [ ] `backend/models/stock_models.py`

### Third Batch - KP Astrology:
- [ ] `backend/kp_astrology/__init__.py` (empty)
- [ ] `backend/kp_astrology/chart_calculator.py`
- [ ] `backend/kp_astrology/significator.py`

### Fourth Batch - Data & Templates:
- [ ] `backend/data/__init__.py` (empty)
- [ ] `backend/data/stock_data.py`
- [ ] `backend/templates/index.html`

### Fifth Batch - Deployment:
- [ ] `backend/render.yaml`
- [ ] `backend/Procfile`
- [ ] `backend/runtime.txt`

## Time-Saving Tips:

1. **Use copy-paste** from my previous messages for file content
2. **Create folders first** by typing `folder_name/` as filename
3. **Batch commit** related files together
4. **Test as you go** - deploy after core files are created

## Quick Start - Minimal Files Needed for Deployment:

If you want the absolute minimum to test deployment:

**Essential Files:**
1. `backend/requirements.txt`
2. `backend/app.py` (basic version)
3. `backend/render.yaml`
4. `backend/Procfile`

You can add the complex astrology logic later after basic deployment works.

## Which approach would you prefer?

1. **Full setup** - Create all 15+ files now for complete functionality
2. **Minimal setup** - Create just 4-5 core files first, then add features later
3. **Step-by-step guided** - I'll give you exact file content for each file one by one

Let me know which method you'd like, and I'll provide the exact file content for each file you need to create on GitHub!
