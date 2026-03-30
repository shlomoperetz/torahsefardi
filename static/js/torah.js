// TORAH.JS

// ── Auto-hide header: ocultar al bajar, mostrar al subir ──
(function(){
  var hdr=document.getElementById('site-header');
  if(!hdr)return;
  var lastY=0;
  window.addEventListener('scroll',function(){
    var y=window.scrollY||window.pageYOffset||0;
    if(y<=10){
      hdr.classList.remove('hide-header');
    } else if(y<lastY-4){
      hdr.classList.remove('hide-header');
    } else if(y>lastY+4){
      hdr.classList.add('hide-header');
    }
    lastY=y;
  },{passive:true});
})();

(function(){
  var t=localStorage.getItem('theme');
  var dark=t?t==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.classList.toggle('dark-mode',dark);
  document.documentElement.classList.toggle('light-mode',!dark);
  var lang=localStorage.getItem('torah-lang')||'es';
  document.documentElement.classList.toggle('lang-he',lang==='he');
})();

function toggleDarkMode(){
  var r=document.documentElement;
  var d=r.classList.toggle('dark-mode');
  r.classList.toggle('light-mode',!d);
  localStorage.setItem('theme',d?'dark':'light');
  var s=document.getElementById('iconSun'),m=document.getElementById('iconMoon');
  if(s)s.style.display=d?'':'none';
  if(m)m.style.display=d?'none':'';
}

function adjustFont(n){
  var r=document.documentElement;
  var c=parseInt(getComputedStyle(r).getPropertyValue('--font'))||30;
  var v=Math.min(Math.max(c+n*2,16),36);
  r.style.setProperty('--font',v+'px');
  localStorage.setItem('fontSize',v);
}
function toggleFontMenu(){
  var p=document.querySelector('.font-popover');
  if(p)p.classList.toggle('open');
}
document.addEventListener('click',function(e){
  if(!e.target.closest('.font-popover-wrap')){
    var p=document.querySelector('.font-popover');
    if(p)p.classList.remove('open');
  }
});

var VS={he:true,es:true};
function toggleView(k){
  var active=Object.keys(VS).filter(function(x){return VS[x];});
  if(VS[k]&&active.length===1)return;
  VS[k]=!VS[k];
  applyView();
  localStorage.setItem('VS_torah',JSON.stringify(VS));
}
function applyView(){
  document.querySelectorAll('.verse-he').forEach(function(el){el.style.display=VS.he?'':'none';});
  document.querySelectorAll('.verse-es').forEach(function(el){el.style.display=VS.es?'':'none';});
  var bh=document.getElementById('btnHe'),be=document.getElementById('btnEs');
  if(bh)bh.classList.toggle('active',VS.he);
  if(be)be.classList.toggle('active',VS.es);
}

// ── i18n ──
var CURRENT_LANG = 'es';
var STRINGS = {
  es: {
    brand_title:  'Torah Sefardí',
    nav_home:     'Inicio',
    nav_torah:    'Torá',
    nav_parashot: 'Parashot',
    nav_haftarot: 'Haftarot',
    nav_neviim:   "Nevi'im",
    nav_ketuvim:  'Ketuvim',
    search_ph:    'Buscar libro o capítulo…',
    no_results:  'Sin resultados',
    landing_desc:'La Torá en hebreo con traducción al español sefardí',
    tile1_label: 'Empezar desde el principio',
    tile1_sub:   'Bereshit 1:1 — En el principio…',
    tile_parasha_label: 'Parashá de la semana',
    tile_parasha_sub: 'Las 54 porciones semanales',
    tile2_label: 'Los cinco libros',
    tile2_sub:   'Bereshit · Shemot · Vayikrá · Bamidbar · Devarim',
    ch_prev: function(n){ return '← Cap. '+n; },
    ch_next: function(n){ return 'Cap. '+n+' →'; },
  },
  he: {
    brand_title:  'תּוֹרָה סְפָרַדִּי',
    nav_home:     'בית',
    nav_torah:    'תּוֹרָה',
    nav_parashot: 'פָּרָשִׁיּוֹת',
    nav_haftarot: 'הַפְטָרוֹת',
    nav_neviim:   'נְבִיאִים',
    nav_ketuvim:  'כְּתוּבִים',
    search_ph:    'חפש ספר או פרק…',
    no_results:  'אין תוצאות',
    landing_desc:'התורה בעברית עם תרגום לספרדית',
    tile1_label: 'התחל מהתחלה',
    tile1_sub:   'בראשית א:א — בְּרֵאשִׁית…',
    tile_parasha_label: 'פרשת השבוע',
    tile_parasha_sub: '54 פרשיות התורה',
    tile2_label: 'חמשה חומשי תורה',
    tile2_sub:   'בְּרֵאשִׁית · שְׁמוֹת · וַיִּקְרָא · בְּמִדְבַּר · דְּבָרִים',
    ch_prev: function(n){ return 'פרק '+n+' →'; },
    ch_next: function(n){ return '← פרק '+n; },
  }
};

function applyStrings(lang){
  var s=STRINGS[lang]||STRINGS['es'];
  // Elementos con data-i18n
  document.querySelectorAll('[data-i18n]').forEach(function(el){
    var k=el.dataset.i18n;
    if(s[k]&&typeof s[k]==='string')el.textContent=s[k];
  });
  // Placeholder buscador
  var inp=document.getElementById('searchInput');
  if(inp)inp.placeholder=s.search_ph;
  // Etiqueta de capítulo (estático)
  document.querySelectorAll('.chapter-label[data-ch]').forEach(function(el){
    el.textContent=(lang==='he'?el.dataset.bookHe:el.dataset.bookEs)+' '+el.dataset.ch;
  });
  // Nav prev / next (estático)
  document.querySelectorAll('[data-nav="prev"]').forEach(function(el){
    el.innerHTML=s.ch_prev(el.dataset.n);
  });
  document.querySelectorAll('[data-nav="next"]').forEach(function(el){
    el.innerHTML=s.ch_next(el.dataset.n);
  });
  // Nav lista de libro
  document.querySelectorAll('.nav-list[data-book-es]').forEach(function(el){
    el.textContent=lang==='he'?el.dataset.bookHe:el.dataset.bookEs;
  });
  // Dirección página
  document.documentElement.classList.toggle('lang-he',lang==='he');
}

function toggleLangMenu(){
  var m=document.getElementById('lang-menu');
  if(m)m.classList.toggle('open');
}
document.addEventListener('click',function(e){
  if(!e.target.closest('.tnav-lang-wrap')){
    var m=document.getElementById('lang-menu');
    if(m)m.classList.remove('open');
  }
});
function setLang(lang){
  CURRENT_LANG=lang;
  var btn=document.getElementById('btn-lang');
  document.querySelectorAll('.tnav-lang-opt').forEach(function(o){
    o.classList.toggle('active',o.dataset.lang===lang);
  });
  if(btn)btn.textContent=lang==='he'?'עב':lang.toUpperCase();
  localStorage.setItem('torah-lang',lang);
  if(lang==='he'){VS.he=true;VS.es=false;}
  else{VS.he=true;VS.es=true;}
  applyStrings(lang);
  applyView();
  var m=document.getElementById('lang-menu');
  if(m)m.classList.remove('open');
}
function initLang(){
  var lang=localStorage.getItem('torah-lang')||'es';
  CURRENT_LANG=lang;
  var btn=document.getElementById('btn-lang');
  if(btn)btn.textContent=lang==='he'?'עב':lang.toUpperCase();
  document.querySelectorAll('.tnav-lang-opt').forEach(function(o){
    o.classList.toggle('active',o.dataset.lang===lang);
    o.addEventListener('click',function(){setLang(o.dataset.lang);});
  });
  if(lang==='he'){VS.he=true;VS.es=false;}
  applyStrings(lang);
}

var SI=null;
function openSearch(){
  var o=document.getElementById('searchOverlay'),p=document.getElementById('searchPanel');
  if(o)o.style.display='';
  if(p)p.style.display='';
  setTimeout(function(){var i=document.getElementById('searchInput');if(i)i.focus();},50);
  if(!SI)fetch('/index.json').then(function(r){return r.json();}).then(function(d){SI=d;}).catch(function(){SI=[];});
}
function closeSearch(){
  var o=document.getElementById('searchOverlay'),p=document.getElementById('searchPanel');
  if(o)o.style.display='none';
  if(p)p.style.display='none';
  var i=document.getElementById('searchInput');if(i)i.value='';
  var r=document.getElementById('searchResults');if(r)r.innerHTML='';
}
function doSearch(q){
  var r=document.getElementById('searchResults');
  if(!q){if(r)r.innerHTML='';return;}
  if(!SI){setTimeout(function(){doSearch(q);},200);return;}
  var ql=q.toLowerCase().trim(),isNum=!isNaN(ql)&&ql!=='';
  var hits=SI.filter(function(p){
    if(isNum)return String(p.chapter).startsWith(ql);
    return(p.book_es&&p.book_es.toLowerCase().includes(ql))||(p.es_preview&&p.es_preview.toLowerCase().includes(ql));
  }).slice(0,15);
  if(r)r.innerHTML=hits.length
    ?hits.map(function(p){
        return '<a class="search-result-item" href="'+p.url+'">'
          +'<span class="search-result-num">'+p.book_es+' '+p.chapter+'</span>'
          +'<span class="search-result-title">'+(p.es_preview||'').slice(0,55)+'</span></a>';
      }).join('')
    :'<div style="padding:14px;opacity:0.5;font-size:0.9em">'+(STRINGS[CURRENT_LANG]||STRINGS.es).no_results+'</div>';
}
document.addEventListener('keydown',function(e){
  if(e.key==='Escape')closeSearch();
  if((e.metaKey||e.ctrlKey)&&e.key==='k'){e.preventDefault();openSearch();}
});

// INFINITE SCROLL
var BOOK_CHAPTERS={
  bereshit:50,shemot:40,vayikra:27,bamidbar:36,devarim:34,
  yehoshua:24,shoftim:21,shmuel1:31,shmuel2:24,melakhim1:22,melakhim2:25,
  yeshayahu:66,yirmiyahu:52,yehezkel:48,hoshea:14,yoel:4,amos:9,
  ovadyah:1,yonah:4,mikhah:7,nahum:3,havakkuk:3,tzefanyah:3,
  haggai:2,zekharyah:14,malakhi:3,
  tehilim:150,mishlei:31,iyov:42,shir_hashirim:8,rut:4,ekhah:5,
  kohelet:12,esther:10,daniel:12,ezra:10,nekhemyah:13,
  divreiy_hayamim1:29,divreiy_hayamim2:36
};
var scrollState={section:'torah',book:null,bookEs:null,bookHe:null,nextChapter:null,prevChapter:null,maxChapters:0,loadingNext:false,loadingPrev:false};
var chObs=null;

function initChapterObserver(){
  if(!('IntersectionObserver' in window))return;
  chObs=new IntersectionObserver(function(entries){
    var best=null;
    entries.forEach(function(e){if(e.isIntersecting&&(!best||e.intersectionRatio>best.intersectionRatio))best=e;});
    if(best){
      var ch=best.target.dataset.chapter,book=best.target.dataset.book;
      var url='/'+scrollState.section+'/'+book+'/'+String(ch).padStart(3,'0')+'/';
      if(location.pathname!==url){history.replaceState(null,'',url);document.title=(scrollState.bookEs||book)+' '+ch+' | Torah Sefardi';}
      if(scrollState.section==='torah')updateParashaCrumb(book, parseInt(ch,10));
    }
  },{threshold:0.15,rootMargin:'-80px 0px -40% 0px'});
  document.querySelectorAll('.chapter-section').forEach(function(s){chObs.observe(s);});
}

function initScroll(){
  window.addEventListener('scroll',function(){
    var y=window.scrollY||window.pageYOffset;
    var dh=document.documentElement.scrollHeight;
    var wh=window.innerHeight;
    if(y+wh>=dh-800&&!scrollState.loadingNext)loadNextChapter();
    if(y<=400&&!scrollState.loadingPrev)loadPrevChapter();
  },{passive:true});
}

function buildVerse(v){
  var h='<div class="verse" id="v'+v.num+'">'
    +'<div class="verse-he"><sup class="verse-num">'+v.num+'</sup>'+v.he+'</div>';
  if(v.es)h+='<div class="verse-es"><sup class="verse-num-es">'+v.num+'</sup>'+v.es+'</div>';
  return h+'</div>';
}

function buildSection(data,ch){
  var s=STRINGS[CURRENT_LANG]||STRINGS['es'];
  var bkEs=data.book_es||scrollState.bookEs||'';
  var bkHe=data.book_he||scrollState.bookHe||'';
  var bk=CURRENT_LANG==='he'?bkHe:bkEs;
  var prev=ch>1?ch-1:null,next=ch<scrollState.maxChapters?ch+1:null;
  var base=scrollState.book;
  var sec=scrollState.section||'torah';
  return '<div class="chapter-header">'
    +'<div class="chapter-label" data-ch="'+ch+'" data-book-es="'+bkEs+'" data-book-he="'+bkHe+'">'+bk+' '+ch+'</div>'
    +'<div class="chapter-he-title">'+(data.title_he||'')+'</div></div>'
    +'<div class="torah-verses">'+data.verses.map(buildVerse).join('')+'</div>'
    +'<nav class="torah-nav">'
    +(prev?'<a href="/'+sec+'/'+base+'/'+String(prev).padStart(3,'0')+'/" class="nav-prev" data-nav="prev" data-n="'+prev+'">'+s.ch_prev(prev)+'</a>':'<span></span>')
    +'<a href="/'+sec+'/'+base+'/" class="nav-list" data-book-es="'+bkEs+'" data-book-he="'+bkHe+'">'+bk+'</a>'
    +(next?'<a href="/'+sec+'/'+base+'/'+String(next).padStart(3,'0')+'/" class="nav-next" data-nav="next" data-n="'+next+'">'+s.ch_next(next)+'</a>':'<span></span>')
    +'</nav>';
}

async function loadNextChapter(){
  if(scrollState.loadingNext)return;
  if(!scrollState.nextChapter||scrollState.nextChapter>scrollState.maxChapters)return;
  scrollState.loadingNext=true;
  var dots=document.getElementById('loadingDots');
  if(dots)dots.style.display='flex';
  try{
    var ch=scrollState.nextChapter;
    var res=await fetch('/'+scrollState.section+'/'+scrollState.book+'/'+String(ch).padStart(3,'0')+'/index.json');
    if(!res.ok)throw new Error(res.status);
    var data=await res.json();
    var feed=document.getElementById('chapters-feed');
    var sentinel=document.getElementById('scroll-sentinel');
    var sec=document.createElement('section');
    sec.className='chapter-section';
    sec.dataset.book=scrollState.book;
    sec.dataset.chapter=ch;
    sec.id='ch'+ch;
    sec.innerHTML=buildSection(data,ch);
    feed.insertBefore(sec,sentinel);
    applyView();
    if(chObs)chObs.observe(sec);
    scrollState.nextChapter++;
  }catch(e){console.warn('next:',e);}
  if(dots)dots.style.display='none';
  scrollState.loadingNext=false;
}

async function loadPrevChapter(){
  if(scrollState.loadingPrev)return;
  if(!scrollState.prevChapter||scrollState.prevChapter<1)return;
  scrollState.loadingPrev=true;
  try{
    var ch=scrollState.prevChapter;
    var res=await fetch('/'+scrollState.section+'/'+scrollState.book+'/'+String(ch).padStart(3,'0')+'/index.json');
    if(!res.ok)throw new Error(res.status);
    var data=await res.json();
    var feed=document.getElementById('chapters-feed');
    var stTop=document.getElementById('scroll-sentinel-top');
    var sec=document.createElement('section');
    sec.className='chapter-section';
    sec.dataset.book=scrollState.book;
    sec.dataset.chapter=ch;
    sec.id='ch'+ch;
    sec.innerHTML=buildSection(data,ch);
    var ph=feed.scrollHeight;
    stTop.parentNode.insertBefore(sec,stTop.nextSibling);
    window.scrollBy(0,feed.scrollHeight-ph);
    applyView();
    if(chObs)chObs.observe(sec);
    scrollState.prevChapter--;
  }catch(e){console.warn('prev:',e);}
  scrollState.loadingPrev=false;
}

function initTorahPage(){
  var fs=localStorage.getItem('fontSize');
  if(fs)document.documentElement.style.setProperty('--font',fs+'px');
  var dark=document.documentElement.classList.contains('dark-mode');
  var s=document.getElementById('iconSun'),m=document.getElementById('iconMoon');
  if(s)s.style.display=dark?'':'none';
  if(m)m.style.display=dark?'none':'';
  var sv=localStorage.getItem('VS_torah');
  if(sv){try{VS=JSON.parse(sv);}catch(e){}}
  initLang();
  applyView();
  var ctx=window.TORAH_CTX;
  if(typeof ctx==='string'){try{ctx=JSON.parse(ctx);}catch(e){ctx=null;}}
  if(ctx&&ctx.book){
    scrollState.section=ctx.section||'torah';
    scrollState.book=ctx.book;
    scrollState.bookEs=ctx.bookEs;
    scrollState.bookHe=ctx.bookHe||'';
    scrollState.maxChapters=BOOK_CHAPTERS[ctx.book]||50;
    scrollState.nextChapter=parseInt(ctx.chapter,10)+1;
    scrollState.prevChapter=parseInt(ctx.chapter,10)-1;
    initChapterObserver();
    initScroll();
    initCrumb(ctx);
  }
}

function initCrumb(ctx){
  var crumb=document.getElementById('topbar-crumb');
  if(!crumb)return;
  var sec=ctx.section||'torah';
  var secLabels={torah:'Torá',neviim:"Nevi'im",ketuvim:'Ketuvim'};
  var secLabel=secLabels[sec]||sec;
  var bookLabel=CURRENT_LANG==='he'?(ctx.bookHe||ctx.bookEs):ctx.bookEs;
  crumb.innerHTML=
    '<a href="/'+sec+'/">'+secLabel+'</a>'
    +'<span class="crumb-sep">›</span>'
    +'<a href="/'+sec+'/'+ctx.book+'/">'+bookLabel+'</a>';
  // Add parasha context if available
  if(window.PARASHA_MAP&&ctx.book&&sec==='torah'){
    updateParashaCrumb(ctx.book, parseInt(ctx.chapter,10)||1);
  }
}

function updateParashaCrumb(libro, ch){
  var crumb=document.getElementById('topbar-crumb');
  if(!crumb||!window.PARASHA_MAP)return;
  var map=window.PARASHA_MAP[libro];
  if(!map)return;
  var result=null;
  for(var i=0;i<map.length;i++){
    var e=map[i];
    if(e.ch<ch||(e.ch===ch)){result=e;}
    else break;
  }
  if(!result)return;
  // Remove existing parasha crumb if any
  var existing=crumb.querySelector('.crumb-sep-parasha');
  if(existing){existing.nextSibling&&crumb.removeChild(existing.nextSibling);crumb.removeChild(existing);}
  var existing2=crumb.querySelector('.crumb-parasha');
  if(existing2)crumb.removeChild(existing2);
  var existing3=crumb.querySelector('.crumb-aliya');
  if(existing3)crumb.removeChild(existing3);
  var sep=document.createElement('span');
  sep.className='crumb-sep crumb-sep-parasha';
  sep.textContent='›';
  var aParasha=document.createElement('a');
  aParasha.className='crumb-parasha';
  aParasha.href=result.parasha_url;
  aParasha.textContent=result.nombre;
  var aAliya=document.createElement('span');
  aAliya.className='crumb-aliya';
  aAliya.textContent=' '+result.aliya_num_he;
  crumb.appendChild(sep);
  crumb.appendChild(aParasha);
  crumb.appendChild(aAliya);
}

// Parasha de la semana
function getCurrentWeekParasha(){
  if(!window.PARASHA_SCHEDULE)return null;
  var today=new Date();
  today.setHours(12,0,0,0);
  var result=null;
  for(var i=0;i<PARASHA_SCHEDULE.length;i++){
    var entry=PARASHA_SCHEDULE[i];
    var d=new Date(entry[0]+'T12:00:00');
    if(d<=today&&entry[1])result=entry[1];
  }
  return result;
}

function highlightCurrentParasha(){
  var slug=getCurrentWeekParasha();
  if(!slug)return;
  // Highlight on parasha list page
  var cards=document.querySelectorAll('.parasha-card[data-slug]');
  cards.forEach(function(card){
    if(card.dataset.slug===slug){
      card.classList.add('is-current');
      var badge=document.createElement('span');
      badge.className='parasha-current-badge';
      badge.textContent='Esta semana';
      card.appendChild(badge);
    }
  });
  // Update "Esta semana" landing card
  if(window.PARASHA_INFO&&PARASHA_INFO[slug]){
    var info=PARASHA_INFO[slug];
    var elHe=document.getElementById('esm-he');
    var elNombre=document.getElementById('esm-nombre');
    var elParasha=document.getElementById('esm-parasha-link');
    var elHaftara=document.getElementById('esm-haftara-link');
    if(elHe)elHe.textContent=info.nombre_he;
    if(elNombre)elNombre.textContent=info.nombre;
    if(elParasha)elParasha.href=info.url;
    if(elHaftara)elHaftara.href=info.url+'haftara/';
  }
}

// Aliyah verse loader
async function fetchAliyaVerses(ctx){
  var verses=[];
  var ch=ctx.ch_start;
  while(ch<=ctx.ch_end){
    var url='/torah/'+ctx.libro+'/'+String(ch).padStart(3,'0')+'/index.json';
    try{
      var res=await fetch(url);
      if(!res.ok)break;
      var data=await res.json();
      if(!data||!data.verses)break;
      var chV=data.verses;
      if(ch===ctx.ch_start&&ch===ctx.ch_end){
        chV=chV.filter(function(v){return v.num>=ctx.v_start&&v.num<=ctx.v_end;});
      }else if(ch===ctx.ch_start){
        chV=chV.filter(function(v){return v.num>=ctx.v_start;});
      }else if(ch===ctx.ch_end){
        chV=chV.filter(function(v){return v.num<=ctx.v_end;});
      }
      verses=verses.concat(chV);
    }catch(e){console.warn('aliya fetch ch'+ch,e);}
    ch++;
  }
  return verses;
}

async function initAliyaPage(){
  var ctx=window.ALIYA_CTX;
  if(!ctx)return;
  if(typeof ctx==='string'){try{ctx=JSON.parse(ctx);}catch(e){ctx=null;}}
  if(!ctx)return;
  // Update topbar crumb for aliyah
  var crumb=document.getElementById('topbar-crumb');
  if(crumb){
    crumb.innerHTML=
      '<a href="/parashot/">Parashot</a>'
      +'<span class="crumb-sep">›</span>'
      +'<a href="'+ctx.parasha_url+'">'+ctx.parasha+'</a>'
      +'<span class="crumb-sep">›</span>'
      +'<span class="crumb-current">'+ctx.aliya_num_he+'</span>';
  }
  // Load verses
  var container=document.getElementById('aliya-verses');
  if(!container)return;
  var verses=await fetchAliyaVerses(ctx);
  if(!verses.length){
    container.innerHTML='<div style="padding:2rem;opacity:0.5;text-align:center;font-family:var(--ui-font);font-size:0.6em">No se pudieron cargar los versículos.</div>';
    return;
  }
  var html='<div class="torah-verses">';
  verses.forEach(function(v){html+=buildVerse(v);});
  html+='</div>';
  container.innerHTML=html;
  applyView();
}

if(document.readyState==='loading'){
  document.addEventListener('DOMContentLoaded',initTorahPage);
}else{
  initTorahPage();
}

// Haftara verse loader
async function initHaftaraPage(){
  var ctx=window.HAFTARA_CTX;
  if(typeof ctx==='string'){try{ctx=JSON.parse(ctx);}catch(e){ctx=null;}}
  if(!ctx||!ctx.ranges)return;

  // Update topbar crumb
  var crumb=document.getElementById('topbar-crumb');
  if(crumb){
    crumb.innerHTML=
      '<a href="/parashot/">Parashot</a>'
      +'<span class="crumb-sep">›</span>'
      +'<a href="'+ctx.parasha_url+'">'+ctx.parasha+'</a>'
      +'<span class="crumb-sep">›</span>'
      +'<span class="crumb-current">Haftará</span>';
  }

  var container=document.getElementById('haftara-verses');
  if(!container)return;

  // Collect unique chapters per libro
  var toFetch={};
  ctx.ranges.forEach(function(r){
    if(!toFetch[r.libro])toFetch[r.libro]=[];
    for(var ch=r.ch_start;ch<=r.ch_end;ch++){
      if(toFetch[r.libro].indexOf(ch)===-1)toFetch[r.libro].push(ch);
    }
  });

  // Fetch all needed chapters
  var chData={};
  var libros=Object.keys(toFetch);
  for(var li=0;li<libros.length;li++){
    var libro=libros[li];
    var chs=toFetch[libro];
    for(var ci=0;ci<chs.length;ci++){
      var ch=chs[ci];
      var key=libro+'_'+ch;
      var url='/neviim/'+libro+'/'+String(ch).padStart(3,'0')+'/index.json';
      try{
        var res=await fetch(url);
        if(res.ok){var d=await res.json();chData[key]=d.verses||[];}
      }catch(e){console.warn('haftara fetch',url,e);}
    }
  }

  // Build verse HTML from ranges in order
  var html='<div class="torah-verses">';
  ctx.ranges.forEach(function(r){
    for(var ch=r.ch_start;ch<=r.ch_end;ch++){
      var verses=chData[r.libro+'_'+ch]||[];
      var vStart=(ch===r.ch_start)?r.v_start:1;
      var vEnd=(ch===r.ch_end)?r.v_end:9999;
      verses.forEach(function(v){
        if(v.num>=vStart&&v.num<=vEnd)html+=buildVerse(v);
      });
    }
  });
  html+='</div>';

  if(html==='<div class="torah-verses"></div>'){
    container.innerHTML='<div style="padding:2rem;opacity:0.5;text-align:center;font-family:var(--ui-font);font-size:0.6em">No se pudieron cargar los versículos.</div>';
  }else{
    container.innerHTML=html;
    applyView();
  }
}

// Run parasha de la semana highlight + aliyah/haftara page init after DOM ready
function initParashaFeatures(){
  highlightCurrentParasha();
  if(window.ALIYA_CTX)initAliyaPage();
  if(window.HAFTARA_CTX)initHaftaraPage();
}
if(document.readyState==='loading'){
  document.addEventListener('DOMContentLoaded',initParashaFeatures);
}else{
  initParashaFeatures();
}
