# -*- coding: utf-8 -*-
"""Сборка автономной версии сайта: весь CSS и все картинки внутри одного HTML-файла.

Запуск из папки проекта:  python3 tools/build_single.py
Результат: «Сайт_одним_файлом.html» рядом с index.html
"""
import base64
import io
import os
import re

from PIL import Image

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SRC, 'Сайт_одним_файлом.html')


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    im = Image.open(path)
    buf = io.BytesIO()
    if ext == '.png':
        im.thumbnail((360, 360), Image.LANCZOS)
        im.save(buf, 'PNG', optimize=True)
        mime = 'image/png'
    else:
        im = im.convert('RGB')
        im.thumbnail((1100, 1100), Image.LANCZOS)
        im.save(buf, 'JPEG', quality=80, optimize=True, progressive=True)
        mime = 'image/jpeg'
    print(f'  {os.path.basename(path):16} {len(buf.getvalue()) // 1024:>4} КБ -> data-URI')
    return f'data:{mime};base64,{base64.b64encode(buf.getvalue()).decode("ascii")}'


images = {f'images/{n}': data_uri(os.path.join(SRC, 'images', n)) for n in os.listdir(os.path.join(SRC, 'images'))}
css = open(os.path.join(SRC, 'style.css'), encoding='utf-8').read()

pages = [
    ('index.html', 'page-1', 'Главная'),
    ('index01.html', 'page-2', 'Туры и цены'),
    ('index02.html', 'page-3', 'О компании'),
]


def rewrite(html):
    def fix_href(m):
        href = m.group(1)
        for fname, pid, _ in pages:
            if href.startswith(fname):
                frag = href[len(fname):]
                return f'href="{"#" + frag[1:] if frag else "#" + pid}"'
        return m.group(0)

    html = re.sub(r'href="([^"]*index(?:01|02)?\.html[^"]*)"', fix_href, html)
    html = re.sub(r'(src=)"([^"]+\.(?:jpg|png))"', lambda m: f'{m.group(1)}"{images.get(m.group(2), m.group(2))}"', html)
    html = re.sub(r'(href=)"(images/[^"]+)"', lambda m: f'{m.group(1)}"{images.get(m.group(2), m.group(2))}"', html)
    return html


body_parts = []
for fname, pid, title in pages:
    body = re.search(r'<body[^>]*>(.*)</body>',
                     open(os.path.join(SRC, fname), encoding='utf-8').read(), re.S).group(1)
    body_parts.append(f'''
<!-- ======================= {title.upper()} ======================= -->
<div class="page-block" id="{pid}">
    <div class="page-sep"><span>{title}</span></div>
{rewrite(body)}
</div>
''')

doc = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Туристическое агентство «Меридиан» — Кабанов А. Г., ИМСИТ</title>
<!--
    АВТОНОМНАЯ ВЕРСИЯ САЙТА.
    Все стили и изображения находятся внутри этого файла (встроенный CSS и data-URI),
    поэтому страница открывается с телефона даже без папки style.css и папки images.
    Три страницы собраны в один документ и связаны якорями.
    Файл собирается скриптом tools/build_single.py — вручную не редактировать.
-->
<style>
{css}

/* ---------- служебные стили автономной версии ---------- */
.page-sep {{
    max-width: 1080px;
    margin: 34px auto 0;
    padding: 0 24px;
}}
.page-sep span {{
    display: block;
    border-top: 2px dashed #C9D6E2;
    padding-top: 10px;
    font-family: Verdana, Geneva, Tahoma, sans-serif;
    font-size: 11px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #7B8B99;
}}
.page-block {{ scroll-margin-top: 10px; }}
</style>
</head>
<body>
{"".join(body_parts)}
</body>
</html>
'''

open(OUT, 'w', encoding='utf-8').write(doc)
print(f'\nГотово: {OUT}  ({os.path.getsize(OUT) / 1024 / 1024:.2f} МБ)')
