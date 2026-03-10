// TORAH.JS — Torah Sefardí
// Aplicar tema antes de render para evitar flash
(function(){
  var t = localStorage.getItem('theme');
  var dark = t ? t === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.classList.toggle('dark-mode', dark);
  document.documentElement.classList.toggle('light-mode', !dark);
})();

// ===== DARK MODE =====
function toggleDarkMode() {
  var r = document.documentElement;
  var d = r.classList.toggle('dark-mode');
  r.classList.toggle('light-mode', !d);
  localStorage.setItem('theme', d ? 'dark' : 'light');
  var sun = document.getElementById('iconSun');
  var moon = document.getElementById('iconMoon');
  if (sun) sun.style.display = d ? '' : 'none';
  if (moon) moon.style.display = d ? 'none' : '';
}

// ===== FUENTE =====
function adjustFont(n) {
  var r = document.documentElement;
  var c = parseInt(getComputedStyle(r).getPropertyValue('--font')) || 22;
  var v = Math.min(Math.max(c + n * 2, 16), 36);
  r.style.setProperty('--font', v + 'px');
  localStorage.setItem('fontSize', v);
}
function toggleFontMenu() {
  var p = document.querySelector('.font-popover');
  if (p) p.classList.toggle('open');
}
document.addEventListener('click', function(e) {
  if (!e.target.closest('.font-popover-wrap')) {
    var p = document.querySelector('.font-popover');
    if (p) p.classList.remove('open');
  }
});

// ===== TOGGLE VISTAS he/es =====
var VS = { he: true, es: true };
function toggleView(k) {
  var active = Object.keys(VS).filter(function(x){ return VS[x]; });
  if (VS[k] && active.length === 1) return; // no desactivar el único activo
  VS[k] = !VS[k];
  applyView();
  localStorage.setItem('VS_torah', JSON.stringify(VS));
}
function applyView() {
  document.querySelectorAll('.verse-he').forEach(function(el) {
    el.style.display = VS.he ? '' : 'none';
  });
  document.querySelectorAll('.verse-es').forEach(function(el) {
    el.style.display = VS.es ? '' : 'none';
  });
  var bh = document.getElementById('btnHe');
  var be = document.getElementById('btnEs');
  if (bh) bh.classList.toggle('active', VS.he);
  if (be) be.classList.toggle('active', VS.es);
}

// ===== BÚSQUEDA =====
var SI = null;
function openSearch() {
  var o = document.getElementById('searchOverlay');
  var p = document.getElementById('searchPanel');
  if (o) o.style.display = '';
  if (p) p.style.display = '';
  setTimeout(function(){ var i = document.getElementById('searchInput'); if (i) i.focus(); }, 50);
  if (!SI) {
    fetch('/index.json')
      .then(function(r){ return r.json(); })
      .then(function(d){ SI = d; })
      .catch(function(){ SI = []; });
  }
}
function closeSearch() {
  var o = document.getElementById('searchOverlay');
  var p = document.getElementById('searchPanel');
  if (o) o.style.display = 'none';
  if (p) p.style.display = 'none';
  var i = document.getElementById('searchInput');
  if (i) i.value = '';
  var r = document.getElementById('searchResults');
  if (r) r.innerHTML = '';
}
function doSearch(q) {
  var r = document.getElementById('searchResults');
  if (!q) { if (r) r.innerHTML = ''; return; }
  if (!SI) { setTimeout(function(){ doSearch(q); }, 200); return; }
  var ql = q.toLowerCase().trim();
  var isNum = !isNaN(ql) && ql !== '';
  var hits = SI.filter(function(p) {
    if (isNum) return String(p.chapter).startsWith(ql);
    return (p.book_es && p.book_es.toLowerCase().includes(ql)) ||
           (p.book_he && p.book_he.includes(q)) ||
           (p.es_preview && p.es_preview.toLowerCase().includes(ql));
  }).slice(0, 15);
  if (r) r.innerHTML = hits.length
    ? hits.map(function(p) {
        return '<a class="search-result-item" href="' + p.url + '">' +
          '<span class="search-result-num">' + p.book_es + ' ' + p.chapter + '</span>' +
          '<span class="search-result-title">' + (p.es_preview || '').slice(0, 55) + '</span>' +
          '</a>';
      }).join('')
    : '<div style="padding:14px;opacity:0.5;font-family:var(--ui-font);font-size:0.9em">Sin resultados</div>';
}
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeSearch();
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); openSearch(); }
});

// ===== INFINITE SCROLL =====
var BOOK_CHAPTERS = { bereshit: 50, shemot: 40, vayikra: 27, bamidbar: 36, devarim: 34 };

var scrollState = {
  book: null,
  bookEs: null,
  nextChapter: null,
  maxChapters: 0,
  loading: false
};

// Observer: actualiza URL y título al hacer scroll
var chapterObserver = null;
function initChapterObserver() {
  if (!('IntersectionObserver' in window)) return;
  chapterObserver = new IntersectionObserver(function(entries) {
    var best = null;
    entries.forEach(function(e) {
      if (e.isIntersecting && (!best || e.intersectionRatio > best.intersectionRatio)) {
        best = e;
      }
    });
    if (best) {
      var ch = best.target.dataset.chapter;
      var book = best.target.dataset.book;
      var newUrl = '/torah/' + book + '/' + String(ch).padStart(3, '0') + '/';
      if (location.pathname !== newUrl) {
        history.replaceState(null, '', newUrl);
        document.title = (scrollState.bookEs || book) + ' ' + ch + ' | Torah Sefardí';
      }
    }
  }, { threshold: 0.15, rootMargin: '-80px 0px -40% 0px' });

  document.querySelectorAll('.chapter-section').forEach(function(sec) {
    chapterObserver.observe(sec);
  });
}

// Observer: carga el siguiente capítulo cuando el sentinel entra en vista
function initSentinelObserver() {
  if (!('IntersectionObserver' in window)) return;
  var sentinel = document.getElementById('scroll-sentinel');
  if (!sentinel || !scrollState.book) return;

  var sentinelObs = new IntersectionObserver(function(entries) {
    if (entries[0].isIntersecting && !scrollState.loading) {
      loadNextChapter();
    }
  }, { rootMargin: '300px' });
  sentinelObs.observe(sentinel);
}

function buildVerseHTML(verse) {
  var html = '<div class="verse" id="v' + verse.num + '">';
  html += '<div class="verse-he"><sup class="verse-num">' + verse.num + '</sup>' + verse.he + '</div>';
  if (verse.es) {
    html += '<div class="verse-es"><sup class="verse-num-es">' + verse.num + '</sup>' + verse.es + '</div>';
  }
  html += '</div>';
  return html;
}

function appendChapter(data, chNum) {
  var feed = document.getElementById('chapters-feed');
  var sentinel = document.getElementById('scroll-sentinel');
  if (!feed || !sentinel) return;

  var section = document.createElement('section');
  section.className = 'chapter-section';
  section.dataset.book = scrollState.book;
  section.dataset.chapter = chNum;
  section.id = 'ch' + chNum;

  var bookEs = data.book_es || scrollState.bookEs || '';
  var chPadded = String(chNum).padStart(3, '0');
  var prevCh = chNum - 1;
  var nextCh = chNum < scrollState.maxChapters ? chNum + 1 : null;

  section.innerHTML =
    '<div class="chapter-header">' +
      '<div class="chapter-label">' + bookEs + ' ' + chNum + '</div>' +
      '<div class="chapter-he-title">' + (data.title_he || '') + '</div>' +
    '</div>' +
    '<div class="torah-verses">' +
      data.verses.map(buildVerseHTML).join('') +
    '</div>' +
    '<nav class="torah-nav">' +
      '<a href="/torah/' + scrollState.book + '/' + String(prevCh).padStart(3,'0') + '/">← Cap. ' + prevCh + '</a>' +
      '<a href="/torah/' + scrollState.book + '/" class="nav-list">' + bookEs + '</a>' +
      (nextCh ? '<a href="/torah/' + scrollState.book + '/' + String(nextCh).padStart(3,'0') + '/">Cap. ' + nextCh + ' →</a>' : '<span></span>') +
    '</nav>';

  feed.insertBefore(section, sentinel);
  applyView(); // aplica estado he/es al contenido nuevo
  if (chapterObserver) chapterObserver.observe(section);
}

async function loadNextChapter() {
  if (scrollState.loading) return;
  if (!scrollState.nextChapter || scrollState.nextChapter > scrollState.maxChapters) {
    // No hay más capítulos
    var sentinel = document.getElementById('scroll-sentinel');
    if (sentinel) sentinel.style.display = 'none';
    return;
  }

  scrollState.loading = true;
  var dots = document.getElementById('loadingDots');
  if (dots) dots.style.display = 'flex';

  var chStr = String(scrollState.nextChapter).padStart(3, '0');
  var url = '/torah/' + scrollState.book + '/' + chStr + '/index.json';

  try {
    var res = await fetch(url);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    var data = await res.json();
    if (!data || !data.verses || data.verses.length === 0) throw new Error('empty');
    appendChapter(data, scrollState.nextChapter);
    scrollState.nextChapter++;
  } catch(e) {
    console.warn('Fin de capítulos o error:', e.message);
    scrollState.nextChapter = null;
    var sentinel = document.getElementById('scroll-sentinel');
    if (sentinel) sentinel.style.display = 'none';
  }

  if (dots) dots.style.display = 'none';
  scrollState.loading = false;
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', function() {
  // Restaurar fuente
  var fs = localStorage.getItem('fontSize');
  if (fs) document.documentElement.style.setProperty('--font', fs + 'px');

  // Restaurar iconos dark mode
  var sun = document.getElementById('iconSun');
  var moon = document.getElementById('iconMoon');
  var dark = document.documentElement.classList.contains('dark-mode');
  if (sun) sun.style.display = dark ? '' : 'none';
  if (moon) moon.style.display = dark ? 'none' : '';

  // Restaurar vista he/es
  var sv = localStorage.getItem('VS_torah');
  if (sv) { try { VS = JSON.parse(sv); } catch(e){} }
  applyView();

  // Leer contexto del elemento JSON (evita problemas con el minificador HTML)
  var ctxEl = document.getElementById('torah-ctx');
  if (ctxEl) {
    try { window.TORAH_CTX = JSON.parse(ctxEl.textContent); } catch(e) {}
  }

  // Infinite scroll — solo en páginas de capítulo
  var ctx = window.TORAH_CTX;
  if (ctx && ctx.book) {
    scrollState.book = ctx.book;
    scrollState.bookEs = ctx.bookEs;
    scrollState.maxChapters = BOOK_CHAPTERS[ctx.book] || 50;
    scrollState.nextChapter = ctx.chapter + 1;

    // Mostrar dots de carga si hay más capítulos
    if (scrollState.nextChapter <= scrollState.maxChapters) {
      var dots = document.getElementById('loadingDots');
      // dots solo se muestran cuando se activa el sentinel
    }

    initChapterObserver();
    initSentinelObserver();
  }
});
