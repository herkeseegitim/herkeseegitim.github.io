(function(){
"use strict";
var VERI={};try{var v=document.getElementById("veri");if(v)VERI=JSON.parse(v.textContent);}catch(e){}
var azHareket=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
function sakla(k,d){try{localStorage.setItem(k,JSON.stringify(d));}catch(e){}}
function oku(k){try{return JSON.parse(localStorage.getItem(k));}catch(e){return null;}}
function trKucuk(s){return String(s||"").replace(/I/g,"ı").replace(/İ/g,"i").toLowerCase();}
function sade(s){return trKucuk(s).replace(/[çğıöşü]/g,function(c){return {"ç":"c","ğ":"g","ı":"i","ö":"o","ş":"s","ü":"u"}[c];}).replace(/[^a-z0-9% ]/g," ");}

/* video: dokununca yüklenir */
document.addEventListener("click",function(e){
 var b=e.target.closest&&e.target.closest("button.vid");if(!b||b.dataset.yuklendi)return;
 var id=b.dataset.id;if(!/^[\w-]{6,20}$/.test(id))return;
 var f=document.createElement("iframe");
 f.src="https://www.youtube-nocookie.com/embed/"+id+"?autoplay=1&rel=0";
 f.title=b.getAttribute("aria-label")||"YouTube videosu";
 f.allow="autoplay; encrypted-media; picture-in-picture; fullscreen";f.allowFullscreen=true;
 var d=document.createElement("div");d.className=b.className;d.appendChild(f);b.replaceWith(d);f.focus();
});

/* karekod penceresi */
var kare=document.getElementById("kare");
document.addEventListener("click",function(e){
 var t=e.target.closest&&e.target.closest("[data-kare]");if(!t||!kare||!kare.showModal)return;
 e.preventDefault();
 var s=document.getElementById("qr-"+t.dataset.kare);if(!s)return;
 kare.querySelector(".qr").innerHTML=s.innerHTML;
 kare.querySelector("h2").textContent=t.dataset.ad;
 kare.querySelector(".adres").textContent=t.dataset.kisa;
 var a=kare.querySelector("a.ac");a.href=t.dataset.url;a.textContent=t.dataset.etiket||"Bu cihazda aç";
 kare.showModal();kare.querySelector("button.kapat").focus();
});
if(kare){kare.addEventListener("click",function(e){if(e.target===kare||e.target.closest("button.kapat"))kare.close();});}

/* spot */
var sahne=document.querySelector(".sahne"),perde=sahne,hedef=document.querySelector(".cuma-not");
if(sahne&&document.querySelector(".duvar.gun")){
 var x=0,y=0,tx=0,ty=0,raf=0,dokundu=false;
 function konum(){var r=sahne.getBoundingClientRect();if(hedef){var h=hedef.getBoundingClientRect();return [h.left+h.width/2-r.left,h.top+h.height/2-r.top];}return [r.width*.5,r.height*.9];}
 var donus=0;function sonra(){clearTimeout(donus);donus=setTimeout(function(){var k=konum();git(k[0],k[1]);},4000);}
 function ciz(){x+=(tx-x)*.1;y+=(ty-y)*.1;perde.style.setProperty("--x",x+"px");perde.style.setProperty("--y",y+"px");if(Math.abs(tx-x)+Math.abs(ty-y)>.5)raf=requestAnimationFrame(ciz);else raf=0;}
 function git(px,py){tx=px;ty=py;if(azHareket){x=tx;y=ty;perde.style.setProperty("--x",x+"px");perde.style.setProperty("--y",y+"px");return;}if(!raf)raf=requestAnimationFrame(ciz);}
 var k=konum();x=azHareket?k[0]:sahne.clientWidth*.15;y=azHareket?k[1]:sahne.clientHeight*.1;git(k[0],k[1]);
 sahne.addEventListener("pointermove",function(e){if(e.pointerType==="mouse"||dokundu){var r=sahne.getBoundingClientRect();git(e.clientX-r.left,e.clientY-r.top);}});
 sahne.addEventListener("pointerdown",function(e){if(e.pointerType!=="mouse"){dokundu=true;var r=sahne.getBoundingClientRect();git(e.clientX-r.left,e.clientY-r.top);sonra();}});
 sahne.addEventListener("pointerleave",function(e){if(e.pointerType==="mouse"){var k=konum();git(k[0],k[1]);}});
 window.addEventListener("resize",function(){var k=konum();git(k[0],k[1]);});
}

/* az önce izlediğin video */
var izl=document.getElementById("izledin");
if(izl&&VERI.son){
 var q=location.search.replace(/^\?/,"").split("&"),plat=null,vid=null;
 q.forEach(function(p){var kv=p.split("=");if(["ig","tt","yt","x","li"].indexOf(kv[0])>-1)plat=kv[0];if(kv[0]==="v"&&/^[\w-]{6,20}$/.test(kv[1]||""))vid=kv[1];});
 if(plat||vid){
  var adlar={ig:"Instagram",tt:"TikTok",yt:"YouTube",x:"X",li:"LinkedIn"};
  var gercek=!!VERI.son[plat],liste=(VERI.son[plat]||VERI.son.yt||[]),s=null;
  if(vid){(VERI.son.hepsi||[]).forEach(function(o){if(o.id===vid)s=o;});}
  else s=liste[0];
  if(s){
   izl.href=s.sayfa;izl.querySelector("img").src=s.kapak;izl.querySelector("img").alt="";
   izl.querySelector(".iz-k").textContent=vid?"Az önce izlediğiniz video":!gercek?"Son videomuz":(adlar[plat]+"'daki son videomuz").replace("X'daki","X'teki").replace("TikTok'daki","TikTok'taki").replace("LinkedIn'daki","LinkedIn'deki");
   izl.querySelector(".iz-b").textContent=s.baslik;izl.querySelector(".iz-i").textContent=s.ileri;
   izl.hidden=false;
  }
 }
}

/* arama */
var girdi=document.getElementById("ara"),kutu=document.getElementById("ara-sonuc");
if(girdi&&kutu){
 var dizin=[],yuklendi=false;
 function dizinAl(){if(yuklendi)return;yuklendi=true;fetch("/ara.json").then(function(r){return r.json();}).then(function(l){dizin=l.map(function(o){o._s=sade(o.b+" "+o.a+" "+(o.k||""));return o;});if(girdi.value)bul();}).catch(function(){yuklendi=false;});}
 girdi.addEventListener("focus",dizinAl);girdi.addEventListener("pointerenter",dizinAl);
 var secili=-1;
 function bul(){
  var q=sade(girdi.value).trim();kutu.innerHTML="";secili=-1;
  girdi.removeAttribute("aria-activedescendant");if(q.length<2){kutu.hidden=true;girdi.setAttribute("aria-expanded","false");return;}
  var parca=q.split(/\s+/),sn=dizin.map(function(o){var p=0;parca.forEach(function(w){var i=o._s.indexOf(w);if(i<0)p-=100;else p+=(i===0||o._s.charAt(i-1)===" ")?3:1;});if(sade(o.b).indexOf(q)>-1)p+=5;return [p,o];}).filter(function(a){return a[0]>0;}).sort(function(a,b){return b[0]-a[0];}).slice(0,8);
  if(!sn.length){var li=document.createElement("li");li.className="bos";li.textContent="Bulamadım. Başka bir sözcük deneyin: konu, sınıf ya da ürün adı.";kutu.appendChild(li);}
  sn.forEach(function(a,i){var o=a[1],li=document.createElement("li");li.setAttribute("role","none");var l=document.createElement("a");l.href=o.u;l.id="s"+i;l.setAttribute("role","option");
   l.innerHTML='<span class="tur t-'+o.t+'"></span><b></b><span></span>';l.children[0].textContent=o.tl;l.children[1].textContent=o.b;l.children[2].textContent=o.a;li.appendChild(l);kutu.appendChild(li);});
  kutu.hidden=false;girdi.setAttribute("aria-expanded","true");var du=document.getElementById("ara-durum");if(du)du.textContent=sn.length?sn.length+" sonuç":"Sonuç yok";
 }
 girdi.addEventListener("input",bul);
 girdi.addEventListener("keydown",function(e){var l=kutu.querySelectorAll("a");if(!l.length)return;
  if(e.key==="ArrowDown"||e.key==="ArrowUp"){e.preventDefault();secili=(secili+(e.key==="ArrowDown"?1:-1)+l.length)%l.length;l.forEach(function(a,i){a.setAttribute("aria-selected",i===secili);});girdi.setAttribute("aria-activedescendant",l[secili].id);}
  else if(e.key==="Enter"){var a=l[Math.max(secili,0)];if(a){e.preventDefault();location.href=a.href;}}
  else if(e.key==="Escape"){kutu.hidden=true;girdi.removeAttribute("aria-activedescendant");girdi.setAttribute("aria-expanded","false");}});
 girdi.addEventListener("blur",function(){setTimeout(function(){if(!kutu.contains(document.activeElement)){kutu.hidden=true;girdi.setAttribute("aria-expanded","false");}},150);});
 document.addEventListener("click",function(e){if(!e.target.closest(".ara"))kutu.hidden=true;});
}

/* kapı: üç soru */
var kapi=document.getElementById("kapi");
if(kapi){
 var sat=[].slice.call(document.querySelectorAll(".katalog .sat")),kat=document.querySelector(".katalog"),cikti=document.getElementById("kapi-sonuc");
 var sira=sat.slice();
 function seçim(){var d={};["kim","kademe","ihtiyac"].forEach(function(n){var i=kapi.querySelector('input[name="'+n+'"]:checked');d[n]=i?i.value:"";});return d;}
 function uygula(kaydet){
  var d=seçim(),n=0;if(kaydet)sakla("he-kapi",d);
  var bos=!d.kim&&!d.kademe&&!d.ihtiyac;
  var puan=sira.map(function(s,i){var p=0;
   if(d.kademe){var k=(s.dataset.kademe||"").split(" ");if(k.indexOf(d.kademe)>-1||k.indexOf("hepsi")>-1)p+=2;else p-=3;}
   if(d.ihtiyac&&(s.dataset.ihtiyac||"").split(" ").indexOf(d.ihtiyac)>-1)p+=2;
   if(d.kim&&(s.dataset.kim||"").split(" ").indexOf(d.kim)>-1)p+=2;
   if(s.dataset.durum!=="yayinda")p-=3;
   return [p,i,s];});
  if(!bos)puan.sort(function(a,b){return b[0]-a[0]||a[1]-b[1];});else puan.sort(function(a,b){return a[1]-b[1];});
  puan.forEach(function(a){var s=a[2],uy=!bos&&a[0]>=2;s.classList.toggle("uygun",uy);if(s.dataset.durum!=="yayinda")uy=false;var r=s.querySelector(".rozet");if(r)r.hidden=!uy;if(uy)n++;kat.appendChild(s);});
  if(cikti)cikti.textContent=bos?"":(n?n+" ürünü listenin başına aldım."+(d.kademe==="lise"?" Lise için iki araç var: ÇizTahta ve eklentisi.":""):"Bu seçime uyan ürün henüz yok.");
 }
 kapi.addEventListener("change",function(){uygula(true);});
 var tem=kapi.querySelector(".temizle");if(tem)tem.addEventListener("click",function(){kapi.querySelectorAll("input").forEach(function(i){i.checked=false;});uygula(true);});
 var es=oku("he-kapi");if(es){Object.keys(es).forEach(function(n){var i=kapi.querySelector('input[name="'+n+'"][value="'+es[n]+'"]');if(i)i.checked=true;});uygula(false);}
}
})();

(function(){function h(){document.documentElement.classList.add("yazi-hazir");}if(document.fonts&&document.fonts.ready)document.fonts.ready.then(h);setTimeout(h,1200);})();

/* sayfa tahta: kalem, temizle, ses, gizli sürpriz */
(function(){
"use strict";
var sahne=document.querySelector(".sahne"),cv=document.getElementById("tahta");
if(!sahne||!cv||!cv.getContext)return;
var VERI={};try{VERI=JSON.parse(document.getElementById("veri").textContent);}catch(e){}
var azH=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
var cx=cv.getContext("2d"),oran=1,cizgiler=[],simdiki=null;
var bKalem=document.getElementById("t-kalem"),bTem=document.getElementById("t-temizle"),bSes=document.getElementById("t-ses"),ipucu=document.getElementById("t-ipucu");
function boyut(){var r=sahne.getBoundingClientRect();oran=Math.min(window.devicePixelRatio||1,2);cv.width=r.width*oran;cv.height=r.height*oran;yenidenCiz();}
function yol(c){if(c.p.length<2)return;cx.strokeStyle=c.renk;cx.lineWidth=c.k*oran;cx.lineCap="round";cx.lineJoin="round";cx.shadowColor="rgba(217,50,43,.35)";cx.shadowBlur=6*oran;cx.beginPath();cx.moveTo(c.p[0][0]*oran,c.p[0][1]*oran);
 for(var i=1;i<c.p.length-1;i++){var mx=(c.p[i][0]+c.p[i+1][0])/2,my=(c.p[i][1]+c.p[i+1][1])/2;cx.quadraticCurveTo(c.p[i][0]*oran,c.p[i][1]*oran,mx*oran,my*oran);}
 var s=c.p[c.p.length-1];cx.lineTo(s[0]*oran,s[1]*oran);cx.stroke();}
function yenidenCiz(){cx.clearRect(0,0,cv.width,cv.height);cizgiler.forEach(yol);if(simdiki)yol(simdiki);}
window.addEventListener("resize",boyut);if(window.ResizeObserver)new ResizeObserver(boyut).observe(sahne);boyut();

/* ses: kapalı başlar, Web Audio ile üretilir, dosya yok */
var ses=false,ac=null,gurultu=null,kazima=null;
function sesHazir(){if(ac)return;try{ac=new (window.AudioContext||window.webkitAudioContext)();var n=ac.createBuffer(1,ac.sampleRate,ac.sampleRate),d=n.getChannelData(0);for(var i=0;i<d.length;i++)d[i]=Math.random()*2-1;gurultu=n;}catch(e){ac=null;}}
function tik(f){if(!ses||!ac)return;var o=ac.createOscillator(),g=ac.createGain();o.frequency.value=f||660;o.type="triangle";g.gain.setValueAtTime(.08,ac.currentTime);g.gain.exponentialRampToValueAtTime(.0001,ac.currentTime+.12);o.connect(g).connect(ac.destination);o.start();o.stop(ac.currentTime+.13);}
function tebesirBasla(){if(!ses||!ac||kazima)return;var s=ac.createBufferSource();s.buffer=gurultu;s.loop=true;var f=ac.createBiquadFilter();f.type="bandpass";f.frequency.value=2600;f.Q.value=1.4;var g=ac.createGain();g.gain.value=0;s.connect(f).connect(g).connect(ac.destination);s.start();kazima={s:s,g:g};}
function tebesirHiz(v){if(kazima)kazima.g.gain.setTargetAtTime(Math.min(.09,v*.004),ac.currentTime,.03);}
function tebesirBitir(){if(kazima){var k=kazima;kazima=null;k.g.gain.setTargetAtTime(0,ac.currentTime,.04);setTimeout(function(){try{k.s.stop();}catch(e){}},200);}}
function zil(){if(!ses||!ac)return;[523,659,784,1047].forEach(function(f,i){setTimeout(function(){tik(f);},i*90);});}
bSes.addEventListener("click",function(){ses=!ses;bSes.setAttribute("aria-pressed",ses);if(ses){sesHazir();if(ac&&ac.resume)ac.resume();tik(880);}});

/* kalem */
function kalemAc(ac_){sahne.classList.toggle("yaziyor",ac_);bKalem.setAttribute("aria-pressed",ac_);if(ac_){ipucu.textContent="Yazın, çizin. Haftanın atölyesini kalemle çember içine alın.";}tik(ac_?740:520);}
bKalem.addEventListener("click",function(){kalemAc(!sahne.classList.contains("yaziyor"));});
bTem.addEventListener("click",function(){cizgiler=[];simdiki=null;yenidenCiz();var a=sahne.querySelector(".soz-an");if(a)a.remove();sahne.classList.remove("soz-acik");tik(420);});
function nokta(e){var r=cv.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top];}
var son=null;
cv.addEventListener("pointerdown",function(e){if(!sahne.classList.contains("yaziyor"))return;cv.setPointerCapture(e.pointerId);simdiki={renk:"#E0362C",k:e.pointerType==="pen"?4+4*(e.pressure||.5):5,p:[nokta(e)]};son=simdiki.p[0];tebesirBasla();});
cv.addEventListener("pointermove",function(e){if(!simdiki)return;var p=nokta(e),v=Math.hypot(p[0]-son[0],p[1]-son[1]);if(v<1.5)return;simdiki.p.push(p);son=p;tebesirHiz(v);yenidenCiz();});
function bitir(){if(!simdiki)return;var c=simdiki;simdiki=null;cizgiler.push(c);tebesirBitir();yenidenCiz();halkaMi(c);}
cv.addEventListener("pointerup",bitir);cv.addEventListener("pointercancel",bitir);
document.addEventListener("keydown",function(e){if(e.key==="Escape"&&sahne.classList.contains("yaziyor"))kalemAc(false);});

/* şaşırtma: haftanın atölyesini çember içine alan bulur */
function icinde(pt,p){var c=false;for(var i=0,j=p.length-1;i<p.length;j=i++){if(((p[i][1]>pt[1])!==(p[j][1]>pt[1]))&&(pt[0]<(p[j][0]-p[i][0])*(pt[1]-p[i][1])/(p[j][1]-p[i][1])+p[i][0]))c=!c;}return c;}
function halkaMi(c){var n=document.querySelector(".cuma-not");if(!n||c.p.length<12)return;var a=c.p[0],b=c.p[c.p.length-1];var uz=0;for(var i=1;i<c.p.length;i++)uz+=Math.hypot(c.p[i][0]-c.p[i-1][0],c.p[i][1]-c.p[i-1][1]);
 if(Math.hypot(a[0]-b[0],a[1]-b[1])>Math.max(90,uz*.25)||uz<250)return;
 var r=n.getBoundingClientRect(),s=cv.getBoundingClientRect(),m=[r.left+r.width/2-s.left,r.top+r.height/2-s.top];
 if(!icinde(m,c.p))return;
 n.classList.remove("buldu");void n.offsetWidth;n.classList.add("buldu");zil();}

/* gizli sürpriz: T tuşu ya da logoya üç dokunuş, tahtaya bir atasözü yazılır */
var sozler=VERI.soz||[],sira=0;
function sozYaz(){if(!sozler.length)return;var o=sozler[sira++%sozler.length];var eski=sahne.querySelector(".soz-an");if(eski)eski.remove();
 var d=document.createElement("div");d.className="soz-an";var p=document.createElement("p");d.appendChild(p);
 o.s.split("").forEach(function(ch){var sp=document.createElement("span");sp.className="harf";sp.textContent=ch;p.appendChild(sp);});
 sahne.classList.add("soz-acik");var a=document.createElement("a");a.href=o.u;a.textContent="Atasözlerimizi Yaşatalım No. "+o.n+": anlamı";a.style.opacity="0";d.appendChild(a);sahne.appendChild(d);
 var h=p.querySelectorAll(".harf"),i=0;
 if(azH){h.forEach(function(x){x.classList.add("on");});a.style.opacity="1";return;}
 tebesirBasla();tebesirHiz(18);
 (function adim(){if(i<h.length){h[i++].classList.add("on");setTimeout(adim,45);}else{tebesirBitir();a.style.transition="opacity .4s";a.style.opacity="1";}})();}
document.addEventListener("keydown",function(e){var t=e.target;if(t&&(t.tagName==="INPUT"||t.tagName==="TEXTAREA"||t.isContentEditable))return;if((e.key==="t"||e.key==="T")&&!e.ctrlKey&&!e.metaKey&&!e.altKey){var r=sahne.getBoundingClientRect();if(r.bottom>0)sozYaz();}});
var logo=document.querySelector(".ust .logo"),dok=0,zaman=0;
if(logo)logo.addEventListener("click",function(e){var t=Date.now();dok=(t-zaman<600)?dok+1:1;zaman=t;if(dok>=3){e.preventDefault();dok=0;sozYaz();}else if(location.pathname==="/"){e.preventDefault();}});
})();

/* süzgeç */
(function(){var g=document.querySelector(".suzgec");if(!g)return;g.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;g.querySelectorAll("button").forEach(function(x){x.setAttribute("aria-pressed",x===b);});var s=b.dataset.s.split(":");document.querySelectorAll(".kartlar .kart").forEach(function(k){if(!s[0]){k.hidden=false;return;}var l=(k.dataset[s[0]]||"").split(" ");k.hidden=!(l.indexOf(s[1])>-1||l.indexOf("hepsi")>-1);});});})();

/* çanta kurucu */
(function(){var k=document.getElementById("canta-kur");if(!k)return;var V=[];try{V=JSON.parse(document.getElementById("canta-veri").textContent);}catch(e){}
 var KD={ilkokul:["1","2","3","4"],ortaokul:["5","6","7","8"],lise:["9","10","11","12"]},liste=document.getElementById("ck-liste"),durum=document.getElementById("ck-durum");
 function sec(n){var i=k.querySelector('input[name="'+n+'"]:checked');return i?i.value:"";}
 function ciz(){var kim=sec("ck"),kd=sec("kd"),br=sec("br");document.getElementById("ck-kademe").hidden=kim==="herkes";document.getElementById("ck-brans").hidden=kim!=="ogretmen";document.getElementById("ck-not").hidden=kim!=="ogrenci";
  liste.innerHTML="";V.forEach(function(u){if(kim==="ogrenci"&&!u.ogr)return;if(kim!=="herkes"&&kd&&!(u.s.indexOf("hepsi")>-1||u.s.some(function(x){return KD[kd].indexOf(x)>-1;})))return;if(kim==="ogretmen"&&br&&!(u.b.indexOf("hepsi")>-1||u.b.indexOf(br)>-1))return;
   var li=document.createElement("li"),l=document.createElement("label"),c=document.createElement("input");c.type="checkbox";c.checked=true;c.value=u.id;l.appendChild(c);var b=document.createElement("b");b.textContent=u.ad;l.appendChild(b);var s=document.createElement("small");s.textContent=u.sinif+", "+String(u.mb).replace(".",",")+" MB";l.appendChild(s);li.appendChild(l);liste.appendChild(li);});
  if(!liste.children.length){var li=document.createElement("li");li.textContent="Bu seçime uyan dosya henüz yok.";liste.appendChild(li);}}
 k.addEventListener("change",ciz);
 var h=location.hash.replace("#","");var r=k.querySelector('input[name="ck"][value="'+h+'"]');if(r)r.checked=true;ciz();
 document.getElementById("ck-indir").addEventListener("click",function(){var s=[].slice.call(liste.querySelectorAll("input:checked")).map(function(c){return V.filter(function(u){return u.id===c.value;})[0];});if(!s.length){durum.textContent="Önce en az bir dosya seçin.";return;}
  if(!window.fflate){location.href="/canta/Herkese%20Egitim%20cantasi.zip";return;}
  durum.textContent="Hazırlanıyor…";var dosyalar={},enc=new TextEncoder();
  Promise.all(s.map(function(u){return fetch("/indir/"+u.id+".html").then(function(r){return r.arrayBuffer();}).then(function(b){dosyalar[u.dosya]=new Uint8Array(b);});})).then(function(){
   dosyalar["OKU.txt"]=enc.encode("Herkese Eğitim çantası\n\nHer dosya çift tıklayınca tarayıcıda açılır, internet gerekmez.\nGüncel sürümler: "+location.origin+"/\n");
   var z=fflate.zipSync(dosyalar,{level:6}),a=document.createElement("a");a.href=URL.createObjectURL(new Blob([z],{type:"application/zip"}));a.download="Herkese Egitim cantasi.zip";document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove();},2000);durum.textContent="İndirildi: "+s.length+" dosya.";
  }).catch(function(){durum.textContent="İndirilemedi. Hepsini tek seferde indirme bağlantısını deneyin.";});});
})();

/* günün sorusu: tarihe göre her gün başka soru */
(function(){var b=document.getElementById("gunun");if(!b)return;var V={};try{V=JSON.parse(document.getElementById("veri").textContent);}catch(e){}var L=V.gs||[];if(!L.length){b.hidden=true;return;}
 var gun=Math.floor((Date.now()+3*3600e3)/864e5),q=L[gun%L.length],baslik=b.querySelector(".gs-soru"),sec=b.querySelector(".gs-sec"),cev=b.querySelector(".gs-cevap"),say=b.querySelector(".gs-sayac"),sn=say.querySelector("span");
 baslik.textContent=q.s;var bitti=false;
 q.se.forEach(function(t,i){var d=document.createElement("button");d.type="button";d.disabled=true;d.textContent=String.fromCharCode(65+i)+") "+t;d.addEventListener("click",function(){if(bitti)return;bitti=true;d.classList.add("secti");goster(i);});sec.appendChild(d);});
 function goster(i){var bs=sec.querySelectorAll("button");bs.forEach(function(x){x.disabled=true;});bs[q.c].classList.add("dogru");cev.textContent="";var p=document.createElement("span");p.textContent=(i===q.c?"Doğru. ":i===undefined?"":"Cevap "+String.fromCharCode(65+q.c)+". ")+q.a+" ";var a=document.createElement("a");a.href=q.u;a.textContent="Videosu";cev.appendChild(p);cev.appendChild(a);}
 var azH2=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;function n0(){basladi=true;sn.textContent="?";sec.querySelectorAll("button").forEach(function(x){x.disabled=false;});}
 var basladi=false;function basla(){if(basladi)return;basladi=true;say.classList.add("akiyor");var n=3;var t=setInterval(function(){n--;sn.textContent=n>0?n:"?";if(n<=0){clearInterval(t);if(!bitti)sec.querySelectorAll("button").forEach(function(x){x.disabled=false;});}},1000);}
 if(azH2)n0();else if("IntersectionObserver" in window){new IntersectionObserver(function(e,o){if(e[0].isIntersecting){basla();o.disconnect();}},{threshold:.6}).observe(b);}else basla();
})();
/* son ziyaretten beri yeni: yalnız bu tarayıcıda */
(function(){var once=null;try{once=localStorage.getItem("he-son");localStorage.setItem("he-son",new Date().toISOString().slice(0,10));}catch(e){}if(!once)return;
 document.querySelectorAll("[data-tarih]").forEach(function(el){var t=el.dataset.tarih;if(t&&t>once&&t<=new Date().toISOString().slice(0,10)){var s=document.createElement("span");s.className="yeni-etk";s.textContent="Yeni";var h=el.querySelector("h3,figcaption");if(h)h.appendChild(s);}});})();
/* zümrene gönder */
document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("[data-paylas]");if(!b)return;var u=b.dataset.paylas,t=b.dataset.baslik;
 if(navigator.share){navigator.share({title:t,url:u}).catch(function(){});}else if(navigator.clipboard){navigator.clipboard.writeText(u).then(function(){b.textContent="Adres kopyalandı";setTimeout(function(){b.textContent="Zümreye gönderin";},2500);});}});
(function(){var ul=document.querySelector("ul.vg");if(!ul)return;
var kart=[].slice.call(ul.querySelectorAll(".vg-k")),ay=[].slice.call(ul.querySelectorAll(".vg-ay")),q=document.getElementById("vg-q"),say=document.querySelector(".vg-say"),yok=document.querySelector(".vg-yok"),daha=document.querySelector(".vg-daha"),SAY=24,sayfa=1,d={dizi:"",brans:"",q:""};
function n(s){return (s||"").toLocaleLowerCase("tr").replace(/[^\wçğıöşü ]+/g," ");}
var bugun=Date.now();kart.forEach(function(k){var t=k.dataset.tarih;if(t&&bugun-new Date(t+"T00:00:00").getTime()<7*864e5)k.classList.add("yeni");k._a=n(k.dataset.ara);});
function hashOku(){var h=location.hash.replace(/^#/,"");var m=h.match(/^d-([\w-]+)$/);if(m){d.dizi=m[1];return;}h.split("&").forEach(function(p){var kv=p.split("=");if(kv[0]==="dizi"||kv[0]==="brans")d[kv[0]]=decodeURIComponent(kv[1]||"");});}
function hashYaz(){var p=[];if(d.dizi)p.push("dizi="+d.dizi);if(d.brans)p.push("brans="+d.brans);history.replaceState(null,"",p.length?"#"+p.join("&"):location.pathname);}
function dugmeler(){document.querySelectorAll(".vg-cip button").forEach(function(b){b.setAttribute("aria-pressed",String(d[b.dataset.k]===b.dataset.d||(b.dataset.k==="brans"&&false)));});}
function uygula(){var sz=n(d.q).trim().split(/\s+/).filter(Boolean),uy=[];
 kart.forEach(function(k){var ok=(!d.dizi||k.dataset.dizi===d.dizi)&&(!d.brans||(" "+k.dataset.brans+" ").indexOf(" "+d.brans+" ")>-1)&&sz.every(function(s){return k._a.indexOf(s)>-1;});k._u=ok;if(ok)uy.push(k);});
 var sinir=sayfa*SAY;kart.forEach(function(k){k.hidden=!k._u;});uy.forEach(function(k,i){if(i>=sinir)k.hidden=true;});
 ay.forEach(function(a){var x=a.nextElementSibling,var_=false;while(x&&!x.classList.contains("vg-ay")){if(!x.hidden){var_=true;break;}x=x.nextElementSibling;}a.hidden=!var_;});
 var gos=Math.min(uy.length,sinir);say.textContent=(d.dizi||d.brans||sz.length)?(uy.length+" video bulundu."):(kart.length+" video, en yenisi en üstte.");
 yok.hidden=uy.length>0;daha.hidden=uy.length<=sinir;if(!daha.hidden)daha.textContent="Daha fazla göster ("+(uy.length-gos)+")";dugmeler();}
document.querySelectorAll(".vg-cip").forEach(function(g){g.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;var k=b.dataset.k;d[k]=(k==="brans"&&d.brans===b.dataset.d)?"":b.dataset.d;sayfa=1;hashYaz();uygula();});});
var zt;q.addEventListener("input",function(){clearTimeout(zt);zt=setTimeout(function(){d.q=q.value;sayfa=1;uygula();},120);});
daha.addEventListener("click",function(){var ilk=kart.filter(function(k){return k._u&&k.hidden;})[0];sayfa++;uygula();if(ilk){var a=ilk.querySelector("a");if(a)a.focus({preventScroll:true});}});
document.querySelector(".vg-sifir").addEventListener("click",function(){d={dizi:"",brans:"",q:""};q.value="";sayfa=1;hashYaz();uygula();q.focus();});
hashOku();uygula();
/* üç saniye */
var veri=[];try{veri=JSON.parse(document.getElementById("vg-veri").textContent);}catch(e){}
var ac=document.querySelector(".vg-ac"),dl=document.querySelector(".vg-sah");if(!veri.length||!dl||!dl.showModal)return;ac.hidden=false;
var sD=dl.querySelector(".vg-sah-d"),sS=dl.querySelector(".vg-sah-s"),saat=dl.querySelector(".vg-saat"),sN=saat.querySelector("span"),cev=dl.querySelector(".vg-cev"),izle=dl.querySelector(".vg-izle"),git=dl.querySelector(".vg-git"),son=-1,tm=[],sec;
function temiz(){tm.forEach(clearTimeout);tm=[];cev.innerHTML="";cev.hidden=true;}
function yeni(){temiz();var i;do{i=Math.floor(Math.random()*veri.length);}while(veri.length>1&&i===son);son=i;sec=veri[i];
 sD.textContent=sec.d;sS.textContent=sec.s;git.href=sec.u;izle.hidden=true;saat.hidden=false;saat.classList.remove("kos","bitti");sN.textContent="3";void saat.offsetWidth;saat.classList.add("kos");
 [2,1].forEach(function(s,j){tm.push(setTimeout(function(){sN.textContent=s;},(j+1)*1000));});
 tm.push(setTimeout(function(){sN.textContent="?";saat.classList.add("bitti");izle.hidden=false;izle.focus();},3000));}
izle.addEventListener("click",function(){saat.hidden=true;izle.hidden=true;cev.className="vg-cev"+(sec.dik?"":" yat");var f=document.createElement("iframe");f.src="https://www.youtube-nocookie.com/embed/"+encodeURIComponent(sec.id)+"?autoplay=1&rel=0&playsinline=1";f.title=sec.s;f.allow="autoplay; encrypted-media; picture-in-picture";f.allowFullscreen=true;cev.appendChild(f);cev.hidden=false;});
dl.querySelector(".vg-baska").addEventListener("click",yeni);
dl.querySelector(".vg-kapat").addEventListener("click",function(){dl.close();});
dl.addEventListener("close",temiz);dl.addEventListener("click",function(e){if(e.target===dl)dl.close();});
ac.addEventListener("click",function(){dl.showModal();yeni();});
})();
(function(){var z=document.querySelector(".cetvel-z");if(!z)return;
var g=document.querySelector(".hk-suz"),yil=[].slice.call(z.querySelectorAll(".yil"));
g.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;g.querySelectorAll("button").forEach(function(x){x.setAttribute("aria-pressed",String(x===b));});var t=b.dataset.t;
 yil.forEach(function(y){var var_=false;y.querySelectorAll(":scope>ul>li").forEach(function(li){var ok=!t||li.classList.contains("t-"+t);li.hidden=!ok;if(ok)var_=true;});y.hidden=!var_;});cizIp();});
var ilk=z.querySelector(".yil.ilk"),ip=document.createElement("span");ip.className="ip";ip.setAttribute("aria-hidden","true");z.appendChild(ip);
var az=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
function cizIp(){if(!ilk||ilk.hidden){ip.style.display="none";return;}ip.style.display="";var zt=z.getBoundingClientRect(),it=ilk.getBoundingClientRect();var bas=it.top-zt.top+14,boy=zt.height-bas;ip.style.top=bas+"px";ip.style.height=boy+"px";
 if(az){ip.style.setProperty("--ip",1);return;}var g2=(innerHeight*.75-(zt.top+bas))/boy;ip.style.setProperty("--ip",Math.max(0,Math.min(1,g2)).toFixed(3));}
addEventListener("scroll",cizIp,{passive:true});addEventListener("resize",cizIp);cizIp();})();
(function(){var p=document.querySelector(".hk-pano");if(!p)return;
var yil=[].slice.call(document.querySelectorAll(".hk-zaman .yil")),od=p.querySelector(".od"),alt=p.querySelector(".od-alt"),mini=p.querySelector(".mini"),Y0=1995,Y1=2026,simdi=null;
var basamak=[];for(var i=0;i<4;i++){var h=document.createElement("span");h.className="h";var s=document.createElement("span");s.className="s";for(var d=0;d<10;d++){var x=document.createElement("span");x.textContent=d;s.appendChild(x);}h.appendChild(s);od.appendChild(h);basamak.push(s);}
var varY={};yil.forEach(function(y){varY[y.dataset.y]=y;});
for(var k=Y0;k<=Y1;k++){var b=document.createElement("button");b.type="button";b.tabIndex=varY[k]?0:-1;if(varY[k]){b.className="var";b.setAttribute("aria-label",(k==Y1?"Bugün":k)+" yılına git");}b.style.left=((k-Y0+.5)/(Y1-Y0+1)*100)+"%";b.dataset.y=k;b.innerHTML="<i></i>";mini.appendChild(b);
 if((k%5==0&&k>Y0&&k<Y1-2)||k==Y1){var t=document.createElement("span");t.className="yaz"+(k==Y1?" son":"");t.style.left=b.style.left;t.textContent=k==Y1?"bugün":k;mini.appendChild(t);}}
var kalem=document.createElement("span");kalem.className="kalem";mini.appendChild(kalem);
mini.addEventListener("click",function(e){var b=e.target.closest("button.var");if(!b)return;var y=varY[b.dataset.y];if(y)y.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"center"});});
function goster(y){if(y===simdi)return;simdi=y;var n=+y.dataset.y,str=String(n);for(var i=0;i<4;i++)basamak[i].style.transform="translateY(-"+(+str[i])+"em)";od.classList.toggle("bugun",y.classList.contains("simdi"));
 var lis=[].slice.call(y.querySelectorAll(":scope>ul>li")).filter(function(l){return !l.hidden;});var AD={paylasim:"Paylaşım",odul:"Ödül",ulus:"Uluslararası",deger:"Değerlendiricilik",egitim:"Eğitim ve sertifika",gonullu:"Gönüllü"},gor={};alt.innerHTML="";lis.forEach(function(l){var t=(l.className.match(/t-(\w+)/)||[])[1];if(t&&!gor[t]){gor[t]=1;var e=document.createElement("span");e.className="od-t t-"+t;e.textContent=AD[t];alt.appendChild(e);}});
 kalem.style.left=((n-Y0+.5)/(Y1-Y0+1)*100)+"%";yil.forEach(function(x){x.classList.toggle("su",x===y);});}
function bak(){var orta=innerHeight*.45,en=null,ed=1e9;yil.forEach(function(y){if(y.hidden)return;var r=y.getBoundingClientRect();var d=Math.abs(r.top+Math.min(r.height,120)/2-orta);if(d<ed){ed=d;en=y;}});if(en)goster(en);}
addEventListener("scroll",bak,{passive:true});addEventListener("resize",bak);document.querySelector(".hk-suz").addEventListener("click",function(){simdi=null;setTimeout(bak,0);});bak();})();
