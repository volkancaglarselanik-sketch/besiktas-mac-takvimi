# Beşiktaş maç takvimi

Telefon takvimine abone olmak için:

    https://raw.githubusercontent.com/volkancaglarselanik-sketch/besiktas-mac-takvimi/main/besiktas.ics

GitHub Actions günde 3 kez ESPN'den Beşiktaş'ın tüm maçlarını (Süper Lig, Avrupa kupaları, kupa) çeker
ve `besiktas.ics` dosyasını günceller. Telefon aboneliği yenilediğinde yeni tarih ve saatler kendiliğinden gelir.

- Saati belli maçlar: 1 gün ve 1 saat önce uyarı.
- Saati açıklanmamış maçlar: tüm gün etkinliği; önceki akşam 20:00 ve maç günü 10:00 uyarı.
- Veri alınamazsa dosya değiştirilmez ve çalıştırma başarısız görünür (Actions sekmesi).
- iPhone'da abonelik ayarlarında "Uyarıları Sil" kapalı olmalı, yoksa uyarılar çalmaz.
