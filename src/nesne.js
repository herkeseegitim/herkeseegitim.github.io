'use strict';
// Halka içi nesneler: Cancan stili (boya) ya da kâğıt katlama (kagit). Hepsi kodla; logo yok.
// Fırça ve mürekkep işlevleri Cancan karakter sayfası v10 kaynağından (karakter.html) alındı.
(function(){
const P={gece:'#141A2E',lacivert:'#232C48',mavi:'#34446E',turuncu:'#E57218',isik:'#FFB45E',sari:'#FFD796',krem:'#FAF2E7',bordo:'#7A1F2B',kiremit:'#9A4A2E',hardal:'#C9A227',murekkep:'#1A1626',ahsap:'#8A5A3A'};
let seed=7; const r=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
const mk=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c;};
const N=400;
function firca(c,b,o){ c.save(); c.lineCap='round'; const n=o.n||400; for(let i=0;i<n;i++){ const x=b[0]+r()*b[2], y=b[1]+r()*b[3], a=(o.aci||0)+(r()-.5)*(o.yay==null?.5:o.yay), L=(o.boy||60)*(.4+r()*.9); c.strokeStyle=o.renk[Math.floor(r()*o.renk.length)]; c.globalAlpha=(o.a||.2)*(.35+r()*.65); c.lineWidth=(o.kal||14)*(.4+r()*.9); c.beginPath(); c.moveTo(x,y); c.lineTo(x+Math.cos(a)*L,y+Math.sin(a)*L); c.stroke(); } c.restore(); }
function boya(hedef,yol,taban,o={}){ const t=mk(N,N), c=t.getContext('2d'); c.fillStyle=taban; yol(c); c.fill(); c.globalCompositeOperation='source-atop'; if(o.renk) firca(c,o.kutu||[0,0,N,N],o); if(o.sonra) o.sonra(c); hedef.drawImage(t,0,0); }
function cr(p0,p1,p2,p3,t){ const t2=t*t,t3=t2*t; return [.5*((2*p1[0])+(-p0[0]+p2[0])*t+(2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2+(-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3), .5*((2*p1[1])+(-p0[1]+p2[1])*t+(2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2+(-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)]; }
function murekkep(c,pts,kal=5,renk=P.murekkep,tit=.8){ const q=[pts[0],...pts,pts[pts.length-1]], s=[]; for(let i=0;i<q.length-3;i++) for(let k=0;k<14;k++) s.push(cr(q[i],q[i+1],q[i+2],q[i+3],k/14)); s.push(pts[pts.length-1]);
  c.save(); c.strokeStyle=renk; c.lineCap='round'; for(let i=0;i<s.length-1;i++){ const u=i/(s.length-1), w=kal*(.35+.65*Math.pow(Math.sin(Math.PI*u),.55))*(.85+r()*.3); c.lineWidth=w; c.beginPath(); c.moveTo(s[i][0]+(r()-.5)*tit,s[i][1]+(r()-.5)*tit); c.lineTo(s[i+1][0]+(r()-.5)*tit,s[i+1][1]+(r()-.5)*tit); c.stroke(); } c.restore(); }
function kagitDoku(K,a=.06){ for(let i=0;i<2600;i++){ K.fillStyle=r()<.5?'rgba(255,240,220,'+a+')':'rgba(20,20,40,'+a+')'; K.fillRect(r()*N,r()*N,1+r()*2,1+r()*2); } }
function zemin(K,mod){
  if(mod==='krem'){ // açık kâğıt zemin (B yönü için)
    boya(K,c=>{c.rect(0,0,N,N)},'#F4E6D2',{renk:['#EAD6BC','#FBF1E3','#E9CFB0'],n:260,aci:Math.PI/2,yay:.3,boy:90,kal:22,a:.25}); kagitDoku(K,.05); return; }
  boya(K,c=>{c.rect(0,0,N,N)},P.lacivert,{renk:[P.mavi,P.gece,'#2B3658'],n:300,aci:Math.PI/2,yay:.25,boy:110,kal:26,a:.3});
  const g=K.createRadialGradient(110,70,10,110,70,330); g.addColorStop(0,'rgba(255,180,94,.55)'); g.addColorStop(.45,'rgba(229,114,24,.16)'); g.addColorStop(1,'rgba(20,26,46,0)'); K.fillStyle=g; K.fillRect(0,0,N,N);
  // zemine düşen ışık
  K.save(); K.globalAlpha=.35; boya(K,c=>{c.ellipse(205,330,150,26,0,0,7)},'#3E3A50',{renk:['#55486A','#2E3352'],n:60,aci:0,yay:.2,boy:70,kal:12,a:.3}); K.restore();
}
function toz(K){ for(let i=0;i<40;i++){ const x=40+r()*200,y=30+r()*200; K.fillStyle='rgba(255,215,150,'+(.15+r()*.35)+')'; K.beginPath(); K.arc(x,y,.8+r()*1.6,0,7); K.fill(); } }
function kenarIsik(K,yol){ K.save(); K.strokeStyle='rgba(255,170,80,.55)'; K.lineWidth=6; K.filter='blur(3px)'; yol(K); K.stroke(); K.restore(); }

// ---------- PADLET: mantar pano, üç not kâğıdı, iğne
function padlet(K,mod){ seed=11; zemin(K,mod==='krem'?'krem':'gece');
  K.save(); K.translate(200,205); K.rotate(-.06); K.translate(-200,-205);
  const cer=c=>{c.beginPath(); c.roundRect(78,92,244,206,14)};
  boya(K,cer,P.ahsap,{renk:['#A06A44','#6E4430','#B57A4E'],n:160,aci:0,yay:.2,boy:70,kal:10,a:.35});
  const ic=c=>{c.beginPath(); c.roundRect(94,108,212,174,6)};
  boya(K,ic,'#C79A63',{renk:['#B5854F','#D9AE78','#A87A46'],n:420,aci:.8,yay:3,boy:8,kal:5,a:.5});
  const notlar=[[106,122,82,74,-.08,P.sari],[198,118,88,70,.07,P.krem],[150,190,92,76,-.03,'#F7B98A']];
  notlar.forEach(([x,y,w,h,a,renk],i)=>{ K.save(); K.translate(x+w/2,y+h/2); K.rotate(a); K.translate(-(x+w/2),-(y+h/2));
    K.save(); K.globalAlpha=.35; K.fillStyle='#2A1C14'; K.beginPath(); K.roundRect(x+4,y+6,w,h,3); K.fill(); K.restore();
    boya(K,c=>{c.beginPath();c.roundRect(x,y,w,h,3)},renk,{renk:['rgba(255,255,255,.9)','rgba(200,150,90,.6)'],kutu:[x,y,w,h],n:60,aci:Math.PI/2,yay:.3,boy:30,kal:8,a:.2});
    for(let j=0;j<3;j++) murekkep(K,[[x+12,y+24+j*15],[x+w*.5,y+23+j*15],[x+w-14-(j==2?20:0),y+25+j*15]],2.2,'#5A4A60',.5);
    K.fillStyle=i==1?P.turuncu:P.bordo; K.beginPath(); K.arc(x+w/2,y+9,6,0,7); K.fill(); K.fillStyle='rgba(255,255,255,.6)'; K.beginPath(); K.arc(x+w/2-2,y+7,2,0,7); K.fill();
    K.restore(); });
  murekkep(K,[[80,96],[200,90],[320,96]],2.5,'rgba(26,22,38,.6)');
  K.restore(); kenarIsik(K,c=>{c.beginPath(); c.moveTo(82,300); c.lineTo(80,100); c.lineTo(250,90)}); if(mod!=='krem') toz(K); kagitDoku(K); }

// ---------- WORDWALL: kâğıt çark, ibre
function wordwall(K,mod){ seed=23; zemin(K,mod==='krem'?'krem':'gece');
  const cx=200,cy=205,R=118, renk=[P.turuncu,P.krem,P.mavi,P.isik,'#F6E3C8',P.lacivert];
  // ayak
  boya(K,c=>{c.beginPath(); c.moveTo(cx-14,cy); c.lineTo(cx-46,cy+150); c.lineTo(cx+46,cy+150); c.lineTo(cx+14,cy); c.closePath()},P.ahsap,{renk:['#A06A44','#6E4430'],n:60,aci:Math.PI/2,yay:.2,boy:50,kal:10,a:.35});
  K.save(); K.globalAlpha=.4; K.fillStyle='#0E1222'; K.beginPath(); K.arc(cx+6,cy+8,R+4,0,7); K.fill(); K.restore();
  for(let i=0;i<6;i++){ const a0=-Math.PI/2+i*Math.PI/3+.2, a1=a0+Math.PI/3;
    boya(K,c=>{c.beginPath(); c.moveTo(cx,cy); c.arc(cx,cy,R,a0,a1); c.closePath()},renk[i],{renk:['rgba(255,255,255,.7)','rgba(0,0,0,.25)'],kutu:[cx-R,cy-R,2*R,2*R],n:70,aci:a0+Math.PI/6,yay:.4,boy:60,kal:9,a:.18});
    murekkep(K,[[cx,cy],[cx+Math.cos(a0)*R*.5,cy+Math.sin(a0)*R*.5],[cx+Math.cos(a0)*R,cy+Math.sin(a0)*R]],2.2,'rgba(26,22,38,.75)',.6);
    // dilimde küçük işaret (yazı değil, sayı noktaları)
    const am=(a0+a1)/2; K.fillStyle='rgba(26,22,38,.55)'; for(let k=0;k<=i%3;k++){ K.beginPath(); K.arc(cx+Math.cos(am)*R*(.62+k*.11),cy+Math.sin(am)*R*(.62+k*.11),3.2,0,7); K.fill(); } }
  const pts=[]; for(let i=0;i<=24;i++){ const a=i/24*Math.PI*2; pts.push([cx+Math.cos(a)*(R+1),cy+Math.sin(a)*(R+1)]); } murekkep(K,pts,3.2,'rgba(26,22,38,.85)',.7);
  boya(K,c=>{c.beginPath(); c.arc(cx,cy,14,0,7)},P.krem,{}); murekkep(K,[[cx-13,cy],[cx,cy-14],[cx+13,cy],[cx,cy+14],[cx-13,cy]],2,'rgba(26,22,38,.7)');
  // ibre (üstte)
  boya(K,c=>{c.beginPath(); c.moveTo(cx-16,cy-R-26); c.lineTo(cx+16,cy-R-26); c.lineTo(cx,cy-R+12); c.closePath()},P.krem,{renk:['#EBD9BE'],n:20,a:.3});
  murekkep(K,[[cx-16,cy-R-26],[cx+16,cy-R-26],[cx,cy-R+12],[cx-16,cy-R-26]],2.4,'rgba(26,22,38,.85)');
  kenarIsik(K,c=>{c.beginPath(); c.arc(cx,cy,R+2,Math.PI*1.05,Math.PI*1.6)}); if(mod!=='krem') toz(K); kagitDoku(K); }

// ---------- NOTEBOOKLM: açık defter, kaynak ayracı, ses dalgası
function notebook(K,mod){ seed=37; zemin(K,mod==='krem'?'krem':'gece');
  const sol=c=>{c.beginPath(); c.moveTo(200,150); c.quadraticCurveTo(140,130,72,146); c.lineTo(66,296); c.quadraticCurveTo(140,284,200,302); c.closePath()};
  const sag=c=>{c.beginPath(); c.moveTo(200,150); c.quadraticCurveTo(260,130,328,146); c.lineTo(334,296); c.quadraticCurveTo(260,284,200,302); c.closePath()};
  K.save(); K.globalAlpha=.4; K.fillStyle='#0E1222'; K.beginPath(); K.ellipse(204,306,150,18,0,0,7); K.fill(); K.restore();
  boya(K,c=>{c.beginPath(); c.roundRect(60,150,280,160,10)},'#34446E',{renk:['#2B3658','#45578A'],n:60,a:.3});
  boya(K,sol,P.krem,{renk:['#F1E2CC','#FFF8EE'],kutu:[60,120,150,190],n:80,aci:0,yay:.2,boy:40,kal:10,a:.3});
  boya(K,sag,'#F6EBDB',{renk:['#EAD8BE','#FFF8EE'],kutu:[190,120,150,190],n:80,aci:0,yay:.2,boy:40,kal:10,a:.3});
  for(let j=0;j<6;j++){ const y=170+j*20; murekkep(K,[[86,y+2],[140,y-4],[188,y+2]],1.6,'rgba(52,68,110,.55)',.4); }
  // sağ sayfada üç işaretli satır ve küçük numara
  for(let j=0;j<3;j++){ const y=172+j*30; murekkep(K,[[214,y],[262,y-4],[312,y]],1.8,'rgba(52,68,110,.55)',.4); K.fillStyle=P.turuncu; K.beginPath(); K.arc(318,y-2,5,0,7); K.fill(); }
  murekkep(K,[[200,150],[200,230],[200,302]],2.4,'rgba(26,22,38,.6)');
  murekkep(K,[[72,146],[140,130],[200,150],[260,130],[328,146]],2.6,'rgba(26,22,38,.75)');
  // ayraç
  boya(K,c=>{c.beginPath(); c.moveTo(286,138); c.lineTo(304,138); c.lineTo(304,184); c.lineTo(295,176); c.lineTo(286,184); c.closePath()},P.turuncu,{});
  // defterden yükselen ses dalgası (dinlenen özet)
  const dal=[[0,10],[1,22],[2,36],[3,26],[4,44],[5,30],[6,18],[7,28],[8,12]];
  dal.forEach(([i,h])=>{ const x=140+i*15; murekkep(K,[[x,108-h/2],[x,108],[x,108+h/2]],5.5,i%2?P.isik:P.turuncu,.5); });
  kenarIsik(K,c=>{c.beginPath(); c.moveTo(72,146); c.quadraticCurveTo(140,130,200,150)}); if(mod!=='krem') toz(K); kagitDoku(K); }

// ---------- KAĞIT KATLAMA (C yönü): Gece Kuşu'nun dünyası, düz kâğıt düzlemleri ve kat çizgileri
function kat(K,pts,renk,cizgi){ K.beginPath(); pts.forEach((p,i)=>i?K.lineTo(p[0],p[1]):K.moveTo(p[0],p[1])); K.closePath(); K.fillStyle=renk; K.fill(); K.strokeStyle='rgba(255,255,255,.55)'; K.lineWidth=1.6; K.stroke();
  if(cizgi){ K.save(); K.clip(); K.strokeStyle='rgba(150,120,90,.35)'; K.lineWidth=2; K.setLineDash([9,7]); for(let y=0;y<N;y+=14){ K.beginPath(); K.moveTo(0,y); K.lineTo(N,y-40); K.stroke(); } K.restore(); } }
function kzemin(K){ const g=K.createRadialGradient(200,190,20,200,200,260); g.addColorStop(0,'#2E3A5C'); g.addColorStop(1,'#141A2E'); K.fillStyle=g; K.fillRect(0,0,N,N);
  const h=K.createRadialGradient(200,200,10,200,200,170); h.addColorStop(0,'rgba(255,180,94,.32)'); h.addColorStop(1,'rgba(255,180,94,0)'); K.fillStyle=h; K.fillRect(0,0,N,N); }
function kpadlet(K){ seed=5; kzemin(K);
  kat(K,[[86,110],[316,96],[322,292],[92,304]],'#C9A07A',false);
  kat(K,[[104,130],[192,122],[196,200],[108,206]],'#FFE9C2',true); kat(K,[[192,122],[196,200],[180,190]],'#EBCFA0',false);
  kat(K,[[208,118],[300,126],[294,198],[204,192]],'#FAF2E7',true);
  kat(K,[[150,212],[248,206],[252,284],[154,290]],'#F7C79A',true); kat(K,[[248,206],[252,284],[232,270]],'#E2A774',false);
  [[150,128],[254,124],[200,212]].forEach(([x,y])=>{ K.fillStyle='#E57218'; K.beginPath(); K.arc(x,y,6,0,7); K.fill(); }); }
function kwordwall(K){ seed=6; kzemin(K); const cx=200,cy=200,R=120, renk=['#FAF2E7','#F2D3A8','#FFE9C2','#E8C08E'];
  for(let i=0;i<8;i++){ const a0=-Math.PI/2+i*Math.PI/4, a1=a0+Math.PI/4; kat(K,[[cx,cy],[cx+Math.cos(a0)*R,cy+Math.sin(a0)*R],[cx+Math.cos(a1)*R,cy+Math.sin(a1)*R]],renk[i%4],i%2==0); }
  kat(K,[[cx-14,cy-R-24],[cx+14,cy-R-24],[cx,cy-R+10]],'#E57218',false); K.fillStyle='#E57218'; K.beginPath(); K.arc(cx,cy,9,0,7); K.fill(); }
function knotebook(K){ seed=8; kzemin(K);
  kat(K,[[200,140],[74,126],[68,292],[200,304]],'#FAF2E7',true); kat(K,[[200,140],[326,126],[332,292],[200,304]],'#EBD9BE',true);
  kat(K,[[290,126],[308,126],[308,176],[299,166],[290,176]],'#E57218',false);
  [10,22,36,26,44,30,18,28,12].forEach((h,i)=>{ K.fillStyle=i%2?'#FFB45E':'#E57218'; K.beginPath(); K.roundRect(134+i*15,96-h/2,7,h,3); K.fill(); }); }

window.NESNE={ boya:{padlet,wordwall,notebook}, kagit:{padlet:kpadlet,wordwall:kwordwall,notebook:knotebook} };
window.nesneCiz=function(el){ const t=el.dataset.nesne, s=el.dataset.stil||'boya', z=el.dataset.zemin||'gece'; el.width=N; el.height=N; const K=el.getContext('2d'); NESNE[s][t](K,z==='krem'?'krem':'gece'); };

// ---------- KALEM HALKASI: elle çizilmiş, başı ve sonu üst üste biner (videolardaki turuncu kalem halkası)
window.kalemHalka=function(svg,o){ o=o||{}; const n=o.tohum||1; let s=n*977; const rr=()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};
  const asp=o.en||1, W=100*asp, c=50, cxx=W/2, R=o.r||44, bas=(o.bas==null?-1.9:o.bas), tur=o.tur||1.13, adim=110;
  let d='', pts=[]; for(let i=0;i<=adim;i++){ const u=i/adim, a=bas+u*Math.PI*2*tur; const rad=R*(1+.03*Math.sin(a*2+n)+.022*Math.sin(a*5+n*2)+(.075*(u-.5)))+(rr()-.5)*.35; pts.push([cxx+Math.cos(a)*(rad+(asp-1)*R*1.0)*1.0*(asp>1?1:1.02), c+Math.sin(a)*rad*.985]); }
  pts.forEach((p,i)=>{ d+=(i?'L':'M')+p[0].toFixed(2)+' '+p[1].toFixed(2); });
  const ns='http://www.w3.org/2000/svg'; svg.setAttribute('viewBox','0 0 '+W+' 100'); svg.setAttribute('preserveAspectRatio','none');
  const yol=(w,op)=>{ const p=document.createElementNS(ns,'path'); p.setAttribute('d',d); p.setAttribute('fill','none'); p.setAttribute('stroke',o.renk||'#E57218'); p.setAttribute('stroke-width',w); p.setAttribute('stroke-linecap','round'); p.setAttribute('stroke-linejoin','round'); p.setAttribute('opacity',op); p.setAttribute('vector-effect','non-scaling-stroke'); svg.appendChild(p); return p; };
  if(o.parca){ // C yönü: bölüm sayısı kadar kalem darbesi
    svg.innerHTML=''; const k=o.parca, bos=o.izlenen||0; for(let j=0;j<k;j++){ const a0=-Math.PI/2+j*2*Math.PI/k+.12, a1=a0+2*Math.PI/k-.24; let dd=''; for(let i=0;i<=24;i++){ const a=a0+(a1-a0)*i/24, rad=R*(1+.02*Math.sin(a*3+j))+(rr()-.5)*.3; dd+=(i?'L':'M')+(c+Math.cos(a)*rad).toFixed(2)+' '+(c+Math.sin(a)*rad).toFixed(2); }
      const p=document.createElementNS(ns,'path'); p.setAttribute('d',dd); p.setAttribute('fill','none'); p.setAttribute('stroke-linecap','round'); p.setAttribute('stroke-width', j<bos?2:4); p.setAttribute('vector-effect','non-scaling-stroke'); p.setAttribute('stroke', j<bos?'#B9A893':'#E57218'); svg.appendChild(p); } return; }
  yol(o.kal||4, 1); yol((o.kal||4)*.45, .45).setAttribute('transform','translate(.6 -.5)');
};
})();
