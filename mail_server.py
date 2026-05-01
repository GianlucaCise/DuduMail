import asyncio
from aiosmtpd.controller import Controller
from database import save_email
from email import message_from_bytes
class MyHandler:
    async def handle_DATA(self, server, session, envelope):
        # Trasformiamo il contenuto grezzo in un oggetto "EmailMessage"
        msg = message_from_bytes(envelope.content)
        
        sender = envelope.mail_from
        recipient = ", ".join(envelope.rcpt_tos)
        
        # Estraiamo l'oggetto in modo sicuro
        subject = msg.get('subject', 'Nessun Oggetto')
        
        # Estraiamo il corpo del messaggio
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='replace')

        print(f"Archiviando mail: {subject}")
        save_email(sender, recipient, subject, body)
        
        return '250 Message accepted for delivery'
    
async def main():
    handler = MyHandler()
    # Usiamo 127.0.0.1 per indicare che il server è locale
    controller = Controller(handler, hostname='127.0.0.1', port=1025)
    controller.start()
    print("Server SMTP locale in ascolto sulla porta 1025...")
    
    try:
        # Questo serve a tenere il programma vivo mentre il server gira
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        controller.stop()
        print("\nServer arrestato.")

if __name__ == '__main__':
    # Questo è il modo moderno di avviare programmi asincroni
    asyncio.run(main())