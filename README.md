# py_unshorten_urls

Unshorten URLs in a file.

```
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
```

### Examples

#### Unshorten URLs in a text file using 25 workers in parallel

```
python3 unshorten_urls.py file_containing_urls.txt -w 25
```

#### Import and use as a library

```
from unshorten_urls import UnshortenURLs

unshorten = UnshortenURLs._unshorten

unshorten("url")
```
