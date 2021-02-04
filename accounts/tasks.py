from django.core.mail import send_mail
from django.conf import settings


def trigger_send_email(subject, message, recipients=[]):
    send_mail(
        subject,
        message,
        'example@no-reply.com',
        recipients,
        fail_silently = False,
    )

def send_mail_new_user_register(user, pwd_reset_link):
    pwd_reset_link = "{0}{1}".format(settings.PORTAL_URL, pwd_reset_link)

    subject = "Your registration for portal is confirmed."
    message = """
    Hello {user_fname} {user_lname},

    Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book.

    It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.

    You are confirmed to access the portal as following:
    {portal_link}
    Username: {username}

    You can set you password using following link:
    {pwd_reset_link}

    Thanks!
    Portal Team
    """.format(user_fname=user.first_name, user_lname=user.last_name, username=user.username, portal_link=settings.PORTAL_URL, pwd_reset_link=pwd_reset_link)

    recipients = [user.email]
    trigger_send_email(subject, message, recipients)


def send_mail_for_forgot_password(user):
    pass

def send_mail_for_forgot_password_otp(user):
    pass

def send_mail_for_reset_password_success(user):
    pass
