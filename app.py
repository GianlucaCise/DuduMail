from flask import Flask, render_template, request, redirect, url_for, session # aggiungi session
import sqlite3
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'una_chiave_segreta_molto_difficile' # Indispensabile per le sessioni

# Funzione per verificare il login
def check_user(username, password):
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = check_user(username, password)
        if user:
            session['user'] = username # Salviamo l'utente nella sessione
            return redirect(url_for('index'))
        return "Login fallito!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

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

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Recuperiamo solo le mail destinate a questo utente
    username = session['user']
    conn = sqlite3.connect('emails.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Cerchiamo le mail dove il destinatario contiene lo username
    cursor.execute('SELECT * FROM emails WHERE recipient LIKE ? ORDER BY timestamp DESC', (f'%{username}%',))
    lista_email = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', emails=lista_email, user=username)

if __name__ == '__main__':
    app.run(debug=True, port=5000)