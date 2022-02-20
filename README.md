# py_unshorten_urls

Unshorten URLs in a file.

```
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
```

### Examples

#### Unshorten URLs in a text file using 25 workers in parallel

```
python3 unshorten_urls.py file_containing_urls.txt -w 25
```

An output tab-delimited file by the default name of `file_containing_urls_UNSHORTENED.tab` will be created.

#### Import and use as a library

```
from unshorten_urls import UnshortenURLs

unshorten = UnshortenURLs()._unshorten

unshorten("url")
```

### Notes and limitations

#### Link extraction

Not all URLs are unshortened through simple `requests.HEAD` (default); for example, those which depend on JavaScript for redirecting (like [migre.me](https://migre.me)) are only obtainable by analyzing the returned content from a URL address - that is, using `requests.GET`.

To circumvent this, you may try and add `--method GET` to the command line (or `method="GET"` as an argument parameter) in order to extract any returned links (as in: starting with "http") within the content data, to be stored as an inline JSON dump.

If you'd prefer to get the content only, and later parse it yourself (e.g. using an [HTML parser](https://lxml.de/) or some - of many - [regular expression](https://mathiasbynens.be/demo/url-regex)), add `--raw-content` (or `raw_content=True`) to the list of arguments.

#### Known shorteners

When using `--shortened-only`, a simple condition check is employed to see if a given URL matches it.

If it doesn't, then the URL will be checked against a list of known `SHORTENERS` in file.

___

Found a bug? Please do open an issue so it is registered and can be (hopefully) fixed and/or improved upon. :-)
