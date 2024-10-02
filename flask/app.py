from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from excel_utils import save_subscription, get_subscriptions, update_subscription, delete_subscription, export_to_excel
from admin_utils import register_admin, check_admin_credentials, get_all_users, update_user, delete_user, reset_user_password
import os
from datetime import datetime
import tempfile

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    print(True)
    email = request.form.get('email')
    print(email)
    newsletter = request.form.get('newsletter')
    print(newsletter)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if email:
        save_subscription('data/email_subscriptions.xlsx', email, timestamp)
    if newsletter:
        save_subscription('data/newsletter_subscriptions.xlsx', newsletter, timestamp)

    return redirect(url_for('home'))

@app.route('/adminRNCOS')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    if check_admin_credentials(email, password):
        session['admin'] = email
        return redirect(url_for('admin_panel'))
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/register', methods=['POST'])
def admin_register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    register_admin(name, email, password)
    return redirect(url_for('admin_login'))

@app.route('/admin/panel')
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    email_subs = get_subscriptions('data/email_subscriptions.xlsx')
    newsletter_subs = get_subscriptions('data/newsletter_subscriptions.xlsx')
    users = get_all_users()

    return render_template('admin_panel.html', email_subs=email_subs, newsletter_subs=newsletter_subs, users=users)

@app.route('/admin/update', methods=['POST'])
def admin_update():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 403

    data = request.json
    sheet = data.get('sheet')
    id = data.get('id')

    try:
        if sheet == 'users':
            new_name = data.get('new_name')
            new_email = data.get('new_email')
            update_user(id, new_name, new_email)
        else:
            new_value = data.get('new_value')
            update_subscription(f'data/{sheet}.xlsx', id, new_value)
        return jsonify({'success': True, 'message': 'Updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/reset_password', methods=['POST'])
def admin_reset_password():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 403

    data = request.json
    id = data.get('id')
    new_password = data.get('new_password')

    try:
        reset_user_password(id, new_password)
        return jsonify({'success': True, 'message': 'Password reset successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 403

    data = request.json
    deleted_count = 0

    try:
        if 'users' in data:
            for id in data['users']:
                delete_user(id)
                deleted_count += 1

        if 'email_subscriptions' in data:
            for id in data['email_subscriptions']:
                delete_subscription('data/email_subscriptions.xlsx', id)
                deleted_count += 1

        if 'newsletter_subscriptions' in data:
            for id in data['newsletter_subscriptions']:
                delete_subscription('data/newsletter_subscriptions.xlsx', id)
                deleted_count += 1

        return jsonify({'success': True, 'message': f'Successfully deleted {deleted_count} entries'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
@app.route('/admin/download_excel', methods=['POST'])
def admin_download_excel():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 403

    data = request.json
    table_type = data.get('table_type')
    selected_ids = data.get('selected_ids', [])

    try:
        if table_type == 'users':
            data = get_all_users()
        else:
            data = get_subscriptions(f'data/{table_type}.xlsx')

        if selected_ids:
            data = [item for index, item in enumerate(data) if str(index) in selected_ids]

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            export_to_excel(data, temp_file.name)
            return send_file(temp_file.name, as_attachment=True, download_name=f'{table_type}_export.xlsx')
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)