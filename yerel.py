"""out/ -> yerel/: çift tıklayınca açılan önizleme (göreli adresler, CSP yok)"""
import os, re, shutil, json
K=os.path.dirname(os.path.abspath(__file__)); O=os.path.join(K,"out"); Y=os.path.join(K,"yerel")
if os.path.exists(Y): shutil.rmtree(Y)
shutil.copytree(O,Y)
def yol(u,on):
    if u.startswith("//"): return u
    h=""
    if "#" in u: u,h=u.split("#",1); h="#"+h
    q=""
    if "?" in u: u,q=u.split("?",1); q="?"+q
    u=u.lstrip("/")
    if u=="" : u="index.html"
    elif u.endswith("/"): u+="index.html"
    return on+u+q+h
for kok,_,dosyalar in os.walk(Y):
    for f in dosyalar:
        p=os.path.join(kok,f)
        if f.endswith(".html"):
            d=os.path.relpath(kok,Y); derin=0 if d=="." else d.count(os.sep)+1; on="../"*derin or "./"
            s=open(p,encoding="utf-8").read()
            s=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',s)
            s=re.sub(r'(href|src)="(/[^"]*)"',lambda m:f'{m.group(1)}="{yol(m.group(2),on)}"',s)
            s=re.sub(r'"(u|sayfa|kapak)": ?"(/[^"]*)"',lambda m:f'"{m.group(1)}": "{yol(m.group(2),on)}"',s)
            s=re.sub(r'<link rel="preload"[^>]*>','',s)
            s=s.replace("location.pathname===\"/\"","/index\\.html$|\\/$/.test(location.pathname)&&location.pathname.split('/').length<99")
            open(p,"w",encoding="utf-8").write(s)
        elif f.endswith(".css"):
            import base64
            s=open(p,encoding="utf-8").read()
            for fn in ["bg-ext.woff2","bg.woff2"]:
                b64=base64.b64encode(open(os.path.join(O,"fonts",fn),"rb").read()).decode()
                s=s.replace("url(/fonts/"+fn+")","url(data:font/woff2;base64,"+b64+")")
            open(p,"w",encoding="utf-8").write(s)
print("yerel hazır")
