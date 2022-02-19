#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
usage: unshorten_urls [-h] [-o OUTPUT_NAME] [-c CHUNKSIZE] [-e ENCODING]
                      [-m METHOD] [-t TIMEOUT] [-w WORKERS]
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
                        file encoding (default: utf-8)
  -m METHOD, --method METHOD
                        request method (default: HEAD); for some shorteners
                        like "migre.me" the full URL is only returned via GET
  -t TIMEOUT, --timeout TIMEOUT
                        in seconds (default: 60)
  -w WORKERS, --workers WORKERS
                        max workers (default: 8)
"""

from argparse import ArgumentParser
from csv import writer
from functools import partial
from os.path import basename, splitext
from requests import request
#from requests.exceptions import ConnectionError

from tqdm.contrib.concurrent import process_map
#from tqdm.auto import tqdm

CHUNKSIZE = 1
ENCODING = "utf-8"
METHOD = "HEAD"
TIMEOUT = 60
WORKERS = 8


class UnshortenURLs():

    def __main__(
        self,
        input_name,
        output_name=None,
        allow_redirects=True,
        chunksize=CHUNKSIZE,
        encoding=ENCODING,
        method=METHOD,
        timeout=TIMEOUT,
        workers=WORKERS,
    ) -> None:

        if not output_name:
            name, ext = splitext(basename(input_name))
            output_name = name + "_EXPANDED.csv"

        with open(input_name, "rt", encoding=encoding, errors="ignore") as input_file:
            urls = [x.rstrip().lstrip('"').rstrip('"') for x in input_file.readlines()]

        print(f"Read {len(urls)} lines.")

        expanded_urls = [u for u in process_map(
            partial(
                self._unshorten,
                allow_redirects=allow_redirects,
                method=method,
                timeout=timeout,
            ),
            urls,
            ascii=True,
            chunksize=chunksize,
            desc="Unshortening URLs",
            max_workers=workers,
            total=len(urls))]

        print(f"Returned {len(expanded_urls)} URLs.")

        with open(output_name, "w", newline="", encoding=encoding, errors="ignore") as output_file:
            file_writer = writer(output_file, delimiter="\t")
            file_writer.writerow(["url", "expanded_url"])
            for url, expanded_url in zip(urls, expanded_urls):
                file_writer.writerow([url, expanded_url])

    @staticmethod
    def _unshorten(url, method="HEAD", allow_redirects=True, timeout=TIMEOUT) -> str:
        try:
            r = request(method, url, allow_redirects=allow_redirects, timeout=timeout)
            try:
                content = r.content.decode("utf8")
                if "url=" in content:
                    return content.split('url="',1)[-1].split('">',1)[0] # migre.me
                else:
                    return r.url
            except:
                return r.url
        except:
            return ""


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
                        help="file encoding (default: %s)" % ENCODING)

    parser.add_argument("-m", "--method",
                        action="store",
                        default=METHOD,
                        help="request method (default: %s); for some shorteners like \"migre.me\" the full URL is only returned via GET" % METHOD)

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

    UnshortenURLs().__main__(
        **vars(parser.parse_args())
    )

