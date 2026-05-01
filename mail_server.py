import asyncio
import sqlite3
from aiosmtpd.controller import Controller
from email import message_from_bytes
from database import save_email

class MyHandler:
    async def handle_DATA(self, server, session, envelope):
        # 1. TRASFORMAZIONE IN OGGETTO EMAIL
        # envelope.content contiene i dati grezzi della mail
        msg = message_from_bytes(envelope.content)
        
        sender = envelope.mail_from
        
        # 2. CICLO SUI DESTINATARI
        for rcpt in envelope.rcpt_tos:
            # Controllo se l'utente esiste nel database
            conn = sqlite3.connect('emails.db')
            cursor = conn.cursor()
            cursor.execute('SELECT username FROM users WHERE email_address = ?', (rcpt,))
            user_exists = cursor.fetchone()
            conn.close()

            if user_exists:
                # Estraiamo l'oggetto
                subject = msg.get('subject', 'Nessun Oggetto')
                
                # Estraiamo il corpo (testo semplice)
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                            break
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='replace')

                # Salvataggio
                save_email(sender, rcpt, subject, body)
                print(f"✅ Mail salvata per: {rcpt}")
            else:
                print(f"❌ Utente {rcpt} non trovato. Mail scartata.")
                
        return '250 Message accepted for delivery'

async def main():
    handler = MyHandler()
    controller = Controller(handler, hostname='127.0.0.1', port=1025)
    controller.start()
    print("🚀 Server SMTP in ascolto sulla porta 1025...")
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        controller.stop()

if __name__ == '__main__':
    asyncio.run(main())