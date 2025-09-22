from fastapi import BackgroundTasks

async def send_email_background(background_tasks: BackgroundTasks, to: str, subject: str, body: str):
    # TODO: Implement real email sending (SMTP)
    print(f"[Email Mock] To: {to}, Subject: {subject}, Body: {body}")
