import sqlite3

def init_db():
    # Crea (o apre) il file del database chiamato 'emails.db'
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    
    # Crea la tabella se non esiste già
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            body TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

# Tabella Utenti
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email_address TEXT UNIQUE,  -- <--- Il vero indirizzo @dudumail.local
        password TEXT
    )
''')


def save_email(sender, recipient, subject, body):
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emails (sender, recipient, subject, body)
        VALUES (?, ?, ?, ?)
    ''', (sender, recipient, subject, body))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print("Database inizializzato con successo!")