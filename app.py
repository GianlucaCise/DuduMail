from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import smtplib
from email.message import EmailMessage
# IMPORT PER LA SICUREZZA
from werkzeug.security import generate_password_hash, check_password_hash

from config import DOMAIN

app = Flask(__name__)
app.secret_key = 'una_chiave_segreta_molto_difficile'

# --- NUOVA ROTTA REGISTRAZIONE ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email_addr = request.form['email_address'] # Prendi l'indirizzo
        user_part = request.form.get('email_user') # l'utente scrive solo 'gianluca'
        full_email = f"{user_part}@{DOMAIN}" # il sistema crea 'gianluca@dudumail.local'
        password = generate_password_hash(request.form['password'])
        
        conn = sqlite3.connect('emails.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, email_address, password) VALUES (?, ?, ?)', 
                           (username, email_addr, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Errore: Username o Indirizzo già esistenti!"
        finally:
            conn.close()
    return render_template('register.html')

# --- AGGIORNA LA FUNZIONE DI LOGIN ---
def check_user(username, password):
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # CONFRONTO: Verifichiamo se la password inserita corrisponde all'Hash nel DB
        if check_password_hash(result[0], password):
            return True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            session['user'] = username
            return redirect(url_for('index'))
        return "Login fallito: Username o Password errati!"
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
    if 'user' not in session:
        return redirect(url_for('login'))

    # 1. Recuperiamo l'indirizzo email dell'utente loggato dal DB
    username = session['user']
    conn = sqlite3.connect('emails.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT email_address FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    
    if not user_data:
        conn.close()
        return "Errore: Utente non trovato"
    
    # Questo è il TUO vero indirizzo email
    mio_indirizzo = user_data['email_address']

    # 2. Recuperiamo i dati dal form
    destinatario = request.form.get('to')
    oggetto = request.form.get('subject')
    messaggio = request.form.get('message')

    # 3. Prepariamo la mail con il mittente CORRETTO
    msg = EmailMessage()
    msg.set_content(messaggio)
    msg['Subject'] = oggetto
    msg['From'] = mio_indirizzo  # <--- CORRETTO: non più "io@..."
    msg['To'] = destinatario

    try:
        # Inviamo al server SMTP locale
        with smtplib.SMTP("127.0.0.1", 1025) as server:
            server.send_message(msg)
    except Exception as e:
        print(f"Errore invio: {e}")
    finally:
        conn.close()

    return redirect(url_for('index'))

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    username = session['user']
    
    conn = sqlite3.connect('emails.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Cerchiamo l'utente
    cursor.execute('SELECT email_address FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    
    # --- CONTROLLO SICUREZZA ---
    if user_data is None:
        conn.close()
        session.pop('user', None) # Puliamo la sessione corrotta
        return redirect(url_for('login'))
    # ---------------------------

    my_email = user_data['email_address']

    # Inbox e Sent come prima...
    cursor.execute('SELECT * FROM emails WHERE recipient = ? ORDER BY timestamp DESC', (my_email,))
    inbox_emails = cursor.fetchall()
    
    cursor.execute('SELECT * FROM emails WHERE sender = ? ORDER BY timestamp DESC', (my_email,))
    sent_emails = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', inbox=inbox_emails, sent=sent_emails, my_email=my_email)

if __name__ == '__main__':
    app.run(debug=True, port=5000)