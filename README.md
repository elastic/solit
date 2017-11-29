# Logstash Integration Test

`litaf` is a tool for doing end to end integration tests of your logstash and
elasticsearch configs.

`litaf` can be used hooked up to your CI system of choice and can be used
to automatically test configuration changes to Logstash/ES to keep regressions from
causing downtime or breaking your Elastic Stack pipelines.

## Requirements

* Docker (only tested on 17.11.0-ce) but any "modern" version should work
* Python 3 (should work with python 2 but not tested yet)

### Docker for Mac

A think of note for Docker for Mac users, `litaf` needs access to mount some files into a
docker container for running the tests. By default Docker for Mac does not make this
folder available for mounting.

To findout what directory you need to give Docker access to:

1. Open a new terminal window
2. run `python` or `python3` if your default python is python 2.
3. run the following in the python shell:

```python
import lit
import os

print(os.path.dirname(lit.__file__))
```

This will print the location of your site-packages. Include this directory in
the File Share section of your Docker for Mac properties:

![File Sharing Preferences](/screenshot.png?raw=true "File Sharing Pref")


### Docker for Windows

The Docker for Windows is a bit trickerier and you have to do the same process for
Mac with adding directorys for mouting. Though you also have to enable mounting the
Drive in general.

There are a few other requirements in the `requirements-win.txt` file.
Please look at those.

## Installation

Easiest way is to install via pip:

```
pip install litaf
```

Install from source:

1. Clone this repo
2. run `python setup.py install` from the `litaf` directory

> the first time you run this, it will take some time to download the images needed
> for running the tests but each time afterwards will be faster.

## Usage

See the `examples` directory for examples on how to setup your tests and your
repo for logstash/elastic serach config files

From the `examples` directory just run `litaf`

## Lingering Containers

`litaf` should be able to clean up after itself, but if for some reasong it crashes and
doesn't properly clean up. And the tests are failing to run. Just run `docker system prune`
to have Docker cleanup any lingering containers, lingering networks, etc...



