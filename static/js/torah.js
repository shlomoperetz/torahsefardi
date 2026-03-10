// TORAH.JS — Torah Sefardí
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
  var sun=document.getElementById('iconSun');
  var moon=document.getElementById('iconMoon');
  if(sun)sun.style.display=d?'':'none';
  if(moon)moon.style.display=d?'none':'';
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

// View toggles (Hebrew / Spanish)
var VS={he:true,es:true};
function toggleView(k){
  var active=Object.keys(VS).filter(function(x){return VS[x];});
  if(VS[k]){if(active.length===1)return;VS[k]=false;}
  else{VS[k]=true;}
  applyView();
  localStorage.setItem('VS_torah',JSON.stringify(VS));
}
function applyView(){
  document.querySelectorAll('.verse-he').forEach(function(el){el.style.display=VS.he?'':'none';});
  document.querySelectorAll('.verse-es').forEach(function(el){el.style.display=VS.es?'':'none';});
  var bh=document.getElementById('btnHe');
  var be=document.getElementById('btnEs');
  if(bh)bh.classList.toggle('active',VS.he);
  if(be)be.classList.toggle('active',VS.es);
  document.body.classList.toggle('show-es-only',!VS.he&&VS.es);
}

// Search
var SI=null;
function openSearch(){
  var o=document.getElementById('searchOverlay');
  var p=document.getElementById('searchPanel');
  if(o)o.style.display='';
  if(p)p.style.display='';
  setTimeout(function(){var i=document.getElementById('searchInput');if(i)i.focus();},50);
  if(!SI)fetch('/index.json').then(function(r){return r.json();}).then(function(d){SI=d;}).catch(function(){SI=[];});
}
function closeSearch(){
  var o=document.getElementById('searchOverlay');
  var p=document.getElementById('searchPanel');
  if(o)o.style.display='none';
  if(p)p.style.display='none';
  var i=document.getElementById('searchInput');
  if(i)i.value='';
  var r=document.getElementById('searchResults');
  if(r)r.innerHTML='';
}
function doSearch(q){
  var r=document.getElementById('searchResults');
  if(!q){if(r)r.innerHTML='';return;}
  if(!SI){setTimeout(function(){doSearch(q);},200);return;}
  var ql=q.toLowerCase().trim();
  var hits=SI.filter(function(p){
    return (p.book_es&&p.book_es.toLowerCase().includes(ql))||
           (p.book_he&&p.book_he.includes(q))||
           (String(p.chapter).startsWith(ql))||
           (p.es_preview&&p.es_preview.toLowerCase().includes(ql));
  }).slice(0,15);
  if(r)r.innerHTML=hits.length?hits.map(function(p){
    return '<a class="search-result-item" href="'+p.url+'">'+
      '<span class="search-result-book">'+p.book_es+' '+p.chapter+'</span>'+
      '<span class="search-result-title">'+(p.es_preview||'').slice(0,60)+'</span>'+
      '</a>';
  }).join(''):'<div style="padding:14px;opacity:0.5;font-family:var(--ui-font);font-size:0.9em">Sin resultados</div>';
}

document.addEventListener('keydown',function(e){
  if(e.key==='Escape')closeSearch();
  if((e.metaKey||e.ctrlKey)&&e.key==='k'){e.preventDefault();openSearch();}
});

document.addEventListener('DOMContentLoaded',function(){
  // Restore font size
  var fs=localStorage.getItem('fontSize');
  if(fs)document.documentElement.style.setProperty('--font',fs+'px');
  // Restore icons
  var sun=document.getElementById('iconSun');
  var moon=document.getElementById('iconMoon');
  var dark=document.documentElement.classList.contains('dark-mode');
  if(sun)sun.style.display=dark?'':'none';
  if(moon)moon.style.display=dark?'none':'';
  // Restore view state
  var sv=localStorage.getItem('VS_torah');
  if(sv){try{VS=JSON.parse(sv);}catch(e){}}
  applyView();
});
