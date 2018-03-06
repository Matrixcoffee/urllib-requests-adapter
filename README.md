# urllib-requests-adapter
Make simple [requests](https://github.com/kennethreitz/requests)-using programs use urllib instead, without changing a line of code!

## What is this?
This is a so-called [adapter](https://en.wikipedia.org/wiki/Adapter_pattern), which converts (a subset of) [requests](https://github.com/kennethreitz/requests) API calls into Python's standard urllib API calls.

## Why does it exist?
Mainly to make [matrix-python-sdk](https://github.com/matrix-org/matrix-python-sdk) not depend on the full [requests](https://github.com/kennethreitz/requests) library.

The actual matrix-python-sdk API weighs in at 104K at the time of this writing, whereas the requests API is nearly 2M in size, making it about 1900% bigger. Depending on who you ask, that's a pretty heavy depencency, especially for a component which duplicates standard library functionality.

The end goal of all of this is to be able to simply plop [matrix-python-sdk](https://github.com/matrix-org/matrix-python-sdk) into a directory and start hacking.

## Status
**Alpha**. (Tested to work in a single use case, on Python 3.2, without error handling.)

## Recommended Installation
```
$ cd $SOMEWHERE
$ git clone https://github.com/matrix-org/matrix-python-sdk.git
$ git clone https://github.com/Matrixcoffee/urllib-requests-adapter.git
$ wget -P urllib-requests-adapter https://github.com/Anorov/PySocks/raw/master/socks.py # (optional)
```
And to try:
```
$ PYTHONPATH=matrix-python-sdk:urllib-requests-adapter python3 matrix-python-sdk/samples/SimpleChatClient.py
```

Happy hacking!

## Contributing
See [CONTRIBUTING.rst](https://github.com/matrix-org/matrix-python-sdk/blob/master/CONTRIBUTING.rst).

## Getting help
Get answers from @Coffee:matrix.org and others in [#matrix-python-sdk:matrix.org](https://matrix.to/#/#matrix-python-sdk:matrix.org).

## License
Copyright 2017 @Coffee:matrix.org

   > Licensed under the Apache License, Version 2.0 (the "License");
   > you may not use this file except in compliance with the License.

   > The full text of the License can be obtained from the file called [LICENSE](LICENSE).

   > Unless required by applicable law or agreed to in writing, software
   > distributed under the License is distributed on an "AS IS" BASIS,
   > WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   > See the License for the specific language governing permissions and
   > limitations under the License.
