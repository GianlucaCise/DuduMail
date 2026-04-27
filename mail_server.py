import asyncio
from aiosmtpd.controller import Controller

class MyHandler:
    async def handle_DATA(self, server, session, envelope):
        print(f"Messaggio ricevuto da: {envelope.mail_from}")
        print(f"Inviato a: {envelope.rcpt_tos}")
        # Decodifichiamo il contenuto del messaggio
        content = envelope.content.decode('utf8', errors='replace')
        print(f"Contenuto:\n{content}")
        print("-" * 20)
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