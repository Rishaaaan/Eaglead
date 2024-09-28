import pandas as pd
import xlsxwriter

def save_subscription(file_path, value, timestamp):
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Value', 'Timestamp'])

    new_row = pd.DataFrame({'Value': [value], 'Timestamp': [timestamp]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(file_path, index=False)

def get_subscriptions(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.to_dict('records')
    except FileNotFoundError:
        return []

def update_subscription(file_path, id, new_value):
    df = pd.read_excel(file_path)
    df.loc[int(id), 'Value'] = new_value
    df.to_excel(file_path, index=False)

def delete_subscription(file_path, id):
    df = pd.read_excel(file_path)
    df = df.drop(int(id))
    df.to_excel(file_path, index=False)

def export_to_excel(data, file_path):
    df = pd.DataFrame(data)
    
    with xlsxwriter.Workbook(file_path) as workbook:
        worksheet = workbook.add_worksheet()
        
        # Write headers
        for col, header in enumerate(df.columns):
            worksheet.write(0, col, header)
        
        # Write data
        for row, record in enumerate(df.values, start=1):
            for col, value in enumerate(record):
                worksheet.write(row, col, value)
        
        # Auto-adjust column widths
        for col in range(len(df.columns)):
            max_width = max(df[df.columns[col]].astype(str).map(len).max(), len(df.columns[col]))
            worksheet.set_column(col, col, max_width + 2)