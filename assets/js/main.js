/* ECOSHIELD site script */
(function () {
  var d = document, root = d.documentElement;
  root.classList.remove('no-js');
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  var lang = root.lang === 'en' ? 'en' : 'ko';
  var BASE = (d.body.getAttribute('data-base') || '');

  /* header */
  var hd = $('.hd'), top = $('.fab .top');
  function onScroll() {
    var y = window.scrollY || 0;
    if (hd) hd.classList.toggle('scrolled', y > 40);
    if (top) top.classList.toggle('on', y > 600);
  }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  if (top) top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

  /* mega menu */
  var gnb = $('.gnb'), timer;
  if (gnb && hd) {
    var open = function () { clearTimeout(timer); hd.classList.add('mega-on'); };
    var close = function () { timer = setTimeout(function () { hd.classList.remove('mega-on'); }, 120); };
    gnb.addEventListener('mouseenter', open); gnb.addEventListener('mouseleave', close);
    var mega = $('.mega');
    if (mega) { mega.addEventListener('mouseenter', open); mega.addEventListener('mouseleave', close); }
    $$('.gnb > li > a').forEach(function (a) { a.addEventListener('focus', open); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape') hd.classList.remove('mega-on'); });
  }

  /* mobile nav */
  var mbtn = $('.menu-btn'), mnav = $('.mnav');
  if (mbtn && mnav) mbtn.addEventListener('click', function () {
    var o = !mnav.classList.contains('open');
    mnav.classList.toggle('open', o); hd.classList.toggle('open', o);
    mbtn.setAttribute('aria-expanded', o); d.body.style.overflow = o ? 'hidden' : '';
  });

  /* search overlay */
  var sov = $('.search-ov');
  $$('[data-search]').forEach(function (b) {
    b.addEventListener('click', function () { if (sov) { sov.classList.add('on'); var i = $('input', sov); setTimeout(function () { i && i.focus(); }, 50); } });
  });
  if (sov) {
    $('.x', sov).addEventListener('click', function () { sov.classList.remove('on'); });
    sov.addEventListener('click', function (e) { if (e.target === sov) sov.classList.remove('on'); });
  }

  /* hero slider */
  var hero = $('.hero');
  if (hero) {
    var slides = $$('.slide', hero), tabs = $$('.hero-tabs button', hero), cur = 0, iv, paused = false;
    var numB = $('.hero-num b', hero), bar = $('.hero-bar i', hero), pbtn = $('.hero-pause', hero);
    var go = function (n) {
      slides[cur].classList.remove('on'); tabs[cur] && tabs[cur].classList.remove('on');
      cur = (n + slides.length) % slides.length;
      slides[cur].classList.add('on'); tabs[cur] && tabs[cur].classList.add('on');
      if (numB) numB.textContent = ('0' + (cur + 1)).slice(-2);
      if (bar) { bar.classList.remove('run'); void bar.offsetWidth; if (!paused) bar.classList.add('run'); }
    };
    var play = function () { clearInterval(iv); iv = setInterval(function () { go(cur + 1); }, 6000); };
    tabs.forEach(function (t, i) { t.addEventListener('click', function () { go(i); if (!paused) play(); }); });
    if (pbtn) pbtn.addEventListener('click', function () {
      paused = !paused; pbtn.setAttribute('aria-pressed', paused);
      pbtn.innerHTML = paused ? '<svg viewBox="0 0 12 12"><path d="M2 1l9 5-9 5z" fill="currentColor"/></svg>' : '<svg viewBox="0 0 12 12"><path d="M2 1h3v10H2zM7 1h3v10H7z" fill="currentColor"/></svg>';
      if (paused) { clearInterval(iv); bar && bar.classList.remove('run'); } else { play(); go(cur); }
    });
    go(0); play();
  }

  /* reveal */
  var rvs = $$('.rv');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    rvs.forEach(function (el) { io.observe(el); });
  } else rvs.forEach(function (el) { el.classList.add('in'); });

  /* generic tabs: [data-tabs] > button[data-t] ; panels [data-panel] */
  $$('[data-tabs]').forEach(function (g) {
    var scope = g.closest('[data-tabscope]') || d;
    var btns = $$('button', g);
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        btns.forEach(function (x) { x.classList.toggle('on', x === b); x.setAttribute('aria-selected', x === b); });
        $$('[data-panel]', scope).forEach(function (p) { p.classList.toggle('on', p.getAttribute('data-panel') === b.getAttribute('data-t')); });
      });
    });
  });

  /* strip arrows */
  $$('[data-strip]').forEach(function (c) {
    var s = $(c.getAttribute('data-strip'));
    if (!s) return;
    $$('button', c).forEach(function (b) {
      b.addEventListener('click', function () { s.scrollBy({ left: (b.dataset.dir === 'prev' ? -1 : 1) * Math.min(460, s.clientWidth * .8), behavior: 'smooth' }); });
    });
  });

  /* product filter */
  var pf = $('#pfilter');
  if (pf) {
    var sels = $$('select', pf), cards = $$('.pcard[data-group]'), empty = $('#pempty');
    var q = new URLSearchParams(location.search);
    sels.forEach(function (s) { if (q.get(s.name)) s.value = q.get(s.name); });
    var apply = function () {
      var v = {}; sels.forEach(function (s) { v[s.name] = s.value; });
      var n = 0;
      cards.forEach(function (c) {
        var ok = (!v.group || c.dataset.group === v.group) &&
          (!v.sector || (' ' + c.dataset.sectors + ' ').indexOf(' ' + v.sector + ' ') > -1) &&
          (!v.temp || c.dataset.temp === v.temp);
        c.hidden = !ok; if (ok) n++;
      });
      if (empty) empty.hidden = n > 0;
    };
    sels.forEach(function (s) { s.addEventListener('change', apply); }); apply();
  }

  /* product finder */
  var fd = $('#finder');
  if (fd && window.ES_PRODUCTS) {
    var sel = { sector: '', temp: '', purpose: '' };
    var out = $('#finder-out'), cnt = $('#finder-count');
    var render = function () {
      var list = window.ES_PRODUCTS.filter(function (p) {
        return (!sel.sector || p.sectors.indexOf(sel.sector) > -1) &&
          (!sel.temp || p.temp === sel.temp) &&
          (!sel.purpose || p.purpose.indexOf(sel.purpose) > -1);
      });
      cnt.textContent = list.length;
      out.innerHTML = list.length ? list.map(function (p) {
        return '<a class="pcard" href="' + p.url + '"><div class="ph"><img src="' + p.img + '" alt="" loading="lazy"><span class="no">No.' + p.no + '</span></div><div class="bd"><span class="tag">' + p.tag + '</span><h3>' + p.name + '</h3><p>' + p.sum + '</p><span class="more">' + (lang === 'en' ? 'View product' : '제품 보기') + ' →</span></div></a>';
      }).join('') : '<div class="empty" style="grid-column:1/-1">' + (lang === 'en' ? 'No exact match. Ask our engineers for a recommendation.' : '조건에 맞는 제품이 없습니다. 기술 상담으로 문의해 주세요.') + '</div>';
    };
    $$('.fq', fd).forEach(function (g) {
      var key = g.dataset.key;
      $$('button', g).forEach(function (b) {
        b.addEventListener('click', function () {
          var on = !b.classList.contains('on');
          $$('button', g).forEach(function (x) { x.classList.remove('on'); });
          if (on) b.classList.add('on');
          sel[key] = on ? b.dataset.v : ''; render();
        });
      });
    });
    render();
  }

  /* forms: prefill + validate + go to thanks (no backend yet) */
  $$('form[data-es-form]').forEach(function (f) {
    var q = new URLSearchParams(location.search);
    var p = q.get('product');
    if (p) { var s = f.querySelector('[name=product]'); if (s) { s.value = p; } }
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;
      $$('[required]', f).forEach(function (el) {
        var fld = el.closest('.fld'); var bad = el.type === 'checkbox' ? !el.checked : !String(el.value).trim();
        if (el.type === 'email' && el.value && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(el.value)) bad = true;
        if (fld) fld.classList.toggle('err', bad);
        if (bad) ok = false;
      });
      var msg = $('.form-msg', f);
      if (!ok) { if (msg) msg.style.display = 'block'; return; }
      location.href = f.getAttribute('action');
    });
  });

  /* search page */
  var sres = $('#search-res');
  if (sres && window.ES_INDEX) {
    var inp = $('#search-q'), q0 = new URLSearchParams(location.search).get('q') || '';
    inp.value = q0;
    var run = function () {
      var t = inp.value.trim().toLowerCase();
      if (!t) { sres.innerHTML = ''; return; }
      var r = window.ES_INDEX.filter(function (x) { return (x.t + ' ' + x.d + ' ' + (x.k || '')).toLowerCase().indexOf(t) > -1; });
      sres.innerHTML = r.length ? r.map(function (x) { return '<a href="' + BASE + x.u + '"><b>' + x.t + '</b><span>' + x.d + '</span></a>'; }).join('')
        : '<p class="empty">' + (lang === 'en' ? 'No results for "' : '"') + t.replace(/</g, '&lt;') + (lang === 'en' ? '".' : '"에 대한 검색 결과가 없습니다.') + '</p>';
    };
    inp.addEventListener('input', run); run();
  }

  /* language suggestion banner (no auto redirect) */
  var lb = $('.lang-banner');
  if (lb && !store.get('es-lang-dismiss')) {
    var nl = (navigator.language || 'ko').toLowerCase();
    if ((lang === 'ko' && nl.indexOf('ko') !== 0) || (lang === 'en' && nl.indexOf('ko') === 0)) lb.classList.add('on');
    $('button', lb).addEventListener('click', function () { lb.classList.remove('on'); store.set('es-lang-dismiss', '1'); });
  }
})();
