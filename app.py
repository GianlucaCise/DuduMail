from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

def get_emails():
    conn = sqlite3.connect('emails.db')
    conn.row_factory = sqlite3.Row # Questo ci permette di usare i nomi delle colonne
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emails ORDER BY timestamp DESC')
    emails = cursor.fetchall()
    conn.close()
    return emails

@app.route('/send', methods=['POST'])
def send_email():
    # Recuperiamo i dati dal form HTML
    destinatario = request.form.get('to')
    oggetto = request.form.get('subject')
    messaggio = request.form.get('message')
    mittente = "tuo-account@dudumail.local" # Per ora fisso, poi lo prenderemo dal login

    # Prepariamo la mail usando la libreria standard
    msg = EmailMessage()
    msg.set_content(messaggio)
    msg['Subject'] = oggetto
    msg['From'] = mittente
    msg['To'] = destinatario

    try:
        # Inviamo la mail al NOSTRO server SMTP (porta 1025)
        with smtplib.SMTP("127.0.0.1", 1025) as server:
            server.send_message(msg)
        print("Mail inviata con successo!")
    except Exception as e:
        print(f"Errore nell'invio: {e}")

    return redirect(url_for('index'))


def index():
    lista_email = get_emails()
    return render_template('index.html', emails=lista_email)

if __name__ == '__main__':
    app.run(debug=True, port=5000)