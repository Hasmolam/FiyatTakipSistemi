import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# E-posta ayarları
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Scraping ayarları
SCRAPING_INTERVAL = 60  # dakika cinsinden
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
]

# Dosya yolları
DATA_DIR = 'data'
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.csv')

# Ürün takip ayarları
PRICE_CHECK_THRESHOLD = 0.1  # %10'luk fiyat düşüşü için bildirim 