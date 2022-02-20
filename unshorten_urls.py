#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
usage: unshorten_urls [-h] [-o OUTPUT_NAME] [-c CHUNKSIZE] [-e ENCODING]
                      [-m METHOD] [-t TIMEOUT] [-w WORKERS] [-a] [-r] [-s]
                      [-v] [--as-http] [--as-https] [--max-urls MAX_URLS]
                      input_name

positional arguments:
  input_name            input file name

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_NAME, --output_name OUTPUT_NAME
                        output file name
  -c CHUNKSIZE, --chunksize CHUNKSIZE
                        to send to workers (default: 1)
  -e ENCODING, --encoding ENCODING
                        encoder/decoder (default: utf-8)
  -m METHOD, --method METHOD
                        request method (default: HEAD); some shorteners (like
                        "migre.me") only return the full URL via GET
  -t TIMEOUT, --timeout TIMEOUT
                        in seconds (default: 30)
  -w WORKERS, --workers WORKERS
                        max workers (default: 8)
  -a, --all-urls        try and unshorten all, not only shortened URLs
  -r, --raw-content     stores raw content from link address when using GET
  -s, --stream          enable iterating over streaming endpoints
  -v, --verify          enable security certificate checks
  --as-http             unshorten addresses using HTTP
  --as-https            unshorten addresses using HTTP
  --max-urls MAX_URLS   maximum number of URLs within content to store
"""

import json
from argparse import ArgumentParser
from csv import writer
from functools import partial
from os.path import basename, splitext

from requests import Session
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm.contrib.concurrent import process_map
from urllib3 import disable_warnings
# from requests.exceptions import ConnectionError
# from requests_html import HTMLSession as Session
# from tqdm.auto import tqdm

disable_warnings(InsecureRequestWarning)

ALLOW_REDIRECTS = True
ALL_URLS = False
AS_HTTP = False
AS_HTTPS = False
CHUNKSIZE = 1
ENCODING = "utf-8"
MAX_URLS = None
METHOD = "HEAD"
RAW_CONTENT = False
STREAM = False
TIMEOUT = 30
VERIFY = False
WORKERS = 8

SHORTENERS = [
    "1url.com",
    "adcraft.co",
    "adcrun.ch",
    "adf.ly",
    "adflav.com",
    "aka.gr",
    "bc.vc",
    "bee4.biz",
    "bit.do",
    "bit.ly",
    "bitly.com",
    "buzurl.com",
    "cektkp.com",
    "cur.lv",
    "cutt.us",
    "db.tt",
    "dft.ba",
    "enlar.gr",
    "filoops.info",
    "fun.ly",
    "fzy.co",
    "go.shr.lc",
    "go2l.ink",
    "gog.li",
    "golinks.co",
    "goo.gl",
    "hit.my",
    "id.tl",
    "is.gd",
    "ity.im",
    "j.mp",
    "link.zip.net",
    "linkto.im",
    "ln.is",
    "lnk.co",
    "lnkd.in",
    "megaurl.it",
    "migre.me",
    "nov.io",
    "on.fb.me",
    "ow.ly",
    "p.dw.com",
    "p6l.org",
    "picz.us",
    "po.st",
    "prettylinkpro.com",
    "q.gs",
    "qr.ae",
    "qr.net",
    "scrnch.me",
    "shortquik.com",
    "sk.gy",
    "su.prgraphs",
    "t.co",
    "tinyurl.com",
    "tota2.com",
    "tr.im",
    "tweez.me",
    "twitthis.com",
    "u.bb",
    "u.to",
    "v.gd",
    "vai.la",
    "vzturl.com",
    "x.co",
    "xlinkz.info",
    "xtu.me",
    "yourls.org",
    "youtu.be",
    "yu2.it",
    "zpag.es",
]


class UnshortenURLs():

    def __main__(
        self,
        input_name,
        output_name=None,
        all_urls=ALL_URLS,
        allow_redirects=ALLOW_REDIRECTS,
        as_http=AS_HTTP,
        as_https=AS_HTTPS,
        chunksize=CHUNKSIZE,
        encoding=ENCODING,
        max_urls=MAX_URLS,
        method=METHOD,
        raw_content=RAW_CONTENT,
        stream=STREAM,
        timeout=TIMEOUT,
        verify=VERIFY,
        workers=WORKERS,
    ) -> None:

        if not output_name:
            name, ext = splitext(basename(input_name))
            output_name = name + "_UNSHORTENED.tab"

        with open(input_name, "rt", encoding=encoding, errors="ignore") as input_file:
            urls = [x.rstrip().lstrip('"').rstrip('"') for x in input_file.readlines()]

        print(f"Read {len(urls)} lines.")

        unshortened_urls = [u for u in process_map(
            partial(
                self._unshorten,
                allow_redirects=allow_redirects,
                as_http=as_http,
                as_https=as_https,
                all_urls=all_urls,
                encoding=encoding,
                max_urls=max_urls,
                method=method,
                raw_content=raw_content,
                stream=stream,
                timeout=timeout,
                verify=verify,
            ),
            urls,
            ascii=True,
            chunksize=chunksize,
            desc="Unshortening URLs",
            max_workers=workers,
            total=len(urls))]

        with open(output_name, "w", newline="", encoding=encoding, errors="ignore") as output_file:
            file_writer = writer(output_file, delimiter="\t")
            file_writer.writerow(["url", "full_url", "is_short"])
            for url, unshortened_url in zip(urls, unshortened_urls):
                file_writer.writerow([url, unshortened_url[0], unshortened_url[1] if unshortened_url[1] else ""])

    def _unshorten(
        self,
        url,
        all_urls=ALL_URLS,
        as_http=AS_HTTP,
        as_https=AS_HTTPS,
        allow_redirects=ALLOW_REDIRECTS,
        encoding=ENCODING,
        max_urls=MAX_URLS,
        method=METHOD,
        raw_content=RAW_CONTENT,
        stream=STREAM,
        timeout=TIMEOUT,
        verify=VERIFY,
    ) -> str:

        s = Session()
        is_short = self._is_short(url)
        url = self.__as_http(url) if as_http else self.__as_https(url) if as_https else url

        if not is_short and not all_urls:
            return (url, is_short)

        try:
            r = s.request(
                method,
                url,
                allow_redirects=allow_redirects,
                stream=stream,
                timeout=timeout,
                verify=verify,
            )

            try:
                url_ = self.__as_http(r.url) if as_http else self.__as_https(r.url) if as_https else r.url

                if url == url_ and (is_short or all_urls):
                    try:
                        content = r.content.decode(encoding)
                        # links = list(r.html.links) # requests_html.HTMLSession
                        if raw_content:
                            return content
                        links = self._find_links(content)[:max_urls]
                        return (json.dumps(links) if len(links) else "", is_short)

                    except:
                        return ("", is_short)

                return (r.url, is_short)

            except:
                return (r.url, is_short)

        except:
            return ("", is_short)

    @staticmethod
    def _find_links(content) -> list:
        return [_ for _ in content.split('"') if _.startswith("http")]

    @staticmethod
    def _is_short(url) -> bool:
        url = url.split("?", 1)[0].split("&", 1)[0]

        if (url.count('.') == 1 and url.split('.')[1].count('/') == 1)\
        or any(_ in url for _ in SHORTENERS):
            return True
        return False

    @staticmethod
    def __as_http(url):
        return (
            url.replace("https:", "http:", 1)
            if url.startswith("https:")
            else url
        )

    @staticmethod
    def __as_https(url):
        return (
            url.replace("http:", "https:", 1)
            if url.startswith("http:")
            else url
        )


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("input_name",
                        action="store",
                        help="input file name")

    parser.add_argument("-o", "--output_name",
                        action="store",
                        help="output file name")

    parser.add_argument("-c", "--chunksize",
                        action="store",
                        default=CHUNKSIZE,
                        help="to send to workers (default: %s)" % CHUNKSIZE,
                        type=int)

    parser.add_argument("-e", "--encoding",
                        action="store",
                        default=ENCODING,
                        help="encoder/decoder (default: %s)" % ENCODING)

    parser.add_argument("-m", "--method",
                        action="store",
                        default=METHOD,
                        help="request method (default: %s); some shorteners (like \"migre.me\") only return the full URL via GET" % METHOD)

    parser.add_argument("-t", "--timeout",
                        action="store",
                        default=TIMEOUT,
                        help="in seconds (default: %s)" % TIMEOUT,
                        type=int)

    parser.add_argument("-w", "--workers",
                        action="store",
                        default=WORKERS,
                        help="max workers (default: %s)" % WORKERS,
                        type=int)

    parser.add_argument("-a", "--all-urls",
                        action="store_true",
                        help="try and unshorten all, not only shortened URLs")

    parser.add_argument("-r", "--raw-content",
                        action="store_true",
                        help="stores raw content from link address when using GET")

    parser.add_argument("-s", "--stream",
                        action="store_true",
                        help="enable iterating over streaming endpoints")

    parser.add_argument("-v", "--verify",
                        action="store_true",
                        help="enable security certificate checks")

    parser.add_argument("--as-http",
                        action="store_true",
                        help="unshorten addresses using HTTP")

    parser.add_argument("--as-https",
                        action="store_true",
                        help="unshorten addresses using HTTP")

    parser.add_argument("--max-urls",
                        action="store",
                        help="maximum number of URLs within content to store",
                        type=int)

    UnshortenURLs().__main__(
        **vars(parser.parse_args())
    )
