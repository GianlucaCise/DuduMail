import sqlite3
conn = sqlite3.connect('emails.db')
cursor = conn.cursor()
# Aggiungiamo l'utente gianluca con password 1234
cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('gianluca', '1234'))
conn.commit()
conn.close()
print("Utente creato!")