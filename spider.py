#!/usr/bin/env python3
import requests
import re
from urllib.parse import urljoin, urldefrag, urlparse
import sys
import os
import argparse

class spider:
    def __init__(self, site):
        self.IMG_EXT = r'\.(?:png|gif|jpe?g|bmp)'
        self.imgs = set()
        self.urls = set()
        self.baseurl = site

    def get_imgs(self, url, level):
        self.urls.add(url)

        print(f"[{len(self.urls)} pages, {len(self.imgs)} imgs] level={level} {url}")
        re_img = re.compile(r'<img[^>]*?\ssrc=["\']([^"\'>]+?' + self.IMG_EXT + r')(?:\?[^"\'>]*)?["\']',re.I)

        re_bg = re.compile(r'background(?:-image)?\s*:[^;>]*?url\(\s*(?:["\']|&quot;)?([^"\'()>\s&]+?' + self.IMG_EXT + r')',re.I)
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"skip {url}: {e}")
            return
        html = r.text.strip()
        for l in re_img.findall(html) + re_bg.findall(html):
            self.imgs.add(urljoin(url, l))
        if level > 0:
            regexurl = r'<a\s[^>]*?href=["\'](.*?)["\']'
            lin = re.findall(regexurl, html, re.IGNORECASE)
            for l in lin:
                full, _ = urldefrag(urljoin(url, l))
                if urlparse(full).scheme not in ("http", "https"):
                    continue
                if full in self.urls:
                    continue
                if not self.same_site(self.baseurl, full):
                    continue
                self.get_imgs(full, level - 1)

    def save_images(self, route):
        os.makedirs(route, exist_ok=True)
        for l in self.imgs:
            try:
                img = requests.get(l, timeout=10)
                img.raise_for_status()
            except requests.RequestException as e:
                print(f"skip {l}: {e}")
                continue
            name = re.sub(r'[\/:?&=*<>|\\"#]+', '_', l)
            with open(os.path.join(route, name), 'wb') as handler:
                handler.write(img.content)

    def same_site(self, a, b):
        ha = urlparse(a).hostname or ""
        hb = urlparse(b).hostname or ""
        return ha == hb or ha.endswith("." + hb) or hb.endswith("." + ha)

def main():
    parser = argparse.ArgumentParser(prog="spider")
    parser.add_argument("-r", action="store_true", help="recursive download")
    parser.add_argument("-l", type=int, metavar="N", help="max recursion depth (default 5, needs -r)")
    parser.add_argument("-p", default="./data/", metavar="PATH", help="save path (default ./data/)")
    parser.add_argument("url")
    args = parser.parse_args()

    if args.l is not None:
        if not args.r:
            parser.error("-l requires -r")
        if args.l < 0:
            parser.error("depth can't be negative")

    recursion = (args.l if args.l is not None else 5) if args.r else 0

    tspider = spider(args.url)
    tspider.get_imgs(args.url, recursion)
    tspider.save_images(args.p)
    for l in tspider.imgs:
        print(l)

if __name__ == "__main__":
    main()