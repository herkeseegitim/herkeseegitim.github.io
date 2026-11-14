# build.py içinden exec ile çalışır: liste, sınıf, branş, video sayfaları, çanta, RSS, gizlilik
BRANS_AD = {"fen":"Fen bilimleri","matematik":"Matematik","bilisim":"Bilişim teknolojileri ve yazılım","sinif":"Sınıf öğretmenliği","turkce":"Türkçe","hepsi":"Her branş"}
EK_YOLLAR = []
def yaz(yol, icerik):
    p = os.path.join(OUT, yol.strip("/"), "index.html") if yol.endswith("/") else os.path.join(OUT, yol.strip("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p,"w",encoding="utf-8").write(icerik)
    if yol.endswith("/"): EK_YOLLAR.append(yol)
def sayfa(baslik, aciklama, yol, govde, sema=None, yolcuk="", og=None, og_baslik=None, og_aciklama=None):
    return bas(baslik, aciklama, yol, sema=sema, og=og, og_baslik=og_baslik, og_aciklama=og_aciklama) + ust_koyu() + f'<main id="ana" class="sayfa"><div class="w"><p class="yol"><a class="eve" href="/" title="Ana sayfa"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10M10 20v-6h4v6"/></svg>Ana sayfa</a>{yolcuk}</p>{govde}</div></main>{qr_gizli()}{ALT}'
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
            f'<a href="{video_sayfa(v)}"><span class="vg-g">{img}</span>{ust}<b>{E(v.get("kisa_ad"))}</b><span class="vg-a">{alt}</span></a></li>')
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
SIK = "abcçdefgğh"
def _sik(k, ops, sec_l):
    li = ""
    for i,(d,ad,l,n,r) in enumerate(ops):
        st = ' style="--r:var(--%s)"' % r if r else ""
        nk = '<s aria-hidden="true"></s>' if r else ""
        bas_ = "true" if not d else "false"
        li += f'<li><button type="button" data-k="{k}" data-d="{d}" data-l="{E(l)}" aria-pressed="{bas_}"{st}><u>{SIK[i]})</u>{nk}<span>{E(ad)}</span><i>{n}</i></button></li>'
    et = "Dizi seçin" if k=="dizi" else "Branş seçin"
    return (f'<span class="vg-bl" data-k="{k}"><button type="button" class="vg-sl" aria-expanded="false" aria-controls="vg-s-{k}"><span>{E(sec_l)}</span></button>'
            f'<span class="vg-sk" id="vg-s-{k}" hidden><ul class="vg-cip" aria-label="{et}">{li}</ul></span></span>')
d_ops = [("","Hepsi","her diziden",len(videolar),"")] + [(d,DIZI[d][0],f"«{DIZI[d][0]}» dizisinden",n,VRENK[d]) for d,n in dsay.items() if n]
b_ops = [("","Hepsi","her branş",len(videolar),"")] + [(b,BRANS_AD.get(b,b),BRANS_AD.get(b,b).lower(),n,"") for b,n in sorted(bsay.items(), key=lambda x:-x[1])]
_bsl = _sik("brans", b_ops, "her branş") if len(bsay)>1 else "her branş"
cumle = (f'<div class="vg-cumle"><p class="vg-yon"><b>Boşluğu doldurun.</b> Şıkkı seçin, liste değişsin.</p>'
         f'<div class="vg-c">{_sik("dizi", d_ops, "her diziden")}, {_bsl} için '
         f'<b class="vg-say" role="status" aria-live="polite">{len(videolar)} video</b>.'
         f'<button type="button" class="vg-sil" hidden>Baştan</button></div></div>')
oyun = [dict(id=v["id"], s=v.get("kisa_ad"), d=DIZI.get(v.get("dizi"),("",))[0], k=v.get("kapak_w") or "", u=video_sayfa(v), dik=bool(v.get("dik"))) for v in videolar if v.get("dizi")!="tanitim" and (v.get("kisa_ad") or "").strip().endswith("?")]
oyun_json = json.dumps(oyun, ensure_ascii=False).replace("</","<\\/")
gv = f'''<section class="vg-bas"><div><h1>Videolar</h1><p>Kısa sorular, atasözleri, özel günler ve tanıtımlar. {len(videolar)} video, hepsi <a href="https://www.youtube.com/@egitimtek">YouTube kanalında</a> da var.</p></div>
<div class="vg-oyna"><svg class="vg-torba" viewBox="0 0 170 180" aria-hidden="true"><g class="tk tk2"><rect x="88" y="16" width="42" height="54" rx="6"/><text x="109" y="52">?</text></g><g class="tk tk1"><rect x="52" y="8" width="46" height="60" rx="6"/><text x="75" y="48">?</text></g><path class="tb" d="M52 70C28 92 18 124 26 150C34 174 136 174 144 150C152 124 142 92 118 70Z"/><path class="tb-k" d="M40 120c18 6 32 8 45 8s28-2 45-8"/><rect class="tb-a" x="46" y="62" width="78" height="14" rx="7"/><path class="tb-i" d="M86 76c-6 10-14 14-22 12M86 76c6 10 14 14 22 12"/><circle class="tb-e" cx="85" cy="139" r="21"/><text class="tb-y" x="85" y="139">3</text><text class="tb-s" x="85" y="152">sn</text></svg>
<div class="vg-oy-m"><p class="vg-oy-b">Torbada <b>{len(oyun)}</b> soru var.</p><p>Birini çekin. Üç saniye düşünün, sonra cevabı izleyin.</p><p class="vg-oy-a"><button type="button" class="dugme kir vg-ac" hidden>Torbadan çek</button></p></div></div></section>
<div class="vg-ust">{cumle}<div class="vg-ara"><label for="vg-q" class="gizli">Videolarda ara</label><input id="vg-q" type="search" placeholder="Ara: makara, harman…" autocomplete="off"></div></div>
<ul class="vg">{izgara}</ul>
<p class="vg-yok" hidden>Bu aramayla video çıkmadı. Başka bir sözcük deneyin ya da <button type="button" class="vg-sifir">süzgeci temizleyin</button>.</p>
<p class="vg-daha-k"><button type="button" class="dugme acik vg-daha" hidden>Daha fazla göster</button></p>
<dialog class="vg-sah" aria-label="Üç saniye"><div class="vg-sah-i"><p class="vg-sah-d"></p><p class="vg-sah-s"></p><p class="vg-sah-n" aria-live="polite"></p>
<div class="vg-saat" aria-hidden="true"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="52"/><circle class="vg-kalan" cx="60" cy="60" r="52"/></svg><span>3</span></div>
<div class="vg-cev" hidden></div>
<p class="vg-sah-b"><button type="button" class="dugme kir vg-izle" hidden>Cevabı izle</button> <button type="button" class="dugme acik vg-baska">Başka soru</button> <a class="vg-git" href="#">Sayfasına git</a></p><p class="vg-seri" aria-live="polite"></p>
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
yaz("/gizlilik/", sayfa("Gizlilik | Herkese Eğitim","Bu sitede takip kodu ve çerez yok. Ziyaretler kişisel veri toplanmadan sayılır.","/gizlilik/",'''<div class="yan-yana"><article class="makale"><h1>Gizlilik</h1>
<p>Bu sitede takip kodu ve çerez yok. Sitede hesap açılmaz, form doldurulmaz.</p>
<p>Kaç kişinin hangi sayfayı açtığı GoatCounter ile kişisel veri toplanmadan sayılır. Çerez yazılmaz, sizi tanıyan bir kimlik tutulmaz. Araçlar, atölyeler ve indirilen dosyalarda sayaç yoktur.</p>
<p>Tarayıcınızda iki küçük not kalır: "Üç soru" seçimleriniz ve son ziyaret tarihiniz ("Yeni" etiketleri için). İkisi de bize gelmez. Yandaki düğmeyle hemen silebilirsiniz.</p>
<p>Videolar YouTube'dan gelir ve siz oynat düğmesine dokunana kadar yüklenmez. Dokununca YouTube'un çerezsiz oynatıcısı (youtube-nocookie.com) açılır; o andan sonra YouTube'un kendi kuralları geçerlidir.</p>
<p>Site GitHub Pages'ta durur, alan adı Cloudflare'dedir. Bu hizmetler, her web sitesinde olduğu gibi, sayfanın size ulaşması için teknik kayıt tutar. Biz kimin baktığını görmeyiz.</p>
<p>Araçlar ve atölyeler tarayıcınızda çalışır; içlerine yazdığınız bir şey bize gönderilmez.</p>
<p>Soru ve öneri: <a href="mailto:herkeseegitimtek@gmail.com">herkeseegitimtek@gmail.com</a></p></article>
<aside class="yan-pano"><div class="tahta-liste"><p class="tl-b">Bu sitede yok</p><ul class="cizik"><li>Takip kodu</li><li>Çerez</li><li>Reklam</li><li>Hesap açma</li><li>Form</li></ul></div>
<div class="not-kagit"><p class="tl-b">Bu tarayıcıda kalan</p><ul class="kalan"><li data-k="he-kapi"><b>Üç soru seçimi</b><span></span></li><li data-k="he-son"><b>Son ziyaret tarihi</b><span></span></li></ul><button type="button" class="dugme kir sil-not">Bu tarayıcıdan sil</button><p class="sil-durum" role="status"></p></div></aside></div>''', None, " / Gizlilik"))

konu_konu = urllib.parse.quote("Atölye önerisi")
konu_govde = urllib.parse.quote("Sınıf:\nBranş:\nKonu ya da öğrenme çıktısı:\nÖğrencilerin en çok takıldığı yer:\n")
yaz("/konu/", sayfa("Konu önerin | Herkese Eğitim","Sınıfınızın konusunu yazın, atölyesini birlikte düşünelim.","/konu/",f'''<div class="yan-yana"><article class="makale"><h1>Konu önerin</h1>
<p>Sınıfınızın konusunu yazın, atölyesini birlikte düşünelim. Öğrencilerin en çok nerede takıldığını yazarsanız atölye oradan başlar.</p>
<p>Öğrenci adı yazmayın.</p>
<div class="paylas" style="margin-top:22px"><a class="dugme kir" href="https://mail.google.com/mail/?view=cm&amp;to=herkeseegitimtek@gmail.com&amp;su={konu_konu}&amp;body={konu_govde}" rel="noopener">Gmail ile yaz</a><a class="dugme acik" href="https://outlook.live.com/mail/0/deeplink/compose?to=herkeseegitimtek@gmail.com&amp;subject={konu_konu}&amp;body={konu_govde}" rel="noopener">Outlook ile yaz</a><a class="dugme acik" href="mailto:herkeseegitimtek@gmail.com?subject={konu_konu}&amp;body={konu_govde}">E-posta programı</a></div>
<p style="margin-top:18px;font-size:16px">Adres: herkeseegitimtek@gmail.com</p></article>
<aside class="yan-pano"><div class="not-kagit ornek"><p class="tl-b">Örnek bir öneri</p><dl><dt>Sınıf</dt><dd>7</dd><dt>Branş</dt><dd>Matematik</dd><dt>Konu</dt><dd>Yüzdeler</dd><dt>En çok takıldıkları yer</dt><dd>İndirimden sonra yeniden zam yapınca fiyatın eskisine döneceğini sanıyorlar.</dd></dl></div></aside></div>''', None, " / Konu önerin"))

# ---- İngilizce giriş sayfası (/en/): yalnız bu sayfa İngilizce; araç ve atölye adresleri veriden
EN_ARAC = {
 "ciztahta": dict(ne="A whiteboard that opens in your browser. Open a PDF and write on every page.",
   ozellik=["Pen, curtain, spotlight and laser", "Timer, random name picker and groups", "Save the lesson and your notes as a PDF"],
   dil="Opens in English when your browser is not set to Turkish.", video="ydp5nstgcnI", ek=""),
 "yaztahta": dict(ne="Keyboard skills for grades 1 to 4. Where each key is and what it does.",
   ozellik=["At the computer, or the whole class at the board", "Letters are introduced in Jolly Phonics order", "English interface and US keyboard layout"],
   dil="The link below opens it in English.", video="BfgQQ4M0OvQ", ek="#en-us"),
}
EN_ATOLYE = {
 "basit-makineler": ("Simple machines", "Grade 8 science. Build pulleys, levers and winches on the board and try them out."),
 "bilgisayarin-ici": ("Inside the computer", "Grade 5 IT. A 3D model shows where your typing goes, and why saving matters."),
 "yuzdeler": ("Percentages", "Grade 7 math. Drag a bar to find a part, the whole, or a percentage change."),
}
_ue = {u["id"]: u for u in urunler}
def _en_arac(k, i):
    u = _ue.get(k); d = EN_ARAC[k]
    if not u or u["durum"] != "yayinda": return ""
    li = "".join(f"<li>{E(x)}</li>" for x in d["ozellik"])
    return (f'<article class="en-arac en-{i}"><h3>{E(u["ad"])}</h3><p class="en-ne">{E(d["ne"])}</p><ul>{li}</ul>'
            f'<p class="en-dil">{E(d["dil"])}</p><p class="en-eyl"><a class="dugme kir" href="{E(u["url"] + d["ek"])}">Open {E(u["ad"])}</a>'
            f'<a class="dugme acik" href="https://www.youtube.com/watch?v={d["video"]}">Watch the English video</a></p></article>')
_en_tr = "".join(f'<li><b>{E(EN_ATOLYE[k][0])}</b><span>{E(EN_ATOLYE[k][1])}</span><a href="{E(_ue[k]["url"])}" lang="tr">{E(_ue[k]["ad"])}</a><i>Turkish interface</i></li>'
                 for k in EN_ATOLYE if k in _ue and _ue[k]["durum"] == "yayinda")
EN_SLOGAN = "Old wisdom, new technology."
EN_ALT_SL = "For using technology well, ethically and where it fits."
def _kisalt(t, n):
    return t if len(t) <= n else t[:n-1].rsplit(' ',1)[0].rstrip(',;:') + '…'
_EN_UST = f'<header class="ust koyu"><div class="w"><a class="logo" href="/en/"><img src="{LOGO}" alt="Herkese Eğitim, English home" width="200" height="46"></a><nav aria-label="Main"><a href="/en/#teachers">Tools</a><a href="/en/proverbs/">Turkish proverbs</a><a href="/en/about/">About</a><a class="dil" href="/" hreflang="tr" lang="tr">Türkçe</a></nav></div></header>'
_soz_en = [a for a in atasozleri if a.get("en")]
_bugun_en = max(_soz_en, key=lambda a: ((a.get("tarih") or ""), a.get("no") or 0)) if _soz_en else None
# İngilizce sayfa sonu: Türkçe sayfa sonunun (ALT) aynısı, metinler İngilizce
_en_odev = (f'<a class="odev" href="{en_soz(_bugun_en["en"])}"><span class="odev-e">Today’s homework</span><b>{E(_bugun_en["en"]["literal"])}</b>'
            f'<span class="odev-n">Guess the meaning first, then check.</span></a>') if _bugun_en else ""
_EN_ALT = re.sub(r'<dialog class="kare".*?</dialog>\n?', "", ALT, flags=re.S)
_EN_ALT = _EN_ALT.replace('<p class="cikis-b">Zil çaldı.</p>', '<p class="cikis-b">Zil çaldı</p>')  # 11 Kas: başlıkta nokta yok; eski build.py ile de çalışır
for _a, _b in [("<p class=\"cikis-b\">Zil çaldı</p>", "<p class=\"cikis-b\">The bell rang.</p>"),
               ("Yarın yine buradayız. Çıkmadan bir ödev:", "See you tomorrow. One piece of homework before you go:"),
               ('aria-label="Sosyal medya"', 'aria-label="Social media"'),
               ("Mıknatısları tahtada gezdirebilirsiniz.", "You can move the magnets around the board."),
               ('<li><a href="/konu/">Konu önerin</a></li><li><a href="/hakkinda/">Hakkında</a></li><li><a href="/gizlilik/">Gizlilik</a></li>',
                '<li><a href="/en/about/">About</a></li><li><a href="/" hreflang="tr" lang="tr">Türkçe</a></li>'),
               ("Bu site çerez kullanmaz; ziyaretler kişisel veri toplanmadan sayılır. YouTube videoları siz dokunana kadar yüklenmez.", "No cookies. Visits are counted without collecting personal data. YouTube videos load only when you tap them.")]:
    assert _a in _EN_ALT, ("EN sayfa sonu", _a)
    _EN_ALT = _EN_ALT.replace(_a, _b)
_EN_ALT = _EN_ALT.replace(">Claude ile birlikte hazırlandı</a>", ">Made together with Claude</a>").replace(">Claude ile birlikte hazırlandı</span>", ">Made together with Claude</span>")  # 11 Kas: yeni build.py ile gelir; eski build.py'de yoksa dokunmaz
if _oh: _EN_ALT = _EN_ALT.replace(_oh, _en_odev)
assert "Bugünün ödevi" not in _EN_ALT and "Zil çaldı" not in _EN_ALT
_EV_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10M10 20v-6h4v6"/></svg>'
def _en_yol(*parca):
    """Türkçe yol satırının aynısı (ev, ayak izi, tabela), İngilizce."""
    ic = [f'<a class="eve" href="/en/" title="Home">{_EV_SVG}Home</a>']
    for i, (ad, h) in enumerate(parca):
        ic.append('<i class="ayak" aria-hidden="true"></i>')
        ic.append(f'<a href="{h}">{E(ad)}</a>' if h else f'<span class="tabela" aria-current="page">{E(ad)}</span>')
    return '<nav class="yol" aria-label="You are here">' + "".join(ic) + '</nav>'
def _en_vid(v, ad):
    if not v: return ""
    img = f'<img src="{v["kapak_w"]}" alt="" loading="lazy">' if v.get("kapak_w") else ""
    return f'<button class="vid{" dik" if v.get("dik") else ""}" type="button" data-id="{E(v["id"])}" data-cc="en" aria-label="Play the video: {E(ad)}">{img}<span class="oynat" aria-hidden="true"></span></button>'
def _en_band(k, ad, ne, hid):
    return f'<div class="yol-band yb-{k}" id="{hid}"><div class="w"><h2>{ad}</h2><p>{ne}</p></div></div>'
_EN_YOL = [
 ("merak", "Curious minds", "A Turkish proverb every day, translated word for word. Short videos: guess first, then watch.",
   [("Turkish proverbs", "/en/proverbs/")] + ([("Today’s proverb", en_soz(_bugun_en["en"]))] if _bugun_en else []), "curious"),
 ("ogretmen", "Teachers", "For the classroom: tools that open in the browser. Nothing to install, no account.",
   [("Two tools in English", "#teachers")], "teachers"),
 ("ogrenci", "Students", "Workshops students work through at their own pace: guess, try, see what happens. Turkish interface for now.",
   [("Workshops", "#students")], "students"),
]
_en_yollar = '<nav class="yollar en-yollar" aria-label="Who it is for"><div class="w">' + "".join(
  f'<div class="yk yk-{k}"><h2><a href="#{hid}">{ad}</a></h2><p>{ne}</p><p class="yk-b">' + "".join(f'<a href="{h}">{E(t)}</a>' for t,h in l) + '</p></div>'
  for k,ad,ne,l,hid in _EN_YOL) + '</div></nav>'
_en_bsoz = (f'<section class="blm bsoz" aria-labelledby="en-bsoz"><div class="w"><p class="bsoz-k">Today’s Turkish proverb</p>'
  f'<h2 id="en-bsoz"><a href="{en_soz(_bugun_en["en"])}">{E(_bugun_en["en"]["literal"])}</a></h2>'
  f'<p class="bsoz-a"><span lang="tr">{E(_bugun_en["soz"])}</span></p>'
  f'<p class="bsoz-b"><a class="dugme acik" href="{en_soz(_bugun_en["en"])}">Meaning and video</a><a class="dugme acik" href="/en/proverbs/">All Turkish proverbs</a></p></div></section>') if _bugun_en else ""
_EN_NAV = '<nav aria-label="Main"><a href="/en/#teachers">Tools</a><a href="/en/proverbs/">Turkish proverbs</a><a href="/en/about/">About</a><a class="dil" href="/" hreflang="tr" lang="tr">Türkçe</a></nav>'
_bk = None
if _bugun_en:
    _bv = VBY.get(_bugun_en.get("video")) or {}
    _bk = _bugun_en.get("kapak_w") or _bv.get("kapak_w")
_en_cuma = (f'<a class="cuma-not" href="{en_soz(_bugun_en["en"])}">' + (f'<img src="{_bk}" alt="">' if _bk else f'<span class="soru-b">{E(_bugun_en["en"]["literal"])}</span>')
            + f'<small>Today’s Turkish proverb</small><b>{E(_bugun_en["en"]["literal"])}</b><span>Guess what it means.</span>'
            + '<span class="bul">You found it. Now guess what it means.</span></a>') if _bugun_en else ""
_en_veri = json.dumps({"soz":[{"s":a["soz"],"u":en_soz(a["en"]),"n":a.get("no")} for a in _soz_en]}, ensure_ascii=False).replace("</","<\\/")
_EN_SAHNE = f'''<header class="ust"><div class="w"><a class="logo" href="/en/"><img src="{LOGO_ACIK}" alt="Herkese Eğitim, English home" width="200" height="46"></a>{_EN_NAV}</div></header>
<main id="ana" class="en-ana">
<section class="sahne" aria-labelledby="h1" data-soz-et="Turkish proverb No. " data-soz-son=": meaning"><div class="arka" aria-hidden="true"><div class="duvar gece">{"".join(duvar)}</div><div class="gunkat"><div class="duvar gun">{"".join(duvar).replace(' loading="lazy"',"")}</div></div><div class="ortu"></div></div>
<canvas class="tahta" id="tahta" aria-hidden="true"></canvas>
<div class="w"><div class="yazi">
<h1 id="h1" class="gir" style="--d:150ms">{E(EN_SLOGAN)}</h1>
<p class="alt alt-sl gir" style="--d:300ms">{E(EN_ALT_SL)}</p>
<a class="ben gir" style="--d:420ms" href="/en/about/"><img src="{AVATAR}" alt="" width="58" height="58"><span><b style="color:var(--krem);font-weight:650" lang="tr">İdiye Ökten</b><br><i class="soz">For the love of learning and teaching.</i></span></a>
<div class="en-sahne-not gir" style="--d:700ms"><p>Free classroom tools, workshops and a Turkish proverb every day, from Türkiye. Nothing to install, no account.</p><p class="en-sozluk"><span lang="tr">Herkese Eğitim</span>: Turkish for “education for everyone”.</p></div>
</div></div>
{_en_cuma}
<div class="cetvel" role="toolbar" aria-label="Board"><button type="button" id="t-kalem" aria-pressed="false">Pen</button><button type="button" id="t-temizle">Clear</button><button type="button" id="t-ses" aria-pressed="false">Sound</button><span class="ipucu" id="t-ipucu" data-yaz="Write and draw. Circle today’s proverb with the pen.">This page is a board too. Pick up the pen and write.</span></div>
</section>'''

_en_sema = [{"@context":"https://schema.org","@type":"WebPage","name":"Herkese Eğitim in English","description":EN_SLOGAN+" "+EN_ALT_SL,"inLanguage":"en","url":SITE+"/en/","isPartOf":{"@id":SITE+"/#site"},"publisher":{"@id":KURUM["@id"]}}]
_en = bas("Herkese Eğitim: old wisdom, new technology",
  "Old wisdom, new technology. Free classroom tools, workshops and a Turkish proverb every day, for using technology well, ethically and where it fits.",
  "/en/", sema=_en_sema, dil="en", alt=DIL_ALT) + _EN_SAHNE + f'''
{_en_yollar}
{_en_band("merak", "Curious minds", "Old Turkish sayings, word for word, with a short video for each.", "curious")}
{_en_bsoz}
<div class="w"><section class="en-blok en-son" aria-labelledby="en-h2c"><h2 id="en-h2c">Short videos</h2>
<p>Three-second quiz questions, Turkish proverbs and special days, mostly in Turkish. The proverb videos have English subtitles. The English videos have their own playlist on the channel.</p>
<p><a class="dugme acik" href="https://www.youtube.com/@egitimtek">YouTube: @egitimtek</a></p>
</section></div>
{_en_band("ogretmen", "Teachers", "Free tools that open in the browser. Nothing to install, no account.", "teachers")}
<div class="w"><section class="en-blok" aria-labelledby="en-h2a"><h2 id="en-h2a">Two tools that work in English</h2>
<div class="en-araclar">{_en_arac("ciztahta",1)}{_en_arac("yaztahta",2)}</div></section></div>
{_en_band("ogrenci", "Students", "Workshops students work through on their own, from a link their teacher or parent gives them.", "students")}
<div class="w"><section class="en-blok" aria-labelledby="en-h2b"><h2 id="en-h2b">Workshops, in Turkish for now</h2>
<p class="en-not">Curriculum simulations for Turkish classrooms. The interface is in Turkish, but you can still try them. No account needed.</p>
<ul class="en-tr">{_en_tr}</ul></section></div>
</main><script type="application/json" id="veri">{_en_veri}</script>{_EN_ALT}'''
yaz("/en/", _en)

# ---- Turkish proverbs (/en/proverbs/): veri data/atasozleri_en.json + icerik.json atasozleri; sayfalara elle dokunulmaz
def _en_soz_li(a):
    e = a["en"]
    return (f'<li><a href="{en_soz(e)}"><small>No. {E(a.get("no"))}</small><b>{E(e["literal"])}</b>'
            f'<span lang="tr">{E(a["soz"])}</span></a></li>')
_ens_set = {"@type":"DefinedTermSet","@id":SITE+"/en/proverbs/#set","name":"Turkish proverbs","inLanguage":"en","url":SITE+"/en/proverbs/"}
if _soz_en:
    yaz("/en/proverbs/", bas("Turkish proverbs, word for word | Herkese Eğitim",
      "Old Turkish proverbs translated word for word, with their meaning, the closest English saying and a short video with English subtitles.",
      "/en/proverbs/", sema=[dict({"@context":"https://schema.org"}, **_ens_set, hasDefinedTerm=[{"@type":"DefinedTerm","name":a["soz"],"alternateName":a["en"]["literal"],"url":SITE+en_soz(a["en"])} for a in _soz_en])],
      dil="en", alt=[("en","/en/proverbs/"),("tr","/atasozleri/")]) + _EN_UST + f'''
<main id="ana" class="sayfa en"><div class="w">
{_en_yol(("Turkish proverbs", None))}
<section class="en-pbas"><h1>Turkish proverbs, word for word</h1>
<p>Old Turkish sayings, first translated literally, then explained. Each one has a short video with English subtitles.</p></section>
<ol class="soz-liste en-pl">{"".join(_en_soz_li(a) for a in reversed(_soz_en))}</ol>
</div></main>{_EN_ALT}''')
def _ats_kelime(a, e):
    """Türkçe sözcükler + İngilizce karşılıklar ve literal içindeki parlatma aralıkları. Uymazsa (None, None) ve UYARI."""
    w = e.get("words") or []
    if not w: return None, None
    tr = re.sub(r"[.,;:!?]", "", a["soz"]).split()
    if [x[0] for x in w] != tr:
        print("UYARI: atasozleri_en words Türkçe sözle uymuyor, no", a.get("no")); return None, None
    lit = e["literal"]; ar = []
    for i, x in enumerate(w):
        for parca in (x[2] if len(x) > 2 else "").split("|"):
            if not parca: continue
            m = re.fullmatch(r"(.*?)(?:#(\d+))?", parca); ifade, kac = m.group(1), int(m.group(2) or 1)
            bul = [k.start() for k in re.finditer(r"(?<!\w)" + re.escape(ifade) + r"(?!\w)", lit)]
            if len(bul) < kac:
                print("UYARI: atasozleri_en parlatma bulunamadı, no", a.get("no"), parca); return None, None
            ar.append((bul[kac-1], bul[kac-1] + len(ifade), i))
    bir = {}
    for s1, e1, i in ar: bir.setdefault((s1, e1), []).append(str(i))  # aynı parça iki sözcüğe ait olabilir (çok + olur)
    ar = sorted((s1, e1, " ".join(ii)) for (s1, e1), ii in bir.items())
    for (s1, e1, _), (s2, _, _) in zip(ar, ar[1:]):
        if s2 < e1:
            print("UYARI: atasozleri_en parlatma çakışıyor, no", a.get("no")); return None, None
    h, p = "", 0
    for s1, e1, i in ar:
        h += E(lit[p:s1]) + f'<span class="ats-p" data-w="{i}">{E(lit[s1:e1])}</span>'; p = e1
    h += E(lit[p:])
    h = re.sub(r"\(([^()<]*)\)", r'<span class="ats-par">(\1)</span>', h)
    k = " ".join(f'<button class="ats-k" type="button" data-w="{i}"><span class="ats-t">{E(x[0])}</span><span class="ats-gl" lang="en">{E(x[1])}</span></button>' for i, x in enumerate(w))
    return h, k
for i,a in enumerate(_soz_en):
    e = a["en"]; v = VBY.get(a.get("video")) or ({"id":a["video"],"baslik":a["soz"],"kapak_w":a.get("kapak_w"),"dik":True,"tarih":a.get("tarih")} if a.get("video") else None)
    lit = e["literal"].rstrip(".")
    esd = e.get("equivalent") or "No direct English equivalent."
    esb = "English equivalent"
    if esd.startswith("Closest:"): esb, esd = "Nearest English saying", esd[8:].strip()[:1].upper() + esd[8:].strip()[1:]
    kay = ("A folk saying not found in the TDK dictionary. The meaning is our own interpretation." if (e.get("source") or "").lower().startswith("folk")
           else "Meaning from the TDK (Turkish Language Association) dictionary.")
    sema = [{"@context":"https://schema.org","@type":"DefinedTerm","name":a["soz"],"alternateName":e["literal"],"description":e["meaning"],"inLanguage":"tr",
             "inDefinedTermSet":_ens_set,"url":SITE+en_soz(e),"sameAs":SITE+soz_sayfa(a)}]
    if v:
        _vs = sema_video(v, en_soz(e))
        if _vs: sema.append(_vs)
    onc = _soz_en[i-1] if i>0 else None; snr = _soz_en[i+1] if i+1<len(_soz_en) else None
    gez = ('<p class="en-gez">' + (f'<a href="{en_soz(onc["en"])}">Previous: {E(onc["en"]["literal"])}</a>' if onc else "<span></span>")
           + (f'<a href="{en_soz(snr["en"])}">Next: {E(snr["en"]["literal"])}</a>' if snr else "") + "</p>")
    lit_h, kel_h = _ats_kelime(a, e)
    tr_h = f'<p class="ats-tr" lang="tr">{kel_h or E(a["soz"])}</p>'
    no = E(a.get("no"))
    yaz(en_soz(e), bas(f"Turkish proverb: {lit}", _kisalt(f"{e['literal']} Meaning: {e['meaning']}", 160), en_soz(e), sema=sema, og=a.get("kapak_w"),
        dil="en", alt=[("en",en_soz(e)),("tr",soz_sayfa(a))]) + _EN_UST + f"""
<main id="ana" class="sayfa en"><div class="w">{_en_yol(("Turkish proverbs", "/en/proverbs/"), (f"No. {a.get('no')}", None))}
<div class="soz-sayfa ats"><article class="makale">
<h1 class="soz ats-lit">{lit_h or E(e["literal"])}</h1>
<p class="ats-q">What do you think it means?</p>
{tr_h}
<p class="ats-ac-p"><button class="dugme ats-ac" type="button" aria-expanded="false" aria-controls="ats-c{no}">Reveal meaning</button></p>
<div class="ats-c" id="ats-c{no}">
<div class="kutu"><h2>Meaning</h2><p>{E(e["meaning"])}</p></div>
<div class="kutu"><h2>{esb}</h2><p>{E(esd)}</p></div>
</div>
<p class="ats-trs"><a href="{soz_sayfa(a)}" hreflang="tr">In Turkish: <span lang="tr">{E(a["soz"])}</span></a></p>
<p class="ats-kay">{E(kay)}</p>
{gez}</article>
<aside>{_en_vid(v, e["literal"]) if v else ""}</aside></div>
</div></main>{_EN_ALT}""")

# ---- About (/en/about/): Türkçe Hakkında'nın ilk tahtası, İngilizce; Claude satırı yalnız burada
_EN_MISYON = "Rooted in education, Herkese Eğitim works to spread the use of technology done well, ethically and where it fits. It aims to make people’s work easier and to help them be more productive and build more meaningful lives."
yaz("/en/about/", bas("About: İdiye Ökten | Herkese Eğitim",
    "İdiye Ökten and Herkese Eğitim. Old wisdom, new technology: free classroom tools, workshops and videos for using technology well, ethically and where it fits.",
    "/en/about/", sema=[{"@context":"https://schema.org","@type":"ProfilePage","mainEntity":KISI,"url":SITE+"/en/about/","inLanguage":"en"}],
    dil="en", alt=[("en","/en/about/"),("tr","/hakkinda/")]) + _EN_UST + f"""
<main id="ana" class="sayfa en"><div class="w">{_en_yol(("About", None))}<article class="hk">
<section class="hk-bas">
<div class="hk-kim"><img src="{AVATAR}" alt="Drawing of İdiye Ökten" width="150" height="150"><div><h1 lang="tr">İdiye Ökten</h1><p class="soz">For the love of learning and teaching.</p></div>
<aside class="hk-yaz" aria-label="Write to me"><p class="hk-yaz-b">Write to me</p><p>Tell me your class topic and let’s think about a workshop together.</p><p class="hk-yaz-a"><a class="dugme kir" href="mailto:herkeseegitimtek@gmail.com">Send an email</a></p><p class="hk-yaz-e">herkeseegitimtek@gmail.com</p></aside></div>
<div class="hk-oyku">
<p>I have worked with technology in education for about thirty years. At <span lang="tr">Herkese Eğitim</span> I share free resources for teachers, students and anyone else: tools that open on the classroom board, workshops built on Turkish curriculum outcomes, three-second quiz questions, a Turkish proverb series and special-day videos.</p>
<p>My first job, in 1997, brought me into education. <span lang="tr">Herkese Eğitim</span> was first the name of a project we entered in the education category of the TEKNOFEST Technology for Humanity competition in 2018. During the pandemic, in the summer of 2020, we met with teachers every evening for 15 days, under this name. Each day we looked at one web tool; the articles appeared on <span lang="tr">Bilim Şenliği</span> and the how-to videos on the <a href="https://www.youtube.com/@egitimtek">YouTube channel</a>. More than a hundred videos on Padlet, Wakelet, Wordwall, Edpuzzle, Quizizz, Flipgrid, Mentimeter and others were collected on a Wakelet board. Now it is the name of this library. In the age of AI, the sharing goes on.</p>
<p>Claude is my teammate in this work. <span class="kalp" role="img" aria-label="heart">♥</span></p>
</div>
</section>
<section class="hk-misyon" aria-label="Herkese Eğitim"><p class="hk-sl">{E(EN_SLOGAN)}</p><p class="hk-mi">{E(_EN_MISYON)}</p></section>
<p class="ats-trs"><a href="/hakkinda/" hreflang="tr">In Turkish: <span lang="tr">Hakkında</span></a> (with talks, certificates and the full timeline)</p>
<p class="ats-trs">This site uses no cookies. GoatCounter counts how many people open each page, without collecting personal data.</p>
</article></div></main>{_EN_ALT}""")

# ---- İçinde Ne Var? (bilişim dizisi): data/icinde-ne-var/bolumler.json; her bölüm kendi tek dosyalık 3B sayfası
_INV_YOL = os.path.join(KOK, "data", "icinde-ne-var", "bolumler.json")
INV = json.load(open(_INV_YOL, encoding="utf-8")) if os.path.exists(_INV_YOL) else []
INV_ADRES = "/icinde-ne-var/"
def _inv_video(b):
    if not b.get("video"): return ""
    return ('<style>#hev-ac{position:fixed;left:12px;bottom:80px;z-index:50;font:600 14px/1 system-ui,sans-serif;padding:10px 14px;border-radius:999px;border:2px solid #2A2420;background:#FFC21A;color:#2A2420;cursor:pointer}@media (max-width:700px){#hev-ac{left:auto;right:10px;bottom:auto;top:132px;font-size:13px;padding:8px 12px}}</style>'
      '<button type="button" id="hev-ac">▶ Videosu</button>'
      '<dialog id="hev-d" style="position:fixed;inset:0;margin:auto;padding:0;border:0;background:#2A2420;border-radius:14px;max-width:96vw;max-height:96vh;height:fit-content;width:fit-content"><div style="display:flex;justify-content:flex-end;padding:6px"><button type="button" id="hev-k" style="font:600 14px system-ui,sans-serif;background:#F7F0E1;border:0;border-radius:999px;padding:8px 14px;cursor:pointer">Kapat</button></div><div id="hev-v" style="height:min(640px,82vh);aspect-ratio:9/16;max-width:92vw"></div></dialog>'
      '<script>(function(){var d=document.getElementById("hev-d"),v=document.getElementById("hev-v");document.getElementById("hev-ac").onclick=function(){v.innerHTML=\'<iframe src="https://www.youtube-nocookie.com/embed/' + E(b["video"]) + '?autoplay=1&rel=0" title="Video" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen style="width:100%;height:100%;border:0"></iframe>\';d.showModal()};document.getElementById("hev-k").onclick=function(){d.close()};d.addEventListener("close",function(){v.innerHTML=""})})();</script>')
def _inv_og(b):  # bağlantı önizlemesi: başlık, açıklama, görsel (bölüm kendi görselini og_gorsel ile verebilir)
    ad = b["ad"][:1].lower() + b["ad"][1:]
    return b.get("og_baslik") or f'{b["soru"]} | İçinde Ne Var?', b.get("og_aciklama") or f"Sayfada kendiniz sökün: {ad}, parça parça.", b.get("og_gorsel") or "/img/paylas-icinde-ne-var.png"
def _inv_meta(b):
    t, a, g = _inv_og(b); u = SITE + INV_ADRES + b["slug"] + "/"
    return (f'<meta property="og:type" content="website"><meta property="og:title" content="{E(t)}"><meta property="og:description" content="{E(a)}">'
      f'<meta property="og:url" content="{E(u)}"><meta property="og:image" content="{SITE}{g}"><meta property="og:locale" content="tr_TR">'
      f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{SITE}{g}">\n')
# Müze kapısı: "durum": "mesgul" olan (yayında olmayan) vitrin koridora "Hat meşgul" kutusu olarak girer. Kapıdaki yer tutucu buradan dolar.
# Taslak vitrinin ani/metin alanları sayfaya taşınmaz: yalnız no, mesgul.baslik, mesgul.alt ve video gider.
def _mesgul_vitrinler(b):
    return [v for v in (b or {}).get("vitrinler") or [] if v.get("durum") == "mesgul" and not v.get("yayinda") and v.get("mesgul")]
def _muze_ek(b):
    h = open(os.path.join(KOK, "data", b["ek"]), encoding="utf-8").read()
    if "/*hev-mesgul*/" in h:
        m = [dict(no=v["no"], baslik=v["mesgul"]["baslik"], alt=v["mesgul"]["alt"], video=v.get("video")) for v in _mesgul_vitrinler(b)]
        h = h.replace("null/*hev-mesgul*/", json.dumps(m, ensure_ascii=False).replace("</", "<\\/") + "/*hev-mesgul*/", 1)
    return h
_inv_k = []; _inv_son = None; _inv_one = ""
for b in INV:
    assert re.fullmatch(r"[a-z0-9-]{3,60}", b["slug"]), "İçinde Ne Var: kötü slug"
    assert not b.get("video") or re.fullmatch(r"[A-Za-z0-9_-]{11}", b["video"]), "İçinde Ne Var: kötü video kimliği"
    if (b.get("tarih") or "9") > BUGUN.isoformat(): continue
    h = open(os.path.join(KOK, "data", b["sayfa"]), encoding="utf-8").read()
    if b.get("video"): h = h.replace("</body>", _inv_video(b) + "\n</body>", 1)
    if b.get("ek"): h = h.replace("</body>", _muze_ek(b) + "\n</body>", 1)
    if b.get("og_kapak"):
        _ok = Image.open(os.path.join(KOK, "data", b["kapak"])).convert("RGB"); assert _ok.size == (1200, 630), "İçinde Ne Var: og kapak 1200x630 olmalı"
        _ok.save(os.path.join(OUT, "img", f"paylas-{b['slug']}.jpg"), quality=86, optimize=True, progressive=True); b["og_gorsel"] = f"/img/paylas-{b['slug']}.jpg"
    assert "</head>" in h and 'property="og:' not in h, "İçinde Ne Var: head"
    h = h.replace("</head>", _inv_meta(b) + "</head>", 1); _inv_son = b
    yaz(f"{INV_ADRES}{b['slug']}/", h)
    if b.get("kisa_adres"):  # kısa adres (videoda yazılan): /<kisa>/ -> bölüm sayfası; site haritasına girmez. Sorgu korunur (lang= -> dil=); tarayıcı dili Türkçe değilse ?dil=en eklenir
        assert re.fullmatch(r"[a-z0-9-]{3,30}", b["kisa_adres"]), "İçinde Ne Var: kötü kısa adres"
        _ky = os.path.join(OUT, b["kisa_adres"], "index.html"); assert not os.path.exists(_ky), "İçinde Ne Var: kısa adres dolu"
        _hd = INV_ADRES + b["slug"] + "/"
        _en = "" if b.get("tek_dil") else f' · <a href="{_hd}?dil=en" lang="en">Open in English</a>'  # tek_dil: yalnız Türkçe sayfa
        os.makedirs(os.path.dirname(_ky), exist_ok=True)
        open(_ky, "w", encoding="utf-8").write(f'<!DOCTYPE html>\n<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{E(b["ad"])} | İçinde Ne Var?</title><meta name="robots" content="noindex"><link rel="canonical" href="{SITE}{_hd}"><script>(function(){{var q=location.search.replace(/([?&])lang=/,"$1dil=");if(!/[?&]dil=/.test(q)&&!/^tr/i.test(navigator.language||""))q=(q?q+"&":"?")+"dil=en";location.replace("{_hd}"+q)}})()</script><meta http-equiv="refresh" content="0; url={_hd}"></head><body style="font:18px/1.5 system-ui,sans-serif;padding:24px;background:#F7F0E1;color:#2A2420"><p><a href="{_hd}">{E(b["ad"])}: sayfayı açın</a>{_en}</p></body></html>\n')
    b["kapak_w"] = resim(b.get("kapak"), "inv-" + b["slug"], 420)
    if b.get("one_cikan"):  # öne çıkan giriş: liste sayfasında en üstte büyük kart
        _bw = resim(b.get("kapak"), "inv-" + b["slug"] + "-b", 960)
        _inv_one = (f'<a class="inv-one" href="{INV_ADRES}{b["slug"]}/">' + (f'<img src="{_bw}" alt="" width="960" height="504">' if _bw else "")
          + f'<span class="inv-one-m"><b>{E(b["ad"])}</b><span class="inv-one-a">{E(b["kisa"])}</span><span class="dugme">{E(b.get("etiket") or "Sayfayı açın")}</span></span></a>'
          + (f'<p class="inv-one-v"><a class="inv-vid" href="https://www.youtube.com/shorts/{b["video"]}" rel="noopener">Videoyu YouTube\'da izleyin</a></p>' if b.get("video") else ""))
        continue
    _inv_k.append(f'<li class="kart inv"><a href="{INV_ADRES}{b["slug"]}/">' + (f'<img src="{b["kapak_w"]}" alt="" loading="lazy">' if b.get("kapak_w") else "")
      + f'<b>{b["no"]:02d} · {E(b["ad"])}</b><span>{E(b["kisa"])}</span><span class="etk">{E(b.get("etiket") or "Sayfayı açın, kendiniz sökün")}</span></a>'
      + (f'<a class="inv-vid" href="https://www.youtube.com/shorts/{b["video"]}" rel="noopener">Videoyu YouTube\'da izleyin</a>' if b.get("video") else "") + '</li>')
if _inv_k:
    _inv_ac = "Gündelik aletleri 3B olarak açıyoruz. Sayfayı tarayıcıda açın, parçaları ekranda kendiniz ayırın; kurulum yok."
    yaz(INV_ADRES, sayfa("İçinde Ne Var? | Herkese Eğitim", _inv_ac, INV_ADRES,
      lbas("İçinde Ne Var?", E(_inv_ac), [("Defter", "İçinde Ne Var?"), ("İçinde", f"{len(_inv_k) + bool(_inv_one)} bölüm"), ("Konu", "gündelik aletlerin içi")])
      + _inv_one + f'<ul class="kartlar">{"".join(_inv_k)}</ul>',
      [{"@context":"https://schema.org","@type":"CollectionPage","name":"İçinde Ne Var?","url":SITE+INV_ADRES,"description":_inv_ac}], " / İçinde Ne Var?", og="/img/paylas-icinde-ne-var.png"))  # liste kendi önizlemesini taşır (bölümün başlığı ve görseli değil)

# ---- Kayıp Aletler Müzesi: her vitrinin kendi sayfası (kurul v1, 13 Kas). bolumler.json, müze kaydı, "vitrinler" listesi.
# /icinde-ne-var/muze/<vitrin>/ kendi kanonik adresi, og'si ve anıyla açılan başlığıyla; metin HTML'de durur (JavaScript'e bağlı değil).
# "yayinda": false olan vitrin üretilmez. Yerel önizleme: VITRIN_TASLAK=telefon python build.py (Merkez yayına alırken bayrağı true yapar).
# "sayfa" verilmişse vitrin müzenin kendi dosyasıyla açılır (etkileşim oradan), verilmemişse yalnız metinli etiket sayfası çıkar.
# "muzede": true olunca etiket sayfasında "Müzeye girin" düğmesi çıkar (vitrin müze dosyasına girmeden kaset vitrinine götürmesin).
MUZE_ADRES = INV_ADRES + "muze/"
_VT_TASLAK = set(filter(None, os.environ.get("VITRIN_TASLAK", "").split(",")))
_muze = next((b for b in INV if b.get("slug") == "muze" and (b.get("tarih") or "9") <= BUGUN.isoformat()), None)
VITRINLER = []
for _v in (_muze or {}).get("vitrinler") or []:
    assert re.fullmatch(r"[a-z0-9-]{3,30}", _v["slug"]), "Müze: kötü vitrin slug"
    assert not _v.get("video") or re.fullmatch(r"[A-Za-z0-9_-]{11}", _v["video"]), "Müze: kötü video kimliği"
    if _v.get("yayinda") or _v["slug"] in _VT_TASLAK: VITRINLER.append(_v)
def vitrin_sayfa(v): return MUZE_ADRES + v["slug"] + "/"
MESGUL = [v for v in _mesgul_vitrinler(_muze) if v["slug"] not in _VT_TASLAK]  # vitrin sayfası üretilmez, ana sayfa bandında "Hat meşgul" kartı
for _v in MESGUL: _v["kapak_w"] = resim(_v.get("kapak"), "vitrin-" + _v["slug"], 640)
_VT_CSS = ('<style>.vt-etiket{box-sizing:border-box;max-width:760px;margin:0 auto;padding:40px 16px 56px;color:#f5e6c8;font:18px/1.6 "Inter",system-ui,sans-serif}'
  '.vt-wrap{background:#10151d;border-top:1px solid rgba(232,163,90,.35)}'
  '.vt-etiket .vt-k{margin:0 0 10px;font:600 13px/1.4 "Inter",system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#e8a35a}'
  '.vt-etiket h1{margin:0 0 18px;font:600 clamp(28px,5vw,42px)/1.15 "Fraunces",Georgia,serif;color:#fff3d6}'
  '.vt-etiket p{margin:0 0 14px}.vt-etiket .vt-ani{font-family:"Fraunces",Georgia,serif;font-size:20px;color:#fff3d6}'
  '.vt-etiket .vt-l{display:flex;flex-wrap:wrap;gap:10px 18px;margin-top:22px;font-size:16px}'
  '.vt-etiket a{color:#ffcb80;text-underline-offset:3px}.vt-etiket a:focus-visible{outline:3px solid #ffcb80;outline-offset:3px;border-radius:6px}'
  '.vt-etiket .vt-l a{display:inline-flex;align-items:center;min-height:44px}'
  '.vt-etiket .vt-gir{display:inline-flex;align-items:center;min-height:44px;padding:0 18px;border-radius:999px;background:#e8a35a;color:#231b1b;font-weight:650;text-decoration:none}'
  '</style>')
def _vt_etiket(v, muzede):
    k = f'Kayıp Aletler Müzesi · Vitrin {v["no"]:02d} · {v["ad"]}' + (f' · {v["donem"]}' if v.get("donem") else "")
    l = ([f'<a class="vt-gir" href="{MUZE_ADRES}">Müzeye girin</a>'] if (not muzede and v.get("muzede")) else [])  # vitrin müzeye girmeden düğme çıkmaz
    if v.get("video"): l.append(f'<a href="https://www.youtube.com/shorts/{v["video"]}" rel="noopener">Kısa videoyu YouTube\'da izleyin</a>')
    l += [f'<a href="{MUZE_ADRES}">Müzenin girişi</a>' if muzede else "", f'<a href="{INV_ADRES}">İçinde Ne Var? bütün bölümler</a>']
    return (f'<div class="vt-wrap"><section class="vt-etiket" aria-labelledby="vt-b"><p class="vt-k">{E(k)}</p><h1 id="vt-b">{E(v["baslik"])}</h1>'
      + "".join(f'<p class="vt-ani">{E(p)}</p>' for p in v.get("ani") or []) + "".join(f'<p>{E(p)}</p>' for p in v.get("metin") or [])
      + f'<p class="vt-l">{"".join(x for x in l if x)}</p></section></div>')
for v in VITRINLER:
    _y = vitrin_sayfa(v); _t = f'{v["baslik"]} | Kayıp Aletler Müzesi · {v["ad"]}'
    _ok = Image.open(os.path.join(KOK, "data", v["og_kapak"])).convert("RGB"); assert _ok.size == (1200, 630), "Müze: vitrin og kapağı 1200x630 olmalı"
    _ok.save(os.path.join(OUT, "img", f"paylas-muze-{v['slug']}.jpg"), quality=86, optimize=True, progressive=True)
    v["og_gorsel"] = f"/img/paylas-muze-{v['slug']}.jpg"
    v["kapak_w"] = resim(v.get("kapak"), "vitrin-" + v["slug"], 640)
    _meta = (f'<link rel="canonical" href="{SITE}{_y}">' + _inv_meta(dict(slug="muze/" + v["slug"], ad=v["ad"], soru=v["baslik"], og_baslik=v["og_baslik"], og_aciklama=v["og_aciklama"], og_gorsel=v["og_gorsel"]))
      + '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"WebPage","name":v["baslik"],"description":v["aciklama"],"url":SITE+_y,"inLanguage":"tr",
          "isPartOf":{"@type":"CollectionPage","name":"Kayıp Aletler Müzesi","url":SITE+MUZE_ADRES},"publisher":{"@id":SITE+"/#kurum"}}, ensure_ascii=False).replace("</","<\\/") + '</script>' + _VT_CSS)
    if v.get("sayfa"):  # müzenin kendi dosyası: vitrin sahnesi, kuş, defter aynı; üstüne bu vitrinin başlığı, açıklaması ve düz metni
        h = open(os.path.join(KOK, "data", v["sayfa"]), encoding="utf-8").read()
        assert h.count("<title>") == 1 and h.count('<main id="root"></main>') == 1 and h.count('<html lang="tr">') == 1, "Müze: vitrin sayfası beklenen biçimde değil"
        h = re.sub(r"<title>.*?</title>", f"<title>{E(_t)}</title>", h, count=1)
        h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(v["aciklama"])}">', h, count=1)
        h = h.replace('<html lang="tr">', f'<html lang="tr" data-ilk="{v["slug"]}">', 1)
        h = h.replace('<main id="root"></main>', '<main id="root"></main>' + _vt_etiket(v, True), 1)
        if v.get("video"): h = h.replace("</body>", _inv_video(v) + "\n</body>", 1)
        if _muze.get("ek"): h = h.replace("</body>", _muze_ek(_muze) + "\n</body>", 1)
        assert 'property="og:' not in h.split("</head>")[0], "Müze: head"
        h = h.replace("</head>", _meta + "</head>", 1)
    else:  # vitrin dosyası henüz yok: yalnız metinli etiket sayfası
        h = (f'<!doctype html>\n<html lang="tr" data-ilk="{v["slug"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(_t)}</title>'
          f'<meta name="description" content="{E(v["aciklama"])}"><meta name="theme-color" content="#10151d">{_meta}<style>'
          '@font-face{font-family:BG;src:url(/fonts/bg-ext.woff2) format("woff2");font-weight:200 800;font-display:swap;unicode-range:U+0100-02AF,U+1E00-1EFF}'
          '@font-face{font-family:BG;src:url(/fonts/bg.woff2) format("woff2");font-weight:200 800;font-display:swap;unicode-range:U+0000-00FF,U+2000-206F,U+20AC,U+2122,U+2190-21FF}'
          'html,body{margin:0;background:#10151d}.vt-etiket,.vt-etiket .vt-k,.vt-etiket h1,.vt-etiket .vt-ani{font-family:BG,system-ui,sans-serif}.vt-etiket h1{font-weight:800;letter-spacing:-.02em}'
          '.vt-ust{max-width:760px;margin:0 auto;padding:12px 16px 0}.vt-ust a{display:inline-flex;align-items:center;min-height:44px;color:#f5e6c8;font:600 15px/1 BG,system-ui,sans-serif;text-decoration:none}.vt-ust a:hover{text-decoration:underline}'
          '.vt-ust a:focus-visible{outline:3px solid #ffcb80;outline-offset:3px;border-radius:6px}</style></head><body>'
          f'<p class="vt-ust"><a href="{INV_ADRES}">← Herkese Eğitim · İçinde Ne Var?</a></p>'  # görsel yok: vitrin 02'nin kendi karesi gelince eklenir
          + _vt_etiket(v, False).replace('class="vt-wrap"', 'class="vt-wrap" style="border:0"') + '</body></html>\n')
    yaz(_y, h)
    if v.get("kisa_adres"):  # kısa adres: /muze/<kisa>/ -> vitrin sayfası; noindex, site haritasına girmez, sorgu korunur
        assert re.fullmatch(r"[a-z0-9-]{3,30}", v["kisa_adres"]), "Müze: kötü kısa adres"
        _ky = os.path.join(OUT, (_muze.get("kisa_adres") or "muze"), v["kisa_adres"], "index.html"); assert not os.path.exists(_ky), "Müze: kısa adres dolu"
        os.makedirs(os.path.dirname(_ky), exist_ok=True)
        open(_ky, "w", encoding="utf-8").write(f'<!DOCTYPE html>\n<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{E(_t)}</title><meta name="robots" content="noindex"><link rel="canonical" href="{SITE}{_y}"><script>location.replace("{_y}"+location.search+location.hash)</script><meta http-equiv="refresh" content="0; url={_y}"></head><body style="font:18px/1.5 system-ui,sans-serif;padding:24px;background:#10151d;color:#f5e6c8"><p><a style="color:#ffcb80" href="{_y}">{E(v["baslik"])} Vitrini açın</a></p></body></html>\n')
