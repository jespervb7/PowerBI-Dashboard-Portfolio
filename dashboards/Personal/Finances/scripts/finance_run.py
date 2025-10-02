import os
import sys
import pandas as pd
import hashlib
from tabulate import tabulate

def row_hashing(row):
    row_str = "|".join(map(str, row.values))
    return hashlib.md5(row_str.encode()).hexdigest()

def credit_debit_rename(row):
    if row == 'Credit':
        return 'Income'
    elif row == 'Debit':
        return 'Expense'
    else:
        return ''

# TODO make GDPR compliant by hashing said values instead.
def company_name(row):

    not_company_banking_numbers = ['NL13ABNA0506417344', 'NL92INGB0009427734', 'NL40INGB0003874935','NL84INGB0008203059']
    paypal_banking_numbers = ['LU89751000135104200E', 'DE88500700100175526303']
    tikkie_banking_numbers = ['NL61ABNA0811086593']
    stichting_amstelland_banking_numbers = ['NL38INGB0703076094', 'NL36INGB0000070667']

    banking_map = {
        'NL86INGB0002445588': 'Belastingdienst',
        'NL83INGB0000325513': 'KPN',
        'LU810670006550194759': 'Netflix',
        'NL31ABNA0494688556': 'Thuisbezorgd',
        'NL59ABNA0454503377': 'CE Logistics Group B.V.',
        'DE19210500001001415390': 'IU International Hochschule',
        'NL38INGB0703076094': 'Nationale Nederlanden groep N.V.',
        'NL27INGB0000026500': 'Bol.com',
        'NL43RABO0192303139': 'Achmea',
        'NL14RABO0155503219': 'Steam',
        'NL46INGB0005533333': 'ING',
        'NL58INGB0000003050': 'Zilverenkruis',
        'NL47RABO0153174625': 'Michiel de Ruyter roei en kano vereniging',
        'IE30CITI99005132956548': 'Beach House Media',
        'NL35INGB0000099882': 'ANWB',
        'NL73RABO0325301433': 'Rabobank'
    }
    
    if row in paypal_banking_numbers:
        return 'PayPal'
    elif row in tikkie_banking_numbers:
        return 'Tikkie'
    elif row in not_company_banking_numbers:
        return 'Not a company'
    elif row in stichting_amstelland_banking_numbers:
        return 'Stichting AmstellandBibliotheken'
    elif row in banking_map:
        return banking_map[row]
    
    
def is_tikkie(row):
    if row == 'NL13ABNA0506417344':
        return 'Tikkie'
    else:
        return row

def main():
    raw_data = pd.read_csv("C:/git/PowerBI-Dashboard-Portfolio/data/NL52INGB0003610006_02-10-2015_01-10-2025.csv", sep=";")

    raw_data['Hash value'] = raw_data.apply(row_hashing, axis=1)
    raw_data[''] = raw_data['Debit/credit'].apply(credit_debit_rename)
    raw_data['company_name'] = raw_data['Counterparty'].apply(company_name)

    filter_sorted_bank_numbers = raw_data[raw_data['company_name'].isnull()]
    filtered_data = raw_data[raw_data['Counterparty'].str.contains('NL45INGB0705001903', na=False)]
    grouped = filter_sorted_bank_numbers.groupby('Counterparty').size().sort_values(ascending=False)

    filled_percent = raw_data['company_name'].notna() & (raw_data['company_name'] != '')
    percent_filled = filled_percent.sum() / len(raw_data) * 100

    print(grouped)
    print(tabulate(filtered_data.head(5), headers='keys', tablefmt='psql'))
    print(percent_filled)

if __name__ == "__main__":
    main()