import smtplib

# Dati del messaggio
sender = "marco@dudumail.local"
receiver = "gianluca@dudumail.local"
message = """Subject: Primo Test Locale
From: marco@dudumail.local
To: gianluca@dudumail.local

Ciao Gianluca! Funziona? Questo messaggio dovrebbe finire nel database.
"""

try:
    # Ci connettiamo al TUO server SMTP sulla porta 1025
    with smtplib.SMTP("127.0.0.1", 1025) as server:
        server.sendmail(sender, receiver, message)
    print("Email inviata con successo!")
except Exception as e:
    print(f"Errore: {e}")