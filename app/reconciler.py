import pandas as pd
import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def explain_issues(issues):
    if not GROQ_API_KEY or not issues:
        for issue in issues:
            issue["explanation"] = f"Automated fallback explanation: {issue['description']}"
        return issues
        
    client = Groq(api_key=GROQ_API_KEY)
    
    # We will process issues in batches or one by one. For cost/speed, let's batch up to 10 at a time.
    # To keep it simple, let's formulate a JSON prompt.
    prompt_data = [{"txn_id": i["txn_id"], "issue_type": i["issue_type"], "description": i["description"]} for i in issues]
    
    system_prompt = """
    You are an expert financial reconciliation system. 
    Given a list of transaction reconciliation issues, provide a 1-2 sentence clear, professional explanation for each issue suitable for a finance dashboard.
    Return ONLY a valid JSON array of objects, where each object has 'txn_id' and 'explanation'.
    """
    
    user_prompt = f"Here are the issues: {json.dumps(prompt_data)}"
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        # Groq with JSON mode requires the output to be a json object. 
        # So we should ask for an object with an 'explanations' key containing the array.
        # Let me adjust the prompt logic.
        pass
    except Exception as e:
        print(f"Groq API Error: {e}")
        for issue in issues:
            issue["explanation"] = f"Failed to generate explanation. Error: {str(e)}"
        return issues

    return issues

def explain_issues_fixed(issues):
    if not GROQ_API_KEY or not issues:
        for issue in issues:
            issue["explanation"] = f"Automated explanation: {issue['description']} (No Groq Key)"
        return issues
        
    client = Groq(api_key=GROQ_API_KEY)
    prompt_data = [{"txn_id": i["txn_id"], "issue_type": i["issue_type"], "description": i["description"]} for i in issues]
    
    system_prompt = """
    You are a forensic financial data analyst. You are analyzing discrepancies between platform transactions and bank settlements.
    You will receive a list of issues. For each issue, provide a concise, clear 1-2 sentence explanation.
    You must output a JSON object with a single key "explanations" containing a list of objects with "txn_id" and "explanation".
    Ensure the explanation sounds professional.
    """
    
    user_prompt = f"Issues to explain: {json.dumps(prompt_data)}"
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        result_str = response.choices[0].message.content
        result_json = json.loads(result_str)
        explanations_dict = {item["txn_id"]: item["explanation"] for item in result_json.get("explanations", [])}
        
        for issue in issues:
            issue["explanation"] = explanations_dict.get(issue["txn_id"], "Explanation unavailable.")
            
    except Exception as e:
        print(f"Groq API Error: {e}")
        for issue in issues:
            issue["explanation"] = f"Error generating explanation: {e}"
            
    return issues


def reconcile_data(tx_path: str, set_path: str):
    df_tx = pd.read_csv(tx_path)
    df_set = pd.read_csv(set_path)
    
    # Identify duplicates in transactions
    dup_mask = df_tx.duplicated(subset=['txn_id'], keep=False)
    duplicates_df = df_tx[dup_mask]
    
    # We will work with a deduplicated version for joining, but record duplicates
    df_tx_unique = df_tx.drop_duplicates(subset=['txn_id'])
    
    merged = pd.merge(df_tx_unique, df_set, on="txn_id", how="outer", indicator=True)
    
    issues = []
    
    # 1. Duplicates
    processed_dups = set()
    for _, row in duplicates_df.iterrows():
        if row["txn_id"] not in processed_dups:
            issues.append({
                "txn_id": row["txn_id"],
                "issue_type": "Duplicate Transaction",
                "description": "Transaction ID appears multiple times in platform records.",
                "platform_amount": float(row["amount"]),
                "bank_amount": None
            })
            processed_dups.add(row["txn_id"])
            
    # 2. Missing Settlements
    missing = merged[merged["_merge"] == "left_only"]
    for _, row in missing.iterrows():
        # Might be a refund without original
        if str(row["type"]).lower() == "refund":
            issue_type = "Refund Inconsistency"
            desc = "Refund issued on platform without a corresponding bank settlement."
        else:
            issue_type = "Missing Settlement"
            desc = "Transaction recorded on platform but not settled by bank."
            
        # exclude duplicates already logged
        if row["txn_id"] not in processed_dups:
            issues.append({
                "txn_id": row["txn_id"],
                "issue_type": issue_type,
                "description": desc,
                "platform_amount": float(row["amount"]),
                "bank_amount": None
            })
            
    # 3. Extra Settlements
    extra = merged[merged["_merge"] == "right_only"]
    for _, row in extra.iterrows():
        issues.append({
            "txn_id": row["txn_id"],
            "issue_type": "Extra Settlement",
            "description": "Bank settled a transaction not found in platform records.",
            "platform_amount": None,
            "bank_amount": float(row["settled_amount"])
        })
        
    # 4. Mismatches and Delayed
    both = merged[merged["_merge"] == "both"]
    for _, row in both.iterrows():
        txn_id = row["txn_id"]
        p_amount = float(row["amount"])
        b_amount = float(row["settled_amount"])
        
        # Amount mismatch
        if round(p_amount, 2) != round(b_amount, 2):
            issues.append({
                "txn_id": txn_id,
                "issue_type": "Amount Mismatch",
                "description": f"Platform amount ({p_amount}) differs from bank settlement ({b_amount}).",
                "platform_amount": p_amount,
                "bank_amount": b_amount
            })
            
        # Delayed (Cross month)
        p_date = str(row["date"])
        b_date = str(row["settlement_date"])
        if p_date and b_date and p_date != 'nan' and b_date != 'nan':
            p_month = p_date[:7] # YYYY-MM
            b_month = b_date[:7]
            if p_month != b_month:
                issues.append({
                    "txn_id": txn_id,
                    "issue_type": "Delayed Settlement",
                    "description": f"Transaction in {p_month} settled in {b_month}.",
                    "platform_amount": p_amount,
                    "bank_amount": b_amount
                })
                
    # Explain via AI
    issues = explain_issues_fixed(issues)
    
    # Calculate gross mismatch amount from issues
    gross_mismatch = 0.0
    for issue in issues:
        p_amt = abs(issue.get("platform_amount") or 0.0)
        b_amt = abs(issue.get("bank_amount") or 0.0)
        
        if issue["issue_type"] == "Amount Mismatch":
            gross_mismatch += abs(p_amt - b_amt)
        elif issue["issue_type"] == "Delayed Settlement":
            pass # No monetary loss, just timing
        else:
            # For missing, extra, refund, duplicate, the full value is the mismatch
            gross_mismatch += max(p_amt, b_amt)

    summary = {
        "total_transactions": int(len(df_tx)),
        "total_settlements": int(len(df_set)),
        "total_mismatch_amount": float(gross_mismatch),
        "issues_count": len(issues)
    }
    
    return {
        "summary": summary,
        "issues": issues
    }
