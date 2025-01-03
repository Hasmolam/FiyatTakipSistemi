# Hepsiburada Fiyat Takip ve Bildirim Sistemi

## 1. Amaç
Bu proje, Hepsiburada üzerinde belirli ürünlerin fiyatlarını düzenli olarak takip ederek fiyat düştüğünde e-posta bildirimleri gönderen bir sistem geliştirmeyi hedefler. Ayrıca, çekilen verilerle günlük rapor oluşturulup CSV formatında sunulacak.

---

## 2. Hedef Kullanıcılar
- **Kullanıcı:** Projenin tek kullanıcısı olarak sen (proje sahibi).  
- **Kullanım Amacı:** Kendi ihtiyaçlarına yönelik fiyat takibi ve analiz yapma.  

---

## 3. Özellikler

### Temel Özellikler
1. **Ürün Fiyat Takibi**  
   - Kullanıcı, takip edilecek ürünlerin URL’lerini sisteme girer.  
   - Sistem bu ürünlerin fiyatlarını saatlik olarak kontrol eder.  

2. **Fiyat Alarmı**  
   - Fiyat belirli bir seviyenin altına düştüğünde otomatik olarak e-posta bildirimi gönderir.  

3. **Günlük Raporlama**  
   - Sistem, takip edilen tüm ürünlerin günlük fiyat değişimlerini CSV formatında bir dosyaya kaydeder ve isteğe bağlı olarak e-posta ile gönderir.  

4. **Veri Sunumu**  
   - Fiyat değişimlerini grafik ve tablo olarak görselleştirme.  

---

## 4. Teknik Detaylar

### 4.1 Veri Çekme (Scraping)
- **Veri Türleri:**  
  - Ürün fiyatı  
  - Ürün adı (isteğe bağlı)  
- **Scraping Sıklığı:** Saatlik  

### 4.2 Kullanılacak Teknolojiler
- **Scraping:** `BeautifulSoup`, `requests`, `selenium` (JavaScript ile yüklenen dinamik öğeler varsa).  
- **Veri İşleme:** `pandas`.  
- **Grafik ve Raporlama:** `matplotlib`, `seaborn`.  
- **E-posta Gönderimi:** `smtplib`.  
- **Zamanlama:** `schedule`.  

### 4.3 Dinamik Öğeler ve Bot Algılama
- Eğer Hepsiburada JavaScript ile fiyatları yüklerse, `selenium` kullanılarak bu engel aşılacak.  
- **Anti-Ban Önlemleri:**  
  - User-Agent rotasyonu.  
  - Proxy kullanımı.  
  - Scraping işlemlerinin zamanlamasını rastgele yapmak.

---

## 5. Çıktılar ve Bildirimler
- **CSV Rapor:**  
  - Ürün fiyatları ve fiyat değişimleri günlük olarak CSV formatında kaydedilecek.  
- **E-posta Bildirimleri:**  
  - Fiyat düşüşlerinde anlık bildirimler.  
  - Günlük raporun e-posta yoluyla gönderilmesi (isteğe bağlı).  
- **Grafiksel Çıktılar:**  
  - Fiyat değişimlerini grafiklerle gösteren bir analiz ekranı (opsiyonel).  

---

## 6. Kısıtlamalar ve Riskler
- **Bot Algılama:** Hepsiburada'nın scraping işlemini algılama riski yüksek.  
  - Proxy ve User-Agent değişimleriyle bu risk minimize edilecek.  
  - Yüksek scraping sıklığından kaçınılacak (gerekirse süre artırılabilir).  
- **Teknik Bilinmezlikler:**  
  - Dinamik öğelerin olup olmadığı proje sırasında tespit edilecek.  
  - Bu durumda selenium entegrasyonu yapılabilir.

---

## 7. Zaman Çizelgesi
- **Analiz ve Tasarım:** 1-2 gün  
- **Scraping Modülü:** 3-5 gün  
- **E-posta ve Bildirim Sistemi:** 2 gün  
- **Raporlama ve Grafikler:** 3 gün  
- **Test ve Optimizasyon:** 2-3 gün  

---

## 8. Başarı Ölçütleri
- Fiyatların doğru bir şekilde çekilmesi ve CSV formatında kaydedilmesi.  
- Fiyat düştüğünde e-postaların zamanında gönderilmesi.  
- Bot algılama sistemlerinden kaçınılması.  
