# # Normalize & Score - Complete Implementation
# import pandas as pd
# import numpy as np
# from datetime import datetime
# from pathlib import Path
# import json
# from aps_config import REQUIRED_HEADERS, ENGINE_DIR

# def load_vendor_aliases():
#     """Load vendor column aliases from JSON"""
#     alias_path = ENGINE_DIR.parent / "aliases" / "vendor_alias_map.json"
#     if not alias_path.exists():
#         # Fallback to basic aliases if file missing
#         return {
#             "property_value": ["EstValue", "AVM", "Estimated Value", "Value", "Property Value"],
#             "loan_balance": ["TotalLoanBal", "Loan Balance", "Total Loan Balance"],
#             "loan_date": ["LastLoanDate", "Last Refi Date", "Loan Date", "Recording Date"],
#             "property_address": ["Property Address", "PropertyAddress", "Address"],
#             "city": ["City", "CITY"],
#             "state": ["State", "STATE"],
#             "zip": ["ZIP", "Zip", "ZIP Code"],
#             "owner_name": ["Owner Name", "OwnerName", "Owner"],
#             "mailing_address": ["Mail Address", "Mailing Address"]
#         }
    
#     with open(alias_path, 'r', encoding='utf-8') as f:
#         return json.load(f)

# def normalize_column_names(df, aliases):
#     """Map vendor column names to standardized names"""
#     column_mapping = {}
    
#     for normalized_name, vendor_variations in aliases.items():
#         if normalized_name == 'notes':
#             continue
        
#         for col in df.columns:
#             if col in vendor_variations:
#                 column_mapping[col] = normalized_name
#                 break
    
#     df_normalized = df.rename(columns=column_mapping)
#     return df_normalized

# def clean_numeric_field(series):
#     """Clean numeric fields - remove $, commas, convert to float"""
#     if series.dtype == object:
#         return pd.to_numeric(
#             series.astype(str).str.replace('$', '').str.replace(',', '').str.strip(),
#             errors='coerce'
#         )
#     return pd.to_numeric(series, errors='coerce')

# def parse_date_field(series):
#     """Parse date field with multiple format support"""
#     def parse_single_date(date_str):
#         if pd.isna(date_str) or date_str == '':
#             return pd.NaT
        
#         # Try multiple date formats
#         formats = ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y', '%Y/%m/%d']
#         for fmt in formats:
#             try:
#                 return pd.to_datetime(date_str, format=fmt)
#             except:
#                 continue
        
#         # Try pandas auto-parse as last resort
#         try:
#             return pd.to_datetime(date_str)
#         except:
#             return pd.NaT
    
#     return series.apply(parse_single_date)

# def calculate_loan_age_months(loan_date_series):
#     """Calculate months since loan date"""
#     today = datetime.now()
    
#     def months_diff(loan_date):
#         if pd.isna(loan_date):
#             return np.nan
        
#         years_diff = today.year - loan_date.year
#         months_diff = today.month - loan_date.month
#         total_months = years_diff * 12 + months_diff
        
#         return max(0, total_months)
    
#     return loan_date_series.apply(months_diff)

# def calculate_aps_score(df):
#     """
#     APS Score v2.0 Formula (0-100 scale):
#     - Equity Weight: 40%
#     - Loan Age Weight: 30% (sweet spot: 18-36 months)
#     - LTV Weight: 30% (lower is better)
#     """
    
#     # Normalize equity % to 0-100 scale (higher equity = higher score)
#     equity_score = df['Equity %'].fillna(0).clip(0, 100)
    
#     # Loan age score (optimal range: 18-36 months)
#     def age_score(months):
#         if pd.isna(months):
#             return 0
#         if months < 18:
#             return (months / 18) * 50  # Ramp up to 50
#         elif months <= 36:
#             return 100  # Sweet spot
#         elif months <= 60:
#             return 100 - ((months - 36) / 24) * 30  # Decay to 70
#         else:
#             return max(40, 70 - ((months - 60) / 60) * 30)  # Further decay
    
#     loan_age_score = df['Loan_Age_Mo'].apply(age_score)
    
#     # LTV score (lower LTV = higher score)
#     ltv_score = 100 - df['LTV %'].fillna(100).clip(0, 100)
    
#     # Weighted combination
#     aps_score = (
#         equity_score * 0.40 +
#         loan_age_score * 0.30 +
#         ltv_score * 0.30
#     )
    
#     return aps_score.round(1)

# def assign_tier(row):
#     """
#     Assign APS Tier based on score and characteristics:
#     - Platinum: APS Score >= 80, LTV <= 30%, Equity >= $500K
#     - Gold: APS Score >= 65, LTV <= 50%, Equity >= $300K
#     - Silver: APS Score >= 50, LTV <= 65%, Equity >= $200K
#     - Nurture: Everything else
#     """
#     score = row['APS_Score (v2.0)']
#     ltv = row['LTV %']
#     equity_dollars = row.get('Equity_Dollars', 0)
    
#     if pd.isna(score) or pd.isna(ltv):
#         return 'Nurture'
    
#     if score >= 80 and ltv <= 30 and equity_dollars >= 500000:
#         return 'Platinum'
#     elif score >= 65 and ltv <= 50 and equity_dollars >= 300000:
#         return 'Gold'
#     elif score >= 50 and ltv <= 65 and equity_dollars >= 200000:
#         return 'Silver'
#     else:
#         return 'Nurture'

# def calculate_cci(row):
#     """
#     CCI - Credit Confidence Index (0-100 scale)
#     Factors: Equity stability, LTV health, Loan age maturity
#     """
#     equity_pct = row['Equity %']
#     ltv_pct = row['LTV %']
#     loan_age = row['Loan_Age_Mo']
    
#     if pd.isna(equity_pct) or pd.isna(ltv_pct) or pd.isna(loan_age):
#         return 0.0
    
#     # Equity component (0-40 points)
#     equity_component = min(40, (equity_pct / 100) * 40)
    
#     # LTV component (0-35 points) - lower is better
#     ltv_component = max(0, 35 - (ltv_pct / 100) * 35)
    
#     # Loan age component (0-25 points) - stability indicator
#     if loan_age >= 18:
#         age_component = min(25, 25 * (loan_age / 60))
#     else:
#         age_component = (loan_age / 18) * 15
    
#     cci = equity_component + ltv_component + age_component
    
#     return round(cci, 1)

# def normalize_and_score(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Main normalization and scoring function
#     Steps:
#     1. Load aliases and normalize column names
#     2. Clean numeric fields
#     3. Parse date fields
#     4. Calculate derived fields (LTV, Equity, Loan Age)
#     5. Calculate APS Score v2.0
#     6. Assign APS Tier
#     7. Calculate CCI
#     """
    
#     # Step 1: Load aliases and normalize columns
#     aliases = load_vendor_aliases()
#     df = normalize_column_names(df, aliases)
    
#     # Step 2: Clean numeric fields
#     if 'property_value' in df.columns:
#         df['property_value'] = clean_numeric_field(df['property_value'])
#     elif 'EstValue' in df.columns:
#         df['property_value'] = clean_numeric_field(df['EstValue'])
    
#     if 'loan_balance' in df.columns:
#         df['loan_balance'] = clean_numeric_field(df['loan_balance'])
#     elif 'TotalLoanBal' in df.columns:
#         df['loan_balance'] = clean_numeric_field(df['TotalLoanBal'])
    
#     # Step 3: Parse date field
#     if 'loan_date' in df.columns:
#         df['loan_date'] = parse_date_field(df['loan_date'])
    
#     # Step 4: Calculate derived fields
    
#     # LTV % = (Loan Balance / Property Value) * 100
#     if 'property_value' in df.columns and 'loan_balance' in df.columns:
#         df['LTV %'] = ((df['loan_balance'] / df['property_value']) * 100).round(2)
#         df['LTV %'] = df['LTV %'].fillna(0).clip(0, 100)
#     else:
#         df['LTV %'] = 0.0
    
#     # Equity % = 100 - LTV %
#     df['Equity %'] = (100 - df['LTV %']).round(2)
    
#     # Equity Dollars
#     if 'property_value' in df.columns:
#         df['Equity_Dollars'] = (df['property_value'] * (df['Equity %'] / 100)).round(0)
#     else:
#         df['Equity_Dollars'] = 0
    
#     # Loan Age in Months
#     if 'loan_date' in df.columns:
#         df['Loan_Age_Mo'] = calculate_loan_age_months(df['loan_date'])
#     else:
#         df['Loan_Age_Mo'] = 0
    
#     # Step 5: Calculate APS Score v2.0
#     df['APS_Score (v2.0)'] = calculate_aps_score(df)
    
#     # Step 6: Assign APS Tier
#     df['APS_Tier'] = df.apply(assign_tier, axis=1)
    
#     # Step 7: Calculate CCI
#     df['CCI'] = df.apply(calculate_cci, axis=1)
    
#     # Rename columns to match required headers
#     column_rename_map = {
#         'owner_name': 'Owner Name',
#         'mailing_address': 'Mail Address',
#         'property_address': 'Property Address',
#         'city': 'City',
#         'state': 'State',
#         'zip': 'ZIP',
#         'property_value': 'EstValue',
#         'loan_balance': 'TotalLoanBal',
#         'loan_date': 'LastLoanDate'
#     }
    
#     df = df.rename(columns=column_rename_map)
    
#     # Ensure all required columns exist
#     for col in REQUIRED_HEADERS:
#         if col not in df.columns:
#             df[col] = ''
    
#     return df



























# Normalize & Score - Complete Implementation (Fixed)
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import json
from aps_config import REQUIRED_HEADERS, ENGINE_DIR

def normalize_and_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main normalization and scoring function
    Handles both normalized and raw vendor column names
    """
    
    # Create working columns with consistent names
    # Property Value
    if 'EstValue' in df.columns:
        df['_property_value'] = pd.to_numeric(df['EstValue'].astype(str).str.replace('$', '').str.replace(',', '').str.strip(), errors='coerce')
    elif 'property_value' in df.columns:
        df['_property_value'] = pd.to_numeric(df['property_value'].astype(str).str.replace('$', '').str.replace(',', '').str.strip(), errors='coerce')
    else:
        df['_property_value'] = 0
    
    # Loan Balance
    if 'TotalLoanBal' in df.columns:
        df['_loan_balance'] = pd.to_numeric(df['TotalLoanBal'].astype(str).str.replace('$', '').str.replace(',', '').str.strip(), errors='coerce')
    elif 'loan_balance' in df.columns:
        df['_loan_balance'] = pd.to_numeric(df['loan_balance'].astype(str).str.replace('$', '').str.replace(',', '').str.strip(), errors='coerce')
    else:
        df['_loan_balance'] = 0
    
    # Loan Date
    if 'LastLoanDate' in df.columns:
        df['_loan_date'] = pd.to_datetime(df['LastLoanDate'], errors='coerce')
    elif 'loan_date' in df.columns:
        df['_loan_date'] = pd.to_datetime(df['loan_date'], errors='coerce')
    else:
        df['_loan_date'] = pd.NaT
    
    # Calculate LTV %
    df['LTV %'] = ((df['_loan_balance'] / df['_property_value']) * 100).round(2)
    df['LTV %'] = df['LTV %'].fillna(0).clip(0, 100)
    
    # Calculate Equity %
    df['Equity %'] = (100 - df['LTV %']).round(2)
    
    # Calculate Equity Dollars
    df['Equity_Dollars'] = (df['_property_value'] * (df['Equity %'] / 100)).round(0)
    
    # Calculate Loan Age in Months
    def calculate_months(loan_date):
        if pd.isna(loan_date):
            return 0
        today = datetime.now()
        years_diff = today.year - loan_date.year
        months_diff = today.month - loan_date.month
        total_months = years_diff * 12 + months_diff
        return max(0, total_months)
    
    df['Loan_Age_Mo'] = df['_loan_date'].apply(calculate_months)
    
    # Calculate APS Score v2.0
    def calculate_aps_score(row):
        equity_pct = row['Equity %']
        loan_age = row['Loan_Age_Mo']
        ltv_pct = row['LTV %']
        
        # Equity component (0-100)
        equity_score = equity_pct
        
        # Loan age component (optimal 18-36 months)
        if loan_age < 18:
            age_score = (loan_age / 18) * 50
        elif loan_age <= 36:
            age_score = 100
        elif loan_age <= 60:
            age_score = 100 - ((loan_age - 36) / 24) * 30
        else:
            age_score = max(40, 70 - ((loan_age - 60) / 60) * 30)
        
        # LTV component (lower is better)
        ltv_score = 100 - ltv_pct
        
        # Weighted combination
        aps_score = (equity_score * 0.40 + age_score * 0.30 + ltv_score * 0.30)
        return round(aps_score, 1)
    
    df['APS_Score (v2.0)'] = df.apply(calculate_aps_score, axis=1)
    
    # Assign APS Tier
    def assign_tier(row):
        score = row['APS_Score (v2.0)']
        ltv = row['LTV %']
        equity_dollars = row['Equity_Dollars']
        
        if score >= 80 and ltv <= 30 and equity_dollars >= 500000:
            return 'Platinum'
        elif score >= 65 and ltv <= 50 and equity_dollars >= 300000:
            return 'Gold'
        elif score >= 50 and ltv <= 65 and equity_dollars >= 200000:
            return 'Silver'
        else:
            return 'Nurture'
    
    df['APS_Tier'] = df.apply(assign_tier, axis=1)
    
    # Calculate CCI (Credit Confidence Index)
    def calculate_cci(row):
        equity_pct = row['Equity %']
        ltv_pct = row['LTV %']
        loan_age = row['Loan_Age_Mo']
        
        # Equity component (0-40 points)
        equity_component = min(40, (equity_pct / 100) * 40)
        
        # LTV component (0-35 points)
        ltv_component = max(0, 35 - (ltv_pct / 100) * 35)
        
        # Loan age component (0-25 points)
        if loan_age >= 18:
            age_component = min(25, 25 * (loan_age / 60))
        else:
            age_component = (loan_age / 18) * 15
        
        cci = equity_component + ltv_component + age_component
        return round(cci, 1)
    
    df['CCI'] = df.apply(calculate_cci, axis=1)
    
    # Clean up temporary columns
    df = df.drop(columns=['_property_value', '_loan_balance', '_loan_date'], errors='ignore')
    
    return df