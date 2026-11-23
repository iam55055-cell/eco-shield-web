# -*- coding: utf-8 -*-
"""EXOSKIN 정적 사이트 생성기.
실행: python3 build.py  → ../eco-shield/ 에 HTML 생성 (assets 폴더는 그대로 둠)
"""
import os, json, html, datetime
from content import SITE, GROUPS, PRODUCTS, SECTORS, SPACES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'eco-shield'))
TODAY = '2026-11-18'

G = {g['id']: g for g in GROUPS}
PR = {p['id']: p for p in PRODUCTS}
SE = {s['id']: s for s in SECTORS}
SP = {s['id']: s for s in SPACES}
PAGES = []  # (lang, path, title, desc)

def esc(s):
    return html.escape(str(s), quote=True)

# ------------------------------------------------------------------ paths
def lp(lang, path):
    return ('en/' + path) if lang == 'en' else path

def url(cur, target):
    anchor = ''
    if '#' in target:
        target, anchor = target.split('#', 1)
        anchor = '#' + anchor
    r = os.path.relpath(target or '.', cur or '.')
    r = '' if r == '.' else r + '/'
    return r + 'index.html' + anchor

def asset(cur, a):
    return os.path.relpath('assets/' + a, cur or '.')

def img(cur, name):
    return asset(cur, 'img/%s.jpg' % name)

def group_path(g): return 'products/%s/' % g['slug']
def product_path(p): return 'products/%s/%s/' % (G[p['group']]['slug'], p['slug'])
def sector_path(s): return 'applications/%s/' % s['slug']
def space_path(sp):
    s = SE[sp['sector']]
    return ('applications/%s/%s/' % (s['slug'], sp['slug'])) if sp['landing'] else ('applications/%s/#%s' % (s['slug'], sp['slug']))

def product_sectors(p):
    out = []
    for sid in p['spaces']:
        sec = SP[sid]['sector']
        if sec not in out: out.append(sec)
    return out

# ------------------------------------------------------------------ icons
IC = {
 'arrow': '<path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
 'search': '<circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 20l-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
 'menu': '<path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
 'fire': '<path d="M12 3c1 4 5 5.5 5 10a5 5 0 0 1-10 0c0-2 1-3.5 2-4.5.3 1.6 1.2 2.5 2 2.5-1-3 0-6 1-8z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
 'thermo': '<path d="M10 14V5a2 2 0 1 1 4 0v9a4 4 0 1 1-4 0z" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 9v7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
 'layers': '<path d="M12 3l9 5-9 5-9-5 9-5zM3 13l9 5 9-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
 'film': '<rect x="4" y="5" width="16" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M4 10h16M4 14h16" stroke="currentColor" stroke-width="1.4" opacity=".6"/>',
 'shield': '<path d="M12 3l8 3v6c0 5-3.6 8-8 9-4.4-1-8-4-8-9V6l8-3z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
 'leaf': '<path d="M5 19c0-9 6-14 15-14 0 9-5 15-14 15M5 19l7-7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
 'drop': '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z" fill="none" stroke="currentColor" stroke-width="1.8"/>',
 'feather': '<path d="M20 4C11 4 6 9 6 18M6 18l-2 2M9 15h6M11 11h6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
 'check': '<circle cx="12" cy="12" r="10" fill="currentColor" opacity=".12"/><path d="M7.5 12.5l3 3 6-6.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
 'doc': '<path d="M7 3h7l5 5v13H7z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M14 3v5h5M10 13h6M10 17h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
 'chat': '<path d="M4 5h16v11H9l-5 4z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
 'mail': '<rect x="3" y="5" width="18" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M3 7l9 6 9-6" fill="none" stroke="currentColor" stroke-width="1.8"/>',
 'globe': '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18" fill="none" stroke="currentColor" stroke-width="1.5"/>',
 'tool': '<path d="M14 6a4 4 0 0 0 5 5l-9 9-3-3 9-9a4 4 0 0 1-2-2z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
 'box': '<path d="M3 7l9-4 9 4v10l-9 4-9-4z M3 7l9 4 9-4M12 11v10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
 'play': '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M10 8.5l5 3.5-5 3.5z" fill="currentColor"/>',
 'up': '<path d="M12 19V5M6 11l6-6 6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
 'target': '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/>',
 'users': '<circle cx="9" cy="8" r="3.5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M2.5 20c.5-4 3-6 6.5-6s6 2 6.5 6M16 4.5a3.5 3.5 0 0 1 0 7M18 14c2 .7 3.2 2.6 3.5 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
 'flag': '<path d="M5 21V4M5 4h11l-2 4 2 4H5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
}
def ic(name, cls=''):
    return '<svg viewBox="0 0 24 24" aria-hidden="true"%s>%s</svg>' % ((' class="%s"' % cls) if cls else '', IC[name])
ARROW = ic('arrow')
FEAT_ICONS = ['shield', 'feather', 'leaf', 'drop', 'thermo', 'target']

# ------------------------------------------------------------------ navigation
def nav(lang):
    k = lang == 'ko'
    items = [
        ('about', '회사소개', 'About Us', 'about/ecoshield/', [
            ('엑소스킨 소개', 'About EXOSKIN', 'about/ecoshield/'),
            ('브랜드 스토리', 'Brand Story', 'about/brand/'),
            ('제조 파트너', 'Manufacturing Partner', 'about/manufacturer/'),
            ('품질·공급 체계', 'Quality & Supply', 'about/quality/'),
            ('글로벌 네트워크', 'Global Network', 'about/global-network/'),
            ('오시는 길', 'Location', 'about/location/')]),
        ('products', '제품', 'Products', 'products/',
            [('전체 제품', 'All Products', 'products/')] +
            [(g['ko']['name'], g['en']['name'], group_path(g)) for g in GROUPS] +
            [('제품 선택 가이드', 'Product Finder', 'products/finder/')]),
        ('applications', '적용분야', 'Applications', 'applications/',
            [('전체 분야', 'All Applications', 'applications/')] +
            [(s['ko']['name'], s['en']['name'], sector_path(s)) for s in SECTORS]),
        ('technology', '기술·인증', 'Technology', 'technology/aerogel/', [
            ('에어로젤 기술', 'Aerogel Technology', 'technology/aerogel/'),
            ('인증·시험성적서', 'Certifications & Test Reports', 'technology/certifications/')] +
            ([('기술 칼럼', None, 'technology/insights/')] if k else [])),
        ('projects', '시공사례', 'Projects', 'projects/', [
            ('전체 사례', 'All Projects', 'projects/'),
            ('국내 사례', 'Korea Projects', 'projects/korea/'),
            ('해외 사례', 'Global Projects', 'projects/global/')]),
        ('resources', '자료실', 'Resources', 'resources/', [
            ('카탈로그·브로슈어', 'Catalogs & Brochures', 'resources/catalogs/'),
            ('TDS·SDS', 'TDS & SDS', 'resources/data-sheets/'),
            ('시방서·시공가이드', 'Specs & Application Guides', 'resources/guides/'),
            ('영상', 'Videos', 'resources/videos/')]),
        ('news', '홍보센터', 'Newsroom', 'news/notices/', [
            ('공지·뉴스', 'News', 'news/notices/'),
            ('전시회·행사', 'Exhibitions & Events', 'news/exhibitions/')]),
        ('contact', '문의', 'Contact', 'contact/', [
            ('견적·샘플 문의', 'Request a Quote', 'contact/quote/'),
            ('파트너·대리점 모집', 'Become a Partner', 'contact/partner/'),
            ('기술 상담', 'Technical Consultation', 'contact/technical/'),
            ('자주 묻는 질문', 'FAQ', 'contact/faq/')]),
    ]
    out = []
    for key, ko, en, path, kids in items:
        out.append(dict(key=key, label=ko if k else en, path=path,
                        kids=[(a if k else b, p) for a, b, p in kids if (k or b)]))
    return out

def section_of(path):
    p = path[3:] if path.startswith('en/') else path
    return p.split('/')[0] if p else ''

# ------------------------------------------------------------------ layout
def header(lang, cur, alt):
    k = lang == 'ko'
    N = nav(lang)
    sec = section_of(cur)
    home = lp(lang, '')
    gnb = ''.join('<li class="%s"><a href="%s">%s</a></li>' % ('cur' if n['key'] == sec else '', url(cur, lp(lang, n['path'])), esc(n['label'])) for n in N)
    cols = ''.join('<div><h4>%s</h4>%s</div>' % (esc(n['label']), ''.join('<a href="%s">%s</a>' % (url(cur, lp(lang, p)), esc(l)) for l, p in n['kids'])) for n in N)
    mnav = ''.join('<details%s><summary>%s</summary><div>%s</div></details>' % (' open' if n['key'] == sec else '', esc(n['label']), ''.join('<a href="%s">%s</a>' % (url(cur, lp(lang, p)), esc(l)) for l, p in n['kids'])) for n in N)
    ko_url = url(cur, alt if not k else cur)
    en_url = url(cur, alt if k else cur)
    langsw = '<div class="lang"><a href="%s" class="%s" hreflang="ko" lang="ko">KO</a><span>/</span><a href="%s" class="%s" hreflang="en" lang="en">EN</a></div>' % (ko_url, 'on' if k else '', en_url, '' if k else 'on')
    ctas = ('<a class="btn-hd" href="%s">견적 문의</a>' % url(cur, 'contact/quote/')) if k else \
           ('<a class="btn-hd ghost" href="%s">Become a Partner</a><a class="btn-hd" href="%s">Request a Quote</a>' % (url(cur, 'en/contact/partner/'), url(cur, 'en/contact/quote/')))
    intro = ('<b>EXOSKIN</b><p>에어로젤 방화·단열 소재 전문 브랜드. 숴싱 신소재 한국 공식 총판입니다.</p>' if k else
             '<b>EXOSKIN</b><p>Aerogel fire protection and thermal insulation. Official Korea distributor of Shuoxing New Materials.</p>')
    mcta = ('<a href="%s" class="pri">견적 문의</a><a href="%s">%s</a>' % (url(cur, lp(lang, 'contact/quote/')), en_url if k else ko_url, 'English' if k else '한국어'))
    return f'''<a class="skip" href="#main">{'본문 바로가기' if k else 'Skip to content'}</a>
<header class="hd">
 <div class="wrap">
  <a class="hd-logo" href="{url(cur, home)}" aria-label="EXOSKIN {'홈' if k else 'Home'}"><img class="on-light" src="{asset(cur, 'img/logo.png')}" alt="EXOSKIN 엑소스킨"><img class="on-dark" src="{asset(cur, 'img/logo-dark.png')}" alt=""></a>
  <nav aria-label="{'주 메뉴' if k else 'Main'}"><ul class="gnb">{gnb}</ul></nav>
  <div class="hd-util">
   <button class="icon-btn" type="button" data-search aria-label="{'검색' if k else 'Search'}">{ic('search')}</button>
   {langsw}{ctas}
   <button class="icon-btn menu-btn" type="button" aria-label="{'메뉴 열기' if k else 'Open menu'}" aria-expanded="false">{ic('menu')}</button>
  </div>
 </div>
 <div class="mega" aria-hidden="true"><div class="wrap"><div class="mega-intro">{intro}</div><div class="mega-cols">{cols}</div></div></div>
</header>
<nav class="mnav" aria-label="{'모바일 메뉴' if k else 'Mobile menu'}">{mnav}<div class="mnav-cta">{mcta}</div></nav>
<div class="search-ov" role="dialog" aria-label="{'사이트 검색' if k else 'Site search'}"><button class="x" type="button" aria-label="{'닫기' if k else 'Close'}">&times;</button>
 <form action="{url(cur, lp(lang, 'search/'))}" method="get"><input name="q" type="search" placeholder="{'제품명, 적용 공간, 자료를 검색하세요' if k else 'Search products, applications, documents'}"><button class="btn btn-pri btn-sm" type="submit">{'검색' if k else 'Search'}</button></form></div>'''

def footer(lang, cur, alt):
    k = lang == 'ko'
    N = nav(lang)
    cols = ''.join('<div><h4>%s</h4>%s</div>' % (esc(n['label']), ''.join('<a href="%s">%s</a>' % (url(cur, lp(lang, p)), esc(l)) for l, p in n['kids'][:6])) for n in N[:4])
    if k:
        legal = (f'<a href="{url(cur, "privacy/")}" class="pv">개인정보처리방침</a><a href="{url(cur, "terms/")}">이용약관</a>'
                 f'<a href="{url(cur, "no-email-collection/")}">이메일무단수집거부</a><a href="{url(cur, "sitemap/")}">사이트맵</a>')
        info = ('<span>상호 %s</span><span>대표 %s</span><span>사업자등록번호 %s</span><br>'
                '<span>주소 %s</span><span>대표전화 <a href="tel:%s" style="color:inherit">%s</a></span><span>이메일 <a href="mailto:%s" style="color:inherit">%s</a></span><br>'
                '<span>EXOSKIN은 %s의 에어로젤 소재 브랜드입니다</span><span>숴싱 신소재(Shuoxing New Materials) 한국 공식 총판</span><span>제조원: 숴싱 신소재(중국)</span>') % (SITE['operator_ko'], SITE['ceo_ko'], SITE['bizno'], SITE['addr_ko'], SITE['tel_link'], SITE['tel'], SITE['email'], SITE['email'], SITE['operator_ko'])
        copy = '© 2026 EXOSKIN. All rights reserved.'
        sub = '운영사 <a href="%s" target="_blank" rel="noopener" style="color:#fff">주식회사 에코아트 eco-art.kr</a> · 사이트 이미지는 적용 예시를 표현한 연출 이미지입니다.' % SITE['operator_url']
        tag = '에어로젤 방화·단열 소재 전문 브랜드<br>숴싱 신소재 한국 공식 총판'
    else:
        legal = (f'<a href="{url(cur, "en/privacy/")}" class="pv">Privacy Policy</a><a href="{url(cur, "en/terms/")}">Terms of Use</a>'
                 f'<a href="{url(cur, "en/cookies/")}">Cookie Policy</a><a href="{url(cur, "en/sitemap/")}">Sitemap</a>')
        info = ('<span>%s</span><span>CEO %s</span><span>Business Reg. No. %s</span><br><span>%s</span><br>'
                '<span>Tel <a href="tel:%s" style="color:inherit">%s</a></span><span>Email <a href="mailto:%s" style="color:inherit">%s</a></span><br><span>EXOSKIN is an aerogel materials brand of %s</span><span>Official Korea Distributor of Shuoxing New Materials</span><span>Manufactured by Shuoxing New Materials (China)</span>') % (SITE['operator_en'], SITE['ceo_en'], SITE['bizno'], SITE['addr_en'], SITE['tel_link'], SITE['tel_intl'], SITE['email'], SITE['email'], SITE['operator_en'])
        copy = '© 2026 EXOSKIN. All rights reserved.'
        sub = 'Operated by <a href="%s" target="_blank" rel="noopener" style="color:#fff">ECOART Co., Ltd.</a> · Images on this site are illustrative.' % SITE['operator_url']
        tag = 'Aerogel fire protection &amp; thermal insulation<br>Official Korea Distributor of Shuoxing New Materials'
    return f'''<footer class="ft">
 <div class="wrap">
  <div class="ft-top"><div><img class="ft-logo" src="{asset(cur, 'img/logo-full-dark.png')}" alt="EXOSKIN — Safety wherever protection is needed."><p>{tag}</p></div><nav class="ft-nav" aria-label="{'푸터 메뉴' if k else 'Footer'}">{cols}</nav></div>
  <div class="ft-legal">{legal}</div>
  <p class="ft-info">{info}</p>
  <div class="ft-copy"><span>{copy}</span><span>{sub}</span></div>
 </div>
</footer>'''

def fab(lang, cur):
    k = lang == 'ko'
    if k:
        return f'''<div class="fab"><a class="q" href="{url(cur, 'contact/quote/')}">{ic('doc')}<span>견적 문의</span></a><a href="tel:{SITE['tel_link']}" title="대표전화 {SITE['tel']}">{ic('chat')}<span>전화 상담</span></a><button class="top" type="button" aria-label="맨 위로">{ic('up')}</button></div>
<div class="lang-banner" role="region" aria-label="Language"><span lang="en">View this page in English?</span><a href="{{ALT}}" lang="en">English</a><button type="button" aria-label="close">&times;</button></div>'''
    return f'''<div class="fab"><a class="q" href="{url(cur, 'en/contact/quote/')}">{ic('doc')}<span>Request a Quote</span></a><a href="mailto:{SITE['email']}">{ic('mail')}<span>Email</span></a><button class="top" type="button" aria-label="Back to top">{ic('up')}</button></div>
<div class="lang-banner" role="region" aria-label="언어"><span lang="ko">한국어 페이지로 보시겠어요?</span><a href="{{ALT}}" lang="ko">한국어</a><button type="button" aria-label="닫기">&times;</button></div>'''

def ko_en_pair(lang, path):
    """대응 언어 경로. 상대 언어판이 없으면 그 언어의 홈."""
    if lang == 'ko':
        cand = 'en/' + path
        return cand if cand in EN_PATHS else 'en/'
    base = path[3:]
    return base if base in KO_PATHS else ''

KO_PATHS, EN_PATHS = set(), set()

def write(lang, path, title, desc, body, over=False, keywords='', noindex=False, extra_head=''):
    k = lang == 'ko'
    alt = ko_en_pair(lang, path)
    full_title = (title + ' | EXOSKIN 엑소스킨') if (k and title) else ((title + ' | EXOSKIN') if title else ('EXOSKIN 엑소스킨 | 에어로젤 방화·단열 솔루션' if k else 'EXOSKIN | Aerogel Fire Protection & Thermal Insulation'))
    canon = SITE['domain'] + '/' + path
    hre = ''
    has_ko = (path if not k else path) if k else path[3:]
    if k and ('en/' + path) in EN_PATHS:
        hre = f'<link rel="alternate" hreflang="ko" href="{canon}"><link rel="alternate" hreflang="en" href="{SITE["domain"]}/en/{path}"><link rel="alternate" hreflang="x-default" href="{SITE["domain"]}/en/{path}">'
    elif not k and path[3:] in KO_PATHS:
        hre = f'<link rel="alternate" hreflang="ko" href="{SITE["domain"]}/{path[3:]}"><link rel="alternate" hreflang="en" href="{canon}"><link rel="alternate" hreflang="x-default" href="{canon}">'
    base = os.path.relpath('.', path or '.')
    base = '' if base == '.' else base + '/'
    ogimg = SITE['domain'] + '/assets/img/og-image.jpg'
    doc = f'''<!doctype html>
<html lang="{lang}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
{('<meta name="keywords" content="%s">' % esc(keywords)) if keywords else ''}
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="canonical" href="{canon}">{hre}
<meta property="og:type" content="website"><meta property="og:site_name" content="EXOSKIN"><meta property="og:title" content="{esc(full_title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{ogimg}"><meta property="og:locale" content="{'ko_KR' if k else 'en_US'}">
<meta name="theme-color" content="#001288">
<link rel="icon" type="image/png" sizes="64x64" href="{asset(path, 'img/favicon-64.png')}"><link rel="apple-touch-icon" href="{asset(path, 'img/symbol.png')}">
<link rel="stylesheet" href="{asset(path, 'css/style.css')}">
{extra_head}
</head>
<body class="{'is-over' if over else ''}" data-base="{base}">
{header(lang, path, alt)}
<main id="main">
{body}
</main>
{footer(lang, path, alt)}
{fab(lang, path).replace('{ALT}', url(path, alt))}
<script src="{asset(path, 'js/main.js')}"></script>
</body>
</html>'''
    fp = os.path.join(OUT, path, 'index.html')
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(doc)
    if not noindex:
        PAGES.append(dict(lang=lang, path=path, title=title or ('홈' if k else 'Home'), desc=desc, kw=keywords))

# ------------------------------------------------------------------ shared blocks
def subvis(lang, cur, title, lead, image, crumbs):
    k = lang == 'ko'
    cr = '<a href="%s">%s</a>' % (url(cur, lp(lang, '')), 'HOME') + ''.join(
        '<span><a href="%s">%s</a></span>' % (url(cur, lp(lang, p)), esc(l)) if p else '<span>%s</span>' % esc(l) for l, p in crumbs)
    return f'''<section class="subvis"><img src="{img(cur, image)}" alt=""><div class="wrap"><nav class="crumb" aria-label="{'현재 위치' if k else 'Breadcrumb'}">{cr}</nav><h1>{esc(title)}</h1>{('<p>%s</p>' % esc(lead)) if lead else ''}</div></section>'''

def lnb(lang, cur, key, active=None):
    n = [x for x in nav(lang) if x['key'] == key][0]
    act = active or (cur[3:] if cur.startswith('en/') else cur)
    return '<nav class="lnb" aria-label="sub"><div class="wrap">%s</div></nav>' % ''.join(
        '<a href="%s" class="%s">%s</a>' % (url(cur, lp(lang, p)), 'on' if p == act else '', esc(l)) for l, p in n['kids'])

def sec_hd(eyebrow, h2, lead='', right='', center=False, cls=''):
    return f'''<div class="sec-hd{' center' if center else ''} {cls}"><div class="rv"><span class="eyebrow">{eyebrow}</span><h2 class="h2">{h2}</h2>{('<p class="lead">%s</p>' % lead) if lead else ''}</div>{right}</div>'''

def cta_band(lang, cur, image='space-10', title=None, lead=None):
    k = lang == 'ko'
    t = title or ('현장에 맞는 제품,<br>엑소스킨이 함께 찾겠습니다.' if k else 'Let us find the right product<br>for your project.')
    l = lead or ('도면이나 현장 조건(면적·온도·요구 내화시간)을 보내 주시면 담당 엔지니어가 제품과 소요량을 제안해 드립니다.' if k else
                 'Send us drawings or site conditions (area, temperature, required fire rating) and our engineers will recommend products and quantities.')
    b1 = ('견적·샘플 문의', 'contact/quote/') if k else ('Request a Quote', 'contact/quote/')
    b2 = ('기술 상담', 'contact/technical/') if k else ('Become a Partner', 'contact/partner/')
    return f'''<section class="cta"><img src="{img(cur, image)}" alt="" loading="lazy"><div class="wrap rv"><span class="eyebrow" style="color:var(--lime)">Contact</span><h2 class="h2">{t}</h2><p class="lead">{l}</p><div class="btns"><a class="btn btn-pri" href="{url(cur, lp(lang, b1[1]))}">{b1[0]} {ARROW}</a><a class="btn btn-ghost-w" href="{url(cur, lp(lang, b2[1]))}">{b2[0]}</a></div></div></section>'''

def pcard(lang, cur, p, extra_attr=True):
    t = p[lang]
    attrs = ''
    if extra_attr:
        attrs = ' data-group="%s" data-sectors="%s" data-temp="%s"' % (p['group'], ' '.join(product_sectors(p)), p['temp'])
    chips = ''.join('<span class="chip%s">%s</span>' % (' f' if p['group'] == 'P10' and i == 0 else (' g' if i == 0 else ''), esc(c)) for i, c in enumerate(t['chips']))
    return f'''<a class="pcard rv" href="{url(cur, lp(lang, product_path(p)))}"{attrs}><div class="ph"><img src="{img(cur, p['img'])}" alt="" loading="lazy" style="object-position:{p['pos']}"><span class="no">No.{p['no']:02d}</span></div><div class="bd"><span class="tag">{esc(t['tag'])}</span><h3>{esc(t['name'])}</h3><p>{esc(t['sum'])}</p><div class="chipset">{chips}</div><span class="more">{'제품 상세' if lang == 'ko' else 'View details'} {ARROW}</span></div></a>'''

def rec_list(lang, cur, pids):
    return '<div class="rec-list">%s</div>' % ''.join(
        '<a href="%s"><span><small>%s</small>%s</span>%s</a>' % (url(cur, lp(lang, product_path(PR[i]))), esc(G[PR[i]['group']][lang]['name']), esc(PR[i][lang]['name']), ARROW) for i in pids)

def note_test(lang):
    return ('<p class="note">※ 표기된 수치는 제조사(중국 GB 등) 시험 기준이며, 국내 인증 취득 전입니다. 국내 인증·시험 결과는 확보 후 별도 표기합니다.</p>' if lang == 'ko' else
            '<p class="note">※ Values are based on the manufacturer\'s tests (Chinese GB standards, etc.). They do not imply compliance with EN, ASTM/UL or other regional standards unless stated.</p>')

def form_field(label, name, typ='text', req=False, full=False, opts=None, hint='', ph=''):
    r = ' required' if req else ''
    lab = '<label for="f-%s">%s%s</label>' % (name, esc(label), '<em>*</em>' if req else '')
    if typ == 'select':
        ctl = '<select id="f-%s" name="%s"%s>%s</select>' % (name, name, r, ''.join('<option value="%s">%s</option>' % (esc(v), esc(l)) for v, l in opts))
    elif typ == 'textarea':
        ctl = '<textarea id="f-%s" name="%s"%s placeholder="%s"></textarea>' % (name, name, r, esc(ph))
    else:
        ctl = '<input id="f-%s" name="%s" type="%s"%s placeholder="%s">' % (name, name, typ, r, esc(ph))
    return '<div class="fld%s">%s%s%s</div>' % (' full' if full else '', lab, ctl, ('<p class="hint">%s</p>' % esc(hint)) if hint else '')

def consent(lang):
    if lang == 'ko':
        return '''<div class="consent"><div class="box">[개인정보 수집·이용 안내] 수집 항목: 회사명, 담당자명, 연락처, 이메일, 문의 내용 및 첨부파일 / 수집 목적: 견적·상담 회신 및 고객 관리 / 보유 기간: 문의 처리 완료 후 3년(관계 법령에 따라 보존이 필요한 경우 해당 기간). 동의를 거부할 수 있으나, 거부 시 문의 접수가 제한됩니다.</div><label class="fld"><input type="checkbox" name="agree" required> 개인정보 수집·이용에 동의합니다 (필수)</label></div>'''
    return '''<div class="consent"><div class="box">[Privacy notice] We collect your company name, name, contact details, message and attachments to respond to your inquiry and manage our business relationship. Data is kept for up to 3 years after your inquiry is resolved, unless a longer period is required by law. You may request access, correction or deletion at any time. See our Privacy Policy for details, including transfers to Korea.</div><label class="fld"><input type="checkbox" name="agree" required> I agree to the collection and use of my personal data (required)</label></div>'''

def product_options(lang):
    k = lang == 'ko'
    o = [('', '선택해 주세요' if k else 'Select a product')]
    for g in GROUPS:
        for p in PRODUCTS:
            if p['group'] == g['id']:
                o.append((p['id'], '[%s] %s' % (g[lang]['short'], p[lang]['name'])))
    o.append(('etc', '기타 / 추천 요청' if k else 'Other / need a recommendation'))
    return o

# ================================================================== HOME
def page_home(lang):
    k = lang == 'ko'
    cur = lp(lang, '')
    L = lambda a, b: a if k else b
    slides = [
        ('hero-steel', ['FIRE', '<em class="ac">SAFETY</em>'], 'Aerogel Fire-Resistant Coatings',
         L('얇은 도막 하나로 철골·목재·케이블·콘크리트의 골든타임을 지킵니다.', 'A thin aerogel film that buys steel, timber, cables and concrete critical time in a fire.'),
         L('방화도료 보기', 'Fire-resistant coatings'), group_path(G['P10']), L('방화', 'Fire')),
        ('hero-roof', ['THERMAL', '<em class="ol">SHIELD</em>'], 'Aerogel Insulation Coatings',
         L('지붕과 외벽에 닿는 복사열을 막는 칠하는 단열재. 공장·물류센터의 여름을 바꿉니다.', 'A paint-on insulation that blocks solar heat on roofs and walls of factories and logistics centers.'),
         L('단열도료 보기', 'Insulation coatings'), group_path(G['P20']), L('단열', 'Insulation')),
        ('hero-pipes', ['HEAT', '<em class="ac">CONTROL</em>'], 'Industrial Thermal Solutions',
         L('200℃부터 1500℃까지. 배관·탱크·고온 설비의 열손실과 화상 위험을 줄입니다.', 'From 200 °C to 1500 °C: cutting heat loss and burn risk on pipes, tanks and hot equipment.'),
         L('산업 설비 분야', 'Industrial applications'), sector_path(SE['S20']), L('산업 설비', 'Industrial')),
        ('space-07', ['THIN', '<em class="ol">&amp; LIGHT</em>'], 'Battery Thermal Barriers',
         L('1~5mm 에어로젤 펠트와 0.05mm 필름으로 배터리 셀 사이의 열을 관리합니다.', '1–5 mm aerogel blankets and 0.05 mm film to manage heat between battery cells.'),
         L('모빌리티 분야', 'Mobility applications'), sector_path(SE['S50']), L('모빌리티', 'Mobility')),
    ]
    sl = ''
    for i, (im, kw, eb, tx, bl, bp, tab) in enumerate(slides):
        kwh = ''.join('<span><i>%s</i></span>' % w.replace('<em ', '<b ').replace('</em>', '</b>') for w in kw)
        sl += f'''<div class="slide{' on' if i == 0 else ''}" aria-roledescription="slide" aria-label="{i+1} / 4"><div class="bg" style="background-image:url('{img(cur, im)}')"></div><div class="wrap"><div class="kw" aria-hidden="true">{kwh}</div><div class="hero-copy"><span class="eyebrow">{eb}</span><p>{tx}</p><div class="hero-btns"><a class="btn btn-pri" href="{url(cur, lp(lang, bp))}">{bl} {ARROW}</a><a class="btn btn-ghost-w" href="{url(cur, lp(lang, 'contact/quote/'))}">{L('견적 문의', 'Request a Quote')}</a></div></div></div></div>'''
    tabs = ''.join('<button type="button" class="%s">%s</button>' % ('on' if i == 0 else '', s[6]) for i, s in enumerate(slides))
    hero = f'''<section class="hero" aria-roledescription="carousel" aria-label="{L('주요 솔루션', 'Key solutions')}">
<h1 class="sr-only">{L('EXOSKIN 엑소스킨 — 에어로젤 방화·단열 솔루션, 숴싱 신소재 한국 공식 총판', 'EXOSKIN — Aerogel fire protection and thermal insulation, Official Korea Distributor of Shuoxing New Materials')}</h1>
{sl}
<div class="hero-ctrl"><div class="wrap"><span class="hero-num"><b>01</b> <span>/ 04</span></span><span class="hero-bar"><i></i></span><button class="hero-pause" type="button" aria-label="{L('자동 넘김 정지', 'Pause')}" aria-pressed="false"><svg viewBox="0 0 12 12"><path d="M2 1h3v10H2zM7 1h3v10H7z" fill="currentColor"/></svg></button><div class="hero-tabs">{tabs}</div></div></div>
<div class="scroll-cue">SCROLL<i></i></div>
</section>'''.replace('<b class="ac">', '<b class="ac" style="font-weight:inherit">').replace('<b class="ol">', '<b class="ol" style="font-weight:inherit">')
    # hero kw em styles -> b with classes ac/ol (css .kw .ac/.ol)
    about = f'''<section class="sec dark"><div class="wrap">
<span class="eyebrow rv">About EXOSKIN</span>
<div class="kinetic rv">Aerogel<br><span class="ol">Fire</span> &amp; <span class="ac">Thermal</span><br>Solutions</div>
<div class="about-grid"><p class="rv">{L('<b>엑소스킨(EXOSKIN)</b>는 중국 숴싱 신소재(Shuoxing New Materials)가 생산하는 에어로젤 방화·단열 소재를 한국에 공급하는 <b>공식 총판 브랜드</b>입니다. 바깥(Exo)과 피부(Skin)를 합친 이름처럼, 건물과 설비를 얇은 보호 외피로 감싸 화재와 열로부터 지킵니다.', '<b>EXOSKIN</b> is the <b>official Korea distributor brand</b> for aerogel fire-protection and insulation materials made by Shuoxing New Materials in China. True to its name, Exo + Skin, it wraps buildings and equipment in a thin protective outer skin against fire and heat.')}</p>
<div class="rv d1"><p>{L('운영사 주식회사 에코아트가 수입 검수부터 국내 재고·납기, 현장 기술 상담까지 책임집니다.', 'Operated by ECOART Co., Ltd., we handle inspection, logistics, technical support and partner enablement from Korea.')}</p><p style="margin-top:28px"><a class="btn btn-ghost-w" href="{url(cur, lp(lang, 'about/ecoshield/'))}">{L('엑소스킨 소개', 'About EXOSKIN')} {ARROW}</a></p></div></div>
<div class="stats rv"><div class="stat"><b>180<small>{L('분', 'min')}</small></b><span>{L('최대 내화시간 (철골·콘크리트용)', 'Max. fire resistance (steel & concrete)')}</span></div><div class="stat"><b>1500<small>℃</small></b><span>{L('고온 내열 도료 최고 등급', 'Top grade, high-temp coating')}</span></div><div class="stat"><b>0.021</b><span>{L('단열 펠트 열전도율 W/(m·K)', 'Blanket thermal conductivity W/(m·K)')}</span></div><div class="stat"><b>11<small>{L('종', '')}</small></b><span>{L('4개 제품군 라인업', 'Products in 4 families')}</span></div></div>
{note_test(lang)}
</div></section>'''
    gcards = ''
    for i, g in enumerate(GROUPS):
        items = ''.join('<li>%s</li>' % esc(p[lang]['name']) for p in PRODUCTS if p['group'] == g['id'])
        gcards += f'''<a class="gcard rv d{i}" href="{url(cur, lp(lang, group_path(g)))}"><img src="{img(cur, g['img'])}" alt="" loading="lazy"><span class="arrow">{ARROW}</span><div class="in"><span class="num">0{i+1} · {esc(g[lang]['short'])}</span><h3>{esc(g[lang]['name'])}</h3><p>{esc(g[lang]['lead'])}</p><ul>{items}</ul></div></a>'''
    products = f'''<section class="sec"><div class="wrap">
{sec_hd('Products', L('4개 제품군, 11가지<br>에어로젤 솔루션', 'Four families,<br>eleven aerogel solutions'), L('방화·단열 도료부터 펠트, 필름까지. 칠하고, 감싸고, 붙이는 방식으로 현장 조건에 맞춰 선택하세요.', 'Coatings, blankets and film: paint it, wrap it or stick it, whatever your site requires.'), '<a class="more rv" href="%s">%s %s</a>' % (url(cur, lp(lang, 'products/')), L('전체 제품 보기', 'All products'), ARROW))}
<div class="groups">{gcards}</div></div></section>'''
    tabs2 = ''.join('<button type="button" data-t="%s" class="%s">%s</button>' % (s['id'], 'on' if i == 0 else '', esc(s[lang]['name'])) for i, s in enumerate(SECTORS))
    panels = ''
    for i, s in enumerate(SECTORS):
        sps = [sp for sp in SPACES if sp['sector'] == s['id']]
        rec = []
        for sp in sps:
            for pid in sp['products']:
                if pid not in rec: rec.append(pid)
        panels += f'''<div class="app-panel{' on' if i == 0 else ''}" data-panel="{s['id']}"><div class="img"><img src="{img(cur, s['img'])}" alt="" loading="lazy"></div><div class="txt"><span class="eyebrow">0{i+1}</span><h3>{esc(s[lang]['name'])}</h3><p>{esc(s[lang]['desc'])}</p>
<ul class="spec-list"><li><b>{L('고객 과제', 'Challenge')}</b><span>{esc(s[lang]['problem'])}</span></li><li><b>{L('주요 공간', 'Key spaces')}</b><span>{esc(' · '.join(sp[lang]['name'] for sp in sps))}</span></li><li><b>{L('추천 제품', 'Products')}</b><span>{esc(' · '.join(PR[p][lang]['name'] for p in rec[:4]))}{' …' if len(rec) > 4 else ''}</span></li></ul>
<a class="more" href="{url(cur, lp(lang, sector_path(s)))}">{L('분야 자세히 보기', 'Explore this sector')} {ARROW}</a></div></div>'''
    apps = f'''<section class="sec soft" data-tabscope><div class="wrap">
{sec_hd('Applications', L('우리 현장에는<br>무엇을 써야 할까요?', 'What does<br>your site need?'), L('5개 분야, 22개 시공 공간별로 고객의 과제와 추천 제품을 정리했습니다.', 'Challenges and recommended products for 22 spaces across 5 sectors.'), '<a class="more rv" href="%s">%s %s</a>' % (url(cur, lp(lang, 'applications/')), L('전체 적용분야', 'All applications'), ARROW))}
<div class="app-tabs rv" data-tabs role="tablist">{tabs2}</div>{panels}</div></section>'''
    tech = f'''<section class="sec"><div class="wrap split">
<div class="ph rv"><img src="{img(cur, 'scene-08')}" alt="{L('에어로젤 펠트로 배관을 감싸는 시공 장면', 'Wrapping a pipe with aerogel blanket')}" loading="lazy"></div>
<div class="rv d1"><span class="eyebrow">Aerogel Technology</span><h2 class="h2">{L('공기로 열을 막는 소재,<br>에어로젤', 'A material that stops heat<br>with air')}</h2>
<p class="lead">{L('에어로젤은 나노미터 크기의 기공 속에 공기를 가둔 초경량 고체입니다. 부피 대부분이 공기라 열이 지나갈 길이 극도로 좁고, 그래서 얇은 두께로도 높은 단열 성능을 냅니다.', 'Aerogel is an ultra-light solid that traps air in nanometer-scale pores. Because it is mostly air, heat has almost no path to travel, so even thin layers insulate strongly.')}</p>
<ul class="checks"><li>{ic('check')}<span><b>{L('얇고 가볍게', 'Thin and light')}</b> — {L('기존 보온재·내화보드 대비 적은 두께와 무게', 'less thickness and weight than conventional insulation or fire boards')}</span></li><li>{ic('check')}<span><b>{L('불연·난연', 'Non-combustible')}</b> — {L('무기질 실리카 기반의 A급 소재', 'Class A, inorganic silica-based materials')}</span></li><li>{ic('check')}<span><b>{L('칠하고 감싸고 붙이고', 'Paint, wrap, stick')}</b> — {L('도료·펠트·필름으로 형상과 공간에 맞게 시공', 'coatings, blankets and film for any shape or space')}</span></li></ul>
<p style="margin-top:36px"><a class="btn btn-line" href="{url(cur, lp(lang, 'technology/aerogel/'))}">{L('에어로젤 기술 알아보기', 'Learn about aerogel')} {ARROW}</a></p></div></div></section>'''
    scenes = [('scene-01', 'P11', L('샌드위치 패널 공장 · 철골 내화', 'Panel factory · Steel fireproofing')), ('scene-02', 'P21', L('물류센터 · 지붕 차열 단열', 'Logistics center · Roof cooling')),
              ('scene-03', 'P22', L('오피스텔 · 내벽 결로 방지', 'Apartment · Anti-condensation')), ('scene-04', 'P23', L('플랜트 · 고온 배관 보온', 'Plant · Hot pipe insulation')),
              ('scene-05', 'P13', L('케이블 트레이 · 방화', 'Cable trays · Fire retardant')), ('scene-06', 'P12', L('체육관 · 목재 트러스 방화', 'Gym · Timber truss protection')),
              ('scene-07', 'P14', L('지하주차장 · 콘크리트 내화', 'Parking garage · Concrete fireproofing')), ('scene-08', 'P31', L('기계실 · 에어로젤 펠트', 'Plant room · Aerogel blanket')),
              ('photo-steel', 'P11', L('철골 구조 · 내화도장 작업', 'Steel frame · Fireproof coating')), ('photo-timber', 'P12', L('목재 벽체 · 방화도료 분사', 'Timber wall · Spray application')),
              ('photo-valves', 'P23', L('배관·밸브 · 보온 도장', 'Pipes & valves · Insulation coating')), ('photo-electrical', 'P13', L('전기 설비 · 방화·방습 코팅', 'Electrical equipment · Protective coating')),
              ('photo-furnace', 'P24', L('용해로·고온 설비 · 초고온 단열', 'Furnaces · Ultra-high-temp insulation')), ('photo-roof', 'P21', L('건물 옥상 · 차열 단열 도장', 'Rooftop · Heat-reflective coating'))]
    cards = ''.join(f'''<a class="scard" href="{url(cur, lp(lang, product_path(PR[p])))}"><div class="ph"><img src="{img(cur, s)}" alt="" loading="lazy"></div><span class="cat">{esc(t)}</span><h4>{esc(PR[p][lang]['name'])}</h4></a>''' for s, p, t in scenes)
    strip = f'''<section class="sec soft" style="overflow:hidden"><div class="wrap">{sec_hd('In Action', L('현장에서 만나는 엑소스킨', 'EXOSKIN on site'), L('시공 방식과 적용 공간을 장면으로 확인하세요. (이미지는 적용 예시를 표현한 연출 이미지입니다)', 'See how each product is applied. (Images are illustrative.)'), '<div class="strip-ctrl rv" data-strip="#strip"><button type="button" data-dir="prev" aria-label="prev" style="transform:scaleX(-1)">%s</button><button type="button" data-dir="next" aria-label="next">%s</button></div>' % (ARROW, ARROW))}</div>
<div class="strip" id="strip">{cards}</div></section>'''
    tiles = [('target', L('제품 선택 가이드', 'Product Finder'), L('공간·온도·목적 3가지만 고르면 맞는 제품을 추천합니다.', 'Pick space, temperature and purpose to get a recommendation.'), 'products/finder/'),
             ('doc', L('카탈로그·브로슈어', 'Catalogs'), L('국문·영문 종합 카탈로그와 제품군별 리플릿.', 'Korean and English catalogs and product leaflets.'), 'resources/catalogs/'),
             ('box', 'TDS·SDS', L('제품별 기술자료와 안전보건자료(MSDS).', 'Technical and safety data sheets for each product.'), 'resources/data-sheets/'),
             ('tool', L('기술 상담', 'Technical Consultation'), L('도면·사양서를 첨부하면 엔지니어가 사양을 검토합니다.', 'Attach drawings and specs for an engineering review.'), 'contact/technical/')]
    tl = ''.join(f'''<a class="tile rv d{i}" href="{url(cur, lp(lang, p))}"><span class="ico">{ic(icn)}</span><h3>{t}</h3><p>{d}</p><span class="more">{L('바로가기', 'Go')} {ARROW}</span></a>''' for i, (icn, t, d, p) in enumerate(tiles))
    support = f'''<section class="sec"><div class="wrap">{sec_hd('Support', L('설계부터 시공까지,<br>필요한 자료를 한곳에', 'Everything you need,<br>from design to installation'))}<div class="tiles">{tl}</div></div></section>'''
    partner = ''
    if not k:
        partner = f'''<section class="sec dark"><div class="wrap split"><div class="rv"><span class="eyebrow">Global Partnership</span><h2 class="h2">Grow with EXOSKIN<br>in your market</h2><p class="lead">We are looking for distributors, applicators and EPC partners who want to bring aerogel fire protection and insulation to their customers. Tell us about your business and target market, and we will reply within 2 business days (Korea time).</p><div class="hero-btns"><a class="btn btn-pri" href="{url(cur, 'en/contact/partner/')}">Become a Partner {ARROW}</a><a class="btn btn-ghost-w" href="{url(cur, 'en/about/global-network/')}">Global Network</a></div></div>
<div class="rv d1"><div class="tiles c2">{''.join('<div class="tile"><span class="ico">%s</span><h4 style="color:#fff">%s</h4><p>%s</p></div>' % (ic(a), b, c) for a, b, c in [('users', 'Training', 'Product and application training for your team.'), ('box', 'Samples', 'Sample kits for qualification and customer trials.'), ('doc', 'Sales materials', 'English catalogs, TDS/SDS and marketing assets.'), ('tool', 'Technical support', 'Specification review and on-site guidance.')])}</div></div></div></section>'''
    news_items = news_list(lang)
    news = f'''<section class="sec tight soft"><div class="wrap">{sec_hd('Newsroom', L('엑소스킨 소식', 'News'), '', '<a class="more rv" href="%s">%s %s</a>' % (url(cur, lp(lang, 'news/notices/')), L('전체 보기', 'View all'), ARROW))}
<div class="news rv">{''.join('<a href="%s"><span class="cat">%s</span><h4>%s</h4><time>%s</time></a>' % (url(cur, lp(lang, 'news/notices/#' + n['id'])), n['cat'], n['t'], n['date']) for n in news_items)}</div></div></section>'''
    body = hero + about + products + apps + tech + strip + partner + support + news + cta_band(lang, cur)
    write(lang, cur, '', L('엑소스킨(EXOSKIN)은 숴싱 신소재 한국 공식 총판으로, 에어로젤 방화도료·단열도료·단열 펠트·단열 필름 11종을 공급합니다. 견적·샘플 문의, TDS·SDS 자료 제공.',
                          'EXOSKIN, Official Korea Distributor of Shuoxing New Materials: aerogel fire-resistant coatings, insulation coatings, blankets and film. Request a quote or become a partner.'),
          body, over=True, keywords=L('에어로젤 방화도료, 에어로젤 단열도료, 내화도료, 철골 내화도료, 단열 펠트, 에어로젤 필름, 숴싱, 엑소스킨', 'aerogel fireproofing coating, aerogel insulation coating, aerogel blanket, thermal barrier, EXOSKIN, Shuoxing'))

def news_list(lang):
    if lang == 'ko':
        return [dict(id='n2', cat='공지', t='제품별 TDS·SDS 및 카탈로그 순차 등록 안내', date='2026.11.18',
                     body='제조사 숴싱 신소재로부터 자료를 받는 대로 자료실에 제품별 기술자료(TDS), 안전보건자료(SDS), 국문·영문 카탈로그를 순차 등록합니다. 먼저 필요하신 자료는 자료 요청으로 문의해 주세요.'),
                dict(id='n1', cat='뉴스', t='엑소스킨(EXOSKIN) 홈페이지를 오픈했습니다', date='2026.11.18',
                     body='에어로젤 방화·단열 소재 전문 브랜드 엑소스킨의 공식 홈페이지를 열었습니다. 제품 11종의 사양과 적용분야, 견적·샘플 문의를 한곳에서 확인하실 수 있습니다.')]
    return [dict(id='n2', cat='Notice', t='TDS, SDS and catalogs will be added progressively', date='Nov 18, 2026',
                 body='We will publish technical data sheets, safety data sheets and English catalogs as we receive them from the manufacturer. If you need a document now, please send us a request.'),
            dict(id='n1', cat='News', t='The EXOSKIN website is now live', date='Nov 18, 2026',
                 body='Our new website brings together specifications, applications and quote requests for all eleven EXOSKIN aerogel products.')]

# ================================================================== ABOUT
def page_about(lang):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    crumbs0 = (L('회사소개', 'About Us'), 'about/ecoshield/')
    # --- ecoshield
    cur = lp(lang, 'about/ecoshield/')
    body = subvis(lang, cur, L('엑소스킨 소개', 'About EXOSKIN'), L('에어로젤 방화·단열 소재 전문 브랜드, 숴싱 신소재 한국 공식 총판', 'Aerogel fire protection and insulation, Official Korea Distributor of Shuoxing New Materials'), 'space-08', [crumbs0, (L('엑소스킨 소개', 'About EXOSKIN'), None)]) + lnb(lang, cur, 'about')
    biz = [('box', L('수입·유통', 'Import & distribution'), L('숴싱 신소재 에어로젤 제품의 국내 수입, 재고 운영, 대리점 공급', 'Importing Shuoxing aerogel products, managing stock and supplying partners')),
           ('tool', L('기술 상담', 'Technical support'), L('도면 검토, 제품 선정, 소요량 산출, 시공 가이드 제공', 'Drawing review, product selection, quantity take-off, application guidance')),
           ('users', L('시공 파트너', 'Applicator network'), L('도장·단열·소방 시공사와의 파트너 네트워크 구축', 'Building a network of coating, insulation and fire-protection contractors')),
           ('globe', L('해외 협력', 'International cooperation'), L('유통사·EPC와의 협력 문의 창구', 'A contact point for distributors and EPC partners'))]
    body += f'''<div class="page"><div class="wrap">
<div class="block split"><div class="rv"><span class="eyebrow">Greeting</span><h2 class="h2">{L('더 얇게, 더 안전하게.<br>지켜야 할 것을 지킵니다.', 'Thinner, safer,<br>protecting what matters.')}</h2></div>
<div class="prose rv d1"><p>{L('안녕하십니까. 엑소스킨을 찾아 주셔서 감사합니다.', 'Thank you for visiting EXOSKIN.')}</p><p>{L('화재 안전과 에너지 효율은 이제 건물과 설비를 설계할 때 가장 먼저 따지는 기준이 되었습니다. 엑소스킨은 에어로젤이라는 소재로 이 두 가지 과제를 함께 풀고자 합니다. 얇고 가벼우면서도 불에 강하고 열을 막는 에어로젤은 기존 내화·단열 방식으로는 어려웠던 현장에 새로운 선택지가 됩니다.', 'Fire safety and energy efficiency now come first when buildings and plants are designed. EXOSKIN tackles both with aerogel, a material that is thin and light yet resists fire and blocks heat, opening options where conventional fireproofing and insulation fall short.')}</p><p>{L('우리는 제조사 숴싱 신소재와 긴밀히 협력하여 검증된 제품을 들여오고, 국내 현장에 맞는 기술 자료와 시공 지원을 함께 제공하겠습니다. 고객의 현장을 가장 잘 이해하는 파트너가 되겠습니다.', 'Working closely with Shuoxing New Materials, we import proven products and back them with technical documentation and on-site support suited to each project.')}</p><p><b>{L('주식회사 에코아트 · EXOSKIN 대표 심종훈', 'Jonghun Shim, CEO, ECOART Co., Ltd. (EXOSKIN)')}</b></p></div></div>
<div class="block"><div class="sec-hd"><div class="rv"><span class="eyebrow">Vision &amp; Mission</span><h2 class="h3">{L('비전과 미션', 'Vision and mission')}</h2></div></div>
<div class="tiles c2"><div class="tile rv" style="background:var(--navy);border:0"><span class="tag" style="color:var(--lime)">VISION</span><h3 style="color:#fff">{L('에어로젤 방화·단열의 기준이 되는 브랜드', 'The benchmark brand for aerogel fire protection and insulation')}</h3></div><div class="tile rv d1"><span class="tag">MISSION</span><h3>{L('검증된 소재와 정직한 기술 정보로 사람과 자산을 지킨다', 'Protect people and assets with proven materials and honest technical information')}</h3></div></div></div>
<div class="block"><div class="sec-hd"><div class="rv"><span class="eyebrow">Business</span><h2 class="h3">{L('사업 영역', 'What we do')}</h2></div></div><div class="tiles">{''.join('<div class="tile rv d%d"><span class="ico">%s</span><h3>%s</h3><p>%s</p></div>' % (i, ic(a), b, c) for i, (a, b, c) in enumerate(biz))}</div></div>
<div class="block split" style="align-items:start"><div class="rv"><span class="eyebrow">Company</span><h2 class="h3">{L('운영사 정보', 'Company information')}</h2>
<div class="tbl-wrap" style="margin-top:28px"><table class="tbl"><tbody>
<tr><th>{L('브랜드', 'Brand')}</th><td>EXOSKIN ({L('엑소스킨', 'Exo + Skin')})</td></tr>
<tr><th>{L('법인명(운영사)', 'Company')}</th><td>{L(SITE['operator_ko'], SITE['operator_en'])} · <a href="{SITE['operator_url']}" target="_blank" rel="noopener">eco-art.kr</a></td></tr>
<tr><th>{L('대표자', 'CEO')}</th><td>{L(SITE['ceo_ko'], SITE['ceo_en'])}</td></tr>
<tr><th>{L('설립', 'Established')}</th><td>{L('2024년 3월', 'March 2024')}</td></tr>
<tr><th>{L('사업자등록번호', 'Business reg. no.')}</th><td>{SITE['bizno']}</td></tr>
<tr><th>{L('법인등록번호', 'Corporate reg. no.')}</th><td>{SITE['corpno']}</td></tr>
<tr><th>{L('업태 / 종목', 'Business type')}</th><td>{L('도매업·도소매업 / 건축자재·철물·공구 등, 전자상거래 소매업', 'Wholesale &amp; retail of building materials, hardware and tools; e-commerce retail')}</td></tr>
<tr><th>{L('본점 소재지', 'Head office')}</th><td>{L(SITE['addr_ko'], SITE['addr_en'])}</td></tr>
<tr><th>{L('대표전화', 'Tel')}</th><td><a href="tel:{SITE['tel_link']}">{L(SITE['tel'], SITE['tel_intl'])}</a></td></tr>
<tr><th>{L('이메일', 'Email')}</th><td><a href="mailto:{SITE['email']}">{SITE['email']}</a></td></tr>
<tr><th>{L('제조 파트너', 'Manufacturer')}</th><td>{L('숴싱 신소재 (Shuoxing New Materials, 중국)', 'Shuoxing New Materials (China)')}</td></tr>
<tr><th>{L('웹사이트', 'Website')}</th><td>www.eco-shield.co.kr</td></tr></tbody></table></div></div>
<div class="rv d1"><span class="eyebrow">History</span><h2 class="h3">{L('연혁', 'History')}</h2><ul class="tl" style="margin-top:32px"><li><b>2026.11</b><span>{L('EXOSKIN 브랜드 수립, 홈페이지 오픈', 'EXOSKIN brand launched, website opened')}</span></li><li><b>2026</b><span>{L('숴싱 신소재 에어로젤 제품 한국 공급 준비', 'Preparing supply of Shuoxing aerogel products in Korea')}</span></li><li><b>2024.03</b><span>{L('주식회사 에코아트 설립', 'ECOART Co., Ltd. founded')}</span></li></ul><p class="note">{L('※ 연혁은 주요 일정 확정 시 업데이트합니다.', '※ Updated as milestones are confirmed.')}</p></div></div>
</div></div>''' + cta_band(lang, cur)
    write(lang, cur, L('엑소스킨 소개', 'About EXOSKIN'), L('엑소스킨은 숴싱 신소재 에어로젤 방화·단열 소재의 한국 공식 총판 브랜드입니다. 운영사 주식회사 에코아트.', 'EXOSKIN is the official Korea distributor brand for Shuoxing aerogel materials, operated by ECOART Co., Ltd.'), body)

    # --- brand
    cur = lp(lang, 'about/brand/')
    body = subvis(lang, cur, L('브랜드 스토리', 'Brand Story'), 'Safety wherever protection is needed.', 'space-01', [crumbs0, (L('브랜드 스토리', 'Brand Story'), None)]) + lnb(lang, cur, 'about')
    prom = [('feather', L('더 얇게', 'Thinner'), L('공간과 무게를 덜 차지하는 소재로 설계의 자유를 넓힙니다.', 'Materials that take less space and weight, freeing up design.')),
            ('shield', L('더 안전하게', 'Safer'), L('화재와 고열로부터 사람과 구조물을 지키는 성능에 집중합니다.', 'Focused on protecting people and structures from fire and heat.')),
            ('leaf', L('더 정직하게', 'More honest'), L('시험 기준과 원산지를 분명히 밝히고, 확인된 정보만 말합니다.', 'We state test bases and origin clearly and claim only what is verified.'))]
    body += f'''<div class="page"><div class="wrap">
<div class="block split"><div class="rv"><span class="eyebrow">Brand</span><h2 class="h2">EXO + SKIN</h2><p class="lead">{L('엑소스킨은 바깥(Exo)과 피부(Skin)를 합친 이름으로, 몸 바깥을 감싸 지키는 외골격(Exoskeleton)에서 왔습니다. 건물과 설비를 얇은 보호 외피로 감싸 화재와 열로부터 지킨다는 약속을 담았습니다.', 'EXOSKIN combines Exo (outer) and Skin, inspired by the exoskeleton that protects from the outside: a promise to wrap buildings and equipment in a thin protective skin against fire and heat.')}</p></div>
<div class="rv d1" style="background:var(--soft);border-radius:var(--radius);padding:64px 48px;display:grid;place-items:center"><img src="{asset(cur, 'img/logo-center.png')}" alt="EXOSKIN logo" style="width:100%;max-width:360px"></div></div>
<div class="block"><div class="sec-hd"><div class="rv"><span class="eyebrow">Logo</span><h2 class="h3">{L('로고의 의미', 'About the logo')}</h2></div></div>
<div class="tiles c3"><div class="tile rv"><span class="ico" style="background:#E90102;color:#fff">{ic('leaf')}</span><h3>{L('빨강 · EXO', 'Red · EXO')}</h3><p>{L('바깥에서 먼저 막아서는 힘, 그리고 불을 다스리는 기술을 뜻합니다.', 'The strength that stands guard on the outside, and the technology that keeps fire in check.')}</p></div>
<div class="tile rv d1"><span class="ico" style="background:#001288;color:#fff">{ic('shield')}</span><h3>{L('남색 · SKIN', 'Navy · SKIN')}</h3><p>{L('대상을 빈틈없이 감싸는 얇은 보호 외피, 그리고 신뢰를 뜻합니다.', 'A thin protective skin that wraps every surface, and the trust behind it.')}</p></div>
<div class="tile rv d2"><span class="ico" style="background:#fff;border:1px solid var(--line);padding:6px"><img src="{asset(cur, 'img/symbol.png')}" alt="" style="width:100%"></span><h3>{L('E·S 큐브 심볼', 'E·S cube symbol')}</h3><p>{L('EXO의 E와 SKIN의 S를 맞물려 만든 입체 큐브. 바깥을 단단히 감싸 지키는 외피 구조와 안전을 상징합니다.', 'The E of EXO and the S of SKIN interlocked into a solid cube: an outer shell that protects firmly, wherever it is needed.')}</p></div></div>
<div class="callout rv"><b>Tagline</b> — Safety wherever protection is needed. {L('(필요한 곳 어디서나, 안전을 지키는 기술)', '')}</div>
<div class="chipset rv" style="margin-top:28px"><span class="chip" style="background:#E90102;color:#fff">Red #E90102</span><span class="chip" style="background:#001288;color:#fff">Navy #001288</span><span class="chip" style="background:#1A2BE8;color:#fff">Blue #1A2BE8</span><span class="chip">Gray #3B4550</span></div></div>
<div class="block"><div class="sec-hd"><div class="rv"><span class="eyebrow">Promise</span><h2 class="h3">{L('브랜드 약속', 'Our promises')}</h2></div></div><div class="tiles c3">{''.join('<div class="tile rv d%d"><span class="ico">%s</span><h3>%s</h3><p>%s</p></div>' % (i, ic(a), b, c) for i, (a, b, c) in enumerate(prom))}</div></div>
</div></div>''' + cta_band(lang, cur)
    write(lang, cur, L('브랜드 스토리', 'Brand Story'), L('EXOSKIN 이름과 로고의 의미, 브랜드 약속.', 'The meaning behind the EXOSKIN name and logo, and our brand promises.'), body)

    # --- manufacturer
    cur = lp(lang, 'about/manufacturer/')
    body = subvis(lang, cur, L('제조 파트너', 'Manufacturing Partner'), L('숴싱 신소재(Shuoxing New Materials)', 'Shuoxing New Materials'), 'space-12', [crumbs0, (L('제조 파트너', 'Manufacturing Partner'), None)]) + lnb(lang, cur, 'about')
    body += f'''<div class="page"><div class="wrap">
<div class="block split"><div class="rv"><span class="eyebrow">Manufacturer</span><h2 class="h2">{L('제조원을<br>분명히 밝힙니다', 'We are clear<br>about origin')}</h2><p class="lead">{L('엑소스킨의 모든 제품은 중국 숴싱 신소재(Shuoxing New Materials)가 생산하며, 엑소스킨(주식회사 에코아트)는 한국 공식 총판으로서 수입·유통과 기술 지원을 맡습니다.', 'All EXOSKIN products are manufactured by Shuoxing New Materials in China. EXOSKIN (ECOART Co., Ltd.) is the official Korea distributor, handling import, distribution and technical support.')}</p>
<div class="callout"><b>{L('원산지 표기', 'Country of origin')}</b> — {L('제조국: 중국 (Made in China). 제품 포장·서류(원산지증명서, TDS·SDS)에 제조원과 원산지를 표기합니다.', 'Made in China. Manufacturer and origin are shown on packaging and documents (certificate of origin, TDS/SDS).')}</div></div>
<div class="ph rv d1"><img src="{img(cur, 'space-12')}" alt="" loading="lazy"><figcaption style="position:absolute;left:16px;bottom:14px;font-size:12px;color:#fff;background:rgba(8,26,46,.6);padding:4px 10px;border-radius:999px">{L('연출 이미지 · 제조사 공장 사진 수령 후 교체', 'Illustrative · to be replaced with factory photos')}</figcaption></div></div>
<div class="block"><h2 class="h3 rv">{L('회사 개요', 'Company overview')}</h2><div class="tbl-wrap rv" style="margin-top:28px"><table class="tbl"><tbody>
<tr><th>{L('회사명', 'Company')}</th><td>{L('숴싱 신소재 (Shuoxing New Materials)', 'Shuoxing New Materials')}</td></tr>
<tr><th>{L('소재지', 'Location')}</th><td>{L('중국', 'China')} <span class="pending">{L('상세 주소 확인 중', 'Details to be confirmed')}</span></td></tr>
<tr><th>{L('주요 제품', 'Main products')}</th><td>{L('에어로젤 방화도료, 에어로젤 보온·단열 도료, 에어로젤 단열 펠트, 에어로젤 단열 필름', 'Aerogel fire-resistant coatings, insulation coatings, blankets and film')}</td></tr>
<tr><th>{L('수출 실적', 'Export references')}</th><td>{L('캐나다, 한국, 인도네시아, 필리핀, 태국 (철골 구조용 내화도료 기준, 제조사 자료)', 'Canada, Korea, Indonesia, the Philippines, Thailand (steel fireproofing coating, per manufacturer)')}</td></tr>
<tr><th>{L('한국 총판', 'Korea distributor')}</th><td>{L('EXOSKIN (주식회사 에코아트)', 'EXOSKIN (ECOART Co., Ltd.)')}</td></tr></tbody></table></div></div>
<div class="block"><h2 class="h3 rv">{L('준비 중인 자료', 'Coming soon')}</h2><div class="tiles" style="margin-top:28px">{''.join('<div class="tile rv"><span class="ico">%s</span><h4>%s</h4><p><span class="pending">%s</span></p></div>' % (ic(a), b, L('자료 수령 후 게시', 'To be published')) for a, b in [('box', L('생산설비·연구소 사진', 'Plant & R&D photos')), ('doc', L('특허 목록', 'Patents')), ('globe', L('수출 실적 상세', 'Export details')), ('flag', L('한국 공식 총판 인증서', 'Korea distributorship certificate'))])}</div></div>
<div class="block" style="text-align:center"><a class="btn btn-navy" href="{url(cur, lp(lang, 'technology/certifications/'))}">{L('인증·시험성적서 보기', 'View test reports')} {ARROW}</a></div>
</div></div>'''
    write(lang, cur, L('제조 파트너', 'Manufacturing Partner'), L('엑소스킨 제품의 제조원 숴싱 신소재(중국) 소개와 원산지 안내.', 'About Shuoxing New Materials (China), manufacturer of EXOSKIN products.'), body)

    # --- quality
    cur = lp(lang, 'about/quality/')
    body = subvis(lang, cur, L('품질·공급 체계', 'Quality & Supply'), L('수입품의 품질과 납기, 엑소스킨이 책임집니다.', 'Quality and delivery you can rely on.'), 'space-11', [crumbs0, (L('품질·공급 체계', 'Quality & Supply'), None)]) + lnb(lang, cur, 'about')
    steps = [(L('생산·출하 검사', 'Production & QC'), L('제조사 공정 검사 및 출하 전 로트별 품질 확인', 'Manufacturer in-process checks and lot inspection before shipment')),
             (L('수입·통관', 'Import & customs'), L('원산지증명서·SDS 등 서류 확인 후 통관', 'Customs clearance with certificate of origin and SDS')),
             (L('입고 검수', 'Incoming inspection'), L('외관·수량·로트 번호·유효기간 확인', 'Checks on appearance, quantity, lot number and shelf life')),
             (L('출고·기술 지원', 'Delivery & support'), L('현장 납품과 시공 가이드·기술 상담 제공', 'Site delivery with application guidance and technical support'))]
    body += f'''<div class="page"><div class="wrap">
<div class="block"><span class="eyebrow rv">Process</span><h2 class="h3 rv">{L('수입 검수 절차', 'Supply process')}</h2><div class="steps">{''.join('<div class="step rv d%d"><h4>%s</h4><p>%s</p></div>' % (i, a, b) for i, (a, b) in enumerate(steps))}</div></div>
<div class="block"><div class="tiles">{''.join('<div class="tile rv d%d"><span class="ico">%s</span><h3>%s</h3><p>%s</p></div>' % (i, ic(a), b, c) for i, (a, b, c) in enumerate([
    ('target', L('로트 관리', 'Lot traceability'), L('입고 로트 번호를 기록해 출고 현장까지 추적합니다.', 'Lot numbers are recorded and traced to each delivery.')),
    ('box', L('국내 재고', 'Local stock'), L('주력 제품은 국내 재고를 운영해 납기를 줄입니다.', 'Key products are stocked in Korea to shorten lead times.')),
    ('tool', L('기술 지원', 'Technical support'), L('시공 전 바탕 점검, 시공 중 품질 확인을 지원합니다.', 'Substrate checks before and quality checks during application.')),
    ('doc', L('서류 지원', 'Documentation'), L('TDS·SDS, 원산지증명서, 시험성적서를 제공합니다.', 'TDS, SDS, certificate of origin and test reports.'))]))}</div></div>
{'' if k else '<div class="block"><h2 class="h3 rv">Export terms</h2><div class="tbl-wrap rv" style="margin-top:28px"><table class="tbl"><tbody><tr><th>Port of loading</th><td>Confirmed per order (Korea or direct from manufacturer)</td></tr><tr><th>MOQ</th><td>Confirmed per product and market</td></tr><tr><th>Lead time</th><td>Confirmed per order and quantity</td></tr><tr><th>Packaging</th><td>Pallet quantity per product: to be published with catalogs</td></tr><tr><th>Incoterms</th><td>FOB / CIF / DAP on request</td></tr></tbody></table></div></div>'}
</div></div>''' + cta_band(lang, cur)
    write(lang, cur, L('품질·공급 체계', 'Quality & Supply'), L('엑소스킨의 수입 검수 절차, 로트 관리, 국내 재고와 기술 지원 체계.', 'EXOSKIN supply process: inspection, lot traceability, local stock and technical support.'), body)

    # --- global network
    cur = lp(lang, 'about/global-network/')
    body = subvis(lang, cur, L('글로벌 네트워크', 'Global Network'), L('제조 거점과 한국 총판, 그리고 함께할 파트너', 'Manufacturer, Korea distributor and partners to come'), 'space-02', [crumbs0, (L('글로벌 네트워크', 'Global Network'), None)]) + lnb(lang, cur, 'about')
    world = '''<svg class="world" viewBox="0 0 1000 420" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><defs><pattern id="dots" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.6" fill="rgba(255,255,255,.14)"/></pattern></defs><rect width="1000" height="420" fill="url(#dots)"/>
<path d="M710 170 Q760 120 802 150" fill="none" stroke="#FF4B4B" stroke-width="2" stroke-dasharray="6 6"/>
<circle cx="700" cy="178" r="9" fill="#F26B1D"/><circle cx="700" cy="178" r="20" fill="none" stroke="#F26B1D" opacity=".5"/>
<circle cx="806" cy="150" r="9" fill="#FF4B4B"/><circle cx="806" cy="150" r="22" fill="none" stroke="#FF4B4B" opacity=".5"/>
<g fill="rgba(255,255,255,.55)"><circle cx="230" cy="150" r="5"/><circle cx="480" cy="130" r="5"/><circle cx="560" cy="220" r="5"/><circle cx="740" cy="260" r="5"/><circle cx="860" cy="320" r="5"/><circle cx="320" cy="300" r="5"/></g>
<text x="716" y="206" fill="#fff" font-size="15" font-weight="700">MANUFACTURER · CHINA</text><text x="822" y="140" fill="#fff" font-size="15" font-weight="700">EXOSKIN · KOREA</text></svg>'''
    body += f'''<div class="page"><div class="wrap">
<div class="block"><div class="map-box rv">{world}<div class="map-legend"><span><i style="background:#FF4B4B"></i>{L('한국 총판 (EXOSKIN)', 'Korea distributor (EXOSKIN)')}</span><span><i style="background:#F26B1D"></i>{L('제조 거점 (숴싱 신소재, 중국)', 'Manufacturer (Shuoxing, China)')}</span><span><i style="background:rgba(255,255,255,.55)"></i>{L('파트너 모집 지역', 'Partner opportunities')}</span></div></div>
<p class="note">{L('※ 해외 파트너 모집 지역은 제조사와의 총판 계약 범위가 확정되는 대로 표시합니다.', '※ Partner regions are shown as agreements are confirmed.')}</p></div>
<div class="block split" style="align-items:start"><div class="rv"><span class="eyebrow">Partnership</span><h2 class="h3">{L('파트너 혜택', 'Partner benefits')}</h2><p class="lead">{L('국내 대리점·시공 파트너와 해외 유통사·EPC 파트너에게 제품 교육, 샘플, 영업 자료, 기술 지원을 제공합니다.', 'Distributors, applicators and EPC partners receive product training, samples, sales materials and technical support.')}</p><p style="margin-top:28px"><a class="btn btn-pri" href="{url(cur, lp(lang, 'contact/partner/'))}">{L('파트너 신청', 'Become a Partner')} {ARROW}</a></p></div>
<div class="rv d1"><div class="tbl-wrap"><table class="tbl"><thead><tr><th>{L('구분', 'Region')}</th><th>{L('담당', 'Contact')}</th></tr></thead><tbody><tr><td>{L('국내', 'Korea')}</td><td>{SITE['email']} · {SITE['tel']}</td></tr><tr><td>{L('해외 (Global)', 'International')}</td><td>{SITE['email']} · Tel {SITE['tel_intl']}</td></tr></tbody></table></div></div></div>
</div></div>'''
    write(lang, cur, L('글로벌 네트워크', 'Global Network'), L('엑소스킨 글로벌 네트워크와 파트너 모집 안내.', 'EXOSKIN global network and partnership opportunities.'), body)

    # --- location
    cur = lp(lang, 'about/location/')
    body = subvis(lang, cur, L('오시는 길', 'Location'), '', 'space-08', [crumbs0, (L('오시는 길', 'Location'), None)]) + lnb(lang, cur, 'about')
    body += f'''<div class="page"><div class="wrap">
<div class="block split" style="align-items:start"><div class="rv" style="border-radius:var(--radius);background:var(--soft);aspect-ratio:4/3;display:grid;place-items:center;text-align:center;color:var(--muted);padding:24px"><div><span style="display:block;width:44px;height:44px;margin:0 auto;color:var(--navy)">{ic('flag')}</span><p style="margin-top:12px"><b style="color:var(--ink)">{L(SITE['addr_ko'], SITE['addr_en'])}</b></p><p style="margin-top:18px;display:flex;gap:8px;flex-wrap:wrap;justify-content:center"><a class="btn btn-pri" href="https://map.naver.com/p/search/{SITE['map_q']}" target="_blank" rel="noopener">{L('네이버 지도', 'Naver Map')}</a><a class="btn" style="border:1px solid var(--line)" href="https://map.kakao.com/?q={SITE['map_q']}" target="_blank" rel="noopener">{L('카카오맵', 'Kakao Map')}</a><a class="btn" style="border:1px solid var(--line)" href="https://www.google.com/maps/search/?api=1&amp;query={SITE['map_q']}" target="_blank" rel="noopener">Google Maps</a></p></div></div>
<div class="rv d1"><h2 class="h3">EXOSKIN ({L(SITE['operator_ko'], SITE['operator_en'])})</h2><div class="tbl-wrap" style="margin-top:24px"><table class="tbl"><tbody>
<tr><th>{L('주소', 'Address')}</th><td>{L(SITE['addr_ko'], SITE['addr_en'])}</td></tr>
<tr><th>{L('전화', 'Phone')}</th><td><a href="tel:{SITE['tel_link']}">{L(SITE['tel'], SITE['tel_intl'])}</a></td></tr>
<tr><th>{L('이메일', 'Email')}</th><td><a href="mailto:{SITE['email']}">{SITE['email']}</a></td></tr>
<tr><th>{L('운영 시간', 'Hours')}</th><td>{L('평일 09:00~18:00 (주말·공휴일 휴무)', 'Mon–Fri 09:00–18:00 KST')}</td></tr>
<tr><th>{L('교통', 'Access')}</th><td>{L('광양프런티어밸리 6차 2층 209호 · 방문 전 전화로 예약해 주세요.', 'Please call ahead to book a visit.')}</td></tr></tbody></table></div></div></div>
</div></div>'''
    write(lang, cur, L('오시는 길', 'Location'), L('엑소스킨(주식회사 에코아트) 사무실 위치와 연락처.', 'EXOSKIN (ECOART Co., Ltd.) office location and contact.'), body)

# ================================================================== PRODUCTS
def filters_html(lang):
    k = lang == 'ko'
    g = ''.join('<option value="%s">%s</option>' % (x['id'], esc(x[lang]['name'])) for x in GROUPS)
    s = ''.join('<option value="%s">%s</option>' % (x['id'], esc(x[lang]['name'])) for x in SECTORS)
    t = [('normal', '상온(~120℃)' if k else 'Ambient (≤120 °C)'), ('mid', '중고온(200~400℃)' if k else 'Medium (200–400 °C)'), ('high', '초고온(600℃~)' if k else 'High (600 °C+)')]
    t = ''.join('<option value="%s">%s</option>' % a for a in t)
    return f'''<div class="filters rv" id="pfilter"><label>{'필터' if k else 'Filter'}</label>
<select name="group" aria-label="{'제품군' if k else 'Family'}"><option value="">{'전체 제품군' if k else 'All families'}</option>{g}</select>
<select name="sector" aria-label="{'적용분야' if k else 'Application'}"><option value="">{'전체 적용분야' if k else 'All applications'}</option>{s}</select>
<select name="temp" aria-label="{'사용 온도' if k else 'Temperature'}"><option value="">{'전체 사용 온도' if k else 'All temperatures'}</option>{t}</select></div>'''

def page_products(lang):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    c0 = (L('제품', 'Products'), 'products/')
    cur = lp(lang, 'products/')
    body = subvis(lang, cur, L('제품', 'Products'), L('4개 제품군 11종의 에어로젤 방화·단열 솔루션', 'Eleven aerogel fire-protection and insulation products in four families'), 'scene-04', [c0]) + lnb(lang, cur, 'products')
    cards = ''.join(pcard(lang, cur, p) for g in GROUPS for p in PRODUCTS if p['group'] == g['id'])
    body += f'''<div class="page"><div class="wrap">
<div class="page-hd split" style="align-items:end"><div class="rv"><span class="eyebrow">All Products</span><h2 class="h2">{L('전체 제품', 'All products')}</h2></div><div class="rv d1" style="text-align:right"><a class="btn btn-line btn-sm" href="{url(cur, lp(lang, 'products/finder/'))}">{L('제품 선택 가이드로 찾기', 'Use the Product Finder')} {ARROW}</a></div></div>
{filters_html(lang)}
<div class="pgrid">{cards}</div><div class="empty" id="pempty" hidden>{L('조건에 맞는 제품이 없습니다.', 'No products match these filters.')}</div>
{note_test(lang)}
</div></div>''' + cta_band(lang, cur)
    write(lang, cur, L('전체 제품', 'Products'), L('엑소스킨 에어로젤 방화도료, 보온·단열 도료, 단열 펠트, 단열 필름 전체 제품 목록.', 'All EXOSKIN aerogel products: fire-resistant coatings, insulation coatings, blankets and film.'), body,
          keywords=L('에어로젤 제품, 방화도료, 단열도료, 단열펠트', 'aerogel products'))

    # group pages
    for gi, g in enumerate(GROUPS):
        cur = lp(lang, group_path(g))
        t = g[lang]
        body = subvis(lang, cur, t['name'], t['lead'], g['img'], [c0, (t['name'], None)]) + lnb(lang, cur, 'products')
        prods = [p for p in PRODUCTS if p['group'] == g['id']]
        extra = ''
        if g['id'] == 'P10':
            extra = f'''<div class="block"><span class="eyebrow rv">Guide</span><h2 class="h3 rv">{L('내화도료와 방염도료, 무엇이 다른가요?', 'Fire-resistant vs. flame-retardant coatings')}</h2>
<div class="tbl-wrap rv" style="margin-top:28px"><table class="tbl"><thead><tr><th>{L('구분', '')}</th><th>{L('내화도료', 'Fire-resistant coating')}</th><th>{L('방염(방화)도료', 'Flame-retardant coating')}</th></tr></thead><tbody>
<tr><th>{L('목적', 'Purpose')}</th><td>{L('철골·콘크리트 등 구조체가 화재 중 일정 시간 하중을 견디도록 보호', 'Keeps structural members (steel, concrete) load-bearing for a set time in a fire')}</td><td>{L('목재·케이블·마감재가 불에 잘 붙지 않고 불길이 번지지 않도록 함', 'Keeps timber, cables and finishes from igniting and spreading flame')}</td></tr>
<tr><th>{L('성능 지표', 'Metric')}</th><td>{L('내화시간(분)', 'Fire resistance time (min)')}</td><td>{L('착화·연소 확산 억제, 방화 등급', 'Ignition and flame-spread resistance, fire class')}</td></tr>
<tr><th>{L('엑소스킨 제품', 'EXOSKIN products')}</th><td>{L('철골 구조용(90~180분), 콘크리트용(60~180분)', 'Steel (90–180 min), Concrete (60–180 min)')}</td><td>{L('목구조용(30~120분), 케이블용(60~120분)', 'Timber (30–120 min), Cables (60–120 min)')}</td></tr>
<tr><th>{L('국내 적용 시', 'In Korea')}</th><td colspan="2">{L('내화구조 인정·방염성능 기준 등 국내 인증 체계가 따로 있습니다. 표기된 내화시간은 제조사 시험 기준이며, 국내 인증 현황은 인증·시험성적서 페이지에서 안내합니다.', 'Korea has separate approval schemes for fire-resistant construction and flame retardancy. Times shown are manufacturer test values; see Certifications for status.')}</td></tr></tbody></table></div></div>'''
        elif g['id'] == 'P20':
            extra = f'''<div class="block"><span class="eyebrow rv">Grades</span><h2 class="h3 rv">{L('사용 온도별 선택', 'Choose by temperature')}</h2>
<div class="tbl-wrap rv" style="margin-top:28px"><table class="tbl"><thead><tr><th>{L('구분', 'Type')}</th><th>{L('제품', 'Product')}</th><th>{L('사용 온도', 'Service temp.')}</th><th>{L('주요 용도', 'Typical use')}</th></tr></thead><tbody>
<tr><td>{L('건축용', 'Building')}</td><td><a href="{url(cur, lp(lang, product_path(PR['P21'])))}">{esc(PR['P21'][lang]['name'])}</a></td><td>{L('상온', 'Ambient')}</td><td>{L('지붕·외벽 차열 단열', 'Roof & wall solar insulation')}</td></tr>
<tr><td>{L('건축용', 'Building')}</td><td><a href="{url(cur, lp(lang, product_path(PR['P22'])))}">{esc(PR['P22'][lang]['name'])}</a></td><td>{L('상온', 'Ambient')}</td><td>{L('내벽 보온·결로 방지', 'Interior insulation, anti-condensation')}</td></tr>
<tr><td>{L('설비용', 'Equipment')}</td><td><a href="{url(cur, lp(lang, product_path(PR['P23'])))}">{esc(PR['P23'][lang]['name'])}</a></td><td>200℃ / 400℃</td><td>{L('배관·저장탱크·보일러실', 'Pipes, tanks, boiler rooms')}</td></tr>
<tr><td>{L('설비용', 'Equipment')}</td><td><a href="{url(cur, lp(lang, product_path(PR['P24'])))}">{esc(PR['P24'][lang]['name'])}</a></td><td>600~1500℃</td><td>{L('야금·유리·방위산업 고온 설비', 'Metallurgy, glass, defense equipment')}</td></tr></tbody></table></div></div>'''
        elif g['id'] == 'P30':
            extra = f'''<div class="block"><span class="eyebrow rv">Compare</span><h2 class="h3 rv">{L('두 가지 펠트, 이렇게 고르세요', 'Which blanket?')}</h2>
<div class="tiles c2" style="margin-top:28px"><div class="tile rv"><span class="tag">{L('건축·설비용', 'Building & equipment')}</span><h3>{esc(PR['P31'][lang]['name'])}</h3><p>{L('배관·탱크·기계실·선박 등. 5·10mm 두께, 열전도율 ≤0.021 W/(m·K), A급 불연.', 'Pipes, tanks, plant rooms, ships. 5/10 mm, ≤0.021 W/(m·K), Class A non-combustible.')}</p></div>
<div class="tile rv d1"><span class="tag">{L('배터리용', 'Batteries')}</span><h3>{esc(PR['P32'][lang]['name'])}</h3><p>{L('전기차·ESS 배터리 셀·모듈 간. 1~5mm 두께, -100~400℃, UL94 V-0.', 'EV and ESS cells and modules. 1–5 mm, -100 to 400 °C, UL94 V-0.')}</p></div></div></div>'''
        else:
            extra = f'''<div class="block"><span class="eyebrow rv">Structure</span><h2 class="h3 rv">{L('에어로젤 + PET 복합 구조', 'Aerogel + PET composite')}</h2><p class="lead rv">{L('에어로젤 단열층과 PET 기재, 점착층으로 이루어진 롤 형태 필름입니다. 전자부품·배터리 팩 내부처럼 두께 여유가 거의 없는 곳에서 국부 단열과 전기 절연을 함께 구현합니다.', 'A roll film made of an aerogel insulating layer, PET carrier and adhesive. It provides local insulation and electrical isolation where there is almost no room, such as inside electronics and battery packs.')}</p></div>'''
        body += f'''<div class="page"><div class="wrap">
<div class="block split" style="align-items:start"><div class="rv"><span class="eyebrow">0{gi+1} · {esc(t['short'])}</span><h2 class="h2">{esc(t['name'])}</h2></div><div class="rv d1"><p class="lead" style="margin-top:0">{esc(t['desc'])}</p></div></div>
<div class="block"><div class="pgrid">{''.join(pcard(lang, cur, p, False) for p in prods)}</div>{note_test(lang)}</div>
{extra}
</div></div>''' + cta_band(lang, cur, g['img'])
        write(lang, cur, t['name'], t['desc'], body, keywords=t['name'])

    # detail pages
    for p in PRODUCTS:
        page_product(lang, p)
    page_finder(lang)

def page_product(lang, p):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    g = G[p['group']]
    cur = lp(lang, product_path(p))
    t = p[lang]
    other = p['en' if k else 'ko']['name']
    body = subvis(lang, cur, t['name'], t['tag'], p['img'], [(L('제품', 'Products'), 'products/'), (g[lang]['name'], group_path(g)), (t['name'], None)]) + lnb(lang, cur, 'products', group_path(g))
    chips = ''.join('<span class="chip%s">%s</span>' % (' g' if i == 0 else '', esc(c)) for i, c in enumerate(t['chips']))
    feats = ''.join('<div class="feat rv d%d"><span class="ico">%s</span><p>%s</p></div>' % (i % 4, ic(FEAT_ICONS[i % len(FEAT_ICONS)]), esc(f)) for i, f in enumerate(t['feat']))
    advs = ''.join('<li class="rv">%s</li>' % esc(a) for a in t['adv'])
    spec_rows = ''.join('<tr><th>%s</th><td>%s</td></tr>' % (esc(a), esc(b)) for a, b in t['spec'])
    spec_rows += '<tr><th>%s</th><td>%s</td></tr>' % (L('시험 기준', 'Test basis'), L('제조사 시험 기준(중국 GB 등) · 성적서 번호는 수령 후 기재', 'Manufacturer tests (Chinese GB etc.) · report numbers to be added'))
    spec_rows += '<tr><th>%s</th><td>%s</td></tr>' % (L('제조원 / 원산지', 'Manufacturer / Origin'), L('숴싱 신소재 / 중국', 'Shuoxing New Materials / China'))
    spaces = ''
    for sid in p['spaces']:
        sp = SP[sid]
        spaces += '<a href="%s"><img src="%s" alt="" loading="lazy"><span><small>%s</small>%s</span></a>' % (url(cur, lp(lang, space_path(sp))), img(cur, sp['img']), esc(SE[sp['sector']][lang]['name']), esc(sp[lang]['name']))
    is_coat = p['group'] in ('P10', 'P20')
    if is_coat:
        steps = [(L('바탕 처리', 'Surface prep'), L('녹·유분·먼지 제거, 필요 시 방청 하도', 'Remove rust, oil and dust; prime if needed')),
                 (L('하도', 'Primer'), L('바탕재에 맞는 하도로 부착력 확보', 'Primer suited to the substrate for adhesion')),
                 (L('본도', 'Main coat'), L('롤러·스프레이로 요구 성능에 맞는 도막 두께 확보', 'Roller or spray to the required film thickness')),
                 (L('상도·건조', 'Topcoat & cure'), L('필요 시 상도 마감, 건조 조건 준수', 'Optional topcoat; follow curing conditions'))]
    elif p['group'] == 'P30':
        steps = [(L('표면 점검', 'Inspect'), L('설비 표면의 습기·이물질 제거', 'Clean and dry the surface')),
                 (L('재단', 'Cut'), L('칼·가위로 필요한 치수에 맞춰 재단', 'Cut to size with a knife or scissors')),
                 (L('감싸기', 'Wrap'), L('겹침부를 두고 감싸 틈을 없앰', 'Wrap with overlapping seams')),
                 (L('고정·마감', 'Secure & finish'), L('밴드·테이프 고정 후 필요 시 외피 마감', 'Fix with bands or tape; jacket if needed'))]
    else:
        steps = [(L('세정', 'Clean'), L('부착면의 유분·먼지 제거', 'Remove oil and dust from the substrate')),
                 (L('재단', 'Cut'), L('부품 형상에 맞게 재단·타발', 'Cut or die-cut to shape')),
                 (L('부착', 'Apply'), L('이형지 제거 후 기포 없이 부착', 'Peel liner and apply without bubbles')),
                 (L('검사', 'Inspect'), L('들뜸·절연 상태 확인', 'Check adhesion and insulation'))]
    steps_h = ''.join('<div class="step rv d%d"><h4>%s</h4><p>%s</p></div>' % (i, a, b) for i, (a, b) in enumerate(steps))
    related = [x for x in PRODUCTS if x['group'] == p['group'] and x['id'] != p['id']][:3]
    if len(related) < 2:
        related += [PR[i] for sid in p['spaces'] for i in SP[sid]['products'] if i != p['id'] and PR[i] not in related][:3 - len(related)]
    qurl = url(cur, lp(lang, 'contact/quote/')) + '?product=' + p['id']
    body += f'''<div class="page"><div class="wrap">
<div class="block pd-top"><figure class="pd-ph rv"><img src="{img(cur, p['img'])}" alt="{esc(t['name'])}" style="object-position:{p['pos']}"><figcaption>{L('적용 예시 이미지 · 제품 사진 준비 중', 'Illustrative application image')}</figcaption></figure>
<div class="pd-info rv d1"><span class="tag">No.{p['no']:02d} · {esc(g[lang]['name'])}</span><h2>{esc(t['name'])}</h2><p class="en">{esc(other)}</p><p class="sum">{esc(t['sum'])}</p><div class="chipset">{chips}</div>
<div class="btns"><a class="btn btn-pri" href="{qurl}">{L('견적·샘플 문의', 'Request a Quote')} {ARROW}</a><a class="btn btn-line" href="{url(cur, lp(lang, 'resources/data-sheets/'))}">{L('TDS 받기', 'Get TDS')}</a></div>
<div class="pd-origin"><span><b>{L('제조원', 'Manufacturer')}</b>{L('숴싱 신소재(중국)', 'Shuoxing New Materials (China)')}</span><span><b>{L('공급', 'Supplied by')}</b>EXOSKIN</span></div></div></div>
<div class="block"><span class="eyebrow rv">Features</span><h2 class="h3 rv">{L('제품 특징', 'Features')}</h2><div class="feat-grid">{feats}</div></div>
<div class="block split" style="align-items:start"><div class="rv"><span class="eyebrow">Benefits</span><h2 class="h3">{L('이런 점이 좋습니다', 'Why choose it')}</h2></div><ol class="adv">{advs}</ol></div>
<div class="block"><span class="eyebrow rv">Applications</span><h2 class="h3 rv">{L('적용 공간', 'Where to use it')}</h2><div class="space-links">{spaces}</div></div>
<div class="block"><span class="eyebrow rv">Specifications</span><h2 class="h3 rv">{L('기술 사양', 'Technical data')}</h2><div class="tbl-wrap rv" style="margin-top:28px"><table class="tbl"><tbody>{spec_rows}</tbody></table></div>{note_test(lang)}</div>
<div class="block"><span class="eyebrow rv">Application</span><h2 class="h3 rv">{L('시공 방법', 'How to apply')}</h2><div class="steps">{steps_h}</div><p class="note">{L('※ 일반적인 시공 순서입니다. 도막 두께·소요량·건조 조건은 제품별 시공가이드(수령 후 게시)를 따릅니다.', '※ General sequence only. Film thickness, coverage and curing follow the product application guide (to be published).')}</p></div>
<div class="block"><span class="eyebrow rv">Downloads</span><h2 class="h3 rv">{L('인증·자료 다운로드', 'Documents')}</h2><div class="dl">{''.join('<div class="rv">%s<span><b>%s</b><span class="pending">%s</span></span></div>' % (ic('doc'), a, L('준비 중', 'Coming soon')) for a in ['TDS', 'SDS', L('시험성적서', 'Test report')])}</div>
<p style="margin-top:20px"><a class="more" href="{url(cur, lp(lang, 'contact/technical/'))}?product={p['id']}">{L('자료가 먼저 필요하시면 요청해 주세요', 'Need a document now? Ask us')} {ARROW}</a></p></div>
<div class="block"><span class="eyebrow rv">Related</span><h2 class="h3 rv">{L('함께 보면 좋은 제품', 'Related products')}</h2><div class="pgrid" style="margin-top:28px">{''.join(pcard(lang, cur, r, False) for r in related)}</div></div>
</div></div>''' + cta_band(lang, cur, p['img'], L('%s<br>견적이 필요하신가요?' % esc(t['name']), 'Need a quote for<br>%s?' % esc(t['name'])))
    write(lang, cur, t['name'], t['sum'], body, keywords='%s, %s' % (t['name'], g[lang]['name']))

def page_finder(lang):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    cur = lp(lang, 'products/finder/')
    body = subvis(lang, cur, L('제품 선택 가이드', 'Product Finder'), L('공간·온도·목적, 세 가지만 고르세요.', 'Choose space, temperature and purpose.'), 'scene-02', [(L('제품', 'Products'), 'products/'), (L('제품 선택 가이드', 'Product Finder'), None)]) + lnb(lang, cur, 'products')
    data = [dict(no='%02d' % p['no'], url=url(cur, lp(lang, product_path(p))), img=img(cur, p['img']), name=p[lang]['name'], tag=p[lang]['tag'], sum=p[lang]['sum'],
                 sectors=product_sectors(p), temp=p['temp'], purpose=p['purpose'] + (['fire'] if p['group'] == 'P10' else [])) for p in PRODUCTS]
    q1 = ''.join('<button type="button" data-v="%s">%s</button>' % (s['id'], esc(s[lang]['name'])) for s in SECTORS)
    q2 = ''.join('<button type="button" data-v="%s">%s</button>' % a for a in [('normal', L('상온 (~120℃)', 'Ambient (≤120 °C)')), ('mid', L('중고온 (200~400℃)', 'Medium (200–400 °C)')), ('high', L('초고온 (600℃ 이상)', 'High (600 °C+)'))])
    q3 = ''.join('<button type="button" data-v="%s">%s</button>' % a for a in [('fire', L('방화·내화', 'Fire protection')), ('thermal', L('보온·단열', 'Thermal insulation')), ('solar', L('차열(복사열 차단)', 'Solar heat blocking')), ('condensation', L('결로 방지', 'Anti-condensation')), ('battery', L('배터리 열관리', 'Battery thermal management'))])
    rows = ''.join('<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td></tr>' % (url(cur, lp(lang, product_path(p))), esc(p[lang]['name']), esc(G[p['group']][lang]['short']), esc(' · '.join(p[lang]['chips']))) for p in PRODUCTS)
    body += f'''<div class="page"><div class="wrap">
<div class="finder" id="finder"><div class="fq rv" data-key="sector"><h3><span>1</span>{L('어디에 시공하나요?', 'Where will it be used?')}</h3><div class="opts">{q1}</div></div>
<div class="fq rv" data-key="temp"><h3><span>2</span>{L('사용 온도는 어느 정도인가요?', 'What is the operating temperature?')}</h3><div class="opts">{q2}</div></div>
<div class="fq rv" data-key="purpose"><h3><span>3</span>{L('무엇이 가장 필요한가요?', 'What do you need most?')}</h3><div class="opts">{q3}</div></div>
<div class="finder-res"><h3 class="h3">{L('추천 제품', 'Recommended')} <span id="finder-count" style="color:var(--green)">11</span></h3><div class="pgrid" id="finder-out"></div></div></div>
<div class="block"><h2 class="h3 rv">{L('전 제품 비교표', 'Compare all products')}</h2><div class="tbl-wrap rv" style="margin-top:28px"><table class="tbl"><thead><tr><th>{L('제품', 'Product')}</th><th>{L('구분', 'Type')}</th><th>{L('핵심 사양', 'Key data')}</th></tr></thead><tbody>{rows}</tbody></table></div>{note_test(lang)}</div>
</div></div>
<script>window.ES_PRODUCTS={json.dumps(data, ensure_ascii=False)};</script>''' + cta_band(lang, cur)
    write(lang, cur, L('제품 선택 가이드', 'Product Finder'), L('시공 공간, 사용 온도, 목적을 선택하면 맞는 에어로젤 제품을 추천합니다.', 'Select space, temperature and purpose to find the right aerogel product.'), body)

# ================================================================== APPLICATIONS
def page_applications(lang):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    c0 = (L('적용분야', 'Applications'), 'applications/')
    cur = lp(lang, 'applications/')
    body = subvis(lang, cur, L('적용분야', 'Applications'), L('분야 → 공간 → 추천 제품 순서로 찾아보세요.', 'Find your sector, then your space, then the product.'), 'space-10', [c0]) + lnb(lang, cur, 'applications')
    cards = ''
    for i, s in enumerate(SECTORS):
        sps = [sp for sp in SPACES if sp['sector'] == s['id']]
        cards += f'''<a class="gcard rv d{i % 3}" href="{url(cur, lp(lang, sector_path(s)))}" style="min-height:460px"><img src="{img(cur, s['img'])}" alt="" loading="lazy"><span class="arrow">{ARROW}</span><div class="in"><span class="num">0{i+1}</span><h3>{esc(s[lang]['name'])}</h3><p>{esc(s[lang]['desc'])}</p><ul>{''.join('<li>%s</li>' % esc(sp[lang]['name']) for sp in sps[:5])}</ul></div></a>'''
    body += f'''<div class="page"><div class="wrap"><div class="page-hd rv"><span class="eyebrow">5 Sectors · 22 Spaces</span><h2 class="h2">{L('어떤 현장이신가요?', 'What kind of site?')}</h2></div>
<div class="groups" style="grid-template-columns:repeat(3,1fr)">{cards}<a class="gcard rv" href="{url(cur, lp(lang, 'products/finder/'))}" style="min-height:460px;background:var(--green)"><span class="arrow">{ARROW}</span><div class="in"><span class="num" style="color:#fff">FINDER</span><h3>{L('공간을 모르겠다면', 'Not sure?')}</h3><p>{L('제품 선택 가이드에서 온도와 목적으로 찾아보세요.', 'Use the Product Finder to search by temperature and purpose.')}</p></div></a></div>
</div></div>''' + cta_band(lang, cur)
    write(lang, cur, L('적용분야', 'Applications'), L('건축물, 산업·공장 설비, 전력·통신, 토목공사, 운송·교통 장비 분야별 에어로젤 방화·단열 적용 안내.', 'Aerogel fire protection and insulation for buildings, industrial plants, power & data, civil infrastructure and mobility.'), body)
    for s in SECTORS:
        cur = lp(lang, sector_path(s))
        sps = [sp for sp in SPACES if sp['sector'] == s['id']]
        body = subvis(lang, cur, s[lang]['name'], s[lang]['desc'], s['img'], [c0, (s[lang]['name'], None)]) + lnb(lang, cur, 'applications')
        anchors = ''.join('<a class="chip" href="#%s">%s</a>' % (sp['slug'], esc(sp[lang]['name'])) for sp in sps)
        secs = ''
        for sp in sps:
            link = ('<p style="margin-top:22px"><a class="more" href="%s">%s %s</a></p>' % (url(cur, lp(lang, space_path(sp))), L('공간 자세히 보기', 'Read more'), ARROW)) if sp['landing'] else ''
            secs += f'''<section class="space-sec rv" id="{sp['slug']}"><div class="ph"><img src="{img(cur, sp['img'])}" alt="" loading="lazy"></div><div><h3>{esc(sp[lang]['name'])}</h3><p>{esc(sp[lang]['desc'])}</p><div class="rec"><b>{L('추천 제품', 'Recommended products')}</b>{rec_list(lang, cur, sp['products'])}</div>{link}</div></section>'''
        body += f'''<div class="page"><div class="wrap">
<div class="block split" style="align-items:start"><div class="rv"><span class="eyebrow">Challenge</span><h2 class="h3">{L('이런 고민이 있습니다', 'The challenge')}</h2></div><div class="rv d1"><p class="lead" style="margin-top:0">{esc(s[lang]['problem'])}</p><div class="chipset" style="margin-top:24px">{anchors}</div></div></div>
<div class="block">{secs}</div>
</div></div>''' + cta_band(lang, cur, s['img'])
        write(lang, cur, s[lang]['name'], s[lang]['desc'], body, keywords=', '.join(sp[lang]['name'] for sp in sps))
        for sp in sps:
            if sp['landing']:
                page_space(lang, s, sp)

def page_space(lang, s, sp):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    cur = lp(lang, space_path(sp))
    t = sp[lang]
    body = subvis(lang, cur, t['name'], s[lang]['name'], sp['img'], [(L('적용분야', 'Applications'), 'applications/'), (s[lang]['name'], sector_path(s)), (t['name'], None)]) + lnb(lang, cur, 'applications', sector_path(s))
    others = [x for x in SPACES if x['sector'] == s['id'] and x['id'] != sp['id']]
    extra_imgs = ''
    if sp['id'] == 'S16':
        extra_imgs = '<div class="space-links" style="margin-top:28px">%s</div>' % ''.join('<a href="#" onclick="return false" style="cursor:default"><img src="%s" alt="" loading="lazy"><span>%s</span></a>' % (img(cur, a), b) for a, b in [('space-09', L('공장 외관', 'Factory exterior')), ('space-11', L('창고 내부', 'Warehouse interior')), ('photo-warehouse', L('창고 외관', 'Warehouse exterior')), ('space-12', L('공장 내부', 'Factory interior'))])
    body += f'''<div class="page"><div class="wrap">
<div class="block split"><div class="rv"><span class="eyebrow">{esc(s[lang]['name'])}</span><h2 class="h2">{esc(t['name'])}</h2><p class="lead">{esc(t['desc'])}</p></div><div class="ph rv d1"><img src="{img(cur, sp['scene'])}" alt="" loading="lazy"></div></div>
{('<div class="block">' + extra_imgs + '</div>') if extra_imgs else ''}
<div class="block split" style="align-items:start"><div class="rv"><span class="eyebrow">Solution</span><h2 class="h3">{L('추천 제품', 'Recommended products')}</h2><p class="lead">{L('현장 조건에 따라 아래 제품을 단독 또는 조합으로 사용합니다.', 'Use these products alone or in combination, depending on site conditions.')}</p></div><div class="rv d1">{rec_list(lang, cur, sp['products'])}</div></div>
<div class="block"><div class="callout rv"><b>{L('시공 시 주의점', 'Application tips')}</b> — {esc(t['tip'])}</div></div>
<div class="block"><span class="eyebrow rv">Products</span><div class="pgrid">{''.join(pcard(lang, cur, PR[i], False) for i in sp['products'])}</div>{note_test(lang)}</div>
<div class="block"><h2 class="h3 rv">{L('같은 분야의 다른 공간', 'Other spaces in this sector')}</h2><div class="space-links">{''.join('<a href="%s"><img src="%s" alt="" loading="lazy"><span>%s</span></a>' % (url(cur, lp(lang, space_path(o))), img(cur, o['img']), esc(o[lang]['name'])) for o in others[:6])}</div></div>
</div></div>''' + cta_band(lang, cur, sp['img'], L('%s 현장,<br>도면을 보내 주세요.' % esc(t['name']), 'Planning a %s project?<br>Send us your drawings.' % esc(t['name'].lower() if not k else t['name'])))
    write(lang, cur, t['name'], t['desc'], body, keywords=t['name'])

# ================================================================== TECHNOLOGY
def page_technology(lang):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    c0 = (L('기술·인증', 'Technology'), 'technology/aerogel/')
    cur = lp(lang, 'technology/aerogel/')
    body = subvis(lang, cur, L('에어로젤 기술', 'Aerogel Technology'), L('얇고 가벼운데 왜 열과 불을 막을까요?', 'Why does something so thin stop heat and fire?'), 'scene-08', [c0, (L('에어로젤 기술', 'Aerogel Technology'), None)]) + lnb(lang, cur, 'technology')
    principles = [('layers', L('나노 기공 구조', 'Nanoporous structure'), L('실리카 입자가 3차원 그물망을 이루고, 그 사이 수십 나노미터 크기의 기공에 공기가 갇혀 있습니다.', 'Silica particles form a 3D network with air trapped in pores tens of nanometers across.')),
                  ('thermo', L('열전달 차단', 'Blocking heat transfer'), L('기공이 공기 분자의 이동 거리보다 작아 대류와 전도가 크게 억제됩니다.', 'Pores smaller than the mean free path of air molecules suppress convection and conduction.')),
                  ('fire', L('무기질 불연 소재', 'Inorganic, non-combustible'), L('실리카 기반 무기질이라 불에 타지 않고 고온에서도 형태를 유지합니다.', 'Silica-based and inorganic, so it does not burn and holds its shape at high temperatures.'))]
    comp = [(L('두께', 'Thickness'), L('두꺼움', 'Thick'), L('얇음', 'Thin')), (L('무게', 'Weight'), L('무거움(내화보드 등)', 'Heavy (fire boards)'), L('가벼움', 'Light')),
            (L('복잡한 형상', 'Complex shapes'), L('재단·가공 부담', 'Hard to fit'), L('칠하거나 감싸서 대응', 'Paint or wrap to fit')),
            (L('흡습·처짐', 'Moisture & sagging'), L('성능 저하 우려', 'Performance loss over time'), L('발수·형태 유지', 'Water repellent, holds shape'))]
    body += f'''<div class="page"><div class="wrap">
<div class="block split"><div class="rv"><span class="eyebrow">What is Aerogel</span><h2 class="h2">{L('부피 대부분이<br>공기인 고체', 'A solid made<br>mostly of air')}</h2><p class="lead">{L('에어로젤은 젤 속의 액체를 기체로 바꿔 만든 초경량 다공성 소재입니다. 고체이지만 부피 대부분이 공기로 채워져 있어, 현존하는 고체 소재 가운데 열을 가장 잘 막는 소재 중 하나로 꼽힙니다.', 'Aerogel is an ultra-light porous material made by replacing the liquid in a gel with gas. Though solid, it is mostly air, making it one of the best solid thermal insulators known.')}</p></div><div class="ph rv d1"><img src="{img(cur, 'space-07')}" alt="" loading="lazy"></div></div>
<div class="block"><span class="eyebrow rv">Principle</span><h2 class="h3 rv">{L('단열·방화의 원리', 'How it works')}</h2><div class="tiles c3" style="margin-top:28px">{''.join('<div class="tile rv d%d"><span class="ico">%s</span><h3>%s</h3><p>%s</p></div>' % (i, ic(a), b, c) for i, (a, b, c) in enumerate(principles))}</div></div>
<div class="block"><span class="eyebrow rv">Comparison</span><h2 class="h3 rv">{L('기존 방식과 비교', 'Compared with conventional methods')}</h2><div class="tbl-wrap rv" style="margin-top:28px"><table class="tbl"><thead><tr><th>{L('항목', '')}</th><th>{L('기존 보온재·내화피복', 'Conventional insulation & fireproofing')}</th><th>{L('에어로젤 소재', 'Aerogel materials')}</th></tr></thead><tbody>{''.join('<tr><th>%s</th><td>%s</td><td><b style="color:var(--green)">%s</b></td></tr>' % c for c in comp)}</tbody></table></div><p class="note">{L('※ 일반적인 소재 특성 비교이며, 제품별 수치는 각 제품 상세의 기술 사양을 확인하세요.', '※ General comparison; see each product page for data.')}</p></div>
<div class="block"><span class="eyebrow rv">Forms</span><h2 class="h3 rv">{L('세 가지 형태', 'Three forms')}</h2><div class="tiles c3" style="margin-top:28px">{''.join('<a class="tile rv d%d" href="%s"><span class="ico">%s</span><h3>%s</h3><p>%s</p><span class="more">%s %s</span></a>' % (i, url(cur, lp(lang, a)), ic(b), c, d, L('제품 보기', 'View'), ARROW) for i, (a, b, c, d) in enumerate([
    ('products/fire-resistant-coating/', 'fire', L('칠하는 에어로젤 · 도료', 'Paint it · Coatings'), L('방화도료 4종, 보온·단열 도료 4종', '4 fire-resistant + 4 insulation coatings')),
    ('products/aerogel-blanket/', 'layers', L('감싸는 에어로젤 · 펠트', 'Wrap it · Blankets'), L('보온·단열 펠트, 배터리용 펠트', 'Insulation and battery blankets')),
    ('products/insulation-film/', 'film', L('붙이는 에어로젤 · 필름', 'Stick it · Film'), L('0.05·0.10mm 초박형 필름', '0.05/0.10 mm ultra-thin film'))]))}</div></div>
<div class="block"><span class="eyebrow rv">Video</span><h2 class="h3 rv">{L('화염 시험 영상', 'Flame test video')}</h2><div class="rv" style="margin-top:28px;border-radius:var(--radius);background:var(--navy);aspect-ratio:16/7;display:grid;place-items:center;color:#fff;text-align:center"><div>{ic('play')}<p style="margin-top:10px;opacity:.8">{L('제조사 화염 시험 영상 수령 후 게시', 'Manufacturer flame-test video coming soon')}</p></div></div></div>
</div></div>''' + cta_band(lang, cur)
    write(lang, cur, L('에어로젤 기술', 'Aerogel Technology'), L('에어로젤이 얇은 두께로도 단열·방화 성능을 내는 원리와 기존 단열재와의 비교.', 'How aerogel insulates and resists fire at minimal thickness, compared with conventional materials.'), body, keywords=L('에어로젤이란, 에어로젤 원리, 에어로젤 단열', 'what is aerogel, aerogel insulation'))

    # certifications
    cur = lp(lang, 'technology/certifications/')
    body = subvis(lang, cur, L('인증·시험성적서', 'Certifications & Test Reports'), L('설계와 검토에 필요한 근거 자료', 'Evidence for specification and review'), 'space-01', [c0, (L('인증·시험성적서', 'Certifications'), None)]) + lnb(lang, cur, 'technology')
    rows = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td><span class="pending">%s</span></td></tr>' % (esc(p[lang]['name']), esc(' · '.join(p[lang]['chips'])), L('제조사 시험(GB 등)', 'Manufacturer (GB etc.)'), L('수령 후 기재', 'To be added')) for p in PRODUCTS)
    body += f'''<div class="page"><div class="wrap" data-tabscope>
<div class="callout warn rv" style="margin-top:0;margin-bottom:48px"><b>{L('표기 원칙', 'How we report')}</b> — {L('엑소스킨은 국내 인증을 취득하기 전에는 "방염 인증", "내화구조 인정" 등의 표현을 쓰지 않습니다. 모든 수치는 시험 주체와 규격(제조사·GB 등)을 함께 표기합니다.', 'We do not claim compliance with EN 13501, ASTM E119/UL 263 or other regional standards until products are tested to them. All values are reported with the test body and standard (manufacturer, GB, etc.).')}</div>
<div class="tabs" data-tabs role="tablist"><button type="button" class="on" data-t="t1">{L('제조사·해외 시험', 'Manufacturer & international tests')}</button><button type="button" data-t="t2">{L('국내 인증', 'Korean certifications')}</button></div>
<div class="tab-panel on" data-panel="t1"><div class="tbl-wrap"><table class="tbl"><thead><tr><th>{L('대상 제품', 'Product')}</th><th>{L('주요 시험값', 'Key values')}</th><th>{L('시험 주체·규격', 'Test body / standard')}</th><th>{L('성적서 번호·발행일', 'Report no. / date')}</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">{L('※ GB, CE, SGS 등 성적서 원본은 제조사로부터 수령하는 대로 PDF로 열람할 수 있게 등록합니다.', '※ Original reports (GB, CE, SGS, etc.) will be posted as PDFs when received. Standard names are kept in their original form with translated summaries.')}</p></div>
<div class="tab-panel" data-panel="t2"><div class="empty">{L('국내 인증은 시험 진행 후 취득 현황을 이곳에 게시합니다.', 'Korean certification status will be posted here once testing is complete.')}</div></div>
<div class="block" style="text-align:center;margin-top:72px"><a class="btn btn-pri" href="{url(cur, lp(lang, 'contact/technical/'))}">{L('자료 요청 · 기술 상담', 'Request documents')} {ARROW}</a></div>
</div></div>'''
    write(lang, cur, L('인증·시험성적서', 'Certifications & Test Reports'), L('엑소스킨 제품의 제조사 시험 성적서와 국내 인증 현황.', 'Manufacturer test reports and certification status for EXOSKIN products.'), body)

    if k:
        cur = 'technology/insights/'
        body = subvis(lang, cur, '기술 칼럼', '현장 실무자를 위한 방화·단열 이야기', 'scene-07', [c0, ('기술 칼럼', None)]) + lnb(lang, cur, 'technology')
        arts = [
            ('fire-vs-flame', '내화도료와 방염도료, 무엇이 다른가요?', 'scene-01', [
                '두 도료 모두 "불에 강하게 만든다"는 점은 같지만 지키는 대상이 다릅니다. <b>내화도료</b>는 철골·콘크리트 같은 구조체가 화재 중에도 일정 시간 무너지지 않도록 보호하는 도료이고, 성능은 <b>내화시간(분)</b>으로 말합니다.',
                '<b>방염도료</b>는 목재·마감재·케이블처럼 불이 붙어 번질 수 있는 재료에 칠해 착화와 연소 확산을 늦추는 도료입니다. 국내에서는 두 제품이 따르는 인증 체계도 다르므로, 설계 단계에서 어떤 성능이 요구되는지 먼저 확인해야 합니다.',
                '엑소스킨의 철골 구조용·콘크리트용 제품은 내화도료, 목구조용·케이블용 제품은 방화도료로 구분됩니다. 표기된 시간은 제조사 시험 기준이며, 국내 인증 현황은 인증·시험성적서 페이지에서 안내합니다.']),
            ('thin-pipe-insulation', '배관 보온, 두께를 줄이는 방법', 'scene-04', [
                '배관 보온재는 두꺼울수록 단열 성능이 좋아지지만, 좁은 파이프랙이나 밸브·플랜지 주변에서는 두께가 곧 시공 난이도가 됩니다.',
                '에어로젤 펠트는 열전도율이 낮아 같은 단열 효과를 더 얇은 두께로 낼 수 있습니다. 칼이나 가위로 재단해 감싸면 되므로 형상이 복잡한 부위에도 대응하기 쉽습니다.',
                '감싸기 어려운 밸브·플랜지·지지대 부위는 G200·G400 고온 내열 도료를 칠해 보완할 수 있습니다. 운전 온도와 배관 구성을 알려 주시면 펠트와 도료의 조합을 제안해 드립니다.']),
        ]
        art = ''
        for sl, ti, im, ps in arts:
            art += f'''<article class="block split" id="{sl}" style="align-items:start;scroll-margin-top:160px"><div class="ph rv"><img src="{img(cur, im)}" alt="" loading="lazy"></div><div class="rv d1 prose"><span class="eyebrow">Insight</span><h2 class="h3" style="margin-bottom:20px">{ti}</h2>{''.join('<p>%s</p>' % x for x in ps)}</div></article>'''
        body += f'''<div class="page"><div class="wrap">{art}</div></div>''' + cta_band(lang, cur)
        write(lang, cur, '기술 칼럼', '내화도료와 방염도료의 차이, 배관 보온 두께를 줄이는 방법 등 방화·단열 실무 칼럼.', body, keywords='내화도료 방염도료 차이, 배관 보온 두께, 에어로젤 펠트')

# ================================================================== PROJECTS
def page_projects(lang):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    c0 = (L('시공사례', 'Projects'), 'projects/')
    cur = lp(lang, 'projects/')
    body = subvis(lang, cur, L('시공사례', 'Projects'), L('실제 현장에서 검증된 적용 사례', 'Proven on real sites'), 'space-10', [c0]) + lnb(lang, cur, 'projects')
    body += f'''<div class="page"><div class="wrap">
<div class="tiles c2"><a class="gcard rv" href="{url(cur, lp(lang, 'projects/korea/'))}" style="min-height:420px"><img src="{img(cur, 'space-09')}" alt="" loading="lazy"><span class="arrow">{ARROW}</span><div class="in"><span class="num">KOREA</span><h3>{L('국내 사례', 'Korea Projects')}</h3><p>{L('국내 시범 시공부터 차곡차곡 쌓아 갑니다.', 'Built up from our first pilot projects in Korea.')}</p></div></a>
<a class="gcard rv d1" href="{url(cur, lp(lang, 'projects/global/'))}" style="min-height:420px"><img src="{img(cur, 'space-02')}" alt="" loading="lazy"><span class="arrow">{ARROW}</span><div class="in"><span class="num">GLOBAL</span><h3>{L('해외 사례', 'Global Projects')}</h3><p>{L('제조사 숴싱 신소재의 해외 적용 사례', 'International references from Shuoxing New Materials')}</p></div></a></div>
<div class="block"><span class="eyebrow rv">Applications in Action</span><h2 class="h3 rv">{L('적용 예시', 'Application examples')}</h2><p class="note rv">{L('※ 아래 이미지는 제품 적용 방식을 보여 주는 연출 이미지이며, 실제 시공 사례가 아닙니다.', '※ Illustrative images showing how products are applied; not actual projects.')}</p>
<div class="pgrid" style="margin-top:28px">{''.join('<a class="pcard rv" href="%s"><div class="ph"><img src="%s" alt="" loading="lazy"></div><div class="bd"><span class="tag">%s</span><h3>%s</h3></div></a>' % (url(cur, lp(lang, product_path(PR[p]))), img(cur, s), L('적용 예시', 'Example'), esc(PR[p][lang]['name'])) for s, p in [('scene-01', 'P11'), ('scene-02', 'P21'), ('scene-05', 'P13'), ('scene-07', 'P14'), ('scene-04', 'P23'), ('scene-08', 'P31')])}</div></div>
</div></div>''' + cta_band(lang, cur)
    write(lang, cur, L('시공사례', 'Projects'), L('엑소스킨 에어로젤 제품의 국내외 시공사례.', 'EXOSKIN aerogel projects in Korea and abroad.'), body)

    cur = lp(lang, 'projects/korea/')
    body = subvis(lang, cur, L('국내 사례', 'Korea Projects'), '', 'space-09', [c0, (L('국내 사례', 'Korea Projects'), None)]) + lnb(lang, cur, 'projects')
    body += f'''<div class="page"><div class="wrap"><div class="empty rv" style="padding:90px 24px">{ic('flag')}<h3 class="h3" style="margin-top:16px">{L('국내 시범 시공 사례를 준비하고 있습니다', 'Our first Korean pilot projects are under way')}</h3><p style="margin-top:12px">{L('첫 현장 사례가 정리되는 대로 현장 개요·적용 제품·시공 전후 사진을 공개합니다. 시범 시공에 참여를 원하시면 문의해 주세요.', 'We will publish site overviews, products used and before/after photos as soon as they are ready. Interested in a pilot? Get in touch.')}</p><p style="margin-top:28px"><a class="btn btn-pri" href="{url(cur, lp(lang, 'contact/quote/'))}">{L('유사 현장 문의', 'Ask about a similar project')} {ARROW}</a></p></div></div></div>'''
    write(lang, cur, L('국내 사례', 'Korea Projects'), L('엑소스킨 국내 시공사례.', 'EXOSKIN projects in Korea.'), body)

    cur = lp(lang, 'projects/global/')
    body = subvis(lang, cur, L('해외 사례', 'Global Projects'), '', 'space-02', [c0, (L('해외 사례', 'Global Projects'), None)]) + lnb(lang, cur, 'projects')
    flags = ''.join('<div class="tile rv"><span class="ico">%s</span><h4>%s</h4><p><span class="pending">%s</span></p></div>' % (ic('globe'), c, L('사례 게시 준비 중', 'Case study coming')) for c in ([L('캐나다', 'Canada'), L('인도네시아', 'Indonesia'), L('필리핀', 'Philippines'), L('태국', 'Thailand')]))
    body += f'''<div class="page"><div class="wrap"><div class="page-hd rv"><span class="eyebrow">Export References</span><h2 class="h2">{L('제조사 해외 수출 국가', 'Manufacturer export markets')}</h2><p class="lead">{L('숴싱 신소재의 철골 구조용 내화도료는 아래 국가에 수출된 실적이 있습니다(제조사 자료). 개별 현장 사례는 제조사 사용 허락을 받은 뒤 공개합니다.', 'Shuoxing steel fireproofing coating has been exported to the markets below (per manufacturer). Individual case studies will be published with the manufacturer\'s permission.')}</p></div><div class="tiles">{flags}</div></div></div>'''
    write(lang, cur, L('해외 사례', 'Global Projects'), L('제조사 숴싱 신소재의 해외 수출 실적과 사례.', 'International references from Shuoxing New Materials.'), body)

    # template (noindex)
    cur = lp(lang, 'projects/case-template/')
    body = subvis(lang, cur, L('[사례명] 사례 상세 템플릿', '[Project name] case template'), L('관리자용 예시 페이지입니다.', 'Admin template page.'), 'space-10', [c0, (L('사례 상세', 'Project detail'), None)])
    body += f'''<div class="page"><div class="wrap"><div class="callout warn" style="margin:0 0 48px"><b>{L('템플릿', 'Template')}</b> — {L('실제 사례가 아닙니다. 사례 등록 시 이 구성을 복사해 사용하세요.', 'Not a real project. Copy this layout when adding a case study.')}</div>
<div class="tbl-wrap"><table class="tbl"><tbody>{''.join('<tr><th>%s</th><td>%s</td></tr>' % (a, b) for a, b in [(L('국가·지역', 'Country'), '[ ]'), (L('분야', 'Sector'), '[ ]'), (L('면적·수량', 'Area / quantity'), '[ ]'), (L('적용 제품', 'Products'), '[ ]'), (L('시공 기간', 'Period'), '[ ]')])}</tbody></table></div>
<div class="tiles c2" style="margin-top:48px"><div class="tile"><h4>{L('시공 전', 'Before')}</h4><p>[{L('사진', 'photo')}]</p></div><div class="tile"><h4>{L('시공 후', 'After')}</h4><p>[{L('사진', 'photo')}]</p></div></div>
<div class="callout"><b>{L('고객 코멘트', 'Client comment')}</b> — [ ]</div></div></div>'''
    write(lang, cur, L('사례 상세 템플릿', 'Case template'), '', body, noindex=True)

# ================================================================== RESOURCES
def page_resources(lang):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    c0 = (L('자료실', 'Resources'), 'resources/')
    cur = lp(lang, 'resources/')
    body = subvis(lang, cur, L('자료실', 'Resources'), L('카탈로그, TDS·SDS, 시방서, 영상', 'Catalogs, data sheets, guides and videos'), 'scene-03', [c0]) + lnb(lang, cur, 'resources')
    items = [('doc', L('카탈로그·브로슈어', 'Catalogs & Brochures'), L('국문·영문 종합 카탈로그, 제품군별 리플릿', 'Korean and English catalogs, product leaflets'), 'resources/catalogs/'),
             ('box', 'TDS·SDS', L('제품별 기술자료·안전보건자료', 'Technical and safety data sheets'), 'resources/data-sheets/'),
             ('tool', L('시방서·시공가이드', 'Specs & Guides'), L('표준 시방서, 시공 가이드, CAD 상세도, 소요량 계산표', 'Specifications, application guides, CAD details, coverage calculator'), 'resources/guides/'),
             ('play', L('영상', 'Videos'), L('시공 과정과 화염 시험 영상', 'Application and flame-test videos'), 'resources/videos/')]
    body += f'''<div class="page"><div class="wrap"><div class="tiles">{''.join('<a class="tile rv d%d" href="%s"><span class="ico">%s</span><h3>%s</h3><p>%s</p><span class="more">%s %s</span></a>' % (i, url(cur, lp(lang, p)), ic(a), b, c, L('바로가기', 'Go'), ARROW) for i, (a, b, c, p) in enumerate(items))}</div>
<div class="callout rv" style="margin-top:48px"><b>{L('자료 등록 안내', 'Note')}</b> — {L('자료는 제조사로부터 받는 대로 순차 등록합니다. 카탈로그는 바로 내려받을 수 있고, TDS·SDS·시방서는 이메일 입력 후 받으실 수 있습니다.', 'Documents are added as we receive them. Catalogs are open downloads; TDS, SDS and guides require a short form.')}</div></div></div>'''
    write(lang, cur, L('자료실', 'Resources'), L('엑소스킨 카탈로그, TDS·SDS, 시방서·시공가이드, 영상 자료.', 'EXOSKIN catalogs, TDS/SDS, guides and videos.'), body)

    def dl_page(path, title, desc, image, inner):
        cur = lp(lang, path)
        b = subvis(lang, cur, title, desc, image, [c0, (title, None)]) + lnb(lang, cur, 'resources')
        b += '<div class="page"><div class="wrap">%s</div></div>' % inner(cur)
        write(lang, cur, title, desc, b)

    dl_page('resources/catalogs/', L('카탈로그·브로슈어', 'Catalogs & Brochures'), L('영업·설계용 종합 자료', 'Sales and specification materials'), 'scene-02',
            lambda cur: '<div class="dl">%s</div>' % ''.join('<div class="rv">%s<span><b>%s</b><span class="pending">%s</span></span></div>' % (ic('doc'), a, L('제작 중', 'In production')) for a in [L('EXOSKIN 종합 카탈로그 (국문)', 'EXOSKIN catalog (Korean)'), L('EXOSKIN 종합 카탈로그 (영문)', 'EXOSKIN catalog (English)'), L('방화도료 리플릿', 'Fire-resistant coatings leaflet'), L('보온·단열 도료 리플릿', 'Insulation coatings leaflet'), L('단열 펠트 리플릿', 'Blankets leaflet'), L('단열 필름 리플릿', 'Film leaflet')]))
    dl_page('resources/data-sheets/', 'TDS·SDS' if k else 'TDS & SDS', L('제품별 기술자료·안전보건자료', 'Technical and safety data sheets'), 'scene-04',
            lambda cur: '<div class="tbl-wrap rv"><table class="tbl"><thead><tr><th>%s</th><th>TDS</th><th>%s</th><th></th></tr></thead><tbody>%s</tbody></table></div><p class="note">%s</p>' % (
                L('제품', 'Product'), L('SDS (MSDS)', 'SDS (GHS)'),
                ''.join('<tr><td><a href="%s">%s</a></td><td><span class="pending">%s</span></td><td><span class="pending">%s</span></td><td><a href="%s?product=%s">%s</a></td></tr>' % (url(cur, lp(lang, product_path(p))), esc(p[lang]['name']), L('준비 중', 'Coming'), L('준비 중', 'Coming'), url(cur, lp(lang, 'contact/technical/')), p['id'], L('자료 요청', 'Request')) for p in PRODUCTS),
                L('※ SDS는 국내용 한글 MSDS 양식으로 제공합니다.', '※ SDS are provided in GHS format (English).')))
    dl_page('resources/guides/', L('시방서·시공가이드', 'Specs & Application Guides'), L('설계·시공 실무 자료', 'For designers and applicators'), 'scene-01',
            lambda cur: '<div class="dl">%s</div>' % ''.join('<div class="rv">%s<span><b>%s</b><span class="pending">%s</span></span></div>' % (ic(i), a, L('준비 중', 'Coming soon')) for i, a in [('doc', L('표준 시방서', 'Standard specification')), ('tool', L('제품별 시공 가이드', 'Application guides')), ('layers', L('CAD 상세도', 'CAD details')), ('box', L('소요량 계산표', 'Coverage calculator'))]))
    dl_page('resources/videos/', L('영상', 'Videos'), L('시공 과정과 화염 시험', 'Application and flame tests'), 'scene-05',
            lambda cur: '<div class="tiles c3">%s</div>' % ''.join('<div class="tile rv" style="padding:0;overflow:hidden"><div style="aspect-ratio:16/9;background:var(--navy);display:grid;place-items:center;color:#fff">%s</div><div style="padding:22px 24px"><h4>%s</h4><p><span class="pending">%s</span></p></div></div>' % (ic('play'), a, L('영상 등록 예정', 'Coming soon')) for a in [L('철골 내화도료 화염 시험', 'Steel fireproofing flame test'), L('지붕 차열 단열 도료 시공', 'Roof insulation coating application'), L('에어로젤 펠트 배관 시공', 'Aerogel blanket on pipes')]))

# ================================================================== NEWS
def page_news(lang):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    c0 = (L('홍보센터', 'Newsroom'), 'news/notices/')
    cur = lp(lang, 'news/notices/')
    body = subvis(lang, cur, L('공지·뉴스', 'News'), '', 'space-08', [c0, (L('공지·뉴스', 'News'), None)]) + lnb(lang, cur, 'news')
    items = news_list(lang)
    body += '<div class="page"><div class="wrap"><div class="acc news-acc">%s</div></div></div>' % ''.join(
        '<details id="%s" class="rv"%s><summary style="padding-left:0"><span class="chip g" style="margin-right:12px">%s</span>%s <span style="color:var(--muted);font-weight:500;font-size:14px;margin-left:10px">%s</span></summary><div class="a">%s</div></details>' % (n['id'], ' open' if i == 0 else '', n['cat'], n['t'], n['date'], n['body']) for i, n in enumerate(items))
    body = body.replace('<summary style="padding-left:0">', '<summary class="nq" style="padding-left:0">')
    write(lang, cur, L('공지·뉴스', 'News'), L('엑소스킨 공지사항과 소식.', 'EXOSKIN news and notices.'), body, extra_head='<style>.news-acc summary.nq::before{content:none}</style>')
    cur = lp(lang, 'news/exhibitions/')
    body = subvis(lang, cur, L('전시회·행사', 'Exhibitions & Events'), L('현장에서 직접 만나 보세요.', 'Meet us in person.'), 'space-06', [c0, (L('전시회·행사', 'Exhibitions'), None)]) + lnb(lang, cur, 'news')
    body += f'''<div class="page"><div class="wrap">
<div class="empty rv" style="padding:70px 24px">{ic('flag')}<h3 class="h3" style="margin-top:14px">{L('전시회 참가 일정이 확정되면 이곳에 안내합니다', 'Upcoming exhibitions will be announced here')}</h3><p style="margin-top:10px">{L('부스 위치와 일정, 현장 미팅 예약을 함께 받을 예정입니다.', 'Booth details and meeting bookings will be available.')}</p></div>
<div class="block"><h2 class="h3 rv">{L('미팅 예약 문의', 'Book a meeting')}</h2><p class="lead rv">{L('전시회 현장 또는 사무실 미팅을 원하시면 남겨 주세요.', 'Leave your details to meet us at a show or our office.')}</p>
<form class="form rv" style="margin-top:32px" data-es-form action="{url(cur, lp(lang, 'contact/thanks/'))}" novalidate>
{form_field(L('회사명', 'Company'), 'company', req=True)}{form_field(L('담당자', 'Name'), 'name', req=True)}{form_field(L('이메일', 'Email'), 'email', 'email', req=True)}{form_field(L('희망 일정', 'Preferred date'), 'date', 'date')}
{form_field(L('문의 내용', 'Message'), 'message', 'textarea', full=True)}{consent(lang)}<p class="form-msg">{L('필수 항목을 확인해 주세요.', 'Please complete the required fields.')}</p><div class="form-actions"><button class="btn btn-pri" type="submit">{L('예약 문의', 'Send')} {ARROW}</button></div></form></div>
</div></div>'''
    write(lang, cur, L('전시회·행사', 'Exhibitions & Events'), L('엑소스킨 전시회 참가 일정과 미팅 예약.', 'EXOSKIN exhibitions and meeting bookings.'), body)

# ================================================================== CONTACT
def contact_aside(lang):
    k = lang == 'ko'
    return f'''<aside class="contact-aside rv"><h3>{'문의 안내' if k else 'Contact'}</h3><ul>
<li><b>EMAIL</b><a href="mailto:{SITE['email']}" style="color:inherit">{SITE['email']}</a></li>
<li><b>{'전화' if k else 'PHONE'}</b><a href="tel:{SITE['tel_link']}" style="color:inherit">{SITE['tel'] if k else SITE['tel_intl']}</a></li>
<li><b>{'운영 시간' if k else 'HOURS'}</b>{'평일 09:00~18:00' if k else 'Mon–Fri 09:00–18:00 (KST, GMT+9)'}</li>
<li><b>{'회신' if k else 'REPLY'}</b>{'영업일 기준 1~2일 내 회신' if k else 'Within 24–48 business hours'}</li></ul></aside>'''

def page_contact(lang):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    c0 = (L('문의', 'Contact'), 'contact/')
    thanks = lambda cur: url(cur, lp(lang, 'contact/thanks/'))
    msg = '<p class="form-msg">%s</p>' % L('필수 항목(*)을 확인해 주세요.', 'Please complete the required fields (*).')
    cur = lp(lang, 'contact/')
    body = subvis(lang, cur, L('문의', 'Contact'), L('무엇을 도와드릴까요?', 'How can we help?'), 'space-08', [c0]) + lnb(lang, cur, 'contact')
    cards = [('doc', L('견적·샘플 문의', 'Request a Quote'), L('제품·수량·현장 정보를 보내 주시면 견적과 샘플을 안내합니다.', 'Send product, quantity and site details for a quote and samples.'), 'contact/quote/'),
             ('users', L('파트너·대리점 모집', 'Become a Partner'), L('국내 대리점·시공 파트너를 모집합니다.', 'Distributors, applicators and EPC partners.') if True else '', 'contact/partner/'),
             ('tool', L('기술 상담', 'Technical Consultation'), L('도면·사양서 검토와 제품 선정을 도와드립니다.', 'Drawing review and product selection.'), 'contact/technical/'),
             ('chat', L('자주 묻는 질문', 'FAQ'), L('제품·시공·인증·주문에 관한 질문', 'Products, application, certification, orders'), 'contact/faq/')]
    body += f'''<div class="page"><div class="wrap"><div class="tiles">{''.join('<a class="tile rv d%d" href="%s"><span class="ico">%s</span><h3>%s</h3><p>%s</p><span class="more">%s %s</span></a>' % (i, url(cur, lp(lang, p)), ic(a), b, c, L('바로가기', 'Go'), ARROW) for i, (a, b, c, p) in enumerate(cards))}</div>
<div class="block tiles c3">{''.join('<div class="tile rv"><span class="tag">%s</span><h4>%s</h4></div>' % (a, b) for a, b in [('EMAIL', SITE['email']), (L('전화', 'PHONE'), '<a href="tel:%s" style="color:inherit">%s</a>' % (SITE['tel_link'], L(SITE['tel'], SITE['tel_intl']))), (L('운영 시간', 'HOURS'), L('평일 09:00~18:00', 'Mon–Fri 09:00–18:00 KST'))])}</div></div></div>'''
    write(lang, cur, L('문의', 'Contact'), L('견적·샘플 문의, 파트너 모집, 기술 상담, 자주 묻는 질문.', 'Request a quote, become a partner, technical consultation and FAQ.'), body)

    # quote
    cur = lp(lang, 'contact/quote/')
    body = subvis(lang, cur, L('견적·샘플 문의', 'Request a Quote'), L('제품 상세에서 오셨다면 제품명이 자동으로 입력됩니다.', 'Coming from a product page? The product is pre-selected.'), 'space-10', [c0, (L('견적·샘플 문의', 'Request a Quote'), None)]) + lnb(lang, cur, 'contact')
    if k:
        fields = (form_field('회사명', 'company', req=True) + form_field('담당자', 'name', req=True) + form_field('연락처', 'phone', 'tel', req=True, ph='010-0000-0000') + form_field('이메일', 'email', 'email', req=True) +
                  form_field('관심 제품', 'product', 'select', req=True, opts=product_options(lang)) + form_field('현장 위치', 'site', ph='예: 경기도 평택시') +
                  form_field('면적·수량', 'qty', ph='예: 지붕 3,000㎡ / 20L 50통') + form_field('희망 납기', 'due', 'date') +
                  form_field('도면·사양서 첨부', 'file', 'file', full=True, hint='PDF, DWG, JPG (최대 20MB)') + form_field('문의 내용', 'message', 'textarea', full=True, ph='요구 내화시간, 사용 온도 등 현장 조건을 적어 주시면 더 정확한 견적이 가능합니다.'))
    else:
        fields = (form_field('Company', 'company', req=True) + form_field('Name', 'name', req=True) + form_field('Country', 'country', req=True) + form_field('Email', 'email', 'email', req=True) +
                  form_field('Phone / WhatsApp', 'phone', 'tel') + form_field('Company type', 'ctype', 'select', req=True, opts=[('', 'Select'), ('distributor', 'Distributor'), ('contractor', 'Contractor / Applicator'), ('epc', 'EPC'), ('end', 'End user'), ('other', 'Other')]) +
                  form_field('Target product', 'product', 'select', req=True, opts=product_options(lang)) + form_field('Estimated annual volume', 'volume', ph='e.g. 20 t / year or 5,000 m²') +
                  form_field('Incoterms', 'incoterms', 'select', opts=[('', 'Select'), ('FOB', 'FOB'), ('CIF', 'CIF'), ('DAP', 'DAP'), ('other', 'Other / not sure')]) + form_field('Destination port', 'port', ph='e.g. Port of Jakarta') +
                  form_field('Attachments', 'file', 'file', full=True, hint='PDF, DWG, JPG (max 20 MB)') + form_field('Message', 'message', 'textarea', full=True, ph='Required fire rating, operating temperature (°C/°F), project schedule…'))
    body += f'''<div class="page"><div class="wrap form-layout"><form class="form rv" data-es-form action="{thanks(cur)}" novalidate>{fields}{consent(lang)}{msg}<div class="form-actions"><button class="btn btn-pri" type="submit">{L('문의 접수', 'Submit request')} {ARROW}</button></div></form>{contact_aside(lang)}</div></div>'''
    write(lang, cur, L('견적·샘플 문의', 'Request a Quote'), L('엑소스킨 에어로젤 제품 견적·샘플 문의.', 'Request a quote or samples for EXOSKIN aerogel products.'), body)

    # partner
    cur = lp(lang, 'contact/partner/')
    body = subvis(lang, cur, L('파트너·대리점 모집', 'Become a Partner'), L('에어로젤 방화·단열 시장을 함께 열어 갈 파트너를 찾습니다.', 'Join us in bringing aerogel fire protection and insulation to your market.'), 'space-02', [c0, (L('파트너·대리점 모집', 'Become a Partner'), None)]) + lnb(lang, cur, 'contact')
    ptypes = [('box', L('유통 대리점', 'Distributor'), L('지역 내 제품 유통과 고객 관리', 'Distribution and customer management in your territory')),
              ('tool', L('시공 파트너', 'Applicator'), L('도장·단열·소방 시공사', 'Coating, insulation and fire-protection contractors')),
              ('target', L('EPC·설계', 'EPC & specifiers'), L('플랜트·건축 프로젝트 사양 반영', 'Specification on plant and building projects'))]
    support = [L('제품·시공 교육', 'Product and application training'), L('샘플 키트 제공', 'Sample kits'), L('카탈로그·영업 자료 지원', 'Catalogs and sales materials'), L('기술 상담·현장 지원', 'Technical and on-site support')]
    if k:
        fields = (form_field('회사명', 'company', req=True) + form_field('담당자', 'name', req=True) + form_field('연락처', 'phone', 'tel', req=True) + form_field('이메일', 'email', 'email', req=True) +
                  form_field('희망 지역', 'region', req=True, ph='예: 충청권') + form_field('사업 분야', 'biz', 'select', req=True, opts=[('', '선택'), ('paint', '도장'), ('ins', '단열'), ('fire', '소방'), ('dist', '유통'), ('etc', '기타')]) +
                  form_field('보유 인력·장비', 'staff') + form_field('연 매출 규모', 'rev', 'select', opts=[('', '선택'), ('a', '10억 미만'), ('b', '10~50억'), ('c', '50~100억'), ('d', '100억 이상')]) +
                  form_field('희망 품목', 'items', full=True, ph='예: 방화도료, 지붕 단열 도료') + form_field('소개·문의 내용', 'message', 'textarea', full=True))
    else:
        fields = (form_field('Company', 'company', req=True) + form_field('Name', 'name', req=True) + form_field('Country / Region', 'country', req=True) + form_field('Email', 'email', 'email', req=True) +
                  form_field('Business type', 'biz', 'select', req=True, opts=[('', 'Select'), ('dist', 'Distributor / Trader'), ('app', 'Applicator / Contractor'), ('epc', 'EPC / Engineering'), ('other', 'Other')]) + form_field('Years in business', 'years', 'number') +
                  form_field('Annual revenue range', 'rev', 'select', opts=[('', 'Select'), ('a', '< USD 1M'), ('b', 'USD 1–5M'), ('c', 'USD 5–20M'), ('d', '> USD 20M')]) + form_field('Website', 'web', 'url', ph='https://') +
                  form_field('Current product lines', 'lines', full=True) + form_field('Target market & message', 'message', 'textarea', full=True, ph='Which customers and regions would you serve?'))
    body += f'''<div class="page"><div class="wrap">
<div class="block"><span class="eyebrow rv">Partner Types</span><h2 class="h3 rv">{L('모집 분야', 'Who we are looking for')}</h2><div class="tiles c3" style="margin-top:28px">{''.join('<div class="tile rv d%d"><span class="ico">%s</span><h3>%s</h3><p>%s</p></div>' % (i, ic(a), b, c) for i, (a, b, c) in enumerate(ptypes))}</div></div>
<div class="block split" style="align-items:start"><div class="rv"><span class="eyebrow">Support</span><h2 class="h3">{L('파트너 지원', 'What partners get')}</h2><ul class="checks">{''.join('<li>%s<span>%s</span></li>' % (ic('check'), s) for s in support)}</ul></div>
<div class="rv d1"><div class="callout" style="margin-top:0"><b>{L('지역 조건', 'Territories')}</b> — {L('지역별 대리점 조건은 상담을 통해 안내합니다.', 'Territory and exclusivity terms are discussed individually, within the scope of our distribution agreement with the manufacturer.')}</div></div></div>
<div class="block"><h2 class="h3 rv">{L('파트너 신청', 'Apply')}</h2><form class="form rv" style="margin-top:32px" data-es-form action="{thanks(cur)}" novalidate>{fields}{consent(lang)}{msg}<div class="form-actions"><button class="btn btn-pri" type="submit">{L('파트너 신청', 'Submit application')} {ARROW}</button></div></form></div>
</div></div>'''
    write(lang, cur, L('파트너·대리점 모집', 'Become a Partner'), L('엑소스킨 국내 대리점·시공 파트너 모집.', 'Distribution, applicator and EPC partnership with EXOSKIN.'), body)

    # technical
    cur = lp(lang, 'contact/technical/')
    body = subvis(lang, cur, L('기술 상담', 'Technical Consultation'), L('사양 검토·제품 선정이 필요한 엔지니어를 위한 창구', 'For engineers who need specification review'), 'scene-04', [c0, (L('기술 상담', 'Technical Consultation'), None)]) + lnb(lang, cur, 'contact')
    fields = (form_field(L('회사명', 'Company'), 'company', req=True) + form_field(L('담당자', 'Name'), 'name', req=True) + form_field(L('이메일', 'Email'), 'email', 'email', req=True) + form_field(L('연락처', 'Phone'), 'phone', 'tel') +
              form_field(L('관련 제품', 'Product'), 'product', 'select', opts=product_options(lang)) + form_field(L('적용 공간', 'Application'), 'space', 'select', opts=[('', L('선택', 'Select'))] + [(s['id'], s[lang]['name']) for s in SECTORS]) +
              form_field(L('사용 온도', 'Operating temperature'), 'temp', ph=L('예: 350℃', 'e.g. 350 °C / 660 °F')) + form_field(L('요구 내화시간', 'Required fire rating'), 'rating', ph=L('예: 120분', 'e.g. 120 min')) +
              form_field(L('시공 면적', 'Area'), 'area', ph=L('예: 1,200㎡', 'e.g. 1,200 m²')) + form_field(L('도면·사양서', 'Drawings / specs'), 'file', 'file') +
              form_field(L('상담 내용', 'Details'), 'message', 'textarea', req=True, full=True))
    body += f'''<div class="page"><div class="wrap form-layout"><form class="form rv" data-es-form action="{thanks(cur)}" novalidate>{fields}{consent(lang)}{msg}<div class="form-actions"><button class="btn btn-pri" type="submit">{L('상담 신청', 'Request consultation')} {ARROW}</button></div></form>{contact_aside(lang)}</div></div>'''
    write(lang, cur, L('기술 상담', 'Technical Consultation'), L('도면·사양서를 첨부해 에어로젤 제품 기술 상담을 신청하세요.', 'Request technical consultation with drawings and specifications.'), body)

    # FAQ
    cur = lp(lang, 'contact/faq/')
    body = subvis(lang, cur, L('자주 묻는 질문', 'FAQ'), '', 'scene-03', [c0, ('FAQ', None)]) + lnb(lang, cur, 'contact')
    if k:
        faq = [('제품', [('에어로젤 도료와 일반 단열·방화 도료는 무엇이 다른가요?', '에어로젤은 나노 기공에 공기를 가둔 초경량 소재로, 얇은 도막에서도 열전달을 크게 줄입니다. 엑소스킨 도료는 이 에어로젤을 함유해 단열·방화 기능을 높였습니다.'),
                       ('제품 사양의 수치는 어떤 기준인가요?', '모든 수치는 제조사(중국 GB 등) 시험 기준입니다. 국내 인증은 취득 후 인증·시험성적서 페이지에 별도로 게시합니다.'),
                       ('제조사는 어디인가요?', '중국 숴싱 신소재(Shuoxing New Materials)가 생산하며, 엑소스킨(주식회사 에코아트)가 한국 공식 총판으로 공급합니다.')]),
               ('시공', [('직접 시공할 수 있나요?', '내벽용 도료와 단열 펠트는 일반 도장·보온 시공 경험이 있으면 시공할 수 있습니다. 내화도료는 요구 도막 두께 관리가 중요하므로 전문 시공사 시공을 권장합니다.'),
                       ('소요량은 어떻게 계산하나요?', '시공 면적, 요구 성능(내화시간·사용 온도)에 따라 달라집니다. 도면이나 면적을 보내 주시면 산출해 드립니다.')]),
               ('인증', [('국내 인증이 있나요?', '현재 국내 인증 취득을 준비하고 있습니다. 취득 전에는 "방염 인증", "내화구조 인정" 등의 표현을 쓰지 않으며, 진행 상황은 홈페이지에 공지합니다.')]),
               ('주문·배송', [('샘플을 받을 수 있나요?', '견적·샘플 문의에 제품과 용도를 남겨 주시면 샘플 제공 여부와 일정을 안내합니다.'),
                          ('납기는 얼마나 걸리나요?', '국내 재고 제품은 주문 확인 후 빠르게 출고하며, 재고가 없는 제품은 수입 일정에 따라 달라집니다. 견적 시 함께 안내합니다.')])]
    else:
        faq = [('Products', [('How do aerogel coatings differ from standard insulation or fire-protection coatings?', 'Aerogel traps air in nanoscale pores, cutting heat transfer even in thin films. EXOSKIN coatings contain aerogel to boost insulation and fire performance.'),
                             ('What standards are the values based on?', 'All values are from the manufacturer\'s tests (Chinese GB standards, etc.). We do not claim compliance with EN, ASTM/UL or other regional standards unless products have been tested to them.'),
                             ('Who manufactures the products?', 'Shuoxing New Materials in China. EXOSKIN (ECOART Co., Ltd., Korea) is the official Korea distributor.')]),
               ('Orders & export', [('What is the MOQ?', 'MOQ depends on the product and packaging. Tell us your target products and volumes and we will confirm.'),
                                    ('What are the lead times?', 'Lead time depends on product, quantity and stock. We confirm it with every quotation.'),
                                    ('Which Incoterms and payment terms do you offer?', 'FOB, CIF and DAP are available on request. Payment terms are agreed per order.'),
                                    ('What documents are provided?', 'Commercial invoice, packing list, certificate of origin (COO), SDS and TDS. HS codes are provided per product with your quotation.')]),
               ('Application', [('Do you provide technical support?', 'Yes. Send drawings and site conditions and our engineers will review specifications and recommend products and quantities.')])]
    acc = ''.join('<p class="acc-cat rv">%s</p>%s' % (c, ''.join('<details class="rv"><summary>%s</summary><div class="a">%s</div></details>' % (q, a) for q, a in qs)) for c, qs in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for c, qs in faq for q, a in qs]}
    body += f'''<div class="page"><div class="wrap" style="max-width:980px"><div class="acc">{acc}</div><p style="margin-top:56px;text-align:center"><a class="btn btn-pri" href="{url(cur, lp(lang, 'contact/technical/'))}">{L('원하는 답이 없나요? 문의하기', 'Still have questions? Ask us')} {ARROW}</a></p></div></div>'''
    write(lang, cur, L('자주 묻는 질문', 'FAQ'), L('엑소스킨 제품·시공·인증·주문 관련 자주 묻는 질문.', 'Frequently asked questions about EXOSKIN products, export and application.'), body,
          extra_head='<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False))

    # thanks
    cur = lp(lang, 'contact/thanks/')
    body = subvis(lang, cur, L('문의가 접수되었습니다', 'Thank you'), '', 'space-10', [c0, (L('접수 완료', 'Thank you'), None)])
    body += f'''<div class="page"><div class="wrap" style="text-align:center;max-width:760px"><span class="ico" style="display:inline-grid;width:80px;height:80px;border-radius:50%;background:rgba(46,158,91,.12);color:var(--green);place-items:center">{ic('check').replace('<svg', '<svg style="width:40px;height:40px"')}</span>
<h2 class="h2" style="margin-top:24px">{L('감사합니다.', 'Thank you for contacting us.')}</h2><p class="lead" style="margin:16px auto 0">{L('담당자가 영업일 기준 1~2일 안에 연락드리겠습니다. 접수 확인 메일을 보내 드렸습니다.', 'We will reply within 24–48 business hours (Korea time, GMT+9). A confirmation email is on its way.')}</p>
<div class="hero-btns" style="justify-content:center;margin-top:40px"><a class="btn btn-pri" href="{url(cur, lp(lang, 'resources/catalogs/'))}">{L('카탈로그 받기', 'Get the catalog')} {ARROW}</a><a class="btn btn-line" href="{url(cur, lp(lang, ''))}">{L('홈으로', 'Back to home')}</a></div>
<p class="note" style="margin-top:40px">{L('※ 현재 시안 단계로 문의 양식은 서버에 연결되어 있지 않습니다.', '※ Draft site: forms are not yet connected to a server.')}</p></div></div>'''
    write(lang, cur, L('문의 완료', 'Thank you'), '', body, noindex=True)

# ================================================================== UTILITY
def page_util(lang):
    k = lang == 'ko'
    L = lambda a, b: a if k else b
    # search
    cur = lp(lang, 'search/')
    body = subvis(lang, cur, L('통합검색', 'Search'), '', 'space-06', [(L('통합검색', 'Search'), None)])
    body += f'''<div class="page"><div class="wrap"><form class="search-box" onsubmit="return false"><input id="search-q" type="search" placeholder="{L('제품명, 적용 공간, 자료를 검색하세요', 'Search products, applications, documents')}" aria-label="search"></form><div class="search-res" id="search-res"></div></div></div>
<script src="{asset(cur, 'js/search-%s.js' % lang)}"></script>'''
    write(lang, cur, L('통합검색', 'Search'), L('엑소스킨 사이트 통합검색', 'Search the EXOSKIN site'), body, noindex=True)

    def legal(path, title, sections, image='space-08'):
        cur = lp(lang, path)
        b = subvis(lang, cur, title, '', image, [(title, None)])
        b += '<div class="page"><div class="wrap prose" style="max-width:920px">%s<p class="note" style="margin-top:48px">%s</p></div></div>' % (''.join('<h2 class="h3" style="margin:48px 0 8px">%s</h2>%s' % (h, ''.join('<p>%s</p>' % x for x in ps)) for h, ps in sections), L('시행일: 2026년 [ ]월 [ ]일 · 법률 검토 후 확정', 'Effective: [date] · subject to legal review'))
        write(lang, cur, title, title, b)
    if k:
        legal('privacy/', '개인정보처리방침', [
            ('1. 수집하는 개인정보 항목', ['회사는 견적·상담·파트너 신청을 위해 회사명, 담당자명, 연락처, 이메일, 문의 내용, 첨부파일을 수집합니다.']),
            ('2. 수집·이용 목적', ['문의 회신, 견적 제공, 계약 이행, 고객 관리 및 서비스 개선에 이용합니다.']),
            ('3. 보유·이용 기간', ['문의 처리 완료 후 3년간 보관 후 파기합니다. 관계 법령에 따라 보존이 필요한 경우 해당 기간 동안 보관합니다.']),
            ('4. 제3자 제공 및 처리 위탁', ['회사는 정보주체의 동의 없이 개인정보를 제3자에게 제공하지 않습니다. 처리 위탁이 발생하는 경우 본 방침을 통해 공개합니다.']),
            ('5. 정보주체의 권리', ['정보주체는 언제든지 개인정보 열람·정정·삭제·처리정지를 요구할 수 있습니다.']),
            ('6. 개인정보 보호책임자', ['성명: %s (대표이사) / 전화: %s / 이메일: %s' % (SITE['ceo_ko'], SITE['tel'], SITE['email'])])])
        legal('terms/', '이용약관', [('제1조 (목적)', ['이 약관은 주식회사 에코아트(이하 "회사")가 운영하는 EXOSKIN 웹사이트의 이용 조건과 절차를 정합니다.']),
                                  ('제2조 (정보의 제공)', ['사이트에 게시된 제품 정보와 수치는 제조사 시험 기준이며, 실제 성능은 시공 조건에 따라 달라질 수 있습니다. 설계·시공 시에는 최신 TDS와 담당자 상담을 통해 확인하십시오.']),
                                  ('제3조 (저작권)', ['사이트의 콘텐츠에 대한 저작권은 회사 또는 정당한 권리자에게 있으며, 사전 동의 없이 복제·배포할 수 없습니다.'])])
        legal('no-email-collection/', '이메일무단수집거부', [('', ['본 웹사이트에 게시된 이메일 주소가 전자우편 수집 프로그램이나 그 밖의 기술적 장치를 이용하여 무단으로 수집되는 것을 거부하며, 이를 위반 시 정보통신망법에 의해 형사 처벌됨을 유념하시기 바랍니다.'])])
    else:
        legal('privacy/', 'Privacy Policy', [
            ('1. Data we collect', ['Company name, name, country, email, phone/WhatsApp, inquiry details and attachments you submit through our forms.']),
            ('2. Why we use it', ['To respond to inquiries, prepare quotations, manage partnerships and improve our services.']),
            ('3. International transfers', ['Data is processed in the Republic of Korea. Where required (e.g. under the GDPR), we rely on appropriate safeguards for transfers.']),
            ('4. Retention', ['Up to 3 years after your inquiry is resolved, unless a longer period is required by law.']),
            ('5. Your rights', ['You may request access, correction, deletion or restriction of processing, and object to processing, by contacting %s.' % SITE['email']])])
        legal('terms/', 'Terms of Use', [('Information', ['Product data on this site is based on manufacturer tests. Actual performance depends on site conditions. Always confirm with the latest TDS and our engineers.']),
                                         ('Intellectual property', ['Content on this site belongs to ECOART Co., Ltd. or its licensors and may not be reproduced without permission.'])])
        legal('cookies/', 'Cookie Policy', [('Cookies we use', ['This site currently uses only essential browser storage (for example, remembering that you dismissed the language banner). If analytics cookies are added, a consent banner will be shown first.'])])

    # sitemap page
    cur = lp(lang, 'sitemap/')
    cols = ''
    for n in nav(lang):
        cols += '<div class="tile rv"><h3>%s</h3><ul style="margin-top:14px">%s</ul></div>' % (esc(n['label']), ''.join('<li style="padding:4px 0"><a href="%s">%s</a></li>' % (url(cur, lp(lang, p)), esc(l)) for l, p in n['kids']))
    body = subvis(lang, cur, L('사이트맵', 'Sitemap'), '', 'space-06', [(L('사이트맵', 'Sitemap'), None)])
    body += '<div class="page"><div class="wrap"><div class="tiles">%s</div></div></div>' % cols
    write(lang, cur, L('사이트맵', 'Sitemap'), L('엑소스킨 전체 메뉴', 'All EXOSKIN pages'), body)

# ================================================================== BUILD
def collect_paths():
    """hreflang/언어 전환용 경로 목록을 미리 만든다."""
    base = ['', 'about/ecoshield/', 'about/brand/', 'about/manufacturer/', 'about/quality/', 'about/global-network/', 'about/location/',
            'products/', 'products/finder/'] + [group_path(g) for g in GROUPS] + [product_path(p) for p in PRODUCTS] + \
           ['applications/'] + [sector_path(s) for s in SECTORS] + [space_path(sp) for sp in SPACES if sp['landing']] + \
           ['technology/aerogel/', 'technology/certifications/', 'projects/', 'projects/korea/', 'projects/global/', 'projects/case-template/',
            'resources/', 'resources/catalogs/', 'resources/data-sheets/', 'resources/guides/', 'resources/videos/',
            'news/notices/', 'news/exhibitions/', 'contact/', 'contact/quote/', 'contact/partner/', 'contact/technical/', 'contact/faq/', 'contact/thanks/',
            'search/', 'privacy/', 'terms/', 'sitemap/']
    KO_PATHS.update(base + ['technology/insights/', 'no-email-collection/'])
    EN_PATHS.update(['en/' + p for p in base] + ['en/cookies/'])

def main():
    collect_paths()
    for lang in ('ko', 'en'):
        page_home(lang); page_about(lang); page_products(lang); page_applications(lang)
        page_technology(lang); page_projects(lang); page_resources(lang); page_news(lang)
        page_contact(lang); page_util(lang)
    # search indexes
    for lang in ('ko', 'en'):
        idx = [dict(t=p['title'], u=p['path'] + 'index.html', d=p['desc'], k=p['kw']) for p in PAGES if p['lang'] == lang]
        with open(os.path.join(OUT, 'assets/js/search-%s.js' % lang), 'w', encoding='utf-8') as f:
            f.write('window.ES_INDEX=' + json.dumps(idx, ensure_ascii=False) + ';')
    # sitemap.xml / robots.txt
    urls = ''.join('<url><loc>%s/%s</loc><lastmod>%s</lastmod></url>' % (SITE['domain'], p['path'], TODAY) for p in PAGES)
    with open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>' % urls)
    with open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write('User-agent: *\nAllow: /\nDisallow: /projects/case-template/\nDisallow: /en/projects/case-template/\nSitemap: %s/sitemap.xml\n' % SITE['domain'])
    print('pages:', len(PAGES), 'ko:', sum(1 for p in PAGES if p['lang'] == 'ko'), 'en:', sum(1 for p in PAGES if p['lang'] == 'en'))

if __name__ == '__main__':
    main()
