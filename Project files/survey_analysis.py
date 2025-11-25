import os
import pandas as pd
import numpy as np
from scipy import stats
import re

print("\n" + "*" * 150)
print("\nWorking directory:", os.getcwd())

#********************************* Load Data *********************************
try:
    df_a = pd.read_excel("Project files/SurveyA_results.xlsx") # Variant (Free Shipping)
    df_b = pd.read_excel("Project files/SurveyB_results.xlsx") # Control (No Banner)
    print("\nFiles loaded successfully.")
except FileNotFoundError:
    print("\nError: Files not found. Please ensure the Excel files are in the same directory.")
    exit()

#********************************* Standardize Column Names *********************************
cols = [
    "Timestamp", 
    "Likelihood_Purchase",  # H1 Metric
    "Perceived_Value",      # H2 Metric
    "Expected_Spend",       # H3 Metric
    "Noticed_Offers", 
    "Stood_Out", 
    "Age", 
    "Frequency", 
]


df_a.columns.values[:len(cols)] = cols
df_b.columns.values[:len(cols)] = cols

#quick check
print("\n Dataset sample")
print(df_a.head())

#********************************* Data Cleaning Function *********************************
def clean_currency(value):
    """Extracts numeric value from strings like '$89.99', 'approx 100', etc."""
    if pd.isna(value):
        return np.nan
    # Find all integer or float numbers
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", str(value))
    if not matches:
        return np.nan
    
    # Convert found numbers to floats
    values = [float(x) for x in matches]
    
    # We assume valid price are likely >= 80 based on context
    prices = [v for v in values if v >= 80]
    
    if prices:
        return np.mean(prices)
    return np.nan

#********************************* function end *********************************

# Apply cleaning
df_a['Cleaned_Spend'] = df_a['Expected_Spend'].apply(clean_currency)
df_b['Cleaned_Spend'] = df_b['Expected_Spend'].apply(clean_currency)

print("\n Cleaned Dataset sample")
print(df_a.head()) #check last column --> Cleaned_Spend was added

# Force numeric on Likelihood and Value to avoid potential issues 
df_a['Likelihood_Purchase'] = pd.to_numeric(df_a['Likelihood_Purchase'], errors='coerce')
df_b['Likelihood_Purchase'] = pd.to_numeric(df_b['Likelihood_Purchase'], errors='coerce')
df_a['Perceived_Value'] = pd.to_numeric(df_a['Perceived_Value'], errors='coerce')
df_b['Perceived_Value'] = pd.to_numeric(df_b['Perceived_Value'], errors='coerce')


#********************************* Analysis & Statistical Tests *********************************

def run_ttest(group_a, group_b, metric_name):
    
    # Independent t-test (we only use the p-value)
    _, p_val = stats.ttest_ind(group_a.dropna(), group_b.dropna(), equal_var=False)
    
    mean_a = group_a.mean()
    mean_b = group_b.mean()
    
    # Determine significance
    significant = p_val < 0.05
    
    return {
        "metric": metric_name,
        "mean_a": mean_a,
        "mean_b": mean_b,
        "diff": mean_a - mean_b,
        "p_value": p_val,
        "significant": significant
    }

# Run tests for H1, H2, H3
h1_results = run_ttest(df_a['Likelihood_Purchase'], df_b['Likelihood_Purchase'], "Purchase Likelihood (1-7)")
h2_results = run_ttest(df_a['Perceived_Value'], df_b['Perceived_Value'], "Perceived Value (1-7)")
h3_results = run_ttest(df_a['Cleaned_Spend'], df_b['Cleaned_Spend'], "Expected Spend ($)")

# 5. Generate Report Output
print("\n" + "="*60)
print("AB TEST EXPERIMENT RESULTS REPORT")
print("="*60)
print(f"Sample Size: Variant (n={len(df_a)}) | Control (n={len(df_b)})")
print("-" * 60)

# --- H1 Report ---
print(f"\nH1: LIKELIHOOD TO PURCHASE")
print(f"Hypothesis: Variant > Control")
print(f"   Variant Mean: {h1_results['mean_a']:.2f}")
print(f"   Control Mean: {h1_results['mean_b']:.2f}")
print(f"   Difference:   {h1_results['diff']:+.2f}")
print(f"   P-Value:      {h1_results['p_value']:.4f}")
if h1_results['significant'] and h1_results['diff'] > 0: # if significant = True and the mean for those with free shipping banner is higher
    print(">> CONCLUSION: H1 VALIDATED (Statistically Significant Increase)")
else:
    print(">> CONCLUSION: H1 REJECTED (No significant increase)")

# --- H2 Report ---
print(f"\nH2: PERCEIVED VALUE")
print(f"Hypothesis: Variant > Control")
print(f"   Variant Mean: {h2_results['mean_a']:.2f}")
print(f"   Control Mean: {h2_results['mean_b']:.2f}")
print(f"   Difference:   {h2_results['diff']:+.2f}")
print(f"   P-Value:      {h2_results['p_value']:.4f}")
if h2_results['significant'] and h2_results['diff'] > 0: #same condition as for H1
    print(">> CONCLUSION: H2 VALIDATED (Statistically Significant Increase)") 
else:
    print(">> CONCLUSION: H2 REJECTED (No significant increase)")

# --- H3 Report ---
print(f"\nH3: EXPECTED SPEND")
print(f"Hypothesis: Variant > Control (Higher Expected Spend)")
print(f"   Variant Mean: ${h3_results['mean_a']:.2f}")
print(f"   Control Mean: ${h3_results['mean_b']:.2f}")
print(f"   Difference:   ${h3_results['diff']:+.2f}")
print(f"   P-Value:      {h3_results['p_value']:.4f}")

if h3_results['significant'] and h3_results['diff'] > 0: # same as before
    print(">> CONCLUSION: H3 VALIDATED") #People that see the banner have a significantly higher expected spend 
else:
    print(">> CONCLUSION: H3 INVALIDATED (No significant increase)")

# --- Qualitative Check ---
print("-" * 60)
print("\nQUALITATIVE CHECK: OFFER VISIBILITY")
noticed_a = df_a[df_a['Noticed_Offers'].str.contains("Yes", case=False, na=False)].shape[0]
noticed_b = df_b[df_b['Noticed_Offers'].str.contains("Yes", case=False, na=False)].shape[0]

print(f"Variant Group who noticed offers: {noticed_a}/{len(df_a)} ({noticed_a/len(df_a)*100:.1f}%)")
print(f"Control Group who noticed offers: {noticed_b}/{len(df_b)} ({noticed_b/len(df_b)*100:.1f}%)")
print("="*60)