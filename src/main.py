import os
import time
import schedule
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from scraper import get_scraper_for_url
from notifier import EmailNotifier
from config import (
    DATA_DIR, REPORTS_DIR, PRODUCTS_FILE,
    SCRAPING_INTERVAL, PRICE_CHECK_THRESHOLD
)
from difflib import SequenceMatcher
import re

class PriceTracker:
    def __init__(self):
        print("\nFiyat takip sistemi başlatılıyor...")
        print("E-posta sistemi hazırlanıyor...")
        self.notifier = EmailNotifier()
        print("Dizinler oluşturuluyor...")
        self.setup_directories()
        print("Ürün listesi yükleniyor...")
        self.load_products()
        print("Sistem başlatıldı ve kullanıma hazır!\n")

    def setup_directories(self):
        """Gerekli dizinleri oluşturur"""
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)
        print(f"Veri dizini: {DATA_DIR}")
        print(f"Rapor dizini: {REPORTS_DIR}")

    def load_products(self):
        """Takip edilecek ürünleri yükler"""
        if os.path.exists(PRODUCTS_FILE):
            self.products_df = pd.read_csv(PRODUCTS_FILE)
            print(f"Mevcut ürün listesi yüklendi. Toplam {len(self.products_df)} ürün takip ediliyor.")
            
            # Platform bilgisini ekle (eski kayıtlar için)
            if 'platform' not in self.products_df.columns:
                self.products_df['platform'] = self.products_df['url'].apply(lambda x: 'hepsiburada' if 'hepsiburada.com' in x else ('trendyol' if 'trendyol.com' in x else 'n11' if 'n11.com' in x else 'unknown'))
            
            # Ürün grubu bilgisini ekle (eski kayıtlar için)
            if 'group' not in self.products_df.columns:
                self.products_df['group'] = self.products_df['name'].apply(self.extract_product_group)
            
            self.products_df.to_csv(PRODUCTS_FILE, index=False)
        else:
            self.products_df = pd.DataFrame(columns=['url', 'name', 'last_price', 'min_price', 'max_price', 'platform', 'group'])
            self.products_df.to_csv(PRODUCTS_FILE, index=False)
            print("Yeni ürün listesi oluşturuldu.")

    def clean_product_name(self, name):
        """Ürün adını temizler ve standartlaştırır"""
        # Küçük harfe çevir
        name = name.lower()
        
        # Gereksiz kelimeleri kaldır
        remove_words = ['garantili', 'türkiye', 'distribütör', 'ithalatçı', 'resmi', 'orijinal', 'yeni']
        for word in remove_words:
            name = name.replace(word, '')
        
        # Rakamları ve GB/TB gibi birimleri koru, diğer özel karakterleri kaldır
        name = re.sub(r'[^a-z0-9\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()

    def extract_product_group(self, name):
        """Ürün adından grup adını çıkarır"""
        clean_name = self.clean_product_name(name)
        
        # Marka ve model numarasını bul
        words = clean_name.split()
        if len(words) >= 2:
            return f"{words[0]} {words[1]}"
        return clean_name

    def are_similar_products(self, name1, name2, threshold=0.8):
        """İki ürünün benzer olup olmadığını kontrol eder"""
        clean_name1 = self.clean_product_name(name1)
        clean_name2 = self.clean_product_name(name2)
        
        # Sequence Matcher ile benzerlik oranını hesapla
        similarity = SequenceMatcher(None, clean_name1, clean_name2).ratio()
        return similarity >= threshold

    def add_products_from_file(self, file_path='products.txt'):
        """products.txt dosyasından ürünleri ekler"""
        if not os.path.exists(file_path):
            print(f"Hata: {file_path} dosyası bulunamadı!")
            return
        
        print(f"\n{file_path} dosyasından ürünler ekleniyor...")
        
        # Dosyayı oku
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Her URL için
        for url in urls:
            self.add_product(url)
        
        # Ürünleri grupla
        self.group_similar_products()
        
        print("\nÜrün grupları:")
        for group in self.products_df['group'].unique():
            group_products = self.products_df[self.products_df['group'] == group]
            print(f"\n{group.upper()}:")
            print("=" * 80)
            for _, product in group_products.iterrows():
                print(f"Platform: {product['platform']}")
                print(f"Ürün: {product['name']}")
                print(f"Fiyat: {product['last_price']} TL")
                print("-" * 80)

    def group_similar_products(self):
        """Benzer ürünleri gruplar"""
        # Henüz grubu olmayan ürünler için
        ungrouped = self.products_df[self.products_df['group'].isnull()]
        
        for idx, product in ungrouped.iterrows():
            # Diğer ürünlerle karşılaştır
            for _, other in self.products_df.iterrows():
                if self.are_similar_products(product['name'], other['name']):
                    # Aynı gruba ekle
                    self.products_df.at[idx, 'group'] = other['group']
                    break
            
            # Eğer hala grubu yoksa, yeni grup oluştur
            if pd.isnull(self.products_df.at[idx, 'group']):
                self.products_df.at[idx, 'group'] = self.extract_product_group(product['name'])
        
        # Değişiklikleri kaydet
        self.products_df.to_csv(PRODUCTS_FILE, index=False)

    def add_product(self, url):
        """Yeni ürün ekler"""
        print(f"\nYeni ürün ekleniyor: {url}")
        if url in self.products_df['url'].values:
            print("Bu ürün zaten takip listesinde!")
            return

        try:
            scraper = get_scraper_for_url(url)
            details = scraper.get_product_details(url)
            
            if details and details['price']:
                # Ürün grubunu belirle
                group = self.extract_product_group(details['name'])
                
                new_product = pd.DataFrame({
                    'url': [url],
                    'name': [details['name']],
                    'last_price': [details['price']],
                    'min_price': [details['price']],
                    'max_price': [details['price']],
                    'platform': [details['platform']],
                    'group': [group]
                })
                
                self.products_df = pd.concat([self.products_df, new_product], ignore_index=True)
                self.products_df.to_csv(PRODUCTS_FILE, index=False)
                print(f"Yeni ürün başarıyla eklendi: {details['name']}")
                print(f"Başlangıç fiyatı: {details['price']} TL")
                print(f"Platform: {details['platform']}")
                print(f"Grup: {group}")
            else:
                print(f"Ürün detayları alınamadı: {url}")
        except ValueError as e:
            print(f"Hata: {str(e)}")
        except Exception as e:
            print(f"Beklenmeyen hata: {str(e)}")

    def check_prices(self):
        """Tüm ürünlerin fiyatlarını kontrol eder"""
        print(f"\nFiyat kontrolü başlatılıyor... {datetime.now()}")
        
        if len(self.products_df) == 0:
            print("Takip edilen ürün bulunmuyor!")
            return
            
        for _, product in self.products_df.iterrows():
            print(f"\nÜrün kontrol ediliyor: {product['name']} ({product['platform']})")
            print(f"Grup: {product['group']}")
            
            try:
                scraper = get_scraper_for_url(product['url'])
                details = scraper.get_product_details(product['url'])
                
                if details and details['price']:
                    current_price = details['price']
                    print(f"Mevcut fiyat: {current_price} TL")
                    print(f"Önceki fiyat: {product['last_price']} TL")
                    
                    # Fiyat düşüşü kontrolü
                    if product['last_price'] > 0:
                        price_drop = (product['last_price'] - current_price) / product['last_price']
                        print(f"Fiyat değişimi: %{price_drop*100:.1f}")
                        
                        if price_drop > PRICE_CHECK_THRESHOLD:
                            print("Önemli fiyat düşüşü tespit edildi! Bildirim gönderiliyor...")
                            
                            # Aynı gruptaki diğer ürünlerin fiyatlarını da bildir
                            group_products = self.products_df[
                                (self.products_df['group'] == product['group']) & 
                                (self.products_df['url'] != product['url'])
                            ]
                            
                            comparison = f"\n\nAynı Ürünün Diğer Platformlardaki Fiyatları:\n"
                            for _, other in group_products.iterrows():
                                comparison += f"{other['platform'].capitalize()}: {other['last_price']} TL\n"
                            
                            self.notifier.send_price_alert(
                                product['name'],
                                product['last_price'],
                                current_price,
                                product['url'],
                                additional_info=comparison
                            )
                    
                    # Fiyat güncelleme
                    self.products_df.loc[self.products_df['url'] == product['url'], 'last_price'] = current_price
                    self.products_df.loc[self.products_df['url'] == product['url'], 'min_price'] = min(current_price, product['min_price'])
                    self.products_df.loc[self.products_df['url'] == product['url'], 'max_price'] = max(current_price, product['max_price'])
                    print("Fiyat bilgileri güncellendi.")
                    
                time.sleep(5)  # Anti-ban önlemi
            except Exception as e:
                print(f"Ürün kontrol edilirken hata oluştu: {str(e)}")
                continue
        
        self.products_df.to_csv(PRODUCTS_FILE, index=False)
        print("\nFiyat kontrolü tamamlandı.")

    def generate_daily_report(self):
        """Günlük rapor oluşturur ve gönderir"""
        print("\nGünlük rapor oluşturuluyor...")
        report_date = datetime.now().strftime('%Y-%m-%d')
        report_file = os.path.join(REPORTS_DIR, f'report_{report_date}.csv')
        
        # CSV raporu oluştur
        self.products_df.to_csv(report_file, index=False)
        print(f"CSV raporu oluşturuldu: {report_file}")
        
        # Grup ve platform bazlı grafik oluştur
        print("Grafikler oluşturuluyor...")
        
        # Her grup için ayrı grafik
        groups = self.products_df['group'].unique()
        plt.figure(figsize=(15, 7 * len(groups)))
        
        for i, group in enumerate(groups, 1):
            group_data = self.products_df[self.products_df['group'] == group]
            
            plt.subplot(len(groups), 1, i)
            
            # Platform bazlı renklendirme
            sns.barplot(data=group_data, x='platform', y='last_price', hue='platform')
            plt.xticks(rotation=45, ha='right')
            plt.title(f'{group.upper()} - Platform Karşılaştırması')
            
            # Fiyat etiketlerini ekle
            for j, price in enumerate(group_data['last_price']):
                plt.text(j, price, f'{price:.2f} TL', ha='center', va='bottom')
            
            plt.tight_layout()
        
        graph_file = os.path.join(REPORTS_DIR, f'graph_{report_date}.png')
        plt.savefig(graph_file, bbox_inches='tight')
        plt.close()
        print(f"Grafik kaydedildi: {graph_file}")
        
        # Raporu gönder
        print("Rapor e-posta ile gönderiliyor...")
        self.notifier.send_daily_report(report_file)
        print("Günlük rapor tamamlandı.")

def main():
    parser = argparse.ArgumentParser(description='Çoklu Platform Fiyat Takip Sistemi')
    parser.add_argument('--ekle', '-e', type=str, help='Takip edilecek ürün URL\'si')
    parser.add_argument('--listele', '-l', action='store_true', help='Takip edilen ürünleri listele')
    parser.add_argument('--sil', '-s', type=str, help='Takipten çıkarılacak ürün URL\'si')
    parser.add_argument('--takip', '-t', action='store_true', help='Fiyat takibini başlat')
    parser.add_argument('--dosya', '-d', action='store_true', help='products.txt dosyasından ürünleri ekle')
    
    args = parser.parse_args()
    
    tracker = PriceTracker()
    
    if args.dosya:
        tracker.add_products_from_file()
        return
    
    if args.ekle:
        print(f"\nYeni ürün ekleniyor: {args.ekle}")
        tracker.add_product(args.ekle)
        return
        
    elif args.listele:
        if len(tracker.products_df) == 0:
            print("\nTakip edilen ürün bulunmuyor!")
        else:
            # Grup bazlı gruplama
            groups = tracker.products_df['group'].unique()
            for group in groups:
                group_products = tracker.products_df[tracker.products_df['group'] == group]
                print(f"\n{group.upper()}:")
                print("=" * 80)
                for _, product in group_products.iterrows():
                    print(f"Platform: {product['platform']}")
                    print(f"Ürün: {product['name']}")
                    print(f"Fiyat: {product['last_price']} TL")
                    print(f"Min Fiyat: {product['min_price']} TL")
                    print(f"Max Fiyat: {product['max_price']} TL")
                    print(f"URL: {product['url']}")
                    print("-" * 80)
        return
        
    elif args.sil:
        if args.sil in tracker.products_df['url'].values:
            product = tracker.products_df[tracker.products_df['url'] == args.sil].iloc[0]
            tracker.products_df = tracker.products_df[tracker.products_df['url'] != args.sil]
            tracker.products_df.to_csv(PRODUCTS_FILE, index=False)
            print(f"\nÜrün başarıyla takipten çıkarıldı:")
            print(f"Grup: {product['group']}")
            print(f"Platform: {product['platform']}")
            print(f"Ürün: {product['name']}")
            print(f"URL: {args.sil}")
        else:
            print("\nBu URL takip listesinde bulunamadı!")
        return
    
    elif args.takip or not any(vars(args).values()):
        # Zamanlanmış görevleri ayarla
        print("\nZamanlanmış görevler ayarlanıyor...")
        schedule.every(SCRAPING_INTERVAL).minutes.do(tracker.check_prices)
        schedule.every().day.at("23:00").do(tracker.generate_daily_report)
        
        print(f"""
Fiyat takip sistemi başlatıldı!
- Her {SCRAPING_INTERVAL} dakikada bir fiyat kontrolü yapılacak
- Her gün 23:00'da günlük rapor oluşturulacak
- Fiyat düşüşü %{PRICE_CHECK_THRESHOLD*100} üzerinde olduğunda bildirim gönderilecek

Desteklenen Platformlar:
- Hepsiburada
- Trendyol
- N11

Kullanım:
1. Ürün eklemek için products.txt dosyasına URL'leri ekleyin
2. python main.py --dosya komutu ile ürünleri yükleyin
3. python main.py --listele ile ürünleri görüntüleyin
4. python main.py --takip ile takibi başlatın

Programı durdurmak için Ctrl+C tuşlarına basın.
""")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nProgram durduruluyor...")
            print("Program başarıyla durduruldu.")

if __name__ == "__main__":
    main() 