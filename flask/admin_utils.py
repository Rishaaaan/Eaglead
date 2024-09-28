import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

ADMIN_FILE = 'data/admin_users.xlsx'

def register_admin(name, email, password):
    try:
        df = pd.read_excel(ADMIN_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Name', 'Email', 'Password'])

    hashed_password = generate_password_hash(password)
    new_row = pd.DataFrame({'Name': [name], 'Email': [email], 'Password': [hashed_password]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(ADMIN_FILE, index=False)

def check_admin_credentials(email, password):
    try:
        df = pd.read_excel(ADMIN_FILE)
    except FileNotFoundError:
        return False

    user = df[df['Email'] == email]
    if not user.empty:
        return check_password_hash(user.iloc[0]['Password'], password)
    return False

def get_all_users():
    try:
        df = pd.read_excel(ADMIN_FILE)
        return df[['Name', 'Email']].to_dict('records')
    except FileNotFoundError:
        return []

def update_user(id, new_name, new_email):
    df = pd.read_excel(ADMIN_FILE)
    df.loc[int(id), 'Name'] = new_name
    df.loc[int(id), 'Email'] = new_email
    df.to_excel(ADMIN_FILE, index=False)

def delete_user(id):
    df = pd.read_excel(ADMIN_FILE)
    df = df.drop(int(id))
    df.to_excel(ADMIN_FILE, index=False)

def reset_user_password(id, new_password):
    df = pd.read_excel(ADMIN_FILE)
    hashed_password = generate_password_hash(new_password)
    df.loc[int(id), 'Password'] = hashed_password
    df.to_excel(ADMIN_FILE, index=False)