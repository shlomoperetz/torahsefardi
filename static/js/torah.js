// TORAH.JS — Torah Sefardí
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
  if (VS[k] && active.length === 1) return;
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

// ===== INFINITE SCROLL BIDIRECCIONAL =====
var BOOK_CHAPTERS = { bereshit: 50, shemot: 40, vayikra: 27, bamidbar: 36, devarim: 34 };

var scrollState = {
  book: null,
  bookEs: null,
  nextChapter: null,
  prevChapter: null,
  maxChapters: 0,
  loadingNext: false,
  loadingPrev: false
};

var chapterObserver = null;

function initChapterObserver() {
  if (!('IntersectionObserver' in window)) return;
  chapterObserver = new IntersectionObserver(function(entries) {
    var best = null;
    entries.forEach(function(e) {
      if (e.isIntersecting && (!best || e.intersectionRatio > best.intersectionRatio)) best = e;
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

function initSentinelObservers() {
  if (!('IntersectionObserver' in window)) return;

  // Sentinel inferior → carga siguiente
  var sentinelBottom = document.getElementById('scroll-sentinel');
  if (sentinelBottom && scrollState.book) {
    new IntersectionObserver(function(entries) {
      if (entries[0].isIntersecting && !scrollState.loadingNext) loadNextChapter();
    }, { rootMargin: '300px' }).observe(sentinelBottom);
  }

  // Sentinel superior → carga anterior
  var sentinelTop = document.getElementById('scroll-sentinel-top');
  if (sentinelTop && scrollState.book) {
    new IntersectionObserver(function(entries) {
      if (entries[0].isIntersecting && !scrollState.loadingPrev) loadPrevChapter();
    }, { rootMargin: '300px' }).observe(sentinelTop);
  }
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

function buildSectionHTML(data, chNum) {
  var bookEs = data.book_es || scrollState.bookEs || '';
  var prevCh = chNum > 1 ? chNum - 1 : null;
  var nextCh = chNum < scrollState.maxChapters ? chNum + 1 : null;

  return '<div class="chapter-header">' +
      '<div class="chapter-label">' + bookEs + ' ' + chNum + '</div>' +
      '<div class="chapter-he-title">' + (data.title_he || '') + '</div>' +
    '</div>' +
    '<div class="torah-verses">' +
      data.verses.map(buildVerseHTML).join('') +
    '</div>' +
    '<nav class="torah-nav">' +
      (prevCh ? '<a href="/torah/' + scrollState.book + '/' + String(prevCh).padStart(3,'0') + '/">← Cap. ' + prevCh + '</a>' : '<span></span>') +
      '<a href="/torah/' + scrollState.book + '/" class="nav-list">' + bookEs + '</a>' +
      (nextCh ? '<a href="/torah/' + scrollState.book + '/' + String(nextCh).padStart(3,'0') + '/">Cap. ' + nextCh + ' →</a>' : '<span></span>') +
    '</nav>';
}

async function loadNextChapter() {
  if (scrollState.loadingNext) return;
  if (!scrollState.nextChapter || scrollState.nextChapter > scrollState.maxChapters) {
    var s = document.getElementById('scroll-sentinel');
    if (s) s.style.display = 'none';
    return;
  }
  scrollState.loadingNext = true;
  var dots = document.getElementById('loadingDots');
  if (dots) dots.style.display = 'flex';

  var chStr = String(scrollState.nextChapter).padStart(3, '0');
  try {
    var res = await fetch('/torah/' + scrollState.book + '/' + chStr + '/index.json');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    var data = await res.json();
    if (!data || !data.verses || !data.verses.length) throw new Error('empty');

    var feed = document.getElementById('chapters-feed');
    var sentinel = document.getElementById('scroll-sentinel');
    var section = document.createElement('section');
    section.className = 'chapter-section';
    section.dataset.book = scrollState.book;
    section.dataset.chapter = scrollState.nextChapter;
    section.id = 'ch' + scrollState.nextChapter;
    section.innerHTML = buildSectionHTML(data, scrollState.nextChapter);
    feed.insertBefore(section, sentinel);
    applyView();
    if (chapterObserver) chapterObserver.observe(section);
    scrollState.nextChapter++;
  } catch(e) {
    console.warn('loadNextChapter:', e.message);
    var s = document.getElementById('scroll-sentinel');
    if (s) s.style.display = 'none';
  }
  if (dots) dots.style.display = 'none';
  scrollState.loadingNext = false;
}

async function loadPrevChapter() {
  if (scrollState.loadingPrev) return;
  if (!scrollState.prevChapter || scrollState.prevChapter < 1) {
    var s = document.getElementById('scroll-sentinel-top');
    if (s) s.style.display = 'none';
    return;
  }
  scrollState.loadingPrev = true;

  var chStr = String(scrollState.prevChapter).padStart(3, '0');
  try {
    var res = await fetch('/torah/' + scrollState.book + '/' + chStr + '/index.json');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    var data = await res.json();
    if (!data || !data.verses || !data.verses.length) throw new Error('empty');

    var feed = document.getElementById('chapters-feed');
    var sentinelTop = document.getElementById('scroll-sentinel-top');
    var section = document.createElement('section');
    section.className = 'chapter-section';
    section.dataset.book = scrollState.book;
    section.dataset.chapter = scrollState.prevChapter;
    section.id = 'ch' + scrollState.prevChapter;
    section.innerHTML = buildSectionHTML(data, scrollState.prevChapter);

    // Guardar posición de scroll antes de prepend para no saltar
    var prevHeight = feed.scrollHeight;
    feed.insertBefore(section, sentinelTop.nextSibling);
    window.scrollBy(0, feed.scrollHeight - prevHeight);

    applyView();
    if (chapterObserver) chapterObserver.observe(section);
    scrollState.prevChapter--;
  } catch(e) {
    console.warn('loadPrevChapter:', e.message);
    var s = document.getElementById('scroll-sentinel-top');
    if (s) s.style.display = 'none';
  }
  scrollState.loadingPrev = false;
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', function() {
  var fs = localStorage.getItem('fontSize');
  if (fs) document.documentElement.style.setProperty('--font', fs + 'px');

  var sun = document.getElementById('iconSun');
  var moon = document.getElementById('iconMoon');
  var dark = document.documentElement.classList.contains('dark-mode');
  if (sun) sun.style.display = dark ? '' : 'none';
  if (moon) moon.style.display = dark ? 'none' : '';

  var sv = localStorage.getItem('VS_torah');
  if (sv) { try { VS = JSON.parse(sv); } catch(e){} }
  applyView();

  var ctxEl = document.getElementById('torah-ctx');
  if (ctxEl) {
    try { window.TORAH_CTX = JSON.parse(ctxEl.textContent); } catch(e) {}
  }

  var ctx = window.TORAH_CTX;
  if (ctx && ctx.book) {
    scrollState.book = ctx.book;
    scrollState.bookEs = ctx.bookEs;
    scrollState.maxChapters = BOOK_CHAPTERS[ctx.book] || 50;
    scrollState.nextChapter = ctx.chapter + 1;
    scrollState.prevChapter = ctx.chapter - 1;

    initChapterObserver();
    initSentinelObservers();
  }
});
