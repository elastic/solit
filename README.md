# Logstash Integration Test

`solit` is a tool for doing end to end integration tests of your logstash and
elasticsearch configs.

`solit` can be used hooked up to your CI system of choice and can be used
to automatically test configuration changes to Logstash/ES to keep regressions from
causing downtime or breaking your Elastic Stack pipelines.

## Requirements

* Docker 17.09.0-ce+,  but any "modern" version should work
* Python


### Docker for Windows

The Docker for Windows is a bit trickerier and you have to setup File Sharing (volume mounts).

There are also few other requirements in the `requirements-win.txt` file.
Please look at those.

## Installation

Easiest way is to install via pip:

```
pip install solit
```
> Note: Not avail from PyPI yet, so only install from source.

Install from source:

1. Clone this repo
2. run `python setup.py install` from the `solit` directory

> **NOTE**: the first time you run this, it will take some time to download the images needed
> for running the tests but each time afterwards will be faster.

## Usage

See the `examples` directory for examples on how to setup your tests and your
repo for logstash/elastic serach config files

From the `examples` directory just run `solit`

## Lingering Containers

`solit` should be able to clean up after itself, but if for some reasong it crashes and
doesn't properly clean up. And the tests are failing to run. Just run `docker system prune`
to have Docker cleanup any lingering containers, lingering networks, etc...



