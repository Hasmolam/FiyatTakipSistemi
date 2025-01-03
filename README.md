# Çoklu Platform Fiyat Takip Sistemi

Bu proje, Hepsiburada, Trendyol ve N11 gibi popüler e-ticaret platformlarındaki ürünlerin fiyatlarını takip eden ve fiyat düşüşlerinde e-posta bildirimleri gönderen bir sistemdir.

## Özellikler

- Çoklu platform desteği (Hepsiburada, Trendyol, N11)
- Ürün fiyatlarını otomatik olarak takip etme
- Fiyat düşüşlerinde e-posta bildirimleri
- Günlük fiyat raporları (CSV formatında)
- Fiyat değişimlerini görselleştirme
- Ürün gruplandırma ve karşılaştırma
- Anti-bot koruması bypass teknikleri
- Gelişmiş hata yönetimi

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `.env.example` dosyasını `.env` olarak kopyalayın ve e-posta bilgilerinizi girin:
```bash
cp .env.example .env
```

3. `.env` dosyasını düzenleyin:
```
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_password
```

Not: Gmail kullanıyorsanız, normal şifreniz yerine bir uygulama şifresi oluşturmanız gerekecektir.

## Kullanım

### Komut Satırı ile Kullanım

1. Programı başlatın:
```bash
python main.py
```

2. Ürün eklemek için:
```bash
python main.py --ekle "ÜRÜN_LİNKİ"
```

3. Ürünleri listelemek için:
```bash
python main.py --listele
```

4. Ürün silmek için:
```bash
python main.py --sil "ÜRÜN_LİNKİ"
```

### Toplu Ürün Ekleme

1. `products.txt` dosyasına ürün linklerini ekleyin:
```
https://www.hepsiburada.com/urun-url
https://www.trendyol.com/urun-url
https://www.n11.com/urun-url
```

2. Dosyadan ürünleri yükleyin:
```bash
python main.py --dosya
```

## Sistem Nasıl Çalışır

- Sistem her saat başı fiyat kontrolü yapar
- Fiyat %10'dan fazla düştüğünde e-posta bildirimi gönderir
- Her gün 23:00'da günlük rapor oluşturur ve gönderir
- Tüm veriler `data` klasöründe saklanır
- Raporlar `data/reports` klasöründe saklanır
- Ürünler platformlar arası karşılaştırılır ve gruplandırılır

## Güvenlik Önlemleri

- User-Agent rotasyonu
- İstekler arasında dinamik bekleme süresi
- Selenium WebDriver gizleme
- JavaScript bot algılama bypass
- IP rotasyonu desteği

## Desteklenen Platformlar

- Hepsiburada
- Trendyol
- N11

## Geliştirme

Projeye katkıda bulunmak için:

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Bir Pull Request oluşturun

## Hata Giderme

- Chrome sürücüsü hatası alıyorsanız, en son Chrome tarayıcısını yüklediğinizden emin olun
- Bot algılama sorunlarında, bekleme sürelerini artırmayı deneyin
- Fiyat bilgisi alınamıyorsa, ürün linkinin doğru olduğundan emin olun
- Proxy kullanımında sorun yaşıyorsanız, farklı bir proxy sunucusu deneyin

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın. 