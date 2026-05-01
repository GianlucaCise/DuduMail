from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_emails():
    conn = sqlite3.connect('emails.db')
    conn.row_factory = sqlite3.Row # Questo ci permette di usare i nomi delle colonne
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emails ORDER BY timestamp DESC')
    emails = cursor.fetchall()
    conn.close()
    return emails

@app.route('/')
def index():
    lista_email = get_emails()
    return render_template('index.html', emails=lista_email)

if __name__ == '__main__':
    app.run(debug=True, port=5000)