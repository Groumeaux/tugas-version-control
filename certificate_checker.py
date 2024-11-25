"""
certificate_checker.py
-----------------------
This script checks SSL certificate expiration for specified domains and sends alerts via email.
"""

import ssl
import socket
from datetime import datetime, timezone
from email.mime.text import MIMEText
import smtplib

def ambil_waktu_expire_ssl(domain):
    """
    Retrieves the SSL certificate expiration date for the given domain.

    Args:
        domain_name (str): The domain to check.

    Returns:
        datetime: Expiration date of the SSL certificate, or None if retrieval fails.
    """
    context = ssl.create_default_context()
    try:
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
        tgl_expire_str = cert['notAfter']
        tgl_expire = datetime.strptime(tgl_expire_str, '%b %d %H:%M:%S %Y %Z')
        tgl_expire = tgl_expire.replace(tzinfo=timezone.utc)
        return tgl_expire
    except (ssl.SSLError, socket.error) as e:
        print(f"Terjadi error ketika mengambil sertifikat SSL untuk {domain}: {e}")
        return None

def kirim_alert_email(domain, sisa_hari=None, no_ssl=False):
    """
    Sends an alert email regarding SSL certificate status.

    Args:
        domain_name (str): The domain for which the alert is being sent.
        sisa_hari (int, optional): Days remaining before the certificate expires.
        no_ssl (bool, optional): Whether the domain lacks a valid SSL certificate.
    """
    
    sender = 'back.upl4pt0p1@gmail.com'
    receiver = 'juventinopalandeng@gmail.com'
    if no_ssl:
        subject = f'Alert: Tidak Ada Sertifikat SSL untuk {domain}'
        body = f'Website {domain} tidak memiliki sertifikat SSL yang valid.'
    else:
        subject = f'Alert Expiration Sertifikat SSL: {domain}'
        body = f'Sertifikat SSL {domain} akan expire dalam {sisa_hari} hari.'

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, 'rrhpavlnhczttlzo')
        server.sendmail(sender, receiver, msg.as_string())

def cek_ssl(domain, batas_hari=50):
    """
    Checks the SSL certificate expiration status for the given domain.

    Args:
        domain_name (str): The domain to check.
        batas_hari (int): Threshold in days to trigger alerts.
    """


    tgl_expire = ambil_waktu_expire_ssl(domain)
    if tgl_expire is None:

        print(f"ALERT: Tidak ada sertifikat SSL untuk {domain}")
        kirim_alert_email(domain, no_ssl=True)
        return

    sisa_hari = (tgl_expire - datetime.now(tz=timezone.utc)).days
    print(f'Sertifikat SSL {domain} akan expire dalam {sisa_hari} hari')

    if sisa_hari < batas_hari:
        print(f'ALERT: Sertifikat SSL {domain} akan expire dalam {sisa_hari} hari!')
        kirim_alert_email(domain, sisa_hari)

if __name__ == "__main__":
    domain_list = ['google.com', 'seal.or.id','expired.badssl.com']
    for domain in domain_list:
        cek_ssl(domain, batas_hari=20)


