import pandas as pd

print("\n" + "*" * 60)
print("DEMOGRAPHIC ANALYSIS")
print("*" * 60)

#Load Data
try:
    df_a = pd.read_excel("Project files/SurveyA_results.xlsx") 
    df_b = pd.read_excel("Project files/SurveyB_results.xlsx") 
    df_total = pd.concat([df_a, df_b], ignore_index=True)
    print(f"Loaded {len(df_total)} total participants.")
except FileNotFoundError:
    print("Error: Files not found. Please check your directory.")
    exit()

try:
    df_total.rename(columns={
        df_total.columns[7]: 'Frequency'
    }, inplace=True)
except IndexError:
    exit()

#asusme "frequent" implies weekly or daily
frequent_labels = ['Weekly', 'Daily']

def is_frequent(val):
    if pd.isna(val): 
        return False
    return any(label.lower() in str(val).lower() for label in frequent_labels)

#apply logic
df_total['Is_Frequent'] = df_total['Frequency'].apply(is_frequent)

freq_count = df_total['Is_Frequent'].sum()
freq_pct = (freq_count / len(df_total)) * 100

#output
print("\n--- Final Report Sentence ---")
print(f"{freq_pct:.1f}% identified as frequent online shoppers.")
print("-" * 30)