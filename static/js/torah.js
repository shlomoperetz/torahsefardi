// TORAH.JS
(function(){
  var t=localStorage.getItem('theme');
  var dark=t?t==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.classList.toggle('dark-mode',dark);
  document.documentElement.classList.toggle('light-mode',!dark);
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
  var c=parseInt(getComputedStyle(r).getPropertyValue('--font'))||22;
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
    :'<div style="padding:14px;opacity:0.5;font-size:0.9em">Sin resultados</div>';
}
document.addEventListener('keydown',function(e){
  if(e.key==='Escape')closeSearch();
  if((e.metaKey||e.ctrlKey)&&e.key==='k'){e.preventDefault();openSearch();}
});

// INFINITE SCROLL
var BOOK_CHAPTERS={bereshit:50,shemot:40,vayikra:27,bamidbar:36,devarim:34};
var scrollState={book:null,bookEs:null,nextChapter:null,prevChapter:null,maxChapters:0,loadingNext:false,loadingPrev:false};
var chObs=null;

function initChapterObserver(){
  if(!('IntersectionObserver' in window))return;
  chObs=new IntersectionObserver(function(entries){
    var best=null;
    entries.forEach(function(e){if(e.isIntersecting&&(!best||e.intersectionRatio>best.intersectionRatio))best=e;});
    if(best){
      var ch=best.target.dataset.chapter,book=best.target.dataset.book;
      var url='/torah/'+book+'/'+String(ch).padStart(3,'0')+'/';
      if(location.pathname!==url){history.replaceState(null,'',url);document.title=(scrollState.bookEs||book)+' '+ch+' | Torah Sefardi';}
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
  var bk=data.book_es||scrollState.bookEs||'';
  var prev=ch>1?ch-1:null,next=ch<scrollState.maxChapters?ch+1:null;
  return '<div class="chapter-header"><div class="chapter-label">'+bk+' '+ch+'</div>'
    +'<div class="chapter-he-title">'+(data.title_he||'')+'</div></div>'
    +'<div class="torah-verses">'+data.verses.map(buildVerse).join('')+'</div>'
    +'<nav class="torah-nav">'
    +(prev?'<a href="/torah/'+scrollState.book+'/'+String(prev).padStart(3,'0')+'/">&larr; Cap. '+prev+'</a>':'<span></span>')
    +'<a href="/torah/'+scrollState.book+'/" class="nav-list">'+bk+'</a>'
    +(next?'<a href="/torah/'+scrollState.book+'/'+String(next).padStart(3,'0')+'/">Cap. '+next+' &rarr;</a>':'<span></span>')
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
    var res=await fetch('/torah/'+scrollState.book+'/'+String(ch).padStart(3,'0')+'/index.json');
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
    var res=await fetch('/torah/'+scrollState.book+'/'+String(ch).padStart(3,'0')+'/index.json');
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

document.addEventListener('DOMContentLoaded',function(){
  var fs=localStorage.getItem('fontSize');
  if(fs)document.documentElement.style.setProperty('--font',fs+'px');
  var dark=document.documentElement.classList.contains('dark-mode');
  var s=document.getElementById('iconSun'),m=document.getElementById('iconMoon');
  if(s)s.style.display=dark?'':'none';
  if(m)m.style.display=dark?'none':'';
  var sv=localStorage.getItem('VS_torah');
  if(sv){try{VS=JSON.parse(sv);}catch(e){}}
  applyView();
  var el=document.getElementById('torah-ctx');
  if(el){try{window.TORAH_CTX=JSON.parse(el.textContent);}catch(e){}}
  var ctx=window.TORAH_CTX;
  console.log('TORAH_CTX init:',ctx);
  if(ctx&&ctx.book){
    scrollState.book=ctx.book;
    scrollState.bookEs=ctx.bookEs;
    scrollState.maxChapters=BOOK_CHAPTERS[ctx.book]||50;
    scrollState.nextChapter=ctx.chapter+1;
    scrollState.prevChapter=ctx.chapter-1;
    console.log('scrollState init:',JSON.stringify(scrollState));
    initChapterObserver();
    initScroll();
  }
});
