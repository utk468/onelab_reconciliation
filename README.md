# Payment Reconciliation Dashboard

A fintech-style full-stack web application designed to reconcile platform transactions with bank settlements.

## Features
- **Robust Reconciliation Engine**: Uses Pandas to detect missing settlements, duplicates, extra settlements, amount mismatches, and cross-month delayed settlements.
- **Gross Discrepancy Auditing**: The system calculates the true "Gross Discrepancy" (Total Amount at Risk) across all errors, ensuring that offsetting errors (e.g. +$50 and -$50) don't mask accounting issues.
- **AI Explainability**: Integrates with the Groq API (using a complex system prompt) to automatically analyze each issue and provide a human-readable 1-2 sentence forensic explanation.
- **Custom CSV Uploads**: Features a sleek left-sidebar allowing users to upload their own custom `transactions.csv` and `settlements.csv` data securely for immediate reconciliation.
- **Synthetic Data Generation**: For testing purposes, you can generate sample datasets packed with built-in financial edge cases at the click of a button.
- **Premium Modular Dashboard**: A clean, minimalistic UI built with Tailwind CSS and Chart.js, powered by a heavily modularized ES6 JavaScript architecture.

## Project Structure
- `/app`: Contains core business logic (`generator.py`, `reconciler.py`, `schemas.py`).
- `/templates`: Contains `index.html` (frontend dashboard with sidebar layout).
- `/static`: Contains frontend assets including modular JS (`js/app.js`, `js/api.js`, `js/ui.js`, `js/charts.js`).
- `/data`: Stores generated CSV datasets, uploaded files, and downloadable reports.
- `main.py`: The FastAPI application entry point.
- `render.yaml` & `Procfile`: Infrastructure configuration files for fast cloud deployment.

## Setup Instructions

1. **Install dependencies**
   Ensure you have Python 3.9+ installed.
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   Open the `.env` file and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   *(Note: The system will fall back to automated local explanations if no key is provided.)*

3. **Run Unit Tests**
   To verify the core reconciliation and edge-case detection logic:
   ```bash
   python test_reconciler.py
   ```

4. **Start the Development Server**
   ```bash
   uvicorn main:app --reload
   ```

5. **Access the Dashboard**
   Open your browser and navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## How to Use
1. Use the **Left Sidebar** to upload your own `transactions.csv` and `settlements.csv` files.
2. *(Alternatively)* Click **"Generate Synthetic Data"** under the Testing section to build automated sample datasets.
3. Click **"Run Reconciliation"** in the top navigation bar to execute the Pandas engine and the Groq LLM explanation layer.
4. Review the summary metrics (Gross Discrepancy), visual charts (Transaction Volume per issue type), and highlighted data table.
5. Click **"Download Report"** to export the detailed reconciliation results as JSON.

## Deployment (Render)
This project is configured out-of-the-box for [Render](https://render.com/). 
1. Push this repository to GitHub/GitLab.
2. In your Render Dashboard, click **New > Blueprint**.
3. Connect your repository. Render will automatically read the included `render.yaml` file, provision a Python 3.11 environment, install dependencies, and launch the Uvicorn web server.
*(A `Procfile` is also included for Heroku or alternative PaaS providers).*
