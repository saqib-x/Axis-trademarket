# 18-Point Health Check - Complete Implementation
import pandas as pd
import numpy as np
from datetime import datetime

def health_check(df):
    """
    18-Point comprehensive data quality health check
    Returns dict with check name and status (PASS/WARN/FAIL + details)
    """
    
    checks = {}
    total_records = len(df)
    
    # ===== 1. Record Count Check =====
    checks['1_Record_Count'] = {
        'status': 'PASS' if total_records > 0 else 'FAIL',
        'value': total_records,
        'message': f'{total_records} records found'
    }
    
    # ===== 2. Address Completeness =====
    if 'Property Address' in df.columns:
        address_complete = df['Property Address'].notna().sum()
        address_pct = (address_complete / total_records * 100) if total_records > 0 else 0
        checks['2_Address_Completeness'] = {
            'status': 'PASS' if address_pct >= 95 else 'WARN' if address_pct >= 80 else 'FAIL',
            'value': f'{address_pct:.1f}%',
            'message': f'{address_complete}/{total_records} addresses present'
        }
    else:
        checks['2_Address_Completeness'] = {'status': 'FAIL', 'value': '0%', 'message': 'Column missing'}
    
    # ===== 3. ZIP Code Validity =====
    if 'ZIP' in df.columns:
        valid_zips = df['ZIP'].astype(str).str.match(r'^\d{5}$').sum()
        zip_pct = (valid_zips / total_records * 100) if total_records > 0 else 0
        checks['3_ZIP_Validity'] = {
            'status': 'PASS' if zip_pct >= 95 else 'WARN' if zip_pct >= 80 else 'FAIL',
            'value': f'{zip_pct:.1f}%',
            'message': f'{valid_zips}/{total_records} valid 5-digit ZIPs'
        }
    else:
        checks['3_ZIP_Validity'] = {'status': 'FAIL', 'value': '0%', 'message': 'Column missing'}
    
    # ===== 4. Property Value Range Check =====
    value_col = 'EstValue' if 'EstValue' in df.columns else 'property_value'
    if value_col in df.columns:
        value_numeric = pd.to_numeric(df[value_col], errors='coerce')
        valid_values = ((value_numeric >= 50000) & (value_numeric <= 10000000)).sum()
        value_pct = (valid_values / total_records * 100) if total_records > 0 else 0
        median_value = value_numeric.median()
        checks['4_Property_Value_Range'] = {
            'status': 'PASS' if value_pct >= 90 else 'WARN' if value_pct >= 70 else 'FAIL',
            'value': f'${median_value:,.0f}' if not pd.isna(median_value) else 'N/A',
            'message': f'{valid_values}/{total_records} values in $50K-$10M range'
        }
    else:
        checks['4_Property_Value_Range'] = {'status': 'FAIL', 'value': 'N/A', 'message': 'Column missing'}
    
    # ===== 5. LTV Range Check (0-100%) =====
    if 'LTV %' in df.columns:
        ltv_valid = ((df['LTV %'] >= 0) & (df['LTV %'] <= 100)).sum()
        ltv_pct = (ltv_valid / total_records * 100) if total_records > 0 else 0
        median_ltv = df['LTV %'].median()
        checks['5_LTV_Range'] = {
            'status': 'PASS' if ltv_pct >= 95 else 'WARN' if ltv_pct >= 80 else 'FAIL',
            'value': f'{median_ltv:.1f}%' if not pd.isna(median_ltv) else 'N/A',
            'message': f'{ltv_valid}/{total_records} LTV values 0-100%'
        }
    else:
        checks['5_LTV_Range'] = {'status': 'FAIL', 'value': 'N/A', 'message': 'Column missing'}
    
    # ===== 6. Equity % Accuracy Check =====
    if 'Equity %' in df.columns and 'LTV %' in df.columns:
        equity_accuracy = (abs((df['Equity %'] + df['LTV %']) - 100) < 1).sum()
        equity_pct = (equity_accuracy / total_records * 100) if total_records > 0 else 0
        checks['6_Equity_Accuracy'] = {
            'status': 'PASS' if equity_pct >= 95 else 'WARN' if equity_pct >= 80 else 'FAIL',
            'value': f'{equity_pct:.1f}%',
            'message': f'{equity_accuracy}/{total_records} records: Equity% + LTV% = 100%'
        }
    else:
        checks['6_Equity_Accuracy'] = {'status': 'FAIL', 'value': 'N/A', 'message': 'Required columns missing'}
    
    # ===== 7. Loan Date Format Check =====
    date_col = 'LastLoanDate' if 'LastLoanDate' in df.columns else 'loan_date'
    if date_col in df.columns:
        valid_dates = pd.to_datetime(df[date_col], errors='coerce').notna().sum()
        date_pct = (valid_dates / total_records * 100) if total_records > 0 else 0
        checks['7_Loan_Date_Format'] = {
            'status': 'PASS' if date_pct >= 90 else 'WARN' if date_pct >= 70 else 'FAIL',
            'value': f'{date_pct:.1f}%',
            'message': f'{valid_dates}/{total_records} parseable dates'
        }
    else:
        checks['7_Loan_Date_Format'] = {'status': 'FAIL', 'value': '0%', 'message': 'Column missing'}
    
    # ===== 8. Loan Age Reasonableness =====
    if 'Loan_Age_Mo' in df.columns:
        reasonable_age = ((df['Loan_Age_Mo'] >= 0) & (df['Loan_Age_Mo'] <= 360)).sum()
        age_pct = (reasonable_age / total_records * 100) if total_records > 0 else 0
        median_age = df['Loan_Age_Mo'].median()
        checks['8_Loan_Age_Reasonable'] = {
            'status': 'PASS' if age_pct >= 95 else 'WARN' if age_pct >= 80 else 'FAIL',
            'value': f'{median_age:.0f} mo' if not pd.isna(median_age) else 'N/A',
            'message': f'{reasonable_age}/{total_records} ages 0-360 months'
        }
    else:
        checks['8_Loan_Age_Reasonable'] = {'status': 'FAIL', 'value': 'N/A', 'message': 'Column missing'}
    
    # ===== 9. Duplicate Detection =====
    if 'Property Address' in df.columns and 'ZIP' in df.columns:
        duplicates = df.duplicated(subset=['Property Address', 'ZIP'], keep=False).sum()
        dup_pct = (duplicates / total_records * 100) if total_records > 0 else 0
        checks['9_Duplicate_Detection'] = {
            'status': 'PASS' if dup_pct == 0 else 'WARN' if dup_pct < 5 else 'FAIL',
            'value': f'{duplicates}',
            'message': f'{duplicates} potential duplicate records ({dup_pct:.1f}%)'
        }
    else:
        checks['9_Duplicate_Detection'] = {'status': 'WARN', 'value': 'N/A', 'message': 'Cannot check - missing columns'}
    
    # ===== 10. Missing Value Count =====
    missing_critical = 0
    critical_cols = ['Property Address', 'ZIP', 'EstValue', 'TotalLoanBal', 'LastLoanDate']
    for col in critical_cols:
        if col in df.columns:
            missing_critical += df[col].isna().sum()
    
    missing_pct = (missing_critical / (total_records * len(critical_cols)) * 100) if total_records > 0 else 0
    checks['10_Missing_Values'] = {
        'status': 'PASS' if missing_pct < 5 else 'WARN' if missing_pct < 15 else 'FAIL',
        'value': f'{missing_critical}',
        'message': f'{missing_pct:.1f}% missing in critical fields'
    }
    
    # ===== 11. APS Score Distribution =====
    if 'APS_Score (v2.0)' in df.columns:
        valid_scores = ((df['APS_Score (v2.0)'] >= 0) & (df['APS_Score (v2.0)'] <= 100)).sum()
        score_pct = (valid_scores / total_records * 100) if total_records > 0 else 0
        median_score = df['APS_Score (v2.0)'].median()
        checks['11_APS_Score_Distribution'] = {
            'status': 'PASS' if score_pct >= 95 else 'WARN',
            'value': f'{median_score:.1f}' if not pd.isna(median_score) else 'N/A',
            'message': f'{valid_scores}/{total_records} scores in 0-100 range'
        }
    else:
        checks['11_APS_Score_Distribution'] = {'status': 'FAIL', 'value': 'N/A', 'message': 'Column missing'}
    
    # ===== 12. Tier Assignment Coverage =====
    if 'APS_Tier' in df.columns:
        valid_tiers = df['APS_Tier'].isin(['Platinum', 'Gold', 'Silver', 'Nurture']).sum()
        tier_pct = (valid_tiers / total_records * 100) if total_records > 0 else 0
        tier_dist = df['APS_Tier'].value_counts().to_dict()
        checks['12_Tier_Assignment'] = {
            'status': 'PASS' if tier_pct >= 95 else 'WARN',
            'value': f'{tier_pct:.1f}%',
            'message': f'Distribution: {tier_dist}'
        }
    else:
        checks['12_Tier_Assignment'] = {'status': 'FAIL', 'value': 'N/A', 'message': 'Column missing'}
    
    # ===== 13. CCI Index Validity =====
    if 'CCI' in df.columns:
        valid_cci = ((df['CCI'] >= 0) & (df['CCI'] <= 100)).sum()
        cci_pct = (valid_cci / total_records * 100) if total_records > 0 else 0
        median_cci = df['CCI'].median()
        checks['13_CCI_Validity'] = {
            'status': 'PASS' if cci_pct >= 95 else 'WARN',
            'value': f'{median_cci:.1f}' if not pd.isna(median_cci) else 'N/A',
            'message': f'{valid_cci}/{total_records} CCI scores 0-100'
        }
    else:
        checks['13_CCI_Validity'] = {'status': 'FAIL', 'value': 'N/A', 'message': 'Column missing'}
    
    # ===== 14. State Code Format =====
    if 'State' in df.columns:
        valid_states = df['State'].astype(str).str.match(r'^[A-Z]{2}$').sum()
        state_pct = (valid_states / total_records * 100) if total_records > 0 else 0
        checks['14_State_Code_Format'] = {
            'status': 'PASS' if state_pct >= 95 else 'WARN',
            'value': f'{state_pct:.1f}%',
            'message': f'{valid_states}/{total_records} valid 2-letter state codes'
        }
    else:
        checks['14_State_Code_Format'] = {'status': 'FAIL', 'value': '0%', 'message': 'Column missing'}
    
    # ===== 15. Refi Eligibility Count =====
    if 'LTV %' in df.columns and 'Loan_Age_Mo' in df.columns:
        refi_eligible = ((df['LTV %'] <= 80) & (df['Loan_Age_Mo'] >= 18)).sum()
        refi_pct = (refi_eligible / total_records * 100) if total_records > 0 else 0
        checks['15_Refi_Eligibility'] = {
            'status': 'PASS' if refi_pct >= 50 else 'WARN' if refi_pct >= 25 else 'INFO',
            'value': f'{refi_pct:.1f}%',
            'message': f'{refi_eligible}/{total_records} meet refi criteria (LTV<=80%, Age>=18mo)'
        }
    else:
        checks['15_Refi_Eligibility'] = {'status': 'FAIL', 'value': 'N/A', 'message': 'Required columns missing'}
    
    # ===== 16. Owner Name Completeness =====
    if 'Owner Name' in df.columns:
        owner_present = df['Owner Name'].notna().sum()
        owner_pct = (owner_present / total_records * 100) if total_records > 0 else 0
        checks['16_Owner_Name_Present'] = {
            'status': 'PASS' if owner_pct >= 90 else 'WARN' if owner_pct >= 70 else 'FAIL',
            'value': f'{owner_pct:.1f}%',
            'message': f'{owner_present}/{total_records} records have owner names'
        }
    else:
        checks['16_Owner_Name_Present'] = {'status': 'FAIL', 'value': '0%', 'message': 'Column missing'}
    
    # ===== 17. Data Freshness Check =====
    date_col = 'LastLoanDate' if 'LastLoanDate' in df.columns else 'loan_date'
    if date_col in df.columns:
        loan_dates = pd.to_datetime(df[date_col], errors='coerce')
        recent_loans = (loan_dates >= '2020-01-01').sum()
        recent_pct = (recent_loans / total_records * 100) if total_records > 0 else 0
        checks['17_Data_Freshness'] = {
            'status': 'PASS' if recent_pct >= 70 else 'WARN' if recent_pct >= 40 else 'INFO',
            'value': f'{recent_pct:.1f}%',
            'message': f'{recent_loans}/{total_records} loans from 2020 or later'
        }
    else:
        checks['17_Data_Freshness'] = {'status': 'FAIL', 'value': 'N/A', 'message': 'Column missing'}
    
    # ===== 18. Overall Data Quality Score =====
    pass_count = sum(1 for c in checks.values() if c.get('status') == 'PASS')
    warn_count = sum(1 for c in checks.values() if c.get('status') == 'WARN')
    fail_count = sum(1 for c in checks.values() if c.get('status') == 'FAIL')
    
    quality_score = (pass_count / 17 * 100) if len(checks) > 0 else 0  # 17 checks before this one
    
    if quality_score >= 85:
        overall_status = 'EXCELLENT'
    elif quality_score >= 70:
        overall_status = 'GOOD'
    elif quality_score >= 50:
        overall_status = 'FAIR'
    else:
        overall_status = 'POOR'
    
    checks['18_Overall_Quality'] = {
        'status': overall_status,
        'value': f'{quality_score:.1f}%',
        'message': f'Pass:{pass_count} Warn:{warn_count} Fail:{fail_count}'
    }
    
    return checks