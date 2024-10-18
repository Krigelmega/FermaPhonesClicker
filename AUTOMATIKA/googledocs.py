from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta


workers = {'1315421133': 'Витя',
           '1315421134': 'Мотя',
           '959557274': 'Дима'}


# Путь к вашему файлу с учетными данными Service Account
SERVICE_ACCOUNT_FILE = 'client.json'

# Области доступа для Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Аутентификация и создание клиента службы
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)

# ID существующей таблицы Google Sheets
SPREADSHEET_ID = '1cvLWOvONvjT2nYjrym2_i-uCfkZoRYt93No4rttx6as'

# Получение списка листов в таблице
sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
sheets = sheet_metadata.get('sheets', '')

# Текущая дата и дата следующего дня
current_date = datetime.now().strftime('%d.%m.%Y')
next_day = (datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')

# Определение, является ли текущее время днем или ночью
current_hour = datetime.now().hour
time_of_day = "день" if 7 <= current_hour < 19 else "ночь"

# Вывод данных со всех листов и добавление даты и текста
for sheet in sheets:
    sheet_name = sheet['properties']['title']
    if sheet_name == 'Earnings':
        print(f"Updating sheet: {sheet_name}")

        # Примерный диапазон, можно настроить
        RANGE_NAME = f"{sheet_name}!A2:Z1000"
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        rows = result.get('values', [])

        # Поиск строки с текущей или следующей датой
        for i, row in enumerate(rows):
            if row and (row[0] == current_date or row[0] == next_day):
                # Добавляем 'день' или 'ночь' во вторую колонку
                row[1] = time_of_day

                # Обновление строки
                update_range = f"{sheet_name}!A{i + 2}"  # Смещение на 2 из-за начала с A2
                body = {
                    'values': [row]
                }
                update_result = sheets_service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID, range=update_range,
                    valueInputOption='USER_ENTERED', body=body).execute()

                print(f"Row {i + 2} updated with {time_of_day}.")
                break
        else:
            print("No matching date found for update.")