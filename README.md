# ✨ fastlog: simple and colorful python logs ✨

**Fastlog** is designed to spice up your Python script logs with a simple but familiar interface. 

## Features

  * Works out-of-the-box
  * Sleek defaults
  * Simple, familiar `logging.Logger` interface with new features
  * Supports all terminal types (for Linux, Windows, MacOS, etc.)
  * No external package dependencies
  * Compatible with both Python 2.7 and Python 3
  * Modular styles, but customization is not required

## What is this for?
Fastlog is for anyone who writes quick scripts with lots of print statements but no time for Python's logging module.

Under the hood, fastlog wraps the same `logging.Logger` module that Python developers are used to, but with colorful defaults and more features.

## Example
```python
from fastlog import log
log.setLevel(log.DEBUG)

log.info("log.info")
log.success("log.success")
log.failure("log.failure")

with log.indent():
    log.debug("log.debug")
    log.warning("log.warning")

log.separator()

log.hexdump(list(map(chr, range(256))))
```

<p align="center">
  <img src="https://github.com/Gbps/fastlog/raw/master/docs/img/small-example.png" alt="Example Console Output" width="351px" height="260px">
</p>

## Installation and Usage
To install Fastlog, simply grab the PyPi package with pip.
```
$ pip install fastlog
```
To include fastlog in your script, add the following import:
```python
from fastlog import log
```

## Documentation
Fastlog is documented using regular Python docstrings in the source code itself.

ReadTheDocs compilation is still pending.

## Modular styles
Fastlog supports a modular style interface
```python
# Import styles like python modules
log.setStyle('fastlog.styles.pwntools')
```

[Check out the default style to see how it works.](fastlog/styles/pwntools.py)

## Project Status
This project is currently in Beta while I continue to improve some features. 

There aren't any breaking changes planned, just additions of new features.

## Is this just pwntools?
Fastlog was born out of a sadness for bland Python script outputs and a love of the logging module from the Pwntools project.

While there is some code taken between pwntools (specifically termcap and hexdump), the projects are completely independent.

Pwntools was also only Py2 compatible, where Fastlog is both Py2 and Py3 compatible.


