# herkeseegitim.com

Herkese Eğitim'in sitesi. Sayfalar `build.py` ile `data/icerik.json`'dan üretilir; GitHub her gönderide ve her gece 00:10'da siteyi yeniden üretip yayınlar.

## Yeni içerik nasıl eklenir
Yalnız `data/icerik.json` değişir, sayfalara elle dokunulmaz.

- **Yeni atölye ya da araç:** `urunler` listesine bir kayıt: `id`, `ad`, `tur` (arac, atolye, oyun), `lansman` (YYYY-AA-GG), `sinif` (["7"] ya da ["hepsi"]), `brans` (["matematik"]), `kazanim` (["MAT.7.1.7"]), `url`, `video` (YouTube kimliği). Kapak `data/kapak/<id>.png`, tek dosya HTML `data/canta/`. Anlatım metni `build.py` içindeki `URUN` sözlüğüne. Lansman tarihi gelene kadar sitede "yakında" görünür.
- **Yeni video:** `videolar` listesine: `id`, `baslik`, `dizi` (tahmin, atasozu, ozel-gun, bilgisayarin-icinde, tanitim), `urun`, `tarih`, isteğe bağlı `metin` (cevabın düz metni), `platformlar` (`ig`, `tt`, `x` adresleri). Kapak `data/kapak/<id>.png`.
- **Yeni atasözü:** `atasozleri` listesine: `no`, `soz`, `soru`, `anlam`, `sozcuk` ({kelime, anlam}), `video`, `tarih`.
- **Takvim:** `build.py` içindeki `takvim`.

## Kurallar
Sayaç, takip, çerez, dış istek yok. Okul adı yok. Metin kısa, süssüz, ünlemsiz; hitap "siz".
