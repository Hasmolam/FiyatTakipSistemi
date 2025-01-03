import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT

class EmailNotifier:
    def __init__(self):
        self.email = EMAIL_ADDRESS
        self.password = EMAIL_PASSWORD
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT

    def send_price_alert(self, product_name, old_price, new_price, url, additional_info=""):
        """Fiyat düşüşü durumunda bildirim gönderir"""
        subject = f"Fiyat Düşüşü Bildirimi: {product_name}"
        body = f"""
        Ürün fiyatında düşüş tespit edildi!

        Ürün: {product_name}
        Eski Fiyat: {old_price:.2f} TL
        Yeni Fiyat: {new_price:.2f} TL
        Fark: {old_price - new_price:.2f} TL (%{((old_price - new_price) / old_price * 100):.1f})

        Ürün Linki: {url}
        {additional_info}
        """
        
        self._send_email(subject, body)

    def send_daily_report(self, report_file_path):
        """Günlük raporu e-posta olarak gönderir"""
        subject = "Günlük Fiyat Takip Raporu"
        body = """
        Günlük fiyat takip raporu ekte yer almaktadır.
        
        Rapor içeriği:
        - Tüm ürünlerin güncel fiyatları
        - Platform bazlı karşılaştırmalar
        - Grup bazlı fiyat analizleri
        """
        
        self._send_email(subject, body, attachment_path=report_file_path)

    def _send_email(self, subject, body, attachment_path=None):
        """E-posta gönderme işlemini gerçekleştirir"""
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = self.email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if attachment_path:
            with open(attachment_path, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype='csv')
                attachment.add_header('Content-Disposition', 'attachment', filename=attachment_path.split('/')[-1])
                msg.attach(attachment)

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            print(f"E-posta başarıyla gönderildi: {subject}")
        except Exception as e:
            print(f"E-posta gönderilirken hata oluştu: {str(e)}") 