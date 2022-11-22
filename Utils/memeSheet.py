import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from fuzzywuzzy import fuzz

def memeCompilation():
    # define the scope
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
        ]

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('collective-data-341513-51d04bcf3387.json', scope)

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open_by_key("1Qa-bbX2JQSGDbqkAiZZOyOfMP4MBdwOpTW-RVHdcIZw")

    # get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(0)

    # get all the records of the data
    records_data = sheet_instance.get_all_records()

    # convert the json to dataframe
    records_df = pd.DataFrame.from_dict(records_data)

    df = records_df.reset_index()  # make sure indexes pair with number of rows

    return df