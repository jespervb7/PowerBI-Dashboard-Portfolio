import os
import sys
import pandas as pd
import hashlib
from tabulate import tabulate
from config import HASH_SALT
from typing import Optional, Callable

def hash_individual_column(
    row_value: Optional[str],
    algorithm: str = 'sha256',
    salt: str = ''
) -> Optional[str]:
    """
    Securely hash a DataFrame columns values with a secret salt. Salt is equivalent to a random value you can pass to the hash function to make it more secure.
    Since the salt variable is stored somewhere securely it's impossible to reverse engineer the code.

    Parameters:
        row_value (Optional[str]): The value of row to hash (can be None or NaN)
        algorithm (str): Hash algorithm ('sha256', 'md5', 'sha1', etc.)
        env_var (str): Name of the environment variable holding the secret salt

    Returns:
        Optional[str]: Hexadecimal hash string, or None if input is NaN
    """

    if pd.isna(row_value):
        return None

    h = hashlib.new(algorithm)
    h.update((salt + str(row_value)).encode('utf-8'))
    return h.hexdigest()

def row_hashing(row):
    row_str = "|".join(map(str, row.values))
    return hashlib.md5(row_str.encode()).hexdigest()

def credit_debit_rename(row):
    if row == 'Credit':
        return 'Incoming transaction'
    elif row == 'Debit':
        return 'Outgoing transaction'
    else:
        return ''
    
def company_name(
    row: pd.Series, 
    *func_col_pairs: tuple[Callable, str]
) -> Optional[str]:
    """
    Try multiple (function, column_name) pairs until one returns a non-empty result.

    Example:
        company_name(row,
                     (company_name_from_text, 'Counterparty'),
                     (company_name_by_hash, 'hash_banking_identification'))
    """
    for func, col in func_col_pairs:
        if col not in row:
            # optional: log or warn
            continue

        value = row[col]
        result = func(value)

        if pd.notna(result) and result != '':
            return result

    return None

def company_name_by_hash(row):

    not_company_hash_numbers = [
                                    '6063d00f024d4d5dd9f9810c242b5edbe0d4419b94b43d4bfbaa01e7195dc78d', 
                                    '3c17f9293f23fe80947fdc32f0fcce1965c10d1636c7e8b664851578fb407823',
                                    '77600747dff4969471f23d75f54537f96fe2123b65daa5ddc9d6d5779a972da9',
                                    'c9f891f01c7b74a5af54f5bfd0a0871222ce485672441dbf852b66f5151b6619'
                                    ]
    
    tikkie_hash_numbers = ['de3b846a60d61ef3761f09ef2d97d4e61a854c23a72bf36da95e56608cd97507', '3c17f9293f23fe80947fdc32f0fcce1965c10d1636c7e8b664851578fb407823']
    
    paypal_hash_numbers = [
                                    '953c2232c86d1f6b8701c8d6c84d354f3fc92d58b9c39034323cbbbe5c39c6d6', 
                                    'eaa748ac2ce10da6dac354c7d3a4afa7adc7c67f4ea140948a8df9750fc02505',
                                    'c8732f00634fc6b8a7abe458d982adcc44bd979bd7f7ae97ee1a9d7ed31de454'
                                    ]
    
    stichting_amstelland_hash_numbers = [
                                            '4881fe650fccc68868d6907b4e617261466fa97eb91df4b79ac6b2bb34ad09f5'
                                            ]

    hash_map = {
        '863ab00a3012e8e7738b16b63ab4c1ac56ddb42017cc136d98f4151ce8ad3173': 'Belastingdienst',
        '208c746022825b1c429f6d8ce1b185f039818f69cca40149cd3ff209069ee502': 'KPN',
        '8e7779981dca4f4bdd24a7ad13cdf082b2e15ac9034f444508ee7df6f4162012': 'Netflix',
        '36ac166d93c120667b6058d59c246d702a4cff7102b5a653648680d73dec31e6': 'Thuisbezorgd',
        '6d82b1089f14bd8441c256e7602fc9db5c3fcdee65858713bf3d580eabd44318': 'CE Logistics Group B.V.',
        '68c4686b6f53f775d1ddbe5453640217e11ddd4b90520ff6015c6f2f099c9d2d': 'IU International Hochschule',
        'cd2db137e2ce588f0e82edcfabf0a8cbc39afef557cb22e5666968689aa564ed': 'Nationale Nederlanden groep N.V.',
        'eb76f8b2f0e3302cce88eadd2c4b07b6b59d9cb25081cb90d1523dac18fd1ff8': 'Bol.com',
        'd2a016f1f87b51516858e3d50dea7e586e29eece380c930acaf37f8b947ad9be': 'Achmea',
        '841e9d1f046c313605e4f1da35f39c8a9015254f49c21dc19cb7eb6d082fd137': 'Steam',
        'f60fc8d92afc9d5cd7c74ce9d5d4f830bfb919fca9c2c1dbd5a1986f9de0c6fd': 'ING',
        '2471d363ace675723b9a90b695b95bbe3cad19df59204f88048c57005e7dd84d': 'Zilverenkruis',
        '8b72d9003004609d96eb8ce185c35cfa1327fde550c1b24aa59d4704a4815d07': 'Michiel de Ruyter roei en kano vereniging',
        '19923858546e3a8c9457f28533c6986f204bc0aa6ebf223080a9a25ca93af07f': 'Beach House Media',
        '48ec237c12df91211a642527f1d9691931da9d601c380c00e8c6ee1b4dd1b8ac': 'ANWB',
        '9ab9c34aee2153d976fef1189ad6b433db822975ea40042e4fc65580ba05cef5': 'Rabobank',
        '2f4f7551caaeee871c84d7e9b43e2c1514d5a4419e188d04d853881a7f2de050': 'Yellowstone'
    }
    
    if row in paypal_hash_numbers:
        return 'PayPal'
    elif row in tikkie_hash_numbers:
        return 'Tikkie'
    elif row in not_company_hash_numbers:
        return 'Not a company'
    elif row in stichting_amstelland_hash_numbers:
        return 'Stichting AmstellandBibliotheken'
    elif row in hash_map:
        return hash_map[row]
    
def company_name_from_text(row):

    row_lowercase = str(row).lower()

    if 'albert heijn' in row_lowercase:
        return 'Albert Heijn'
    elif 'ah to go' in row_lowercase:
        return 'Albert Heijn'
    elif 'albertheijn' in row_lowercase:
        return 'Albert Heijn'
    elif 'albert-heijn' in row_lowercase:
        return 'Albert Heijn'
    elif 'mcdonald' in row_lowercase:
        return 'McDonalds'
    elif 'mc donalds' in row_lowercase:
        return 'McDonalds'
    elif "mc donald's" in row_lowercase:
        return 'McDonalds'
    elif 'mc drive' in row_lowercase:
        return 'McDonalds'
    elif 'thuisbezorgd' in row_lowercase:
        return 'Thuisbezorgd'
    elif 'the flying chicken' in row_lowercase:
        return 'The Flying Chicken'
    elif 'www.ovpay.nl' in row_lowercase:
        return 'Openbaar Vervoer'
    elif 'ov busstation' in row_lowercase:
        return 'Openbaar Vervoer'
    elif 'kfc' in row_lowercase:
        return 'KFC'
    elif 'burger king' in row_lowercase:
        return 'Burger King'
    elif 'greggs' in row_lowercase:
        return 'Greggs'
    elif 'achmea' in row_lowercase:
        return 'Achmea'
    elif 'erv-dea b.v.' in row_lowercase:
        return 'Energiebedrijf DeA'
    elif 'energiebedrijf dea' in row_lowercase:
        return 'Energiebedrijf DeA'
    elif 'hermans & schuttevaer' in row_lowercase:
        return 'Hermans & Schuttevaer Notarissen N.V.'
    elif 'hermans + schuttevaer' in row_lowercase:
        return 'Hermans & Schuttevaer Notarissen N.V.'
    elif 'watersport verbond' in row_lowercase:
        return 'Watersportverbond'
    elif 'watersportverbond' in row_lowercase:
        return 'Watersportverbond'
    elif 'huysinc' in row_lowercase:
        return 'Huysinc B.V.'
    elif 'airbnb' in row_lowercase:
        return 'Airbnb'
    elif 'kiosk' in row_lowercase:
        return 'Kiosk'
    elif 'medion' in row_lowercase:
        return 'Medion'
    elif 'coolblue' in row_lowercase:
        return 'Coolblue'
    elif 'emirates' in row_lowercase:
        return 'Emirates'
    elif 'opa 90' in row_lowercase:
        return 'Opa 90'
    elif 'linkedin' in row_lowercase:
        return 'LinkedIn'
    elif 'duo' in row_lowercase:
        return 'DUO'
    elif 'kanopoloshop' in row_lowercase:
        return 'Kanopoloshop'
    elif 'hogeschool inholland' in row_lowercase:
        return 'Hogeschool Inholland'
    elif 'aldi' in row_lowercase:
        return 'Aldi'
    elif 'asr levverz' in row_lowercase:
        return 'ASR'
    elif 'ncoi' in row_lowercase:
        return 'NCOI'
    elif 'van grunsven' in row_lowercase:
        return 'Bouwbedrijf van Grunsven'
    elif 'kosten oranjepakket' in row_lowercase:
        return 'ING'
    elif 'bonusrenterekening' in row_lowercase:
        return 'ING'
    elif 'oranje spaarrekening' in row_lowercase:
        return 'ING'
    elif 'apple' in row_lowercase:
        return 'Apple'
    elif 'febo' in row_lowercase:
        return 'Febo'
    elif 'bella donna' in row_lowercase:
        return 'Bella Donna'
    elif 'bruna' in row_lowercase:
        return 'Bruna'
    elif 'starbuck' in row_lowercase:
        return 'Starbucks'
    elif 'the phone house' in row_lowercase:
        return 'The Phone House'
    elif 'urkv michiel de ru uithoorn' in row_lowercase:
        return 'Michiel de Ruyter roei en kano vereniging'
    elif 'deen' in row_lowercase:
        return 'Deen Supermarkten'
    elif 'netflix' in row_lowercase:
        return 'Netflix'
    elif 'dfds' in row_lowercase:
        return 'DFDS Seaways'
    elif 'isney' in row_lowercase:
        return 'Disney plus'
    elif 'domino' in row_lowercase:
        return "Domino's Pizza"
    elif 'doner city' in row_lowercase:
        return "Doner City"
    elif 'pathe' in row_lowercase:
        return "Pathe"
    elif 'hema' in row_lowercase:
        return "Hema"
    elif 'creditcard' in row_lowercase:
        return "ING"
    elif 'jagexgamesstudio' in row_lowercase:
        return "Jagex Games Studio"
    elif 'jumbo' in row_lowercase:
        return "Jumbo"
    elif 'kwalitaria' in row_lowercase:
        return "Kwalitaria"
    elif 'kruidvat' in row_lowercase:
        return "Kruidvat"
    elif 'praxis' in row_lowercase:
        return "Praxis"
    elif 'lidl' in row_lowercase:
        return "Lidl"
    elif 'media markt' in row_lowercase: 
        return "MediaMarkt"
    elif 'multimate' in row_lowercase: 
        return "Multimate"
    elif 'schaft tweewielers' in row_lowercase: 
        return "Schaft Tweewielers"
    elif 'action' in row_lowercase: 
        return "Action"
    elif 'dienst uitvoering onderwijs' in row_lowercase:
        return "DUO"
    elif 'nationale-nederlanden' in row_lowercase: 
        return "Nationale Nederlanden groep N.V."
    elif 'smullers' in row_lowercase: 
        return "Smullers"
    elif 'theanything' in row_lowercase: 
        return "TheAnything B.V."
    elif 'bcc elektro-speciaalzaken' in row_lowercase: 
        return "BCC Elektro-Speciaalzaken"
    elif 'station doner kebab' in row_lowercase:
        return "Station Döner Kebab"
    elif 'subway' in row_lowercase:
        return "Subway"
    elif 'shell' in row_lowercase: 
        return "Shell"
    elif 'vomar' in row_lowercase: 
        return "Vomar"
    elif 'the doner company' in row_lowercase:
        return "The Döner Company"
    elif 'under armour' in row_lowercase:
        return "Under Armour"
    elif 'la place' in row_lowercase:
        return "La Place"
    elif 'kwaritaria' in row_lowercase:
        return "Kwalitaria"
    #TODO: Make strictrect with re libraary to avoid false positives
    elif ' ing' in row_lowercase:
        return "ING"
    elif 'ah' in row_lowercase:
        return 'Albert Heijn'
    elif 'mcd' in row_lowercase:
        return 'McDonalds'
    elif 'klm' in row_lowercase:
        return 'KLM'
    elif 'ns' in row_lowercase:
        return 'Nederlandse Spoorwegen'
    else:
        return None
    
def is_tikkie(row):
    pass

def is_person_to_person(row):
    hash_mapping = [
        '98ccdc7c949735fc9f2158a403309a2628c7fb5528336ae31cead3a1f10cf982',
        '6656c2285cf7f28e14373c5135ab0fe6dd08d4872baed8b4dcce96cd8a3aad03',
        'e60df24675f775feb9ec00d314c5029cfc937871358c1f80964ee79588156882',
        '69890ddc3547268b4fb6bf43022475f1bc42cdbebf8391c574f99f79e4719dbe',
        '27c1b9d2c0981f9f5b78b574b9b61c947d1e0a35f6258efc7a80be57f8a4ec74',
        '623a8939f1ecaec8188a1f0b6c65f95a94a2dc2244449089337829fbbb9614d9',
        '95c56ed950275b5743b3cc3278957586ec5027c9174ccc4d1ee9adf042760474',
        '9201a4ed823021602ebb1ab5ad6fad629c60246a92c65334777a72725956d322',
        '81c3a67d02b82186c8ff94815c1e0598cadca95b15eec4333c4044cfdef62e72',
        '0f1ecfccba1b263c68a95f831669a626e8e6cce59ce4060010002434bde872e8',
        '1098284f663fb035157bade97b08691f3df45fe957c365ecd00bc804d574629c',
        '10b7fd64fe5de8b2a50f99460e62710f8f460d13bf5c51c5432264a55bd7714d',
        '1dd178327016abf63885ef61781af31373a43d58f2d26c9b261ad8dd9b689220',
        '20dab74091b37c651582acf658e0bb587d99480bdc6380209cdc38875bbbc8ee',
        '2710e98e40b62108804d95837848ab167a103f8e929584e77d9be03a00210e23',
        '27c1b9d2c0981f9f5b78b574b9b61c947d1e0a35f6258efc7a80be57f8a4ec74',
        '2b3e4a90f2d6379d66a30ec12f9e87e942eae851eb62ac2bb1cf61164ba0088a',
        '2e54388a8f5b7aa943c6a8800c913ac421e97a1b96719527f12574d3a9808ccb',
        '3e2af1035ae09ed0f3fd9ef2354b9dcb50e5a45843bd1c96584ca75f0bb7fcfa',
        '49aa6f7e5c28e6b60c5fa383666afd765d04b120f9a836af5b7e20d710e7b53f',
        '4cbbd5b615aeea2560b198aab1dd06150f1fb61b12a7d5617b2b587d0cc0cf64',
        '541870f01bad5658a15648105d3259cfb129f12f5f31ca245b95a81d27d5c930',
        '623a8939f1ecaec8188a1f0b6c65f95a94a2dc2244449089337829fbbb9614d9',
        '7159ace12ccba9667eef7d2b00be01003fc6cb550962af48da47340d93048634',
        '7f98807853b7946adcb6416f60d6ca156609e85fcda27fce7385ed0a3dec8ac0',
        '867ce4f65b76c94ff23cd843d906499aceeed1fd59105ebdfa83be27bbe6ab8e',
        '869cd2fbcf6e02d8813da5e30927f7c1088f29ca1e5fafd120815b385bf95540',
        '90e6b55e5b2a493f33c567ecf8a0d40c819108bf277d695bf02ec6bcf6dc4ce8',
        '916520f6b8018c6ae494061ca08c7c7a2fd5c1100e54bc8649b241bc70eb61dd',
        '93506f431d4eb2fc0a74c28cd5b55162f77fdc2b69ca2a4af379f58c683a37b2',
        '93506f431d4eb2fc0a74c28cd5b55162f77fdc2b69ca2a4af379f58c683a37b2',
        '95c56ed950275b5743b3cc3278957586ec5027c9174ccc4d1ee9adf042760474',
        'a115ba00146f24b599574eed66615e76065642f062183760b0107f803b2f15a6',
        'a20904f69a89fc2d468aa1e293563f30c902dc3571711ea68bb46c4e3b2a3628',
        'a3bb2158dca8094197d2aad648dc33829042e3692a8e2100aa7575c79827e175',
        'a3dbed6bbadf87aabb7ee0fde5e0b3317644eb89fa878406a94777d489bfd051',
        'b54a997bc68cb2ac53eb8b7a14aa7f064c0732f2494b594b676fcc9a7e8935f3',
        'bf476cc651696552905e386cb3d2f048e030321c318f540ec84d6cad25bddcb6',
        'c6609ca86c1935090aa1da0440e591e7797150ab4e9d3225a99fe6609b521447',
        'c85786e9dbb551d8045de372f4d8e365b4715b2ebf7f8a21b0e6b1d8ee2f27bb',
        'cb6c7888de654fe812e73b45485a6da72e64b693a4673302037ce20eccf618ce',
        'ce1d5107e8b37a4df989e77f84efee0f171a6be27d50bad5884ab08781007c92',
        'd17faf0da9fe8488734b6a2880fce0b5197009b8a7952c0827425c992109a295',
        'dbf44f30bc2caf43fd48b7b2d9dd1a7e279590cad7edd981c754831631e9e0bb',
        'ec97959ed894a8fa0a5dd1ba881b2d90d64e6186c1d8d7aa48e858210c4f2dd5',
        'ece04c89bb5c84bc9d7ff91f38bdcec5f579908cc94cfef2a13e01acb71bf27b',
        'fbd27a56a090915cc486d811c43e20e3aca381a01c5453e8cd45c112e5e69682'
    ]

def is_salary(row):
    
    if row['company_name'] in ['Achmea', 'CE Logistics Group B.V.', 'Yellowstone'] and row['type_of_transaction'] == 'Incoming transaction':
        return 'Yes'
    else:
        return 'No'

def is_fastfood(row):

    if row['company_name'] in ['McDonalds', 'Opa 90', 'Thuisbezorgd', 'The Flying Chicken', 'KFC', 'Burger King', 'Subway', "Domino's Pizza", 'Doner City', 'Smullers', 'Station Döner Kebab', 'The Döner Company', 'Starbucks', 'Greggs', 'Febo', 'Kwalitaria']:
        return 'Yes'
    else:
        return 'No'
    
def is_groceries(row):

    if row['company_name'] in ['Albert Heijn', 'Aldi', 'Jumbo', 'Lidl', 'Vomar', 'Deen Supermarkten', 'Kruidvat']:
        return 'Yes'
    else:
        return 'No'
    
def is_restaurant(row):
    if row['company_name'] in ['Bella Donna', '']:
        return 'Yes'
    else:
        return 'No'

def is_recurring_payment(row):
    pass

def is_savings(row):
    #TODO make stricter for futher proofing
    if row['name_or_description'] in ['NOTPROVIDED', 'Oranje Spaarrekening', 'Bonusrenterekening', 'Je oude Bonusrenterekening', 'To Bonusrenterekening', 'From Bonusrenterekening']:
        return 'Yes'
    else:
        return 'No'

def is_investment(row):
    if row['company_name'] in ['Energiebedrijf DeA']:
        return 'Yes'
    else:
        return 'No'

def is_expense(row):
    if row['is_savings'] == 'Yes':
        return 'No'
    elif row['type_of_transaction'] == 'Outgoing transaction':
        return 'Yes'
    else:
        return 'No'

def is_income(row):
    if row['is_salary'] == 'Yes':
        return 'Yes'
    elif row['is_investment'] == 'Yes' and row['type_of_transaction'] == 'Incoming transaction':
        return 'Yes'
    else:
        return 'No'

def add_expense_categories(row):
    pass

def add_surrogate_key(df: pd.DataFrame, key_name: str = "surrogate_key") -> pd.DataFrame:
    """
    Adds a surrogate key column as the first column of the DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.
    key_name : str, optional
        The name of the surrogate key column (default is 'surrogate_key').
        
    Returns
    -------
    pd.DataFrame
        A new DataFrame with the surrogate key as the first column.
    """
    # Create a copy to avoid mutating the original DataFrame
    df = df.copy()
    
    # Creating the surrogate key
    df[key_name] = range(1, len(df) + 1)
    
    # Reorder columns to make the key the first column
    cols = [key_name] + [col for col in df.columns if col != key_name]
    df = df[cols]
    
    return df

def create_dim_companies(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df[['company_name', 'is_restaurant']].drop_duplicates()
    df = add_surrogate_key(df, key_name="company_sk")

    return df

def create_dim_transaction_info(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df[['counterparty', 'name_or_description', 'type_of_transaction','is_person_to_person_transaction', 'is_salary', 'is_fastfood', 'is_groceries', 'is_tikkie', 'is_savings', 'is_investment', 'is_income', 'is_expense']].drop_duplicates()
    df = add_surrogate_key(df, key_name="transaction_info_sk")

    return df

def create_fact_bank_transactions(main_df: pd.DataFrame, dim_companies, dim_transaction_info) -> pd.DataFrame:
    #TODO: dynamic export path
    main_df = main_df.copy()

    merged_companies = main_df.merge(dim_companies, on='company_name', how='left')
    merged_transaction_info = merged_companies.merge(dim_transaction_info, on = ['counterparty', 'name_or_description', 'type_of_transaction','is_person_to_person_transaction', 'is_salary', 'is_fastfood', 'is_groceries', 'is_tikkie', 'is_savings', 'is_investment', 'is_income', 'is_expense'], how='left')
    final_df = merged_transaction_info[['company_sk', 'transaction_info_sk', 'received_date_sk', 'counterparty', 'amount_in_euro']]

    return final_df

def main():
    # TODO: convert to function so that it's anonamized when imported this is for the CSV files. Include metadata columns
    # TODO: make file path dynamic from git repository location

    export_path = "C:/git/PowerBI-Dashboard-Portfolio/data/"
    
    raw_data = pd.read_csv("C:/git/PowerBI-Dashboard-Portfolio/data/NL52INGB0003610006_02-10-2015_01-10-2025.csv", sep=";", decimal=",")

    raw_data.rename(columns={
        'Date': 'received_date_sk',
        'Counterparty': 'counterparty',
        'Name / Description': 'name_or_description',
        'Account': 'account_number',
        'Code': 'code',
        'Debit/credit': 'debit_or_credit',
        'Amount (EUR)': 'amount_in_euro',
        'Resulting balance': 'balance_after_transaction_euro',
        'Notifications': 'notifications',
        'Transaction type': 'transaction_type',
        'Tag': 'tag'
    }, inplace=True)
    
    raw_data['hash_value'] = raw_data.apply(row_hashing, axis=1)
    raw_data['hash_banking_identification'] = raw_data['counterparty'].apply(hash_individual_column, salt=HASH_SALT)
    raw_data['is_person_to_person_transaction'] = raw_data.apply(is_person_to_person)
    raw_data['type_of_transaction'] = raw_data['debit_or_credit'].apply(credit_debit_rename)
    raw_data['company_name'] = raw_data.apply(lambda row: company_name (
        row,
        (company_name_by_hash, 'hash_banking_identification'),
        (company_name_from_text, 'name_or_description')
    ), axis=1)
    raw_data['is_salary'] = raw_data.apply(is_salary, axis=1)
    raw_data['is_fastfood'] = raw_data.apply(is_fastfood, axis=1)
    raw_data['is_groceries'] = raw_data.apply(is_groceries, axis=1)
    raw_data['is_tikkie'] = raw_data.apply(is_tikkie, axis=1)
    raw_data['is_restaurant'] = raw_data.apply(is_restaurant, axis=1)
    raw_data['is_savings'] = raw_data.apply(is_savings, axis=1)
    raw_data['is_investment'] = raw_data.apply(is_investment, axis=1)
    raw_data['is_income'] = raw_data.apply(is_income, axis=1)
    raw_data['is_expense'] = raw_data.apply(is_expense, axis=1)
    raw_data['mandate_id'] = raw_data['notifications'].str.extract(r"Mandate ID:\s*([A-Z0-9]+)(?:\s|$)")

    print(tabulate(raw_data.head(20), headers='keys', tablefmt='psql'))
    print(raw_data.dtypes)
    
    # raw_data.to_excel("C:/git/PowerBI-Dashboard-Portfolio/data/Finances_Anonymized.xlsx", index=False)
    dim_companies = create_dim_companies(raw_data)
    dim_transaction_info = create_dim_transaction_info(raw_data)
    fact_bank_transactions = create_fact_bank_transactions(raw_data, dim_companies, dim_transaction_info)

    dim_companies.to_excel("C:/git/PowerBI-Dashboard-Portfolio/data/DIM_Company.xlsx", index=False)
    dim_transaction_info.to_excel("C:/git/PowerBI-Dashboard-Portfolio/data/DIM_Transaction_info.xlsx", index=False)
    fact_bank_transactions.to_excel("C:/git/PowerBI-Dashboard-Portfolio/data/Fact_bank_transactions.xlsx", index=False)

if __name__ == "__main__":
    main()