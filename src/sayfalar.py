# build.py içinden exec ile çalışır: liste, sınıf, branş, video sayfaları, çanta, RSS, gizlilik
BRANS_AD = {"fen":"Fen bilimleri","matematik":"Matematik","bilisim":"Bilişim teknolojileri ve yazılım","sinif":"Sınıf öğretmenliği","turkce":"Türkçe","hepsi":"Her branş"}
EK_YOLLAR = []
def yaz(yol, icerik):
    p = os.path.join(OUT, yol.strip("/"), "index.html") if yol.endswith("/") else os.path.join(OUT, yol.strip("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p,"w",encoding="utf-8").write(icerik)
    if yol.endswith("/"): EK_YOLLAR.append(yol)
def sayfa(baslik, aciklama, yol, govde, sema=None, yolcuk="", og=None):
    return bas(baslik, aciklama, yol, sema=sema, og=og) + ust_koyu() + f'<main id="ana" class="sayfa"><div class="w"><p class="yol"><a href="/">Ana sayfa</a>{yolcuk}</p>{govde}</div></main>{qr_gizli()}{ALT}'
def kart(u):
    durum = "" if u["durum"]=="yayinda" else f'<span class="etk">{tarih_tr(u["lansman"]) if u.get("lansman") else "Yakında"}</span>'
    img = f'<img src="{u["kapak_w"]}" alt="" loading="lazy">' if u.get("kapak_w") else f'<span class="kart-soru">{E(u["kisa"])}</span>'
    return f'<li class="kart" data-sinif="{" ".join(u["siniflar"])}" data-brans="{" ".join(u["branslar"])}"><a href="{urun_sayfa(u)}">{img}<b>{E(u["ad"])}</b><span>{E(u["sinif"])}</span>{durum}</a></li>'
def vkart(v):
    return f'<figure>{vid_btn(v)}<figcaption><a href="{video_sayfa(v)}">{E(v.get("kisa_ad"))}</a></figcaption></figure>'
def uv(u): return [v for v in videolar if v.get("urun")==u["id"]]

# liste sayfaları
for yol, turler, baslik, ac in [("/atolyeler/",("atolye","oyun"),"Atölyeler","MEB öğrenme hedeflerine bağlı atölyeler ve oyunlar. Sınıfa ya da branşa göre süzün."),
                                ("/araclar/",("arac",),"Araçlar","Tahtada ve tarayıcıda açılan araçlar.")]:
    l = [u for u in urunler if u["tur"] in turler]
    sinif_ = sorted({x for u in l for x in u["siniflar"] if x!="hepsi"}, key=int)
    brans_ = sorted({x for u in l for x in u["branslar"] if x!="hepsi"})
    suzgec = ""
    if len(l) > 3:
        suzgec = '<div class="suzgec" role="group" aria-label="Süz"><button type="button" data-s="" aria-pressed="true">Hepsi</button>' + "".join(f'<button type="button" data-s="sinif:{x}" aria-pressed="false">{x}. sınıf</button>' for x in sinif_) + "".join(f'<button type="button" data-s="brans:{x}" aria-pressed="false">{E(BRANS_AD.get(x,x))}</button>' for x in brans_) + '</div>'
    sema = [{"@context":"https://schema.org","@type":"CollectionPage","name":baslik,"url":SITE+yol,"hasPart":[{"@type":"CreativeWork","name":u["ad"],"url":SITE+urun_sayfa(u)} for u in l]}]
    yaz(yol, sayfa(f"{baslik} | Herkese Eğitim", ac, yol, f'<div class="makale" style="margin-bottom:28px"><h1>{baslik}</h1><p>{ac}</p></div>{suzgec}<ul class="kartlar">{"".join(kart(u) for u in l)}</ul>', sema, f" / {baslik}"))

# sınıf ve branş sayfaları
sinif_hepsi = sorted({x for u in urunler for x in u["siniflar"] if x!="hepsi"}, key=int)
for x in sinif_hepsi:
    l = [u for u in urunler if x in u["siniflar"]]; ortak = [u for u in urunler if "hepsi" in u["siniflar"]]
    vl = [v for u in l for v in uv(u)]
    g = f'<div class="makale" style="margin-bottom:28px"><h1>{x}. sınıf</h1><p>{x}. sınıf için atölyeler, araçlar ve kısa videolar.</p></div><ul class="kartlar">{"".join(kart(u) for u in l)}</ul>'
    if vl: g += f'<h2 class="ara-b">Kısa videolar</h2><div class="raf">{"".join(vkart(v) for v in vl[:16])}</div>'
    if ortak: g += f'<h2 class="ara-b">Her sınıfta kullanılanlar</h2><ul class="kartlar">{"".join(kart(u) for u in ortak)}</ul>'
    yaz(f"/sinif/{x}/", sayfa(f"{x}. sınıf etkinlik, atölye ve araçları | Herkese Eğitim", f"{x}. sınıf için ücretsiz atölyeler, tahta araçları ve kısa videolar.", f"/sinif/{x}/", g, None, f" / {x}. sınıf"))
for b in sorted({x for u in urunler for x in u["branslar"] if x!="hepsi"}):
    l = [u for u in urunler if b in u["branslar"]]; vl = [v for u in l for v in uv(u)]
    ad = BRANS_AD.get(b,b)
    g = f'<div class="makale" style="margin-bottom:28px"><h1>{E(ad)}</h1><p>{E(ad)} için atölyeler, araçlar ve kısa videolar.</p></div><ul class="kartlar">{"".join(kart(u) for u in l)}</ul>'
    if vl: g += f'<h2 class="ara-b">Kısa videolar</h2><div class="raf">{"".join(vkart(v) for v in vl[:16])}</div>'
    yaz(f"/brans/{b}/", sayfa(f"{ad} | Herkese Eğitim", f"{ad} için ücretsiz atölyeler, tahta araçları ve kısa videolar.", f"/brans/{b}/", g, None, f" / {E(ad)}"))

# videolar
gv = '<div class="makale" style="margin-bottom:28px"><h1>Videolar</h1><p>Kısa sorular ve tanıtımlar. Hepsi YouTube kanalında da var: @egitimtek.</p></div><div class="diziler">' + "".join(raf(d, 999) for d in ["tahmin","atasozu","ozel-gun","bilgisayarin-icinde","tanitim"]) + '</div>'
yaz("/videolar/", sayfa("Videolar | Herkese Eğitim", "3 saniyede tahmin et, Atasözlerimizi Yaşatalım, Özel Günler ve tanıtım videoları.", "/videolar/", gv, None, " / Videolar"))
for v in videolar:
    if any(a.get("video")==v["id"] for a in atasozleri): continue
    u = UR.get(v.get("urun") or "")
    ayni = [x for x in videolar if x.get("dizi")==v.get("dizi") and x["id"]!=v["id"]][:8]
    dz = DIZI.get(v.get("dizi"),("Video",""))
    g = f'''<div class="soz-sayfa"><article class="makale"><p style="font-weight:700;color:#9A1B15">{E(dz[0])}</p><h1>{E(v.get("kisa_ad"))}</h1>
{f'<p>{E(v["metin"])}</p>' if v.get("metin") else f'<p>{E(dz[1])}</p>'}
{f'<div class="kutu"><h2>İlgili {"atölye" if u["tur"]=="atolye" else "araç"}</h2><p><a href="{urun_sayfa(u)}">{E(u["ad"])}</a>: {E(u["kisa"])}</p></div>' if u else ""}
<p style="margin-top:22px"><a href="https://www.youtube.com/watch?v={E(v["id"])}">YouTube'da aç</a></p></article><aside>{vid_btn(v)}</aside></div>
{f'<h2 class="ara-b">Aynı diziden</h2><div class="raf">{"".join(vkart(x) for x in ayni)}</div>' if ayni else ""}'''
    yaz(video_sayfa(v), sayfa(f"{v.get('kisa_ad')} | Herkese Eğitim", (v.get("metin") or v.get("kisa_ad") or "")[:150], video_sayfa(v), g, [sema_video(v, video_sayfa(v))], " / <a href=\"/videolar/\">Videolar</a>", og=v.get("kapak_w")))

# indirme: ürün başına tek dosya, kademe çantaları
os.makedirs(os.path.join(OUT,"indir"), exist_ok=True)
for u in urunler:
    if u.get("canta") and u["durum"]=="yayinda":
        shutil.copy(u["canta"], os.path.join(OUT,"indir",u["id"]+".html")); u["indir"] = "/indir/"+u["id"]+".html"
cantalar = []
indirilen = [u for u in urunler if u.get("indir")]
cv = [{"id":u["id"],"ad":u["ad"],"sinif":u["sinif"],"s":u["siniflar"],"b":u["branslar"],"tur":u["tur"],"dosya":os.path.basename(u["canta"]),"mb":round(os.path.getsize(u["canta"])/1048576,1),"ogr":u["tur"]=="atolye" or u["id"]=="yaztahta"} for u in indirilen]
shutil.copy(os.path.join(KOK,"src","fflate.min.js"), os.path.join(OUT,"fflate.min.js"))
cg = '''<div class="makale" style="margin-bottom:24px"><h1>Çanta</h1><p>Seçtikleriniz tek bir zip dosyasında iner. Her dosya çift tıklayınca tarayıcıda açılır, internet istemez. Tahtaya USB bellekle de taşınır.</p></div>
<div id="canta-kur" class="canta-kur">
<fieldset class="soru"><legend>Kim için?</legend><div class="sec">
<label><input type="radio" name="ck" value="ogretmen"><span>Öğretmen</span></label>
<label><input type="radio" name="ck" value="ogrenci"><span>Öğrenci</span></label>
<label><input type="radio" name="ck" value="herkes" checked><span>Herkes</span></label></div></fieldset>
<p class="ck-not" id="ck-not" hidden>Öğrenci çantasını veli ya da öğretmen indirir ve öğrencinin bilgisayarına koyar.</p>
<fieldset class="soru" id="ck-kademe" hidden><legend>Kademe</legend><div class="sec">
<label><input type="radio" name="kd" value=""><span>Hepsi</span></label><label><input type="radio" name="kd" value="ilkokul"><span>İlkokul</span></label><label><input type="radio" name="kd" value="ortaokul"><span>Ortaokul</span></label><label><input type="radio" name="kd" value="lise"><span>Lise</span></label></div></fieldset>
<fieldset class="soru" id="ck-brans" hidden><legend>Branş</legend><div class="sec"><label><input type="radio" name="br" value="" checked><span>Hepsi</span></label>''' + "".join(f'<label><input type="radio" name="br" value="{b}"><span>{E(BRANS_AD.get(b,b))}</span></label>' for b in sorted({x for u in indirilen for x in u["branslar"] if x!="hepsi"})) + '''</div></fieldset>
<ul class="ck-liste" id="ck-liste"></ul>
<p><button class="dugme kir" type="button" id="ck-indir">Seçilenleri indir</button> <span id="ck-durum" role="status"></span></p>
</div>
<noscript><p><a class="dugme" href="/canta/Herkese%20Egitim%20cantasi.zip">Hepsini indir</a></p></noscript>
<p style="margin-top:28px;font-size:16px">Hepsi tek seferde: <a href="/canta/Herkese%20Egitim%20cantasi.zip" download>Herkese Eğitim çantası (zip)</a></p>
<script type="application/json" id="canta-veri">''' + json.dumps(cv, ensure_ascii=False).replace("</","<\\/") + '''</script><script src="/fflate.min.js"></script>'''
yaz("/canta/", sayfa("Çanta | Herkese Eğitim","Atölye ve araçları öğretmen, öğrenci ya da herkes için tek zip dosyasında indirin.","/canta/",cg,None," / Çanta"))

# RSS
def rfc(t):
    d = datetime.datetime.fromisoformat(t+"T09:00:00+03:00"); return d.strftime("%a, %d %b %Y %H:%M:%S +0300")
og = [(u["lansman"], u["ad"], SITE+urun_sayfa(u), u["kisa"]) for u in urunler if u["durum"]=="yayinda" and u.get("lansman")]
og += [(v["tarih"], v.get("kisa_ad"), SITE+video_sayfa(v), DIZI.get(v.get("dizi"),("Video",))[0]) for v in videolar if v.get("tarih")]
og = sorted(og, reverse=True)[:40]
rss = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>Herkese Eğitim: yenilikler</title><link>'+SITE+'/</link><atom:link href="'+SITE+'/yenilikler.xml" rel="self" type="application/rss+xml"/><description>Yeni atölyeler, araçlar ve videolar.</description><language>tr</language>' + "".join(f"<item><title>{E(b)}</title><link>{E(l)}</link><guid>{E(l)}</guid><pubDate>{rfc(t)}</pubDate><description>{E(a)}</description></item>" for t,b,l,a in og) + "</channel></rss>\n"
open(os.path.join(OUT,"yenilikler.xml"),"w",encoding="utf-8").write(rss)

# gizlilik
yaz("/gizlilik/", sayfa("Gizlilik | Herkese Eğitim","Bu sitede sayaç, takip ve çerez yok.","/gizlilik/",'''<article class="makale"><h1>Gizlilik</h1>
<p>Bu sitede sayaç, takip kodu ve çerez yok. Sitede hesap açılmaz, form doldurulmaz.</p>
<p>"Üç soru" seçimleriniz yalnız kendi tarayıcınızda saklanır, bize gelmez. Tarayıcının site verilerini silince kaybolur.</p>
<p>Videolar YouTube'dan gelir ve siz oynat düğmesine dokunana kadar yüklenmez. Dokununca YouTube'un çerezsiz oynatıcısı (youtube-nocookie.com) açılır; o andan sonra YouTube'un kendi kuralları geçerlidir.</p>
<p>Site GitHub Pages'ta durur ve Cloudflare üzerinden sunulur. Bu hizmetler, her web sitesinde olduğu gibi, sayfanın size ulaşması için teknik kayıt tutar; biz bu kayıtlardan yalnız toplam sayfa görüntüleme sayısını görürüz, kimin baktığını görmeyiz.</p>
<p>Araçlar ve atölyeler tarayıcınızda çalışır; içlerine yazdığınız bir şey bize gönderilmez.</p>
<p>Soru ve öneri: <a href="mailto:herkeseegitimtek@gmail.com">herkeseegitimtek@gmail.com</a></p></article>''', None, " / Gizlilik"))

konu_konu = urllib.parse.quote("Atölye önerisi")
konu_govde = urllib.parse.quote("Sınıf:\nBranş:\nKonu ya da öğrenme hedefi:\nÖğrencilerin en çok takıldığı yer:\n")
yaz("/konu/", sayfa("Konu önerin | Herkese Eğitim","Sınıfınızın konusunu yazın, atölyesini birlikte düşünelim.","/konu/",f'''<article class="makale"><h1>Konu önerin</h1>
<p>Sınıfınızın konusunu yazın, atölyesini birlikte düşünelim. Öğrencilerin en çok nerede takıldığını yazarsanız atölye oradan başlar.</p>
<p>Öğrenci adı yazmayın.</p>
<div class="paylas" style="margin-top:22px"><a class="dugme kir" href="https://mail.google.com/mail/?view=cm&amp;to=herkeseegitimtek@gmail.com&amp;su={konu_konu}&amp;body={konu_govde}" rel="noopener">Gmail ile yaz</a><a class="dugme acik" href="https://outlook.live.com/mail/0/deeplink/compose?to=herkeseegitimtek@gmail.com&amp;subject={konu_konu}&amp;body={konu_govde}" rel="noopener">Outlook ile yaz</a><a class="dugme acik" href="mailto:herkeseegitimtek@gmail.com?subject={konu_konu}&amp;body={konu_govde}">E-posta programı</a></div>
<p style="margin-top:18px;font-size:16px">Adres: herkeseegitimtek@gmail.com</p></article>''', None, " / Konu önerin"))
