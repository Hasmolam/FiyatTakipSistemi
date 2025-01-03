import random
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import USER_AGENTS
import os

class BaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.setup_selenium()

    def setup_selenium(self):
        """Selenium için Chrome sürücüsünü hazırlar"""
        try:
            print("Chrome sürücüsü ayarlanıyor...")
            options = Options()
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Chrome sürücüsünü indir
            driver_manager = ChromeDriverManager()
            driver_path = driver_manager.install()
            print(f"Chrome sürücüsü yolu: {driver_path}")
            
            # Doğru sürücü dosyasını bul
            driver_dir = os.path.dirname(driver_path)
            chromedriver_path = None
            for root, dirs, files in os.walk(driver_dir):
                for file in files:
                    if file.startswith('chromedriver') and file.endswith('.exe'):
                        chromedriver_path = os.path.join(root, file)
                        break
                if chromedriver_path:
                    break
            
            if not chromedriver_path:
                raise Exception("chromedriver.exe bulunamadı!")
            
            print(f"Kullanılacak chromedriver: {chromedriver_path}")
            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # JavaScript ile bot algılama değişkenlerini gizle
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US', 'en']})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            
            print("Chrome başarıyla başlatıldı!")
            
        except Exception as e:
            print(f"Chrome başlatılamadı: {str(e)}")
            raise

    def get_random_headers(self):
        """Rastgele bir User-Agent ile header oluşturur"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr,en-US;q=0.7,en;q=0.3',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }

    def wait_and_find_element(self, by, value, timeout=10):
        """Belirli bir elementi bekler ve bulur"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            print(f"Element bulunamadı ({value}): {str(e)}")
            return None

    def __del__(self):
        """Sınıf silindiğinde Selenium sürücüsünü kapat"""
        if hasattr(self, 'driver'):
            print("Chrome kapatılıyor...")
            try:
                self.driver.quit()
                print("Chrome başarıyla kapatıldı!")
            except:
                print("Chrome kapatılırken hata oluştu!")

class HepsiburadaScraper(BaseScraper):
    def get_product_details(self, url):
        """Hepsiburada'dan ürün detaylarını çeker"""
        print(f"\nÜrün bilgileri alınıyor (Hepsiburada): {url}")
        try:
            print("Sayfa yükleniyor...")
            self.driver.get(url)
            time.sleep(10)  # Sayfanın yüklenmesi için daha uzun bekle
            
            # Sayfanın tamamen yüklenmesini bekle
            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            
            # JavaScript ile sayfayı scroll yap
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(3)
            
            # Sayfanın HTML içeriğini al
            html_content = self.driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Ürün adını bul
            name_element = soup.find('h1')
            if name_element:
                name = name_element.text.strip()
                print(f"Bulunan ürün adı: {name}")
            else:
                print("Ürün adı bulunamadı!")
                return None
            
            # Fiyatı bul
            price_element = None
            price_selectors = [
                'span[data-test-id="price-current-price"]',
                'span[data-bind="markupText: currentPrice"]',
                'span.price',
                'div.price-wrapper span',
                'div[data-test-id="product-price-current"]',
                'div[data-test-id="price-current-price"]',
                'div.product-price span',
                'div.extra-discount-price span'
            ]
            
            # Önce Selenium ile dene
            for selector in price_selectors:
                try:
                    price_element = self.wait_and_find_element(By.CSS_SELECTOR, selector)
                    if price_element:
                        break
                except:
                    continue
            
            # Selenium ile bulunamazsa BeautifulSoup ile dene
            if not price_element:
                for selector in price_selectors:
                    price_element = soup.select_one(selector)
                    if price_element:
                        break
            
            if price_element:
                if isinstance(price_element, str):
                    price_text = price_element
                else:
                    price_text = price_element.text.strip()
                # TL işaretini kaldır ve virgülü noktaya çevir
                price = float(price_text.replace('TL', '').replace('.', '').replace(',', '.').strip())
                print(f"Bulunan fiyat: {price} TL")
            else:
                print("Fiyat bulunamadı!")
                print("HTML içeriği:")
                print(html_content[:1000])  # İlk 1000 karakteri göster
                return None

            return {
                'name': name,
                'price': price,
                'url': url,
                'platform': 'hepsiburada'
            }

        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            print("HTML içeriği:")
            print(self.driver.page_source[:1000])  # İlk 1000 karakteri göster
            return None

class TrendyolScraper(BaseScraper):
    def get_product_details(self, url):
        """Trendyol'dan ürün detaylarını çeker"""
        print(f"\nÜrün bilgileri alınıyor (Trendyol): {url}")
        try:
            print("Sayfa yükleniyor...")
            self.driver.get(url)
            time.sleep(3)  # Sayfanın yüklenmesi için bekle
            
            # Ürün adını bul
            name_element = self.wait_and_find_element(By.CLASS_NAME, 'pr-new-br')
            if name_element:
                name = name_element.text.strip()
                print(f"Bulunan ürün adı: {name}")
            else:
                print("Ürün adı bulunamadı!")
                return None
            
            # Fiyatı bul
            price_element = self.wait_and_find_element(By.CLASS_NAME, 'prc-dsc')
            if price_element:
                price_text = price_element.text.strip()
                # TL işaretini kaldır ve virgülü noktaya çevir
                price = float(price_text.replace('TL', '').replace('.', '').replace(',', '.').strip())
                print(f"Bulunan fiyat: {price} TL")
            else:
                print("Fiyat bulunamadı!")
                return None

            return {
                'name': name,
                'price': price,
                'url': url,
                'platform': 'trendyol'
            }

        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            return None

class N11Scraper(BaseScraper):
    def get_product_details(self, url):
        """N11'den ürün detaylarını çeker"""
        print(f"\nÜrün bilgileri alınıyor (N11): {url}")
        try:
            print("Sayfa yükleniyor...")
            self.driver.get(url)
            time.sleep(5)  # Sayfanın yüklenmesi için daha uzun bekle
            
            # Sayfanın tamamen yüklenmesini bekle
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            
            # JavaScript ile sayfayı scroll yap
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            # Ürün adını bul (farklı seçiciler dene)
            selectors = [
                (By.CSS_SELECTOR, 'h1.proName'),
                (By.CSS_SELECTOR, 'h1.productName'),
                (By.CSS_SELECTOR, 'h1[data-product]'),
                (By.TAG_NAME, 'h1')
            ]
            
            name_element = None
            for by, selector in selectors:
                name_element = self.wait_and_find_element(by, selector)
                if name_element:
                    break
            
            if name_element:
                name = name_element.text.strip()
                print(f"Bulunan ürün adı: {name}")
            else:
                # HTML içeriğini kontrol et
                print("HTML içeriği:")
                print(self.driver.page_source[:500])
                print("Ürün adı bulunamadı!")
                return None
            
            # Fiyatı bul (farklı seçiciler dene)
            price_selectors = [
                (By.CSS_SELECTOR, 'div.newPrice ins'),
                (By.CSS_SELECTOR, 'div.priceContainer ins'),
                (By.CSS_SELECTOR, 'span.price'),
                (By.CSS_SELECTOR, 'div.price')
            ]
            
            price_element = None
            for by, selector in price_selectors:
                price_element = self.wait_and_find_element(by, selector)
                if price_element:
                    break
            
            if price_element:
                price_text = price_element.text.strip()
                # TL işaretini kaldır ve virgülü noktaya çevir
                price = float(price_text.replace('TL', '').replace('.', '').replace(',', '.').strip())
                print(f"Bulunan fiyat: {price} TL")
            else:
                print("Fiyat bulunamadı!")
                return None

            return {
                'name': name,
                'price': price,
                'url': url,
                'platform': 'n11'
            }

        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            return None

def get_scraper_for_url(url):
    """URL'ye göre uygun scraper'ı döndürür"""
    print("Scraper başlatılıyor...")
    if 'hepsiburada.com' in url:
        return HepsiburadaScraper()
    elif 'trendyol.com' in url:
        return TrendyolScraper()
    elif 'n11.com' in url:
        return N11Scraper()
    else:
        raise ValueError("Desteklenmeyen platform!") 