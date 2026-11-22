import re, shutil, sys, os
F = "index.html"
if not os.path.exists(F):
    sys.exit("index.html shu papkada topilmadi. patch.py ni index.html yonida ishga tushiring.")
shutil.copyfile(F, "index.backup.html")
s = open(F, encoding="utf-8").read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n:
        sys.exit("TOPILMADI (%d marta): %s" % (c, old[:70]))
    s = s.replace(old, new)

# 1. har doim qorong'i rejim
rep('<meta name="theme-color" content="#1B5FA8">',
    '<meta name="theme-color" content="#05080f"><script>document.documentElement.dataset.theme="dark"</script>')
rep('(function(){const th=load("sl_theme");if(th)document.documentElement.dataset.theme=th})();',
    'document.documentElement.dataset.theme="dark";')

# 2. CSS
CSS = r'''
/* ===== qora gradient fon ===== */
html{background:#02040a}
body{background:radial-gradient(1100px 650px at 10% -8%,rgba(40,100,200,.30),transparent 60%),radial-gradient(900px 620px at 100% 6%,rgba(18,181,166,.18),transparent 55%),radial-gradient(800px 600px at 50% 110%,rgba(120,70,220,.10),transparent 60%),linear-gradient(165deg,#04070d 0%,#0a1320 48%,#020409 100%);background-attachment:fixed;background-repeat:no-repeat;min-height:100vh}
#theme{display:none}
/* ===== bosh sahifa rasmi ===== */
.hero-photo{position:relative;justify-self:center;width:100%;max-width:400px}
.hero-photo::before{content:"";position:absolute;inset:10% -6% 0;border-radius:40px;background:radial-gradient(circle at 50% 35%,rgba(92,157,232,.38),rgba(18,181,166,.16) 55%,transparent 75%);filter:blur(14px)}
.hero-photo img{position:relative;display:block;width:100%;height:auto;filter:drop-shadow(0 24px 40px rgba(0,0,0,.55))}
.hero-photo .chip{position:absolute;z-index:2;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:8px 12px;font:600 13px var(--font-m);box-shadow:var(--shadow);white-space:nowrap}
@media (max-width:700px){.hero-photo{display:none}}
/* ===== ism-familya bilan ro'yxatdan o'tish ===== */
.reg-card{display:grid;gap:10px;margin-bottom:14px;border-color:color-mix(in srgb,var(--accent) 50%,var(--line));background:linear-gradient(120deg,color-mix(in srgb,var(--accent) 14%,var(--surface)),var(--surface))}
.reg-card .row{display:flex;gap:8px;flex-wrap:wrap}
.reg-card input{flex:1;min-width:200px;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--bg);font-size:16px}
/* ===== savollar: faqat forma ===== */
.fb-grid.fb-solo{grid-template-columns:1fr;max-width:680px;margin-inline:auto}
.fb-alert.fb-err{background:var(--warn-soft);color:var(--warn)}
.fb-submit:disabled{opacity:.6;cursor:wait}
</style>'''
rep('</style>', CSS)

# 3. mahalliy kirish: ism-familya profili
rep('async init(cb){this._cb=cb;const e=load("sl_session");const u=this._users()[e];cb(u?{uid:e,email:e,name:u.name}:null)},',
    'async init(cb){this._cb=cb;let p=null;try{p=JSON.parse(load("sl_profile")||"null")}catch(e){}cb(p&&p.uid&&p.name?{uid:p.uid,name:p.name,email:"",phone:""}:{uid:"bilimhub_user",name:"BilimHub",email:"",guest:true})},')
rep('async signOut(){save("sl_session","");this._cb(null)},',
    'async signOut(){save("sl_profile","");this._cb({uid:"bilimhub_user",name:"BilimHub",email:"",guest:true})},')
rep('const defaultUser = { uid: "bilimhub_user", name: "BilimHub", email: "user@bilimhub.uz" };',
    'const defaultUser = { uid: "bilimhub_user", name: "BilimHub", email: "", guest: true };')

REG = r'''function nameUid(n){let h=5381;for(const c of n.toLowerCase())h=((h<<5)+h+c.charCodeAt(0))>>>0;return "n"+h.toString(36)}
function registerLocal(name){
  const u={uid:nameUid(name),name,email:"",phone:""};
  save("sl_profile",JSON.stringify({uid:u.uid,name}));
  state.prog=mergeProg(readLocalProg(progKey(u)),state.prog);
  state.user=u;persist();render();toast(t("welcome")+", "+name);
}
function regCard(){
  if(!state.user||!state.user.guest) return "";
  const ru=lang==="ru";
  return `<form class="panel reg-card" id="reg-form" novalidate>
    <div><b>${ru?"Сохраняйте прогресс":"Progress va qaydlarni saqlang"}</b>
    <div class="muted" style="font-size:14px;margin-top:2px">${ru?"Введите имя и фамилию — при возвращении уроки продолжатся с того же места.":"Ism va familiyangizni yozing — qaytib kirsangiz darslar o'sha joyidan davom etadi."}</div></div>
    <div class="row"><input id="reg-name" autocomplete="name" maxlength="60" placeholder="${ru?"Имя Фамилия":"Ism Familiya"}"><button class="btn btn-p" type="submit">${ru?"Сохранить":"Saqlash"}</button></div>
    <div class="err" id="reg-err" role="alert"></div></form>`;
}
function viewCourses(){'''
rep('function viewCourses(){', REG)
rep('</h1>${top}', '</h1>${regCard()}${top}')
rep('${gameHTML()}', '${regCard()}${gameHTML()}')
rep('if(g("h-start")) g("h-start").onclick=()=>go("#/courses");',
    'if(g("h-start")) g("h-start").onclick=()=>go("#/courses");\n  { const rf=g("reg-form"); if(rf) rf.onsubmit=e=>{e.preventDefault();const n=g("reg-name").value.trim().replace(/\\s+/g," ");if(n.length<3||n.split(" ").length<2){g("reg-err").textContent=lang==="ru"?"Введите имя и фамилию":"Ism va familiyangizni yozing";return}registerLocal(n)}; }')

# 4. bosh sahifa: rasm + qo'llab-quvvatlash bannerini olib tashlash
HERO = '''<div class="hero-photo">
      <img src="hero.png" alt="BilimHub o'quvchisi" width="700" height="924">
      <span class="chip" style="left:0;top:8%">index.html</span>
      <span class="chip" style="right:0;top:28%;color:var(--teal)">*.pages.dev</span>
      <span class="chip" style="left:4%;bottom:7%;color:var(--gold)">gemini-flash</span>
    </div>'''
s, k = re.subn(r'<div class="star-art" aria-hidden="true">.*?gemini-flash</span>\s*</div>', lambda m: HERO, s, count=1, flags=re.S)
if k != 1: sys.exit("Hero bloki topilmadi")
rep('${donateBanner()}', '')

# 5. Savollar: faqat forma, Telegram botga
a = s.index('function getStoredFeedbacks(){'); b = s.index('function viewProfile(){')
FAQ = r'''function initFeedbackEvents(){
  setTimeout(()=>{
    const form=document.getElementById("fb-form"); if(!form) return;
    const msg=document.getElementById("fb-msg"),cnt=document.getElementById("fb-cnt"),box=document.getElementById("fb-alert"),btn=document.getElementById("fb-submit"),ru=lang==="ru";
    msg.oninput=()=>{cnt.textContent=msg.value.length+"/500"};
    form.onsubmit=async e=>{
      e.preventDefault();
      const name=document.getElementById("fb-name").value.trim(),text=msg.value.trim(),hp=document.getElementById("fb-hp").value;
      if(!name||!text) return;
      if(Date.now()-(+load("sl_fb_t")||0)<30000){toast(ru?"Подождите немного перед следующим сообщением":"Keyingi xabar uchun biroz kuting");return}
      btn.disabled=true;box.hidden=true;
      try{
        const r=await fetch(CONFIG.FEEDBACK_URL||"/api/feedback",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name,text,hp})});
        const j=await r.json().catch(()=>({}));
        if(!r.ok||!j.ok) throw 0;
        save("sl_fb_t",String(Date.now()));
        box.className="fb-alert";box.textContent="✅ "+(ru?"Спасибо! Сообщение отправлено.":"Rahmat! Xabaringiz yuborildi.");
        form.reset();cnt.textContent="0/500";
      }catch(x){
        box.className="fb-alert fb-err";box.textContent="⚠️ "+(ru?"Не удалось отправить. Попробуйте позже.":"Yuborib bo'lmadi. Birozdan keyin qayta urinib ko'ring.");
      }
      box.hidden=false;btn.disabled=false;
    };
  },50);
}

function viewFAQ(){
  initFeedbackEvents();
  const ru=lang==="ru";
  return `
  <div class="fb-container">
    <div class="fb-grid fb-solo">
      <div>
        <span class="fb-badge">✍️ ${ru?"ЗАДАЙТЕ ВОПРОС":"SAVOL QOLDIRING"}</span>
        <h2 class="fb-card-title">${ru?"Ваш вопрос или предложение":"Savol va takliflaringiz biz uchun muhim!"}</h2>
        <p class="muted" style="margin:0 0 16px;font-size:14px">${ru?"Напишите ниже — сообщение придёт администратору в Telegram.":"Quyidagiga yozing — xabaringiz to'g'ridan-to'g'ri administratorga Telegram orqali boradi."}</p>
        <form id="fb-form" autocomplete="off">
          <div class="fb-field"><span class="fb-ico">👤</span><input type="text" id="fb-name" placeholder="${ru?"Ваше имя":"Ismingiz"}" maxlength="50" required></div>
          <div class="fb-field"><span class="fb-ico">💬</span><textarea id="fb-msg" placeholder="${ru?"Ваш вопрос или предложение...":"Savolingiz yoki taklifingiz..."}" maxlength="500" required></textarea><span class="fb-counter" id="fb-cnt">0/500</span></div>
          <input id="fb-hp" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;opacity:0">
          <div class="fb-action-row">
            <button type="submit" class="fb-submit" id="fb-submit">${ru?"Отправить →":"Yuborish →"}</button>
            <span class="fb-security">🔒 ${ru?"Видно только администратору":"Faqat administratorga ko'rinadi"}</span>
          </div>
          <div id="fb-alert" class="fb-alert" hidden></div>
        </form>
      </div>
    </div>
  </div>

  <div id="faq-accordion" style="max-width:820px;margin:32px auto 0">
    <h2 style="font-size:clamp(22px,3.6vw,28px);margin-bottom:6px">${t("faqT")}</h2>
    <p class="muted" style="margin:0 0 18px">${t("faqSub")}</p>
    ${FAQ.map(f=>`<details><summary>${esc(L(f.q))}</summary><p>${esc(L(f.a))}</p></details>`).join("")}
    <div class="panel" style="margin-top:20px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;justify-content:space-between">
      <span>${t("askTg")}</span>
      <a class="btn-tg-hdr" href="${esc(CONFIG.TELEGRAM)}" target="_blank" rel="noopener">${I.tg} Telegram</a>
    </div>
  </div>`;
}

'''
s = s[:a] + FAQ + s[b:]

open(F, "w", encoding="utf-8").write(s)
print("Tayyor! Zaxira nusxa: index.backup.html")
