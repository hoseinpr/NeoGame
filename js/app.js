/* ===== ابزارها ===== */
const $=(s,c=document)=>c.querySelector(s);
const $$=(s,c=document)=>[...c.querySelectorAll(s)];
const fa=n=>Number(n).toLocaleString('fa-IR');

/* ===== منوی موبایل ===== */
const menuBtn=$('#menuBtn'),links=$('#navLinks');
menuBtn&&menuBtn.addEventListener('click',()=>links.classList.toggle('open'));

/* ===== لینک فعال ===== */
const page=location.pathname.split('/').pop()||'index.html';
$$('[data-nav]').forEach(a=>a.getAttribute('href')===page&&a.classList.add('active'));

/* ===== ریویل اسکرول ===== */
const ob=new IntersectionObserver(es=>es.forEach(e=>e.isIntersecting&&e.target.classList.add('in')),{threshold:.12});
$$('.reveal').forEach(el=>ob.observe(el));

/* ===== شمارنده‌ها ===== */
const co=new IntersectionObserver(es=>es.forEach(e=>{
  if(!e.isIntersecting)return;co.unobserve(e.target);
  const end=+e.target.dataset.count,suf=e.target.dataset.suffix||'';let t=0;
  const iv=setInterval(()=>{t+=end/60;if(t>=end){t=end;clearInterval(iv)}e.target.textContent=fa(Math.round(t))+suf},25);
}),{threshold:.6});
$$('[data-count]').forEach(el=>co.observe(el));

/* ===== توست ===== */
let tId;const toast=m=>{const t=$('#toast');t.textContent=m;t.classList.add('show');clearTimeout(tId);tId=setTimeout(()=>t.classList.remove('show'),2400)};
$$('[data-toast]').forEach(el=>el.addEventListener('click',()=>toast(el.dataset.toast)));

/* ===== سبد خرید ===== */
let cart=0;
$$('[data-add]').forEach(b=>b.addEventListener('click',()=>{cart++;const d=$('#cartDot');d&&(d.textContent=fa(cart));toast('به سبد خرید اضافه شد ✅')}));

/* ===== تب‌ها ===== */
$$('[data-tabs]').forEach(w=>{
  const btns=$$('.tab-btn',w),panes=$$('.tab-pane',w);
  btns.forEach(b=>b.addEventListener('click',()=>{
    btns.forEach(x=>x.classList.remove('active'));panes.forEach(x=>x.classList.remove('active'));
    b.classList.add('active');$('#'+b.dataset.tab,w)?.classList.add('active');
  }));
});

/* ===== آکاردئون ===== */
$$('.acc-head').forEach(h=>h.addEventListener('click',()=>h.parentElement.classList.toggle('open')));

/* ===== چیپ‌ها ===== */
$$('.f-chips').forEach(g=>$$('.chip',g).forEach(c=>c.addEventListener('click',()=>{
  $$('.chip',g).forEach(x=>x.classList.remove('active'));c.classList.add('active');
})));

/* ===== اسلایدر قیمت ===== */
const rng=$('#priceRange');
rng&&rng.addEventListener('input',()=>$('#rangeVal').textContent='تا $'+fa(rng.value));

/* ===== تعداد محصول ===== */
const qEl=$('#qty');let q=1;
$$('.qty button').forEach(b=>b.addEventListener('click',()=>{q=Math.max(1,q+(b.dataset.d?+b.dataset.d:0));qEl&&(qEl.textContent=fa(q))}));

/* ===== محاسبه‌گر بوست ===== */
const BASE=[29,59,99,149,199];
const calcBoost=()=>{
  const g=$('#bGame');if(!g)return;
  const c=+$('input[name=cur]:checked').value,t=+$('input[name=tgt]:checked').value;
  const out=$('#boostPrice'),eta=$('#boostEta');
  if(t<=c){out.textContent='—';eta.textContent='—';return}
  let p=(BASE[t]-BASE[c])*+g.value,d=(t-c)*2;
  if($('#optPriority').checked){p*=1.25;d=Math.max(1,d-1)}
  if($('#optStream').checked)p*=1.1;
  out.textContent='$'+fa(p);eta.textContent=fa(d)+' روز';
};
['#bGame','#optPriority','#optStream'].forEach(s=>{const el=$(s);el&&el.addEventListener('change',calcBoost)});
$$('input[name=cur],input[name=tgt]').forEach(r=>r.addEventListener('change',calcBoost));
calcBoost();

/* ===== فرم‌های نمایشی ===== */
$$('form[data-fake]').forEach(f=>f.addEventListener('submit',e=>{
  e.preventDefault();toast(f.dataset.fake);
  f.dataset.redirect&&setTimeout(()=>location.href=f.dataset.redirect,1100);
}));