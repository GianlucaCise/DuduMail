from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import smtplib
from email.message import EmailMessage
# IMPORT PER LA SICUREZZA
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'una_chiave_segreta_molto_difficile'

# --- NUOVA ROTTA REGISTRAZIONE ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # CRITTOGRAFIA: Trasformiamo la password in un Hash
        hashed_password = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('emails.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Errore: Lo username esiste già!"
            
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