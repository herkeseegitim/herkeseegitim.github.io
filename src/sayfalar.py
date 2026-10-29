# build.py içinden exec ile çalışır: liste, sınıf, branş, video sayfaları, çanta, RSS, gizlilik
BRANS_AD = {"fen":"Fen bilimleri","matematik":"Matematik","bilisim":"Bilişim teknolojileri ve yazılım","sinif":"Sınıf öğretmenliği","turkce":"Türkçe","hepsi":"Her branş"}
EK_YOLLAR = []
def yaz(yol, icerik):
    p = os.path.join(OUT, yol.strip("/"), "index.html") if yol.endswith("/") else os.path.join(OUT, yol.strip("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p,"w",encoding="utf-8").write(icerik)
    if yol.endswith("/"): EK_YOLLAR.append(yol)
def sayfa(baslik, aciklama, yol, govde, sema=None, yolcuk="", og=None):
    return bas(baslik, aciklama, yol, sema=sema, og=og) + ust_koyu() + f'<main id="ana" class="sayfa"><div class="w"><p class="yol"><a class="eve" href="/" title="Ana sayfa"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 5h18v11H3z"/><path d="M7 20h10M12 16v4"/></svg>Sınıfa dön</a>{yolcuk}</p>{govde}</div></main>{qr_gizli()}{ALT}'
def kart(u):
    durum = "" if u["durum"]=="yayinda" else f'<span class="etk">{tarih_tr(u["lansman"]) if u.get("lansman") else "Yakında"}</span>'
    img = f'<img src="{u["kapak_w"]}" alt="" loading="lazy">' if u.get("kapak_w") else f'<span class="kart-soru">{E(u["kisa"])}</span>'
    return f'<li class="kart" data-sinif="{" ".join(u["siniflar"])}" data-brans="{" ".join(u["branslar"])}"><a href="{urun_sayfa(u)}">{img}<b>{E(u["ad"])}</b><span>{E(u["sinif"])}</span>{durum}</a></li>'
def vkart(v):
    return f'<figure>{vid_btn(v)}<figcaption><a href="{video_sayfa(v)}">{E(v.get("kisa_ad"))}</a></figcaption></figure>'
def uv(u): return [v for v in videolar if v.get("urun")==u["id"]]

def son_ad(l):
    y=[u for u in l if u['durum']=='yayinda']
    y=sorted(y,key=lambda u:u.get('lansman') or '')
    return y[-1]['ad'] if y else '-'
# liste sayfaları
for yol, turler, baslik, ac in [("/atolyeler/",("atolye","oyun"),"Atölyeler","MEB öğrenme çıktılarına bağlı atölyeler ve oyunlar. Sınıfa ya da branşa göre süzün."),
                                ("/araclar/",("arac",),"Araçlar","Tahtada ve tarayıcıda açılan araçlar.")]:
    l = [u for u in urunler if u["tur"] in turler]
    sinif_ = sorted({x for u in l for x in u["siniflar"] if x!="hepsi"}, key=int)
    brans_ = sorted({x for u in l for x in u["branslar"] if x!="hepsi"})
    suzgec = ""
    if len(l) > 3:
        suzgec = '<div class="suzgec" role="group" aria-label="Süz"><button type="button" data-s="" aria-pressed="true">Hepsi</button>' + "".join(f'<button type="button" data-s="sinif:{x}" aria-pressed="false">{x}. sınıf</button>' for x in sinif_) + "".join(f'<button type="button" data-s="brans:{x}" aria-pressed="false">{E(BRANS_AD.get(x,x))}</button>' for x in brans_) + '</div>'
    sema = [{"@context":"https://schema.org","@type":"CollectionPage","name":baslik,"url":SITE+yol,"hasPart":[{"@type":"CreativeWork","name":u["ad"],"url":SITE+urun_sayfa(u)} for u in l]}]
    yaz(yol, sayfa(f"{baslik} | Herkese Eğitim", ac, yol, lbas(baslik, ac, [("Defter", baslik), ("İçinde", f"{len(l)} {baslik.lower()[:-3] if False else ('atölye ve oyun' if 'atolye' in turler else 'araç')}"), ("Son eklenen", E(son_ad(l)))]) + f'{suzgec}<ul class="kartlar">{"".join(kart(u) for u in l)}</ul>', sema, f" / {baslik}"))

# sınıf ve branş sayfaları
sinif_hepsi = sorted({x for u in urunler for x in u["siniflar"] if x!="hepsi"}, key=int)
for x in sinif_hepsi:
    l = [u for u in urunler if x in u["siniflar"]]; ortak = [u for u in urunler if "hepsi" in u["siniflar"]]
    vl = [v for u in l for v in uv(u)]
    g = lbas(f"{x}. sınıf", f"{x}. sınıf için atölyeler, araçlar ve kısa videolar.", [("Defter", f"{x}. sınıf"), ("İçinde", f"{len(l)} atölye ve araç" + (f", {len(vl)} video" if vl else ""))]) + f'<ul class="kartlar">{"".join(kart(u) for u in l)}</ul>'
    if vl: g += f'<h2 class="ara-b">Kısa videolar</h2><div class="raf">{"".join(vkart(v) for v in vl[:16])}</div>'
    if ortak: g += f'<h2 class="ara-b">Her sınıfta kullanılanlar</h2><ul class="kartlar">{"".join(kart(u) for u in ortak)}</ul>'
    yaz(f"/sinif/{x}/", sayfa(f"{x}. sınıf etkinlik, atölye ve araçları | Herkese Eğitim", f"{x}. sınıf için ücretsiz atölyeler, tahta araçları ve kısa videolar.", f"/sinif/{x}/", g, None, f" / {x}. sınıf"))
for b in sorted({x for u in urunler for x in u["branslar"] if x!="hepsi"}):
    l = [u for u in urunler if b in u["branslar"]]; vl = [v for u in l for v in uv(u)]
    ad = BRANS_AD.get(b,b)
    g = lbas(E(ad), f"{E(ad)} için atölyeler, araçlar ve kısa videolar.", [("Defter", ad), ("İçinde", f"{len(l)} atölye ve araç" + (f", {len(vl)} video" if vl else ""))]) + f'<ul class="kartlar">{"".join(kart(u) for u in l)}</ul>'
    if vl: g += f'<h2 class="ara-b">Kısa videolar</h2><div class="raf">{"".join(vkart(v) for v in vl[:16])}</div>'
    yaz(f"/brans/{b}/", sayfa(f"{ad} | Herkese Eğitim", f"{ad} için ücretsiz atölyeler, tahta araçları ve kısa videolar.", f"/brans/{b}/", g, None, f" / {E(ad)}"))

# videolar
VRENK = {"tahmin":"tur","atasozu":"kir","ozel-gun":"cet","bilgisayarin-icinde":"mur","tanitim":"sol"}
VSIRA = ["tahmin","atasozu","ozel-gun","bilgisayarin-icinde","tanitim"]
def _vbrans(v):
    u = UR.get(v.get("urun") or "")
    return " ".join(x for x in (u["branslar"] if u else []) if x!="hepsi")
def _vt(v): return v.get("tarih") or ""
vs = sorted(videolar, key=lambda v: _vt(v), reverse=True)
def vgkart(v):
    dz = v.get("dizi") or "tanitim"; u = UR.get(v.get("urun") or "")
    ust = f'<span class="vg-dz">{E(DIZI.get(dz,("Video",))[0])}</span>'
    alt = " · ".join(x for x in [tarih_tr(v["tarih"]) if v.get("tarih") else "", E(u["ad"]) if u else ""] if x)
    img = f'<img src="{v["kapak_w"]}" alt="" loading="lazy" width="{420 if v.get("dik") else 960}" height="{746 if v.get("dik") else 540}">' if v.get("kapak_w") else f'<span class="vg-bos" aria-hidden="true"><em>{E(v.get("kisa_ad") or "")}</em></span>'
    ara_m = " ".join([v.get("kisa_ad") or "", DIZI.get(dz,("",))[0], u["ad"] if u else ""])
    return (f'<li class="vg-k{" yat" if not v.get("dik") else ""}" data-dizi="{dz}" data-brans="{_vbrans(v)}" data-tarih="{E(_vt(v))}" data-ara="{E(ara_m)}" style="--r:var(--{VRENK.get(dz,"sol")})">'
            f'<a href="{video_sayfa(v)}"><span class="vg-g">{img}{ust}</span><b>{E(v.get("kisa_ad"))}</b><span class="vg-a">{alt}</span></a></li>')
AY_ = {}
for v in vs:
    k = v["tarih"][:7] if v.get("tarih") else "eski"
    AY_.setdefault(k, []).append(v)
def ay_ad(k):
    if k=="eski": return "Daha önce"
    y,m = k.split("-"); return f"{AYLAR[int(m)-1].capitalize()} {y}"
izgara = "".join(f'<li class="vg-ay" data-ay="{k}"><h2>{ay_ad(k)}</h2></li>' + "".join(vgkart(v) for v in l) for k,l in AY_.items())
dsay = {d: sum(1 for v in videolar if v.get("dizi")==d) for d in VSIRA}
bsay = {}
for v in videolar:
    for b in _vbrans(v).split():
        bsay[b] = bsay.get(b,0)+1
cip = '<button type="button" data-k="dizi" data-d="" aria-pressed="true">Hepsi <i>{}</i></button>'.format(len(videolar)) + "".join(
    f'<button type="button" data-k="dizi" data-d="{d}" aria-pressed="false" style="--r:var(--{VRENK[d]})"><s aria-hidden="true"></s>{E(DIZI[d][0])} <i>{n}</i></button>' for d,n in dsay.items() if n)
bcip = "".join(f'<button type="button" data-k="brans" data-d="{b}" aria-pressed="false">{E(BRANS_AD.get(b,b))} <i>{n}</i></button>' for b,n in sorted(bsay.items(), key=lambda x:-x[1])) if len(bsay)>1 else ""
oyun = [dict(id=v["id"], s=v.get("kisa_ad"), d=DIZI.get(v.get("dizi"),("",))[0], k=v.get("kapak_w") or "", u=video_sayfa(v), dik=bool(v.get("dik"))) for v in videolar if v.get("dizi")!="tanitim" and (v.get("kisa_ad") or "").strip().endswith("?")]
oyun_json = json.dumps(oyun, ensure_ascii=False).replace("</","<\\/")
gv = f'''<section class="vg-bas"><div><h1>Videolar</h1><p>Kısa sorular, atasözleri, özel günler ve tanıtımlar. {len(videolar)} video, hepsi <a href="https://www.youtube.com/@egitimtek">YouTube kanalında</a> da var.</p></div>
<div class="vg-oyna"><p><b>Üç saniyen var.</b> Rastgele bir soru gelsin, düşün, cevabı izle.</p><button type="button" class="dugme kir vg-ac" hidden>Bir soru çek</button></div></section>
<div class="vg-ust"><div class="vg-ara"><label for="vg-q" class="gizli">Videolarda ara</label><input id="vg-q" type="search" placeholder="Videolarda ara: makara, harman, fermuar…" autocomplete="off"></div>
<div class="vg-cip" role="group" aria-label="Diziye göre">{cip}</div>{f'<div class="vg-cip vg-b" role="group" aria-label="Branşa göre">{bcip}</div>' if bcip else ""}</div>
<p class="vg-say" role="status" aria-live="polite"></p>
<ul class="vg">{izgara}</ul>
<p class="vg-yok" hidden>Bu aramayla video çıkmadı. Başka bir sözcük deneyin ya da <button type="button" class="vg-sifir">süzgeci temizleyin</button>.</p>
<p class="vg-daha-k"><button type="button" class="dugme acik vg-daha" hidden>Daha fazla göster</button></p>
<dialog class="vg-sah" aria-label="Üç saniye"><div class="vg-sah-i"><p class="vg-sah-d"></p><p class="vg-sah-s"></p>
<div class="vg-saat" aria-hidden="true"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="52"/><circle class="vg-kalan" cx="60" cy="60" r="52"/></svg><span>3</span></div>
<div class="vg-cev" hidden></div>
<p class="vg-sah-b"><button type="button" class="dugme kir vg-izle" hidden>Cevabı izle</button> <button type="button" class="dugme acik vg-baska">Başka soru</button> <a class="vg-git" href="#">Sayfasına git</a></p>
<button type="button" class="vg-kapat" aria-label="Kapat">×</button></div></dialog>
<script type="application/json" id="vg-veri">{oyun_json}</script>'''
yaz("/videolar/", sayfa("Videolar | Herkese Eğitim", "3 saniyede tahmin et, Atasözlerimizi Yaşatalım, Özel Günler ve tanıtım videoları. Sınıfta derse giriş için kısa sorular.", "/videolar/", gv, None, " / Videolar"))
for v in videolar:
    if any(a.get("video")==v["id"] for a in atasozleri): continue
    u = UR.get(v.get("urun") or "")
    ayni = [x for x in videolar if x.get("dizi")==v.get("dizi") and x["id"]!=v["id"]][:8]
    dz = DIZI.get(v.get("dizi"),("Video",""))
    g = f'''<div class="soz-sayfa"><article class="makale"><p style="font-weight:700;color:#9A1B15">{E(dz[0])}</p><h1>{E(v.get("kisa_ad"))}</h1>
{f'<p>{E(v["metin"])}</p>' if v.get("metin") else f'<p>{E(dz[1])}</p>'}
{f'<div class="kutu"><h2>İlgili {"atölye" if u["tur"]=="atolye" else "araç"}</h2><p><a href="{urun_sayfa(u)}">{E(u["ad"])}</a>: {E(u["kisa"])}</p></div>' if u else ""}
<p class="vd-platform"><a href="https://www.youtube.com/watch?v={E(v["id"])}">YouTube'da aç</a>{"".join(f'<a href="{E(u_)}">{ad_}</a>' for k_,ad_ in (("ig","Instagram'da aç"),("tt","TikTok'ta aç"),("x","X'te aç")) for u_ in [(v.get("platformlar") or {}).get(k_)] if u_)}</p></article><aside>{vid_btn(v)}</aside></div>
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
def _cboy(u):
    p_ = u["canta"] if os.path.isabs(u["canta"]) else os.path.join(KOK,"data",u["canta"]); return os.path.getsize(p_)
_ctop = sum(_cboy(u) for u in indirilen)/1048576
_ctop_s = f"{_ctop:.1f}".replace(".",",")
_cad = "".join(f"<li>{E(u['ad'])}</li>" for u in indirilen)
cg = '''<div class="canta-duzen"><div><div class="makale" style="margin-bottom:24px"><h1>Çanta</h1><p>Seçtikleriniz tek bir zip dosyasında iner. Her dosya çift tıklayınca tarayıcıda açılır, internet istemez. Tahtaya USB bellekle de taşınır.</p></div>
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
</div>
<aside class="cnt-hepsi" aria-labelledby="cnt-h"><div class="cnt-kulp" aria-hidden="true"></div><div class="cnt-govde"><div class="cnt-toka" aria-hidden="true"></div>
<h2 id="cnt-h">Hepsi tek seferde</h2><p>Seçmekle uğraşmayın: bütün atölye ve araçlar tek zip dosyasında.</p>
<ul class="cnt-icinde">''' + _cad + f'''</ul>
<a class="dugme cnt-dugme" href="/canta/Herkese%20Egitim%20cantasi.zip" download>Çantayı indir</a><p class="cnt-boy">{len(indirilen)} dosya, yaklaşık {_ctop_s} MB. İnternetsiz açılır.</p></div></aside></div>
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
yaz("/gizlilik/", sayfa("Gizlilik | Herkese Eğitim","Bu sitede sayaç, takip ve çerez yok.","/gizlilik/",'''<div class="yan-yana"><article class="makale"><h1>Gizlilik</h1>
<p>Bu sitede sayaç, takip kodu ve çerez yok. Sitede hesap açılmaz, form doldurulmaz.</p>
<p>Tarayıcınızda iki küçük not kalır: "Üç soru" seçimleriniz ve son ziyaret tarihiniz ("Yeni" etiketleri için). İkisi de bize gelmez. Yandaki düğmeyle hemen silebilirsiniz.</p>
<p>Videolar YouTube'dan gelir ve siz oynat düğmesine dokunana kadar yüklenmez. Dokununca YouTube'un çerezsiz oynatıcısı (youtube-nocookie.com) açılır; o andan sonra YouTube'un kendi kuralları geçerlidir.</p>
<p>Site GitHub Pages'ta durur, alan adı Cloudflare'dedir. Bu hizmetler, her web sitesinde olduğu gibi, sayfanın size ulaşması için teknik kayıt tutar. Biz kimin baktığını görmeyiz.</p>
<p>Araçlar ve atölyeler tarayıcınızda çalışır; içlerine yazdığınız bir şey bize gönderilmez.</p>
<p>Soru ve öneri: <a href="mailto:herkeseegitimtek@gmail.com">herkeseegitimtek@gmail.com</a></p></article>
<aside class="yan-pano"><div class="tahta-liste"><p class="tl-b">Bu sitede yok</p><ul class="cizik"><li>Sayaç</li><li>Takip kodu</li><li>Çerez</li><li>Reklam</li><li>Hesap açma</li><li>Form</li></ul></div>
<div class="not-kagit"><p class="tl-b">Bu tarayıcıda kalan</p><ul class="kalan"><li data-k="he-kapi"><b>Üç soru seçimi</b><span></span></li><li data-k="he-son"><b>Son ziyaret tarihi</b><span></span></li></ul><button type="button" class="dugme kir sil-not">Bu tarayıcıdan sil</button><p class="sil-durum" role="status"></p></div></aside></div>''', None, " / Gizlilik"))

konu_konu = urllib.parse.quote("Atölye önerisi")
konu_govde = urllib.parse.quote("Sınıf:\nBranş:\nKonu ya da öğrenme çıktısı:\nÖğrencilerin en çok takıldığı yer:\n")
yaz("/konu/", sayfa("Konu önerin | Herkese Eğitim","Sınıfınızın konusunu yazın, atölyesini birlikte düşünelim.","/konu/",f'''<div class="yan-yana"><article class="makale"><h1>Konu önerin</h1>
<p>Sınıfınızın konusunu yazın, atölyesini birlikte düşünelim. Öğrencilerin en çok nerede takıldığını yazarsanız atölye oradan başlar.</p>
<p>Öğrenci adı yazmayın.</p>
<div class="paylas" style="margin-top:22px"><a class="dugme kir" href="https://mail.google.com/mail/?view=cm&amp;to=herkeseegitimtek@gmail.com&amp;su={konu_konu}&amp;body={konu_govde}" rel="noopener">Gmail ile yaz</a><a class="dugme acik" href="https://outlook.live.com/mail/0/deeplink/compose?to=herkeseegitimtek@gmail.com&amp;subject={konu_konu}&amp;body={konu_govde}" rel="noopener">Outlook ile yaz</a><a class="dugme acik" href="mailto:herkeseegitimtek@gmail.com?subject={konu_konu}&amp;body={konu_govde}">E-posta programı</a></div>
<p style="margin-top:18px;font-size:16px">Adres: herkeseegitimtek@gmail.com</p></article>
<aside class="yan-pano"><div class="not-kagit ornek"><p class="tl-b">Örnek bir öneri</p><dl><dt>Sınıf</dt><dd>7</dd><dt>Branş</dt><dd>Matematik</dd><dt>Konu</dt><dd>Yüzdeler</dd><dt>En çok takıldıkları yer</dt><dd>İndirimden sonra yeniden zam yapınca fiyatın eskisine döneceğini sanıyorlar.</dd></dl></div></aside></div>''', None, " / Konu önerin"))
