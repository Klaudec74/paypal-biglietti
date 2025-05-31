from flask import Flask, request
import smtplib
from email.message import EmailMessage
from fpdf import FPDF
import os

app = Flask(__name__)

@app.route('/paypal-ipn', methods=['POST'])
def paypal_ipn():
    # Legge i dati mandati da PayPal IPN
    data = request.form
    payer_email = data.get('payer_email')
    first_name = data.get('first_name', 'Utente')
    last_name = data.get('last_name', '')
    full_name = f"{first_name} {last_name}".strip()

    # Genera PDF biglietto
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Il Ragazzo dalla Maschera di Ferro', ln=True, align='C')
    pdf.ln(10)
    pdf.cell(0, 10, '25 Luglio 2025 - Palazzo Platamone, Catania', ln=True, align='C')
    pdf.ln(20)
    pdf.cell(0, 10, f'Biglietto intestato a: {full_name}', ln=True, align='C')
    pdf_output_path = '/tmp/biglietto.pdf'
    pdf.output(pdf_output_path)

    # Invia email con allegato
    send_email(payer_email, full_name, pdf_output_path)

    return 'OK', 200

def send_email(to_email, full_name, attachment_path):
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

    msg = EmailMessage()
    msg['Subject'] = 'Il tuo Biglietto per Il Ragazzo dalla Maschera di Ferro'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(f'Ciao {full_name},\n\nGrazie per la tua donazione! In allegato trovi il tuo biglietto.')

    with open(attachment_path, 'rb') as f:
        file_data = f.read()
        file_name = f.name.split('/')[-1]
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
