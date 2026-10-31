#!/usr/bin/env python3
"""Herkese Eğitim sitesi: data/icerik.json + src/ -> out/"""
import json, os, re, shutil, html, zipfile, datetime, sys, urllib.parse
import segno
from PIL import Image

KOK = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(KOK, "out")
SITE = os.environ.get("SITE", "https://herkeseegitim.github.io").rstrip("/")
BUGUN = datetime.date.fromisoformat(os.environ.get("BUGUN", datetime.date.today().isoformat()))
E = lambda s: html.escape(str(s or ""), quote=True)
AYLAR = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
def tarih_tr(t):
    d = datetime.date.fromisoformat(t); return f"{d.day} {AYLAR[d.month-1]}"
def slug(s):
    s = str(s).replace("I","ı").replace("İ","i").lower()
    for a,b in zip("çğıöşüâî","cgiosuai"): s = s.replace(a,b)
    return re.sub(r"[^a-z0-9]+","-",s).strip("-")

veri = json.load(open(os.path.join(KOK,"data","icerik.json"), encoding="utf-8"))
def _dogrula(v):
    for u in v.get("urunler", []):
        assert re.fullmatch(r"[a-z0-9-]+", u["id"]), u["id"]
        for f in ("url","kilavuz"):
            if u.get(f): assert u[f].startswith("https://"), (u["id"], f)
        if u.get("video"): assert re.fullmatch(r"[\w-]{6,20}", u["video"]), u["video"]
        for x in u.get("sinif") or []: assert x=="hepsi" or re.fullmatch(r"\d{1,2}", x), x
        for x in u.get("brans") or []: assert re.fullmatch(r"[a-z]+", x), x
    for x in v.get("videolar", []):
        assert re.fullmatch(r"[\w-]{6,20}", x["id"]), x["id"]
        if x.get("urun"): assert re.fullmatch(r"[a-z0-9-]+", x["urun"]), x["urun"]
        for p_, a_ in (x.get("platformlar") or {}).items():
            if a_: assert a_.startswith("https://"), a_
    for x in v.get("atasozleri", []):
        if x.get("slug"): assert re.fullmatch(r"[a-z0-9-]+", x["slug"]), x["slug"]
        if x.get("video"): assert re.fullmatch(r"[\w-]{6,20}", x["video"]), x["video"]
_dogrula(veri)

# ---- ürünler: anlatım ve kapı eşlemesi burada; adres, video, tarih veriden gelir
URUN = {
 "ciztahta": dict(ad="ÇizTahta", tur="arac", kisa="Tarayıcıda açılan ücretsiz tahta. PDF üstüne yazın, perde, spot, kura.",
   sinif="Her branş, her sınıf", kademe="hepsi", ihtiyac="tahta", kim="ogretmen", etiket="Tahtada aç",
   ne="Akıllı tahtada ya da projeksiyonda tarayıcıda açılır. PDF ve çalışma kâğıdı üstüne yazarsınız; cevabı perdeyle kapatıp sırayla açarsınız, spotla tek bir yere dikkat çekersiniz, kura ile söz hakkını herkese dağıtırsınız. Hesap açmadan kullanılır."),
 "eklenti": dict(ad="ÇizTahta eklentisi", tur="arac", kisa="Açtığınız her sayfa tahtanız olsun. Derste de, toplantıda da.",
   sinif="Chrome ve Edge", kademe="hepsi", ihtiyac="tahta", kim="ogretmen meraklı", etiket="Mağazada aç",
   ne="Chrome'a bir kez eklenir. Derste hangi sayfa açıksa, web sayfası, PDF, sunum ya da video, Ç'ye basıp üstüne yazarsınız. Online toplantıda sunum yaparken de kullanılır."),
 "yaztahta": dict(ad="YazTahta", tur="arac", kisa="İlkokulda klavye: her tuşun yeri ve işi ekranda.",
   sinif="1–4. sınıf", kademe="ilkokul", ihtiyac="tahta atolye", kim="ogretmen ogrenci veli", etiket="Tahtada aç",
   ne="Harf Treni, Tuşun yolculuğu, Klavye yapbozu, Sınıfın treni. Laboratuvarda her öğrenci kendi klavyesiyle, akıllı tahtada bütün sınıf birlikte çalışır. Bir tuşa ilk dokunuşta sınıf önce tahmin eder, sonra görür."),
 "basit-makineler": dict(ad="Basit Makineler Atölyesi", tur="atolye", kisa="Tahmin edin, deneyin, açıklayın: makara, kaldıraç, eğik düzlem, çıkrık, dişli.",
   sinif="8. sınıf fen bilimleri", kademe="ortaokul", ihtiyac="atolye giris", kim="ogretmen ogrenci veli", etiket="Tahtada aç",
   ne="Öğrenci önce tahmin eder, sonra makarayı, kaldıracı, çıkrığı kendi kurar, ipi parmağıyla çeker. Kuvvetten kazanınca yoldan kaybettiğini kendi görür. Öğretmen sekmesinde ders akışı var."),
 "bilgisayarin-ici": dict(ad="Bilgisayarın İçi Atölyesi", tur="atolye", kisa="Kasa açılır: yazdığın cümle RAM'de mi, fişi çekince nereye gider?",
   sinif="5. sınıf bilişim teknolojileri ve yazılım", kademe="ortaokul", ihtiyac="atolye giris", kim="ogretmen ogrenci veli", etiket="Tahtada aç",
   ne="Öğrenci bir cümle yazar, 3B kasayı açar, harflerin RAM'de bit olarak durduğunu görür. Fişi çekince bitler söner; Kaydet'e basınca işletim sistemi bitleri depolama birimine yazar. Rehberli ders, deney masası, beş görev."),
 "yuzdeler": dict(ad="Yüzdeler Atölyesi", tur="atolye", kisa="%20 indirimin üstüne %20 daha: %40 mı?",
   sinif="7. sınıf matematik", kademe="ortaokul", ihtiyac="atolye kendim giris", kim="ogretmen ogrenci veli", etiket="Tahtada aç",
   ne="Yüzdeyi günlük hayattaki sorularla çalışır: indirim, artış, bütünün değişmesi. Önce \"%100 hangisi?\" sorulur, sonra tahmin. Kendim çalışıyorum bölümünde adım adım yol, takıldığında ipucu ve sınava hazırlık var."),
 "yanki": dict(ad="Yankı: Yer Altı Şehri", tur="oyun", kisa="Yer altı şehrinde Yankı adlı bir ışık yalnız oyuncudan gördüğünü öğrenir.",
   sinif="5–6. sınıf bilişim", kademe="ortaokul", ihtiyac="atolye", kim="ogretmen veli", etiket="Aç",
   ne="Dijital vatandaşlık oyunu."),
}
SIRA = ["ciztahta","yaztahta","eklenti","basit-makineler","bilgisayarin-ici","yuzdeler","yanki"]
EŞ_ = EŞ = {"ciztahta-eklentisi":"eklenti","ciztahta-eklenti":"eklenti","yuzdeler-atolyesi":"yuzdeler","matematik-yuzde":"yuzdeler","basit-makineler-atolyesi":"basit-makineler","bilgisayarin-ici-atolyesi":"bilgisayarin-ici"}
vu = {u.get("id"): u for u in veri.get("urunler", [])}
CANTA = {"ciztahta":"ÇizTahta.html","yaztahta":"YazTahta.html","basit-makineler":"Basit Makineler Atölyesi.html","bilgisayarin-ici":"Bilgisayarın İçi Atölyesi.html","yuzdeler":"Yüzdeler Atölyesi.html"}
BASLIK = {"mY8zhg8sXM8":"Akıllı tahtada bir ders baştan sona: kurulum yok, hesap yok","ydp5nstgcnI":"Bir ders baştan sona (İngilizce)","2qJOXs_TSh8":"Her sayfa tahtanız olsun: ÇizTahta Chrome eklentisi","3dFYUrfl44E":"YazTahta: ilkokulda klavye","4UMHg4ggUS4":"Kaydetmeden kapattınız. Yazınız nereye gitti? | Bilgisayarın İçi"}
def kp(i):
    p = os.path.join(KOK,"data","kapak",i+".png"); return p if os.path.exists(p) else None
for v in veri.get("videolar", []):
    v["kapak_dosya"] = kp(v["id"]); v["urun"] = EŞ_.get(v.get("urun"), v.get("urun"))
    if not v.get("baslik"): v["baslik"] = BASLIK.get(v["id"], "")
for a in veri.get("atasozleri", []): a["kapak_dosya"] = kp(a.get("video") or "")
for k,v in list(vu.items()):
    if k in EŞ: vu[EŞ[k]] = v
urunler = []
for i,k in enumerate(SIRA, 1):
    u = dict(URUN[k]); d = vu.get(k, {})
    u.update(siniflar=d.get("sinif") or ["hepsi"], branslar=d.get("brans") or ["hepsi"], surum_notu=d.get("surum_notu"), kilavuz=d.get("kilavuz"))
    u.update(id=k, no=f"{i:02d}", url=d.get("url"), video=d.get("video"), lansman=d.get("lansman"),
             kazanim=d.get("kazanim") or [], kapak=kp(d.get("id") or k), canta=(os.path.join(KOK,"data","canta",CANTA[k]) if k in CANTA else None))
    u["durum"] = "yayinda" if u["url"] and not (u["lansman"] and datetime.date.fromisoformat(u["lansman"]) > BUGUN) else "yakinda"
    u["bugun"] = False
    if u["durum"]=="yayinda" and u.get("lansman")==BUGUN.isoformat() and os.environ.get("ADRES_DENE"):
        # lansman günü: atölye adresi henüz açılmadıysa "bugün açılıyor" kalır
        try:
            import urllib.request
            urllib.request.urlopen(urllib.request.Request(u["url"], method="HEAD"), timeout=10)
        except Exception:
            u["durum"] = "yakinda"; u["bugun"] = True
    urunler.append(u)
UR = {u["id"]: u for u in urunler}

videolar = sorted(veri.get("videolar", []), key=lambda v: v.get("tarih") or "", reverse=True)
atasozleri = sorted(veri.get("atasozleri", []), key=lambda a: int(a.get("no") or 0))
for a in atasozleri: a["slug"] = a.get("slug") or slug(a["soz"])
takvim = [
 {"tarih":"2026-10-16","baslik":"ÇizTahta","tur":"arac","not":"Tarayıcıda açılan tahta"},
 {"tarih":"2026-10-24","baslik":"Basit Makineler","tur":"atolye","not":"8. sınıf fen","urun":"basit-makineler"},
 {"tarih":"2026-10-25","baslik":"Bilgisayarın İçi","tur":"atolye","not":"5. sınıf bilişim","urun":"bilgisayarin-ici"},
 {"tarih":"2026-10-30","baslik":"Yüzdeler","tur":"atolye","not":"7. sınıf matematik","urun":"yuzdeler"},
 {"tarih":"2026-11-06","baslik":"Yankı","tur":"atolye","not":"5–6. sınıf bilişim oyunu","urun":"yanki"},
]

# ---- çıktı klasörü
if os.path.exists(OUT): shutil.rmtree(OUT)
for d in ["fonts","img","urun","atasozleri","hakkinda","canta"]: os.makedirs(os.path.join(OUT,d), exist_ok=True)
for f in ["bg.woff2","bg-ext.woff2"]: shutil.copy(os.path.join(KOK,"fonts",f), os.path.join(OUT,"fonts",f))
css = open(os.path.join(KOK,"src","site.css"),encoding="utf-8").read()
js = open(os.path.join(KOK,"src","site.js"),encoding="utf-8").read()
open(os.path.join(OUT,"site.css"),"w",encoding="utf-8").write(css)
open(os.path.join(OUT,"site.js"),"w",encoding="utf-8").write(js)

def resim(kaynak, ad, en, oran=None):
    """data/kapak altındaki png'yi webp'ye çevirir; yoksa None"""
    if not kaynak: return None
    p = kaynak if os.path.isabs(kaynak) else os.path.join(KOK,"data",kaynak)
    if not os.path.exists(p): return None
    im = Image.open(p).convert("RGB"); im.thumbnail((en, en*2))
    hedef = f"img/{ad}.webp"; im.save(os.path.join(OUT,hedef), quality=78, method=6)
    return "/"+hedef
for f,ad in [("marka/imza-acik.png","imza-acik"),("marka/imza.png","imza"),("marka/avatar.png","avatar"),("marka/logo.png","logo")]:
    p = os.path.join(KOK,"data",f)
    if os.path.exists(p):
        im = Image.open(p); im.thumbnail((600,600)); im.save(os.path.join(OUT,"img",ad+".png"), optimize=True)
shutil.copy(os.path.join(KOK,"data","marka","paylas.png"), os.path.join(OUT,"img","paylas.png"))
LOGO_ACIK, LOGO, AVATAR = "/img/imza-acik.png", "/img/imza.png", "/img/avatar.png"

for u in urunler: u["kapak_w"] = resim(u["kapak"], "urun-"+u["id"], 960)
for v in videolar:
    dik = True
    if v.get("kapak_dosya"):
        w,h = Image.open(v["kapak_dosya"]).size; dik = h > w
    v["kapak_w"] = resim(v.get("kapak_dosya"), "v-"+v["id"], 420 if dik else 960); v["dik"] = dik
    v["kisa_ad"] = re.split(r"\s+\|\s+", v.get("baslik") or "")[0]
    if not v["kisa_ad"]:
        _u = UR.get(v.get("urun") or "")
        v["kisa_ad"] = (_u["ad"]+" tanıtımı") if _u else "Herkese Eğitim videosu"
for a in atasozleri:
    eş = next((v for v in videolar if v["id"] == a.get("video")), None)
    a["kapak_w"] = eş["kapak_w"] if eş else resim(a.get("kapak_dosya"), "a-"+a["slug"], 420)

def qr_svg(url):
    q = segno.make(url, error="m", micro=False)
    import io; b = io.BytesIO(); q.save(b, kind="svg", xmldecl=False, svgns=True, nl=False, border=2, dark="#2A1C10")
    s = b.getvalue().decode(); return re.sub(r'(width|height)="\d+"', "", s, count=2).replace("<svg ", '<svg viewBox="0 0 %d %d" role="img" aria-label="Karekod" ' % ((q.symbol_size(border=2)[0],)*2), 1)

def kisa_adres(url):
    return re.sub(r"^https?://(www\.)?","",url or "").rstrip("/")

# ---- ortak parçalar
import hashlib as _h
SURUM = _h.sha1((open(os.path.join(KOK,"src","site.css"),encoding="utf-8").read()+open(os.path.join(KOK,"src","site.js"),encoding="utf-8").read()).encode()).hexdigest()[:8]
def bas(baslik, aciklama, yol, ek_head="", sema=None, og=None):
    can = SITE + yol
    s = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False).replace("</","<\\/")}</script>' for x in (sema or []) if x)
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(baslik)}</title><meta name="description" content="{E(aciklama)}"><link rel="canonical" href="{E(can)}">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'sha256-pfgOMgfVZwm2ODyms34QYW9h8EwicylhV77q5LHK8c0='; object-src 'none'; frame-src https://www.youtube-nocookie.com; font-src 'self'; connect-src 'self'; base-uri 'self'; form-action 'none'">
<meta name="referrer" content="strict-origin-when-cross-origin"><meta name="theme-color" content="#2A2420">
<meta property="og:type" content="website"><meta property="og:title" content="{E(baslik)}"><meta property="og:description" content="{E(aciklama)}"><meta property="og:url" content="{E(can)}"><meta property="og:image" content="{SITE}{og or "/img/paylas.png"}"><meta property="og:locale" content="tr_TR">
<meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/img/logo.png">
<script>document.documentElement.className+=" js"</script><link rel="stylesheet" href="/site.css?v={SURUM}"><link rel="alternate" type="application/rss+xml" title="Herkese Eğitim yenilikler" href="/yenilikler.xml">{ek_head}{s}</head><body><a class="atla" href="#ana">İçeriğe geç</a>"""

NAV = '<nav aria-label="Ana menü"><a href="/atolyeler/">Atölyeler</a><a href="/araclar/">Araçlar</a><a href="/videolar/">Videolar</a><a href="/atasozleri/">Atasözleri</a><a href="/canta/">Çanta</a><a href="/hakkinda/">Hakkında</a></nav>'
def ust_koyu():
    return f'<header class="ust koyu"><div class="w"><a class="logo" href="/"><img src="{LOGO}" alt="Herkese Eğitim ana sayfa" width="200" height="46"></a>{NAV}</div></header>'
ALT = f"""<footer class="cikis"><div class="w">
<div class="cikis-ust"><div class="zil-blok"><svg class="zil-b" viewBox="0 0 64 64" aria-hidden="true"><path d="M32 6c-11 0-18 8-18 20v12l-6 8h48l-6-8V26C50 14 43 6 32 6z"/><circle cx="32" cy="52" r="5"/><rect x="29" y="1" width="6" height="7" rx="2"/></svg><p class="cikis-b">Zil çaldı.</p><p class="cikis-a">Yarın yine buradayız. Çıkmadan bir ödev:</p></div>
__ODEV__
<div class="mik-kol"><div class="miknatis" role="list" aria-label="Sosyal medya">
<a role="listitem" class="m m-yt" href="https://www.youtube.com/@egitimtek"><b>YT</b><span>YouTube</span></a>
<a role="listitem" class="m m-ig" href="https://www.instagram.com/egitimtek/"><b>IG</b><span>Instagram</span></a>
<a role="listitem" class="m m-tt" href="https://www.tiktok.com/@egitimtek"><b>TT</b><span>TikTok</span></a>
<a role="listitem" class="m m-x" href="https://x.com/cincinosos"><b>X</b><span>X</span></a>
<a role="listitem" class="m m-in" href="https://www.linkedin.com/in/idiye/"><b>in</b><span>LinkedIn</span></a>
<a role="listitem" class="m m-wp" href="https://egitimteknoloji.wordpress.com/"><b>W</b><span>Blog</span></a>
<a role="listitem" class="m m-gh" href="https://github.com/herkeseegitim"><b>GH</b><span>GitHub</span></a>
</div>
<p class="miknatis-not" aria-hidden="true">Mıknatısları tahtada gezdirebilirsiniz.</p></div></div>

<div class="cikis-alt"><img class="imza" src="{LOGO_ACIK}" alt="Herkese Eğitim" width="200" height="46">
<ul><li><a href="mailto:herkeseegitimtek@gmail.com">herkeseegitimtek@gmail.com</a></li><li><a href="/konu/">Konu önerin</a></li><li><a href="/hakkinda/">Hakkında</a></li><li><a href="/gizlilik/">Gizlilik</a></li></ul></div>
<p class="kucuk">Bu sitede sayaç ve takip yok. YouTube videoları siz dokunana kadar yüklenmez. © 2026 Herkese Eğitim</p></div></footer>
<dialog class="kare" id="kare" aria-labelledby="kare-b"><div class="ic"><h2 id="kare-b">Tahtada aç</h2><div class="qr"></div><p class="adres"></p><p>Adresi tahtadaki tarayıcıya yazın. Öğrenciler karekodu kendi cihazıyla okutabilir.</p><div class="eyl"><a class="dugme kir ac" href="#">Bu cihazda aç</a><button class="dugme acik kapat" type="button">Kapat</button></div></div></dialog>
<script src="/site.js?v={SURUM}"></script></body></html>"""

def vid_btn(v, ad=None):
    if not v: return ""
    ad = ad or v.get("baslik","")
    img = f'<img src="{v["kapak_w"]}" alt="" loading="lazy">' if v.get("kapak_w") else f'<span class="vid-bos" aria-hidden="true">{E(v.get("kisa_ad") or ad)}</span>'
    return f'<button class="vid{" dik" if v.get("dik") else ""}" type="button" data-id="{E(v["id"])}" aria-label="Videoyu oynat: {E(ad)}">{img}<span class="oynat" aria-hidden="true"></span></button>'
VBY = {v["id"]: v for v in videolar}
def urun_video(u):
    v = VBY.get(u.get("video"))
    if v: return v
    if u.get("video"): return {"id":u["video"],"baslik":u["ad"],"kapak_w":u.get("kapak_w"),"dik":False,"tarih":u.get("lansman")}
    return None
def ac_dugme(u, sinif="dugme"):
    if u["durum"] != "yayinda": return ""
    return f'<a class="{sinif}" href="{E(u["url"])}" data-kare="{u["id"]}" aria-haspopup="dialog" data-ad="{E(u["ad"])}" data-url="{E(u["url"])}" data-kisa="{E(kisa_adres(u["url"]))}" data-etiket="Bu cihazda aç">{E(u["etiket"])}</a>'
def qr_gizli():
    return "".join(f'<template id="qr-{u["id"]}">{qr_svg(u["url"])}</template>' for u in urunler if u["durum"]=="yayinda")

# ---- schema.org
KISI = {"@type":"Person","@id":SITE+"/hakkinda/#idiye","name":"İdiye Ökten","url":SITE+"/hakkinda/","sameAs":["https://www.linkedin.com/in/idiye/"]}
KURUM = {"@type":"Organization","@id":SITE+"/#kurum","name":"Herkese Eğitim","url":SITE+"/","logo":SITE+"/img/logo.png","founder":{"@id":KISI["@id"]},"email":"herkeseegitimtek@gmail.com",
  "sameAs":["https://www.youtube.com/@egitimtek","https://www.instagram.com/egitimtek/","https://x.com/cincinosos","https://github.com/herkeseegitim"]}
def sema_urun(u):
    if u["tur"] == "atolye":
        s = {"@context":"https://schema.org","@type":"LearningResource","name":u["ad"],"description":u["ne"],"url":u["url"],"inLanguage":"tr","isAccessibleForFree":True,
             "learningResourceType":"Etkileşimli simülasyon","educationalLevel":u["sinif"],"audience":{"@type":"EducationalAudience","educationalRole":"teacher"},
             "provider":{"@id":KURUM["@id"]},"author":{"@id":KISI["@id"]}}
        if u["kazanim"]: s["teaches"] = u["kazanim"]; s["educationalAlignment"] = [{"@type":"AlignmentObject","alignmentType":"teaches","educationalFramework":"MEB öğretim programı","targetName":k} for k in u["kazanim"]]
    else:
        s = {"@context":"https://schema.org","@type":"SoftwareApplication" if u["tur"]=="arac" else "VideoGame","name":u["ad"],"description":u["ne"],"url":u["url"],"inLanguage":"tr",
             "applicationCategory":"EducationalApplication","operatingSystem":"Tarayıcı","offers":{"@type":"Offer","price":"0","priceCurrency":"TRY"},"author":{"@id":KISI["@id"]},"publisher":{"@id":KURUM["@id"]}}
    if u["durum"] != "yayinda": s.pop("url", None)
    elif u.get("lansman"): s["datePublished"] = u["lansman"]
    return s
def sema_video(v, sayfa):
    s = {"@context":"https://schema.org","@type":"VideoObject","name":v.get("baslik"),"description":v.get("aciklama") or v.get("baslik"),
         "embedUrl":"https://www.youtube-nocookie.com/embed/"+v["id"],"contentUrl":"https://www.youtube.com/watch?v="+v["id"],"inLanguage":"tr","publisher":{"@id":KURUM["@id"]}}
    if v.get("kapak_w"): s["thumbnailUrl"] = SITE + v["kapak_w"]
    t = tarih_iso(v.get("tarih"))
    if t: s["uploadDate"] = t
    eksik = [k for k in ("name","thumbnailUrl","uploadDate") if not s.get(k)]
    if eksik:  # Google VideoObject: name, thumbnailUrl, uploadDate zorunlu; eksik öğe yayınlanmaz
        print(f"UYARI: {v['id']} videosunun şeması yazılmadı, eksik: {', '.join(eksik)} (tarih={v.get('tarih')!r})", file=sys.stderr)
        return None
    return s
def tarih_iso(t):
    """uploadDate: ISO 8601, saat ve saat dilimiyle. Yalnız gün verilirse 09:00 İstanbul; geçersizse None."""
    if not t: return None
    t = str(t).strip().replace(" ", "T")
    try:
        d = datetime.datetime.fromisoformat(t[:-1] + "+00:00" if t.endswith("Z") else t)
    except ValueError:
        return None
    if len(t) == 10: d = d.replace(hour=9)
    if d.tzinfo is None: d = d.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=3)))
    return d.isoformat(timespec="seconds")

# ---- sayfa adresleri
def urun_sayfa(u): return f"/urun/{u['id']}/"
def soz_sayfa(a): return f"/atasozleri/{a['slug']}/"
def video_sayfa(v):
    a = next((a for a in atasozleri if a.get("video")==v["id"]), None)
    if a: return soz_sayfa(a)
    return "/video/"+v["id"]+"/"
_odev = [v for v in videolar if (v.get("kisa_ad") or "").strip().endswith("?")]
if _odev:
    _o = _odev[BUGUN.toordinal() % len(_odev)]
    _oh = f'<a class="odev" href="{video_sayfa(_o)}"><span class="odev-e">Bugünün ödevi</span><b>{E(_o["kisa_ad"])}</b><span class="odev-n">Önce tahmin edin, sonra izleyin.</span></a>'
else: _oh = ""
ALT = ALT.replace("__ODEV__", _oh)
def lbas(h1, p, satirlar):
    et = "".join(f'<div><dt>{E(a)}</dt><dd>{b}</dd></div>' for a,b in satirlar)
    return f'<div class="liste-bas"><div class="makale"><h1>{h1}</h1><p>{p}</p></div><dl class="defter-etiket" aria-label="Bu sayfada">{et}</dl></div>'
DIZI = {"tahmin":("3 saniyede tahmin et","Günlük hayattan bir soru, 3 saniye düşün, cevap sonda. Derse giriş için."),
        "atasozu":("Atasözlerimizi Yaşatalım","Az bilinen atasözleri ve unutulan sözcükleri. Her birinin anlamı kendi sayfasında."),
        "ozel-gun":("Özel Günler","Belirli günler için kısa videolar."),
        "bilgisayarin-icinde":("Bilgisayarın içinde ne oluyor","Bilgisayarın içinde gerçekte ne olduğunu kısa sorularla."),
        "tanitim":("Tanıtımlar","Araçların ve atölyelerin nasıl kullanıldığı.")}

# ---- arama dizini
ara = []
for u in urunler:
    ara.append(dict(t="atolye" if u["tur"]=="atolye" else "arac", tl={"atolye":"Atölye","arac":"Araç","oyun":"Oyun"}[u["tur"]], b=u["ad"], a=u["sinif"]+(" · yakında" if u["durum"]!="yayinda" else ""), k=("atölye " if u["tur"]=="atolye" else "araç ")+u["kisa"]+" "+u["ne"]+" "+" ".join(u["kazanim"]), u=urun_sayfa(u)))
for a in atasozleri:
    ara.append(dict(t="atasozu", tl="Atasözü", b=a["soz"], a=(a.get("anlam") or "")[:90], k="atasözü atasozu "+" ".join(filter(None,[a.get("soru"),(a.get("sozcuk") or {}).get("kelime")])), u=soz_sayfa(a)))
for v in videolar:
    if v.get("dizi")=="atasozu": continue
    ara.append(dict(t="video", tl="Video", b=v.get("kisa_ad"), a=DIZI.get(v.get("dizi"),("Video",))[0], k=v.get("aciklama") or "", u=video_sayfa(v)))

# ---- son videolar (biyografi bağlantısı için)
def son_kaydi(v):
    a = next((a for a in atasozleri if a.get("video")==v["id"]), None)
    ileri = "Atasözünün anlamı ve videosu burada." if a else ("Video ve ilgili atölye burada." if v.get("urun") else "Video ve benzerleri burada.")
    return dict(id=v["id"], baslik=v.get("kisa_ad"), kapak=v.get("kapak_w") or AVATAR, sayfa=video_sayfa(v), ileri=ileri)
son = {"yt":[son_kaydi(v) for v in sorted(videolar, key=lambda v: v.get("tarih") or "", reverse=True)[:3]], "hepsi":[son_kaydi(v) for v in videolar]}
for p in ["ig","tt","x","li"]:
    l = sorted([v for v in videolar if (v.get("platformlar") or {}).get(p)], key=lambda v: v.get("tarih") or "", reverse=True)
    if l: son[p] = [son_kaydi(v) for v in l[:3]]

# ---- ana sayfa
atl = [t for t in takvim if t.get("tur")=="atolye" and t.get("urun") in UR]
gelen = [t for t in atl if datetime.date.fromisoformat(t["tarih"]) > BUGUN]
gecen = [t for t in atl if datetime.date.fromisoformat(t["tarih"]) <= BUGUN]
if gelen and (datetime.date.fromisoformat(gelen[0]["tarih"]) - BUGUN).days <= 1: cuma = gelen[0]; siradaki = gelen[1] if len(gelen)>1 else None
else: cuma = gecen[-1] if gecen else gelen[0]; siradaki = gelen[0] if gelen else None
hafta_u = UR[cuma["urun"]]
ETIKET = ("Cuma, "+tarih_tr(cuma["tarih"])) if datetime.date.fromisoformat(cuma["tarih"]) > BUGUN else "Haftanın atölyesi"
SIRADAKI = f'Sıradaki Cuma: {siradaki["baslik"]}, {tarih_tr(siradaki["tarih"])}' if siradaki else ""
duvar_v = [v for v in videolar if v.get("kapak_w")][:14]
duvar = []
for i in range(16):
    if i % 4 == 2: k = [u for u in urunler if u.get("kapak_w")];
    else: k = None
    if k: duvar.append(f'<img class="yat" src="{k[i % len(k)]["kapak_w"]}" alt="" loading="lazy">')
    elif duvar_v: v = duvar_v[i % len(duvar_v)]; duvar.append(f'<img class="{"dik" if v["dik"] else "yat"}" src="{v["kapak_w"]}" alt="" loading="{"eager" if i<6 else "lazy"}">')

satirlar = []
for u in urunler:
    cls = "sat" + (" cuma" if u is hafta_u else "") + (" yakinda" if u["durum"]!="yayinda" and u is not hafta_u else "")
    zaman = ""
    if u["durum"] != "yayinda":
        zaman = f'<span class="dugme acik" aria-disabled="true">{"Bugün açılıyor" if u.get("bugun") else tarih_tr(u["lansman"])}</span>' if u.get("lansman") else '<span class="dugme acik" aria-disabled="true">Yakında</span>'
    satirlar.append(f'''<div class="{cls}" id="u-{u["id"]}" data-tarih="{u.get("lansman") or ""}" data-durum="{u["durum"]}" data-kademe="{u["kademe"]}" data-ihtiyac="{u["ihtiyac"]}" data-kim="{u["kim"]}"><span class="rozet" hidden>Size uygun</span><span class="no" aria-hidden="true">{u["no"]}</span>
<h3><a href="{urun_sayfa(u)}">{E(u["ad"])}</a></h3><p class="ne">{E(u["kisa"])}</p><p class="sin">{E(u["sinif"])}{"<br><b>"+E(ETIKET)+"</b>" if u is hafta_u else ""}</p><div class="eyl">{ac_dugme(u) or zaman}</div></div>''')

def son_videolar(n=10):
    l = sorted([v for v in videolar if v.get("tarih")], key=lambda v: v["tarih"], reverse=True)[:n]
    kartlar = "".join(f'<figure id="v-{E(v["id"])}" data-tarih="{E(v.get("tarih") or "")}">{vid_btn(v)}<figcaption><span class="vd-dz">{E(DIZI.get(v.get("dizi"),("Video",))[0])}</span><a href="{video_sayfa(v)}">{E(v.get("kisa_ad"))}</a></figcaption></figure>' for v in l)
    sayi = {d: sum(1 for v in videolar if v.get("dizi")==d) for d in DIZI}
    cip = "".join(f'<a class="vd-cip" href="/videolar/#dizi={d}">{E(DIZI[d][0])} <i>{n_}</i></a>' for d,n_ in sayi.items() if n_)
    return f'<div class="dizi"><h3>Son videolar</h3><div class="raf">{kartlar}</div><div class="vd-alt">{cip}<a class="dugme kir" href="/videolar/">Bütün videolar ({len(videolar)})</a></div></div>'
def raf(dizi, sinir=8):
    l = [v for v in videolar if v.get("dizi")==dizi]
    if not l: return ""
    ad, ac = DIZI[dizi]
    kartlar = "".join(f'<figure id="v-{E(v["id"])}" data-tarih="{E(v.get("tarih") or "")}">{vid_btn(v)}<figcaption><a href="{video_sayfa(v)}">{E(v.get("kisa_ad"))}</a></figcaption></figure>' for v in l[:sinir])
    hepsi = f'<p class="hepsi"><a href="/videolar/#d-{dizi}">Bütün {E(ad)} videoları ({len(l)})</a></p>' if len(l) > sinir else ""
    return f'<div class="dizi{" gen" if dizi=="tanitim" else ""}" id="d-{dizi}"><h3>{E(ad)}</h3><p>{E(ac)} {len(l)} video.</p><div class="raf">{kartlar}</div>{hepsi}</div>'

cumalar = "".join(
    f'<li class="{"simdi" if t is cuma else ("gelecek" if datetime.date.fromisoformat(t["tarih"])>BUGUN else "")}"><time datetime="{t["tarih"]}">{tarih_tr(t["tarih"])}</time><b>{E(t["baslik"])}</b><span>{E(t.get("not") or "")}</span></li>'
    for t in takvim)

exec(open(os.path.join(KOK,"src","sayfalar.py"),encoding="utf-8").read())
canta_dosyalar = [u for u in urunler if u.get("canta") and u["durum"]=="yayinda"]
canta_ad = "Herkese Egitim cantasi.zip"
if canta_dosyalar:
    with zipfile.ZipFile(os.path.join(OUT,"canta",canta_ad),"w",zipfile.ZIP_DEFLATED) as z:
        for u in canta_dosyalar:
            p = u["canta"] if os.path.isabs(u["canta"]) else os.path.join(KOK,"data",u["canta"])
            z.write(p, os.path.basename(p))
        z.writestr("OKU.txt", "Herkese Eğitim çantası\n\nHer dosya tek başına açılır: çift tıklayın, tarayıcıda açılır. İnternet gerekmez.\nTahtaya USB bellekle taşıyabilirsiniz.\n\nGüncel sürümler: "+SITE+"/\nSorun ve öneri: herkeseegitimtek@gmail.com\n\n"+"\n".join(f"{os.path.basename(u['canta'] if os.path.isabs(u['canta']) else os.path.join(KOK,'data',u['canta']))}: {u['ad']}, {u['sinif']}" for u in canta_dosyalar)+"\n\nTarih: "+BUGUN.isoformat()+"\n")
    canta_boy = os.path.getsize(os.path.join(OUT,"canta",canta_ad))/1048576
def boy(u):
    p = u["canta"] if os.path.isabs(u["canta"]) else os.path.join(KOK,"data",u["canta"]); return f"{os.path.getsize(p)/1048576:.1f} MB".replace(".",",")
canta_html = f'''<section class="blm canta" id="canta"><div class="w ic"><div><h2>Çanta</h2><p>Atölye ve araçları tek zip dosyasında indirin. Her dosya çift tıklayınca tarayıcıda açılır, internet istemez.</p></div>
<div class="canta-sec"><a class="dugme" href="/canta/#ogretmen">Öğretmen çantası</a><a class="dugme" href="/canta/#ogrenci">Öğrenci çantası</a><a class="dugme" href="/canta/#herkes">Herkes için</a><p>Öğretmende kademe ve branş, öğrencide sınıf seçilir.</p></div></div></section>'''
hv = urun_video(hafta_u)
hafta_html = f'''<section class="blm hafta" id="hafta" aria-labelledby="hafta-b"><div class="w"><div class="ic"><div>
<small>{ETIKET}</small><h2 id="hafta-b">{E(hafta_u["ad"])}</h2><p class="ne">{E(hafta_u["kisa"])}</p><p style="margin-top:8px;font-weight:600">{E(hafta_u["sinif"])}{". "+E(SIRADAKI)+"." if SIRADAKI else ""}</p>
<div class="eyl">{ac_dugme(hafta_u,"dugme kir") or ('<span class="dugme kir" aria-disabled="true">'+(tarih_tr(hafta_u["lansman"]) if hafta_u.get("lansman") else "Cuma")+'\'de açılıyor</span>')}<a class="dugme acik" href="{urun_sayfa(hafta_u)}">Atölyeyi incele</a></div></div>
<div>{vid_btn(hv, hafta_u["ad"]) if hv else (f'<img src="{hafta_u["kapak_w"]}" alt="" style="border-radius:12px">' if hafta_u.get("kapak_w") else "")}</div></div>
<h3 class="gizli">Takvim</h3><ol class="cumalar" aria-label="Takvim">{cumalar}</ol></div></section>'''

kapi_html = '''<section class="kapi" id="kapi" aria-labelledby="kapi-b"><div class="w"><div><h2 id="kapi-b">Üç soru</h2><p class="ac">Seçtiklerinize uyanları listenin başına alırım. Seçiminiz yalnız bu cihazda kalır; sitede sayaç ve takip yok.</p></div><div>
<fieldset class="soru"><legend>Kimsiniz?</legend>''' + '<div class="sec">' + "".join(f'<label><input type="radio" name="kim" value="{v}"><span>{t}</span></label>' for v,t in [("ogretmen","Öğretmenim"),("veli","Veliyim"),("ogrenci","Öğrenciyim"),("meraklı","Merak ettim")]) + '''</div></fieldset>
<fieldset class="soru"><legend>Hangi sınıf?</legend><div class="sec">''' + "".join(f'<label><input type="radio" name="kademe" value="{v}"><span>{t}</span></label>' for v,t in [("ilkokul","İlkokul"),("ortaokul","Ortaokul"),("lise","Lise")]) + '''</div></fieldset>
<fieldset class="soru"><legend>Ne lazım?</legend><div class="sec">''' + "".join(f'<label><input type="radio" name="ihtiyac" value="{v}"><span>{t}</span></label>' for v,t in [("tahta","Tahtada araç"),("giris","Derse giriş sorusu"),("atolye","Konuyu keşfettiren atölye"),("kendim","Evde kendi çalışma")]) + '''</div></fieldset>
<p class="kapi-sonuc" id="kapi-sonuc" role="status" aria-live="polite"></p><button class="temizle" type="button">Seçimleri temizle</button></div></div></section>'''

sema_ana = [{"@context":"https://schema.org","@graph":[KURUM,KISI,{"@type":"WebSite","@id":SITE+"/#site","url":SITE+"/","name":"Herkese Eğitim","inLanguage":"tr","publisher":{"@id":KURUM["@id"]}},
   {"@type":"ItemList","name":"Herkese Eğitim kitaplığı","itemListElement":[{"@type":"ListItem","position":i+1,"url":SITE+urun_sayfa(u),"name":u["ad"]} for i,u in enumerate(urunler)]}]}]
open(os.path.join(OUT,"ara.json"),"w",encoding="utf-8").write(json.dumps(ara, ensure_ascii=False))
gs = [dict(q, u=video_sayfa(VBY[q["v"]]), t=VBY[q["v"]].get("tarih")) for q in json.load(open(os.path.join(KOK,"data","sorular.json"),encoding="utf-8")) if q["v"] in VBY and (VBY[q["v"]].get("tarih") or "9") <= BUGUN.isoformat()]
ana_veri = json.dumps({"son":son,"gs":gs,"soz":[{"s":a["soz"],"u":soz_sayfa(a),"n":a.get("no")} for a in atasozleri]}, ensure_ascii=False).replace("</","<\\/")
ana = bas("Herkese Eğitim: öğretmene, öğrenciye, herkese ücretsiz paylaşımlar",
  "İdiye Ökten'in ücretsiz paylaşımları: tahtada açılan araçlar, MEB öğrenme çıktılarına bağlı atölyeler, tahmin soruları, atasözleri ve özel gün videoları. ", "/", sema=sema_ana) + f'''
<header class="ust"><div class="w"><a class="logo" href="/"><img src="{LOGO_ACIK}" alt="Herkese Eğitim ana sayfa" width="200" height="46"></a>{NAV}</div></header>
<main id="ana">
<section class="sahne" aria-labelledby="h1"><div class="arka" aria-hidden="true"><div class="duvar gece">{"".join(duvar)}</div><div class="gunkat"><div class="duvar gun">{"".join(duvar).replace(' loading="lazy"',"")}</div></div><div class="ortu"></div></div>
<canvas class="tahta" id="tahta" aria-hidden="true"></canvas>
<div class="w"><div class="yazi">
<h1 id="h1" class="gir" style="--d:150ms">Öğretmene, öğrenciye, herkese ücretsiz paylaşımlar.</h1>
<a class="ben gir" style="--d:420ms" href="/hakkinda/"><img src="{AVATAR}" alt="" width="58" height="58"><span><b style="color:var(--krem);font-weight:650">İdiye Ökten</b><br><i class="soz">Öğrenme ve öğretme aşkıyla.</i></span></a>
<p class="alt gir" style="--d:560ms">Tahtada açılan araçlar, MEB öğrenme çıktılarına bağlı atölyeler, kısa tahmin videoları.</p>
<div class="ara gir" style="--d:700ms" role="search"><label for="ara">Ara: araç, atölye, atasözü, video</label><input id="ara" type="search" autocomplete="off" placeholder="yüzde, klavye, harman, makara" role="combobox" aria-expanded="false" aria-controls="ara-sonuc" aria-autocomplete="list"><ul class="sonuc" id="ara-sonuc" role="listbox" aria-label="Arama sonuçları" hidden></ul><p id="ara-durum" class="gizli" role="status"></p></div>
<a class="izledin" id="izledin" href="#" hidden><img src="{AVATAR}" alt=""><div><small class="iz-k"></small><b class="iz-b"></b><span class="iz-i"></span></div></a>
</div></div>
<a class="cuma-not" href="#hafta">{f'<img src="{hafta_u["kapak_w"]}" alt="">' if hafta_u.get("kapak_w") else '<span class="soru-b">'+E(hafta_u["kisa"])+'</span>'}<small>{ETIKET}</small><b>{E(hafta_u["ad"])}</b><span>{E(hafta_u["sinif"])}</span><span class="bul">Buldunuz. Aşağıda sizi bekliyor.</span></a>
<div class="cetvel" role="toolbar" aria-label="Tahta"><button type="button" id="t-kalem" aria-pressed="false">Kalem</button><button type="button" id="t-temizle">Temizle</button><button type="button" id="t-ses" aria-pressed="false">Ses</button><span class="ipucu" id="t-ipucu">Bu sayfa da bir tahta. Kalemi alın, yazın.</span></div>
</section>
{kapi_html}
<section class="blm gunun" id="gunun" aria-labelledby="gs-b"><div class="w ic"><div><small>Günün sorusu</small><h2 id="gs-b" class="gs-soru">3 saniye düşünün.</h2><p class="gs-alt">Her gün bir soru. Cevabı videosunda.</p></div>
<div class="gs-kutu"><div class="gs-sayac" aria-hidden="true"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="52" class="iz"/><circle cx="60" cy="60" r="52" class="dol"/></svg><span>3</span></div><div class="gs-sec" role="group" aria-label="Seçenekler"></div><p class="gs-cevap" role="status" aria-live="polite"></p></div></div></section>
{hafta_html}
<section class="blm" id="kitaplik" aria-labelledby="kit-b"><div class="w"><div class="bas"><h2 id="kit-b">Kitaplık</h2><p>Tahtada açmak için düğmeye dokunun: karekod ve kısa adres çıkar.</p></div>
<div class="katalog">{"".join(satirlar)}</div></div></section>
<section class="blm" id="videolar" aria-labelledby="vid-b" style="padding-top:0"><div class="w"><div class="bas"><h2 id="vid-b">Videolar</h2><p>YouTube kanalı: @egitimtek. Video dokununca oynar.</p></div>
<div class="diziler">{son_videolar()}</div></div></section>
{canta_html}
</main>
<script type="application/json" id="veri">{ana_veri}</script>{qr_gizli()}{ALT}'''
open(os.path.join(OUT,"index.html"),"w",encoding="utf-8").write(ana)

# ---- ürün sayfaları
for u in urunler:
    v = urun_video(u)
    sema = [sema_urun(u)] + ([sema_video(v, urun_sayfa(u))] if v else [])
    sayfa = bas(f"{u['ad']}: {u['sinif']} | Herkese Eğitim", u["kisa"]+" "+u["ne"][:120], urun_sayfa(u), sema=sema, og=u.get("kapak_w")) + ust_koyu() + f'''
<main id="ana" class="sayfa"><div class="w"><p class="yol"><a class="eve" href="/" title="Ana sayfa"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10M10 20v-6h4v6"/></svg>Ana sayfa</a> / <a href="/#kitaplik">Kitaplık</a></p>
<div class="soz-sayfa"><article class="makale"><h1>{E(u["ad"])}</h1><p style="font-size:22px;color:var(--mur)">{E(u["kisa"])}</p><p>{E(u["ne"])}</p>
<div class="kutu"><h2>Kimin için</h2><p>{E(u["sinif"])}{"<br>Öğrenme çıktısı: "+E(", ".join(u["kazanim"])) if u["kazanim"] else ""}</p></div>
<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:24px">{ac_dugme(u,"dugme kir") or ('<span class="dugme acik" aria-disabled="true">'+(tarih_tr(u["lansman"]) if u.get("lansman") else "Yakında")+'</span>')}</div>
{'<div class="kutu"><h2>Veliler için</h2><p>Ücretsiz. Hesap açılmaz, kişisel bilgi istenmez.'+(' Öğrenci tarayıcıda tahmin eder, dener, sonucu kendi görür.' if u["tur"]=="atolye" else '')+'</p></div>' if u["tur"]!="oyun" else ''}
<div class="paylas"><button class="dugme acik" type="button" data-paylas="{SITE}{urun_sayfa(u)}" data-baslik="{E(u["ad"])}">Zümreye gönderin</button><a class="dugme acik" href="https://wa.me/?text={E(urllib.parse.quote(u["ad"]+": "+SITE+urun_sayfa(u)))}" rel="noopener">WhatsApp</a></div>
{f'<div class="kutu"><h2>Bu sürümde</h2><p>{E(u["surum_notu"])}</p></div>' if u.get("surum_notu") else ""}
{f'<p style="margin-top:14px"><a class="dugme acik" href="{E(u["kilavuz"])}">Öğretmen kılavuzu</a></p>' if u.get("kilavuz") else ""}
{f'<p style="margin-top:14px"><a class="dugme acik" href="{u["indir"]}" download="{E(os.path.basename(u["canta"]))}">Tek dosya olarak indir</a></p>' if u.get("indir") else ""}
<p style="margin-top:14px;font-size:16px">{" ".join(f'<a href="/sinif/{x}/">{x}. sınıf</a>' for x in u["siniflar"] if x!="hepsi")} {" ".join(f'<a href="/brans/{b}/">{E(BRANS_AD.get(b,b))}</a>' for b in u["branslar"] if b!="hepsi")}</p>
{f'<p style="margin-top:18px;font-size:16px">Adres: <a href="{E(u["url"])}">{E(kisa_adres(u["url"]))}</a></p>' if u["durum"]=="yayinda" else ""}
</article><aside>{vid_btn(v, u["ad"]) if v else ""}{f'<div class="kutu urun-qr" style="text-align:center"><div style="background:#fff;padding:10px;border-radius:10px">{qr_svg(u["url"])}</div><p style="font-size:16px;margin-top:10px">Öğrenciler kendi cihazıyla okutabilir.</p></div>' if u["durum"]=="yayinda" else ""}</aside></div></div></main>{qr_gizli()}{ALT}'''
    os.makedirs(os.path.join(OUT,"urun",u["id"]), exist_ok=True)
    open(os.path.join(OUT,"urun",u["id"],"index.html"),"w",encoding="utf-8").write(sayfa)

# ---- atasözü sayfaları
for i,a in enumerate(atasozleri):
    v = VBY.get(a.get("video")) or ({"id":a["video"],"baslik":a["soz"],"kapak_w":a.get("kapak_w"),"dik":True,"tarih":a.get("tarih")} if a.get("video") else None)
    sz = a.get("sozcuk") or {}
    sema = [{"@context":"https://schema.org","@type":"DefinedTerm","name":a["soz"],"description":a.get("anlam"),"inDefinedTermSet":{"@type":"DefinedTermSet","name":"Atasözlerimizi Yaşatalım","url":SITE+"/atasozleri/"},"url":SITE+soz_sayfa(a)}]
    if v: sema.append(sema_video(v, soz_sayfa(a)))
    onc = atasozleri[i-1] if i>0 else None; snr = atasozleri[i+1] if i+1<len(atasozleri) else None
    gez = '<p style="margin-top:36px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap">' + (f'<a href="{soz_sayfa(onc)}">Önceki: {E(onc["soz"])}</a>' if onc else "<span></span>") + (f'<a href="{soz_sayfa(snr)}">Sonraki: {E(snr["soz"])}</a>' if snr else "") + "</p>"
    sayfa = bas(f"{a['soz']}: anlamı | Atasözlerimizi Yaşatalım", f"{a['soz']} atasözünün anlamı. "+(a.get("anlam") or "")[:110], soz_sayfa(a), sema=sema, og=a.get("kapak_w")) + ust_koyu() + f'''
<main id="ana" class="sayfa"><div class="w"><p class="yol"><a class="eve" href="/" title="Ana sayfa"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10M10 20v-6h4v6"/></svg>Ana sayfa</a> / <a href="/atasozleri/">Atasözleri</a> / No. {E(a.get("no"))}</p>
<div class="soz-sayfa"><article class="makale"><h1 class="soz">{E(a["soz"])}</h1>
<div class="kutu"><h2>Anlamı</h2><p>{E(a.get("anlam"))}</p></div>
{f'<div class="kutu"><h2>{E((sz.get("kelime") or "")[:1].replace("i","İ").upper()+(sz.get("kelime") or "")[1:])} ne demek?</h2><p>{E(sz.get("anlam"))}</p></div>' if sz.get("kelime") and sz.get("anlam") else ""}
{f'<p style="margin-top:22px">Videodaki soru: {E(a.get("soru"))}</p>' if a.get("soru") else ""}{gez}</article>
<aside>{vid_btn(v, a["soz"]) if v else ""}</aside></div></div></main>{ALT}'''
    os.makedirs(os.path.join(OUT,"atasozleri",a["slug"]), exist_ok=True)
    open(os.path.join(OUT,"atasozleri",a["slug"],"index.html"),"w",encoding="utf-8").write(sayfa)
def _soz_html(a):
    k = (a.get("sozcuk") or {}).get("kelime")
    out = []
    for w in a["soz"].split():
        cls = "k u" if k and k in w.lower() else "k"
        out.append(f'<span class="{cls}">{E(w)}</span>')
    return " ".join(out)
def _soz_li(a):
    sk = a.get("sozcuk") or {}
    not_ = f'<p class="sz-not"><b>{E(sk.get("kelime"))}:</b> {E(sk.get("anlam"))}</p>' if sk.get("kelime") else ""
    return (f'<li class="sz"><span class="sz-no" aria-hidden="true">{E(a.get("no"))}</span><div class="sz-g">'
            f'<p class="sz-s"><a href="{soz_sayfa(a)}">{_soz_html(a)}</a></p><p class="sz-a">{E(a.get("anlam") or "")}</p>{not_}</div></li>')
_ALF = "abcçdefgğhıijklmnoöprsştuüvyz"
def _tr_key(t):
    t = t.replace("I","ı").replace("İ","i").lower()
    return [(_ALF.index(c) if c in _ALF else 99) for c in t if c.isalpha()]
def _bas_harf(t):
    c = t.strip()[0]
    return {"i":"İ","ı":"I"}.get(c, c.upper()) if c not in "Iİ" else c
_one = atasozleri[-1] if atasozleri else None
_gr = {}
for a in sorted(atasozleri, key=lambda a: _tr_key(a["soz"])):
    _gr.setdefault(_bas_harf(a["soz"]), []).append(a)
def _ind_li(a):
    sk = (a.get("sozcuk") or {}).get("kelime") or ""
    ara = " ".join([a["soz"], a.get("anlam") or "", sk])
    sozh = " ".join((f'<mark>{E(w)}</mark>' if sk and sk in w.lower() else E(w)) for w in a["soz"].split())
    return f'<li data-ara="{E(ara)}"><a href="{soz_sayfa(a)}"><b>{sozh}</b><span>{E(a.get("anlam") or "")}</span></a><small>No. {E(a.get("no"))}</small></li>'
_harfler = "".join((f'<a href="#h-{E(h)}">{E(h)}</a>' if h in _gr else f'<span aria-hidden="true">{E(h)}</span>') for h in "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")
_indeks = "".join(f'<section class="sz-grup" id="h-{E(h)}"><h2>{E(h)}</h2><ul>{"".join(_ind_li(a) for a in l)}</ul></section>' for h,l in _gr.items())
_sozcukler = "".join(f'<a href="{soz_sayfa(a)}" title="{E(a["sozcuk"].get("anlam") or "")}">{E(a["sozcuk"]["kelime"])}</a>' for a in atasozleri if (a.get("sozcuk") or {}).get("kelime"))
soz_liste = (f'<p class="sz-etiket">En yeni söz</p><ol class="sz-liste">{_soz_li(_one)}</ol><p class="sz-soyle-k"><button type="button" class="dugme kir sz-soyle" data-soz="{E(_one["soz"])}">Tahtada büyüt, sınıfça söyleyin</button></p>' if _one else "") + f'''
<section class="sz-defter" aria-labelledby="sz-d-b"><div class="sz-defter-bas"><div><h2 id="sz-d-b">Bütün atasözleri</h2><p class="sz-adet">{len(atasozleri)} söz</p></div>
<div class="sz-ara"><label for="sz-q" class="gizli">Atasözlerinde ara</label><input id="sz-q" type="search" placeholder="Söz, anlam ya da kelime: harman, gönül, ağaç" autocomplete="off"><p class="sz-say" role="status" aria-live="polite"></p></div></div>
<nav class="sz-harf" aria-label="Harfe git">{_harfler}</nav>
{f'<div class="sz-bant"><p>Unutulmak üzere olan sözcükler. Dokunun, yeniden yazılsın.</p><div class="sz-bant-k">{_sozcukler}</div></div>' if _sozcukler else ""}
<div class="sz-indeks">{_indeks}</div><p class="sz-yok" hidden>Bu aramayla atasözü çıkmadı. Başka bir kelime deneyin.</p></section>'''

open(os.path.join(OUT,"atasozleri","index.html"),"w",encoding="utf-8").write(
  bas("Atasözlerimizi Yaşatalım | Herkese Eğitim","Az bilinen atasözleri, anlamları ve unutulan sözcükleri. Her atasözünün kendi sayfası ve kısa videosu var.","/atasozleri/",
      sema=[{"@context":"https://schema.org","@type":"DefinedTermSet","name":"Atasözlerimizi Yaşatalım","url":SITE+"/atasozleri/","hasDefinedTerm":[{"@type":"DefinedTerm","name":a["soz"],"url":SITE+soz_sayfa(a)} for a in atasozleri]}])
  + ust_koyu() + f'<main id="ana" class="sayfa"><div class="w"><p class="yol"><a class="eve" href="/" title="Ana sayfa"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10M10 20v-6h4v6"/></svg>Ana sayfa</a> / Atasözleri</p><section class="sz-bas"><p class="sz-ad">Atasözlerimizi Yaşatalım</p><h1>Unutulan sözler,<br>söylendikçe yaşar.</h1><p>Az bilinen atasözleri ve içlerinde unutulan sözcükler. Okudukça soluk sözler yeniden mürekkep tutar. Birini seçin, anlamını ve kısa videosunu açın, sonra sınıfta bir kez söyleyin.</p></section>{soz_liste}</div></main>{ALT}')

# ---- hakkında
hk = open(os.path.join(KOK,"src","hakkinda.html"),encoding="utf-8").read()
open(os.path.join(OUT,"hakkinda","index.html"),"w",encoding="utf-8").write(
  bas("Hakkında: İdiye Ökten | Herkese Eğitim","İdiye Ökten, eğitim teknolojileri. Herkese Eğitim'de öğretmene, öğrenciye, herkese ücretsiz paylaşımlar hazırlıyor.","/hakkinda/",
      sema=[{"@context":"https://schema.org","@type":"ProfilePage","mainEntity":KISI,"url":SITE+"/hakkinda/"}]) + ust_koyu()
  + f'<main id="ana" class="sayfa"><div class="w"><p class="yol"><a class="eve" href="/" title="Ana sayfa"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10M10 20v-6h4v6"/></svg>Ana sayfa</a> / Hakkında</p><article class="hk">{hk.replace("{AVATAR}",AVATAR)}</article></div></main>{ALT}')

# ---- 404, robots, sitemap, llms.txt
open(os.path.join(OUT,"404.html"),"w",encoding="utf-8").write(bas("Teneffüs | Herkese Eğitim","Bu sayfa teneffüse çıktı.","/404.html")+ust_koyu()+'''<main id="ana" class="teneffus"><div class="w">
<div class="tahta-404"><p class="tebesir">Bu sayfa teneffüse çıktı.</p><p class="tebesir kucuk">Zil çalınca döner. Bir atölye yeni açılıyorsa birkaç dakika sonra yeniden deneyin.</p>
<svg class="zil" viewBox="0 0 120 120" aria-hidden="true"><path d="M60 18c-18 0-30 14-30 32v22l-10 14h80L90 72V50c0-18-12-32-30-32z" fill="none" stroke="#FFF4DE" stroke-width="5" stroke-linejoin="round"/><circle cx="60" cy="96" r="8" fill="#FFC21A"/><path d="M60 8v10" stroke="#FFF4DE" stroke-width="5" stroke-linecap="round"/></svg>
<p class="silgi" aria-hidden="true"></p></div>
<p class="git">Bu arada: <a class="eve" href="/" title="Ana sayfa"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10M10 20v-6h4v6"/></svg>Ana sayfa</a> · <a href="/atolyeler/">Atölyeler</a> · <a href="/videolar/">Videolar</a> · <a href="/canta/">Çanta</a></p>
</div></main>'''+ALT)
open(os.path.join(OUT,"robots.txt"),"w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n# Düz metin özet: {SITE}/llms.txt\n")
yollar = ["/","/hakkinda/","/atasozleri/"]+[urun_sayfa(u) for u in urunler]+[soz_sayfa(a) for a in atasozleri]+EK_YOLLAR
open(os.path.join(OUT,"sitemap.xml"),"w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{SITE}{y}</loc><lastmod>{BUGUN.isoformat()}</lastmod></url>" for y in yollar)+"</urlset>\n")
L = [f"# Herkese Eğitim\n\n> İdiye Ökten'in öğretmene, öğrenciye, herkese ücretsiz paylaşımları: tahtada açılan araçlar, MEB öğrenme çıktılarına bağlı atölyeler, tahmin soruları, atasözleri ve özel gün videoları. Site: {SITE}/\n\nİdiye Ökten eğitim teknolojileri alanında çalışır. İletişim: herkeseegitimtek@gmail.com. YouTube: @egitimtek.\n\n## Araçlar, atölyeler, oyunlar\n"]
for u in urunler:
    L.append(f"- [{u['ad']}]({SITE}{urun_sayfa(u)}): {u['kisa']} Kimin için: {u['sinif']}." + (f" Öğrenme çıktısı: {', '.join(u['kazanim'])}." if u['kazanim'] else "") + (f" Adres: {u['url']}" if u['durum']=='yayinda' else (f" Yayın: {u['lansman']}." if u.get('lansman') else " Yakında.")))
L.append("\n## Atasözlerimizi Yaşatalım\n")
for a in atasozleri: L.append(f"- [{a['soz']}]({SITE}{soz_sayfa(a)}): {a.get('anlam') or ''}")
L.append("\n## Videolar\n")
for v in videolar: L.append(f"- {v.get('baslik')} ({DIZI.get(v.get('dizi'),('Video',))[0]}): https://www.youtube.com/watch?v={v['id']}")
L.append("\n## Takvim\n")
for t in takvim: L.append(f"- {t['tarih']}: {t['baslik']}" + (f" ({t['not']})" if t.get('not') else ""))
open(os.path.join(OUT,"llms.txt"),"w",encoding="utf-8").write("\n".join(L)+"\n")
def _yol_cevir(m):
    parca = m.group(1).split(" / ")
    ic = []
    for i,x in enumerate(parca):
        if i: ic.append('<i class="ayak" aria-hidden="true"></i>')
        ic.append(x if (x.startswith("<a") or i < len(parca)-1) else f'<span class="tabela" aria-current="page">{x}</span>')
    return '<nav class="yol" aria-label="Bulunduğunuz yer">' + "".join(ic) + '</nav>'
def _dis_sekme(m):
    ic = m.group(1)
    if "target=" in ic: return m.group(0)
    h = re.search(r'href="([^"]*)"', ic)
    if (h and re.match(r'https?://', h.group(1)) and not re.match(r'https?://(www\.)?herkeseegitim\.com(/|$)', h.group(1))) or 'class="dugme kir ac"' in ic:
        return '<a ' + ic + ' target="_blank" rel="noopener">'
    return m.group(0)
for _k,_d,_ds in os.walk(OUT):
    for _f in _ds:
        if _f.endswith(".html"):
            _p = os.path.join(_k,_f); _h = open(_p,encoding="utf-8").read()
            _y = re.sub(r'<p class="yol">(.*?)</p>', _yol_cevir, _h)
            _y = re.sub(r'<a ([^>]*?)>', _dis_sekme, _y)
            if _y != _h: open(_p,"w",encoding="utf-8").write(_y)
open(os.path.join(OUT,".nojekyll"),"w").write("")
if os.environ.get("CNAME"): open(os.path.join(OUT,"CNAME"),"w").write(os.environ["CNAME"]+"\n")
print("tamam:", len(urunler),"ürün,",len(videolar),"video,",len(atasozleri),"atasözü, çanta:",len(canta_dosyalar))
