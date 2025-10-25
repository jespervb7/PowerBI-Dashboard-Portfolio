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
                     (company_name_by_hash, 'Hash banking identification'))
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

# TODO make GDPR compliant by hashing said values instead.
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
    elif 'Kwaritaria' in row_lowercase:
        return 'Kwalitaria'
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
    if row == 'NL13ABNA0506417344':
        return 'Tikkie'
    else:
        return row

def main():
    # TODO: convert to function so that it's anonamized when imported
    
    raw_data = pd.read_csv("C:/git/PowerBI-Dashboard-Portfolio/data/NL52INGB0003610006_02-10-2015_01-10-2025.csv", sep=";")

    raw_data['Hash value'] = raw_data.apply(row_hashing, axis=1)
    raw_data['Hash banking identification'] = raw_data['Counterparty'].apply(hash_individual_column, salt=HASH_SALT)
    raw_data['Type of transaction'] = raw_data['Debit/credit'].apply(credit_debit_rename)
    raw_data['company_name'] = raw_data.apply(lambda row: company_name (
        row,
        (company_name_by_hash, 'Hash banking identification'),
        (company_name_from_text, 'Name / Description')
    ), axis=1)

    print(tabulate(raw_data.head(20), headers='keys', tablefmt='psql'))
    raw_data.to_excel("C:/git/PowerBI-Dashboard-Portfolio/data/Finances_Anonymized.xlsx", index=False)

if __name__ == "__main__":
    main()