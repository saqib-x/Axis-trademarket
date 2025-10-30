# # create_test_feeds.py - Generate test CSV files for different feed types
# import pandas as pd
# from pathlib import Path
# from datetime import datetime, timedelta
# import random

# # Create test data directory
# test_dir = Path("input/test_feeds")
# test_dir.mkdir(parents=True, exist_ok=True)

# def generate_base_data(rows=100):
#     """Generate base property data"""
#     data = []
#     for i in range(rows):
#         property_value = random.randint(200000, 800000)
#         loan_balance = random.randint(int(property_value * 0.3), int(property_value * 0.85))
#         loan_date = datetime.now() - timedelta(days=random.randint(18*30, 72*30))
        
#         data.append({
#             'Owner Name': f'Owner {i+1}',
#             'Mail Address': f'{100+i} Test St',
#             'Property Address': f'{100+i} Main St',
#             'City': random.choice(['Raleigh', 'Durham', 'Cary']),
#             'State': 'NC',
#             'ZIP': random.choice(['27601', '27609', '27613']),
#             'EstValue': property_value,
#             'TotalLoanBal': loan_balance,
#             'LastLoanDate': loan_date.strftime('%m/%d/%Y')
#         })
    
#     return pd.DataFrame(data)

# # 1. Core Equity Feed
# print("Creating Core Equity Feed test file...")
# df_core = generate_base_data(100)
# df_core.to_csv(test_dir / "core_equity_test.csv", index=False)
# print(f"✓ Created: {test_dir / 'core_equity_test.csv'}")

# # 2. Transactional Momentum Feed
# print("Creating Transactional Momentum Feed test file...")
# df_momentum = generate_base_data(150)
# df_momentum.to_csv(test_dir / "transactional_momentum_test.csv", index=False)
# print(f"✓ Created: {test_dir / 'transactional_momentum_test.csv'}")

# # 3. Predictive Churn Feed
# print("Creating Predictive Churn Feed test file...")
# df_churn = generate_base_data(200)
# df_churn.to_csv(test_dir / "predictive_churn_test.csv", index=False)
# print(f"✓ Created: {test_dir / 'predictive_churn_test.csv'}")

# # 4. Market Activity Feed
# print("Creating Market Activity Feed test file...")
# df_activity = generate_base_data(120)
# df_activity.to_csv(test_dir / "market_activity_test.csv", index=False)
# print(f"✓ Created: {test_dir / 'market_activity_test.csv'}")

# # 5. Lender Engagement Feed
# print("Creating Lender Engagement Feed test file...")
# df_lender = generate_base_data(80)
# df_lender.to_csv(test_dir / "lender_engagement_test.csv", index=False)
# print(f"✓ Created: {test_dir / 'lender_engagement_test.csv'}")

# print("\n" + "="*60)
# print("All test feed files created successfully!")
# print("="*60)
# print("\nTest files location: input/test_feeds/")
# print("\nTo test different feeds, copy any file to input/test.csv and run RUN_ME.bat")

# create_test_feeds.py - Generate test CSV files for different feed types
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import random

# Create test data directory
test_dir = Path("input/test_feeds")
test_dir.mkdir(parents=True, exist_ok=True)

def generate_base_data(rows=100):
    """Generate base property data"""
    data = []
    for i in range(rows):
        property_value = random.randint(200000, 800000)
        loan_balance = random.randint(int(property_value * 0.3), int(property_value * 0.85))
        loan_date = datetime.now() - timedelta(days=random.randint(18*30, 72*30))
        
        data.append({
            'Owner Name': f'Owner {i+1}',
            'Mail Address': f'{100+i} Test St',
            'Property Address': f'{100+i} Main St',
            'City': random.choice(['Raleigh', 'Durham', 'Cary']),
            'State': 'NC',
            'ZIP': random.choice(['27601', '27609', '27613']),
            'EstValue': property_value,
            'TotalLoanBal': loan_balance,
            'LastLoanDate': loan_date.strftime('%m/%d/%Y')
        })
    
    return pd.DataFrame(data)

# 1. Core Equity Feed
print("Creating Core Equity Feed test file...")
df_core = generate_base_data(100)
df_core['feed_type'] = 'core_equity'
df_core.to_csv(test_dir / "core_equity_test.csv", index=False)
print(f"✓ Created: {test_dir / 'core_equity_test.csv'}")

# 2. Transactional Momentum Feed
print("Creating Transactional Momentum Feed test file...")
df_momentum = generate_base_data(150)
df_momentum['feed_type'] = 'transactional_momentum'
df_momentum.to_csv(test_dir / "transactional_momentum_test.csv", index=False)
print(f"✓ Created: {test_dir / 'transactional_momentum_test.csv'}")

# 3. Predictive Churn Feed
print("Creating Predictive Churn Feed test file...")
df_churn = generate_base_data(200)
df_churn['feed_type'] = 'predictive_churn'
df_churn.to_csv(test_dir / "predictive_churn_test.csv", index=False)
print(f"✓ Created: {test_dir / 'predictive_churn_test.csv'}")

# 4. Market Activity Feed
print("Creating Market Activity Feed test file...")
df_activity = generate_base_data(120)
df_activity['feed_type'] = 'market_activity'
df_activity.to_csv(test_dir / "market_activity_test.csv", index=False)
print(f"✓ Created: {test_dir / 'market_activity_test.csv'}")

# 5. Lender Engagement Feed
print("Creating Lender Engagement Feed test file...")
df_lender = generate_base_data(80)
df_lender['feed_type'] = 'lender_engagement'
df_lender.to_csv(test_dir / "lender_engagement_test.csv", index=False)
print(f"✓ Created: {test_dir / 'lender_engagement_test.csv'}")

print("\n" + "="*60)
print("All test feed files created successfully!")
print("="*60)
print("\nTest files location: input/test_feeds/")
print("\nTo test different feeds, copy any file to input/test.csv and run RUN_ME.bat")