"""
Take in LOS CRM Loan status and Total_Mail_Count data
"""


import os
import pandas as pd
import numpy as np
import re
from datetime import datetime

def classify_campaign(lead_campaign):
    if pd.isna(lead_campaign) or lead_campaign.strip() == "":
        return "NONE"  # Explicitly return "NONE" for missing or blank values

    lc = lead_campaign.strip()

    if re.search(r"(?i)-A($|[^a-zA-Z]|msive| Drop \d+)", lc):
        return "Amsive"
    elif re.search(r"(?i)^CT-|^CRT-|Camber", lc):
        return "Camber"
    elif re.search(r"(?i)-M$|Monster", lc):
        return "Monster"
    elif re.search(r"(?i)^RT|-RS|Redstone", lc):
        return "Redstone"
    elif re.search(r"(?i)Amsive", lc):
        return "Amsive"
    else:
        return "OTHER"
# Function to extract Campaign mailing date
def extract_campaign_date(value):
    if pd.isna(value) or str(value).strip() == "":
        return ""

    s = str(value).strip()

    # 1. MM.DD.YYYY
    match = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", s)
    if match:
        month, day, year = match.groups()
        return format_date(year, month, day)

    # 2. MMDD.YYYY
    match = re.search(r"(\d{4})\.(\d{4})", s)
    if match:
        mmdd, yyyy = match.groups()
        month = mmdd[:2]
        day = mmdd[2:]
        return format_date(yyyy, month, day)

    # 3. MMDD.YY
    match = re.search(r"(\d{4})\.(\d{2})", s)
    if match:
        mmdd, yy = match.groups()
        month = mmdd[:2]
        day = mmdd[2:]
        year = str(2000 + int(yy))
        return format_date(year, month, day)

    # 4. MM.DD.YY
    match = re.search(r"(\d{2})\.(\d{2})\.(\d{2})", s)
    if match:
        month, day, yy = match.groups()
        year = str(2000 + int(yy))
        return format_date(year, month, day)

    # Date for missing values
    return "12/31/9999"

def format_date(year, month, day):
    try:
        dt = datetime(int(year), int(month), int(day))
        return dt.strftime("%-m/%-d/%Y")  # Unix/macOS
    except:
        return ""

def resolve_campaign_name(row):
    campaign = str(row["Lead Campaign Name"]).strip()
    source = str(row["Lead Source Name"]).strip()

    # If one is NONE and the other is OTHER - return OTHER
    if (campaign == "NONE" and source == "OTHER") or (campaign == "OTHER" and source == "NONE"):
        return "OTHER"

    # If campaign is NONE or OTHER - return source
    if campaign in ["NONE", "OTHER"] and source not in ["NONE", "OTHER", ""]:
        return source

    # If source is NONE or OTHER → return campaign
    if source in ["NONE", "OTHER"] and campaign not in ["NONE", "OTHER", ""]:
        return campaign

    # If both are valid → prioritize campaign
    return campaign

def generate_maildata():
    # Define base path to raw data
    raw_dir = os.path.join("..", "..", "data", "raw")

    # Load each file into its own variable
    crm_path = os.path.join(raw_dir, "Leads_CRM.csv")
    los_path = os.path.join(raw_dir, "PipelineMetrics_LOS.csv")
    loanstatus_path = os.path.join(raw_dir, "Loanstatus.csv")
    totalmail_path = os.path.join(raw_dir, "Total_Mail_Count.csv")

    df_crm = pd.read_csv(crm_path)
    df_los = pd.read_csv(los_path)
    df_loanstatus = pd.read_csv(loanstatus_path)
    df_totalmail = pd.read_csv(totalmail_path)
    # Function to extract Campaign company names

    # Create 'Name' column 
    df_crm["Name"] = df_crm["Last Name"].str.strip() + ", " + df_crm["First Name"].str.strip()
    df_los["Name"] = df_los["Borrower Name (App#)"]

    # Lead Campaign Name in LOS is derived by matching Lead Source name from CRM
    mapping = (
        df_crm[["Lead Source", "Lead Campaign"]]
        .drop_duplicates(subset="Lead Source", keep="first")
        .set_index("Lead Source")["Lead Campaign"]
    )

    df_los["Lead Campaign"] = df_los["Lead Source"].map(mapping)

    # Create Lead Campaign Name and Lead Source Name columns in CRM
    df_crm["Lead Campaign Name"] = df_crm["Lead Campaign"].apply(classify_campaign)
    df_crm["Lead Source Name"] = df_crm["Lead Source"].apply(classify_campaign)

    # Create Lead Campaign Name and Lead Source Name columns in LOS
    df_los["Lead Campaign Name"] = df_los["Lead Campaign"].apply(classify_campaign)
    df_los["Lead Source Name"] = df_los["Lead Source"].apply(classify_campaign)

    # Create Lead Campaign Date in CRM
    df_crm["Lead Campaign Date"] = df_crm["Lead Campaign"].apply(extract_campaign_date)
    # Create Lead Source Date in CRM
    df_crm["Lead Source Date"] = df_crm["Lead Source"].apply(extract_campaign_date)

    # Create Lead Campaign Date in LOS
    df_los["Lead Campaign Date"] = df_los["Lead Campaign"].apply(extract_campaign_date)
    # Create Lead Source Date in LOS
    df_los["Lead Source Date"] = df_los["Lead Source"].apply(extract_campaign_date)

    # Create Campaign Name from Lead Campaign Name and Lead Source Name
    df_crm["Campaign Name"] = df_crm.apply(resolve_campaign_name, axis=1)
    df_los["Campaign Name"] = df_los.apply(resolve_campaign_name, axis=1)
    df_totalmail.rename(columns={"Campaign Source": "Campaign Name"}, inplace=True)

    # Create Mail Date from Lead Campaign Date and Lead Source Date
    df_crm["Mail Date"] = df_crm[["Lead Campaign Date", "Lead Source Date"]].min(axis=1)
    df_los["Mail Date"] = df_los[["Lead Campaign Date", "Lead Source Date"]].min(axis=1)

    # Loan Officer column (Already exists in LOS)
    df_crm["Loan Officer"] = (
        df_crm["Lead Contact"]
        .astype(str)
        .str.strip()
        .str.extract(r"^\s*(.*?),\s*(.*?)\s*$")  # Extract Last and First
        .apply(lambda x: f"{x[1]} {x[0]}" if pd.notna(x[0]) and pd.notna(x[1]) else "", axis=1)
    )

    # 'Created On' will be used for call counts
    df_crm["Call Date str"] = df_crm["Created On"].astype(str).str[:10]
    df_crm["Call Date"] = pd.to_datetime(df_crm["Call Date str"], errors="coerce")

    df_crm_clean = df_crm[["Name","Campaign Name", "Mail Date",  "Loan Officer", "Call Date"]].copy()
    df_los_clean = df_los[["Name","Campaign Name", "Mail Date",   "Loan Officer"]].copy()
    # merge CRM and LOS to get all calls
    df_calls = pd.concat(
        [df_crm_clean[df_los_clean.columns], df_los_clean],
        ignore_index=True
    )
    df_calls_total = df_calls.merge(
        df_totalmail,
        on=["Campaign Name", "Mail Date"],
        how="left"
    )
    df_totalmail["Mail Date"] = pd.to_datetime(df_totalmail["Mail Date"], errors="coerce")
    df_calls["Mail Date"] = pd.to_datetime(df_calls["Mail Date"], errors="coerce")
    df_calls_total["Mail Date"] = pd.to_datetime(df_calls_total["Mail Date"], errors="coerce")

    df_loanstatus_modded = df_loanstatus.copy()

    df_loanstatus_modded.rename(columns={"Borrower": "Name"}, inplace=True)
    df_loanstatus_modded.rename(columns={"primaryRoleContact": "Loan Officer"}, inplace=True)

    df_loanstatus_modded["Campaign Name"] = df_loanstatus_modded["leadSource"].apply(classify_campaign)
    df_loanstatus_modded["Mail Date"] = df_loanstatus_modded["leadSource"].apply(extract_campaign_date)

    # Creates funded column
    df_loanstatus_modded["funded_flag"] = df_loanstatus_modded["loanStatusName"].str.lower().str.contains("funded", na=False).astype(int)
    # Create withdrawn flag
    df_loanstatus_modded["withdrawn_flag"] = df_loanstatus_modded["loanStatusName"].str.lower().str.contains("withdrawn", na=False).astype(int)
    # Create Locked Not Submitted flag
    df_loanstatus_modded["locked_not_submitted_flag"] = df_loanstatus_modded["loanStatusName"].str.lower().str.contains("locked not submitted", na=False).astype(int)
    # Total 
    df_loanstatus_modded["total"] = df_loanstatus_modded["funded_flag"] + df_loanstatus_modded["withdrawn_flag"] + df_loanstatus_modded["locked_not_submitted_flag"]



    df_loanstatus_modded_clean  = df_loanstatus_modded[["Name", "loanStatusName","Campaign Name", "Mail Date", "funded_flag", "withdrawn_flag" , "locked_not_submitted_flag", "total",  "Loan Officer"]].copy()

    df_loanstatus_modded_clean["Mail Date"] = pd.to_datetime(df_loanstatus_modded_clean["Mail Date"], errors="coerce")

    # Group by 'Campaign Name' and 'Mail Date', then sum the relevant flags to create loan status stats 
    FundedStats = df_loanstatus_modded_clean.groupby(["Campaign Name", "Mail Date"], as_index=False).agg({
        "funded_flag": "sum",
        "withdrawn_flag": "sum",
        "locked_not_submitted_flag": "sum",
        "total": "sum"
    })

    # Rename columns for clarity
    FundedStats.rename(columns={
        "funded_flag": "Funded",
        "withdrawn_flag": "Withdrawn",
        "locked_not_submitted_flag": "LockedNotSubmitted",
        "total": "Locks"
    }, inplace=True)


    MailData_prep = (
        df_calls_total
        .groupby(["Campaign Name", "Mail Date"], as_index=False)
        .agg({
            "Total Mail Pieces": "first",    
            "Mail Type": "first"            
        })
    )

    # Add the count of rows per group as 'Calls'
    MailData_prep["Calls"] = (
        df_calls_total
        .groupby(["Campaign Name", "Mail Date"])
        .size()
        .values  # aligns with MailData rows
    )

    # Optional: sort for presentation
    MailData_prep.sort_values(by=["Campaign Name", "Mail Date"], inplace=True)

    # Final column order
    MailData_prep = MailData_prep[["Campaign Name", "Mail Date", "Total Mail Pieces", "Calls", "Mail Type"]]
    # Ensure both Mail Date columns are datetime
    MailData_prep["Mail Date"] = pd.to_datetime(MailData_prep["Mail Date"], errors="coerce")
    FundedStats["Mail Date"] = pd.to_datetime(FundedStats["Mail Date"], errors="coerce")

    # Now merge safely
    MailData = MailData_prep.merge(FundedStats, on=["Campaign Name", "Mail Date"], how="left")
    MailData.sort_values(by=["Campaign Name", "Mail Date"], inplace=True)
    numeric_cols = ["Calls", "Funded", "Withdrawn", "LockedNotSubmitted", "Locks"]
    MailData[numeric_cols] = MailData[numeric_cols].fillna(0)
    MailData[numeric_cols] = MailData[numeric_cols].astype(int)


    # Response Rate = Calls / Total Mail Pieces
    MailData["Response Rate"] = np.where(
        (MailData["Total Mail Pieces"].isna()) | (MailData["Total Mail Pieces"] == 0),
        0,
        MailData["Calls"] / MailData["Total Mail Pieces"]
    ).round(4)

    # Calls to Lock = LockedNotSubmitted / Calls
    MailData["Calls to Lock"] = np.where(
        (MailData["Calls"] == 0),
        0,
        MailData["Locks"] / MailData["Calls"]
    ).round(4)

    # Lock to Fund = Funded / LockedNotSubmitted
    MailData["Lock to Fund"] = np.where(
        (MailData["Locks"] == 0),
        0,
        MailData["Funded"] / MailData["Locks"]
    ).round(4)

    MailData["Total Mail Pieces"] = MailData["Total Mail Pieces"].fillna(0).astype(int)

    return MailData