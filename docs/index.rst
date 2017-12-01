SOLIT - Logstash Integration Tests
==================================

Witing tests for configuration files can be difficult. Especially when you have two
system that can have different configurations and you want to make sure the integration
between those two systems is working as expected.

Why?
----

You've got Elasticsearch and Logstash setup and running and you've even graduated to
putting your Logstash configs into a git repo. But now that things have become sufficently
complex it's now time to start adding some tests so that a change to your ES template or
Logstash config doesn't break production.

`solit` is designed to allow you to write tests that will input data into LS and query
data out of ES and check that you get expected values.

`solit` is designed to run in your CI system of choice. Also it can be run locally.

The only requirements for `solite` are Python and Docker. Writing a tests is just
as simple as writing some json and some yaml.

Installation
------------

Easiest way is to install via pip:

`pip install solit`

Install from source:

1. Clone this repo
2. run `python setup.py install` from the `solit` directory


Example Usage
-------------

For some example usage please checkout this repository:

https://github.com/fxdgear/solit-examples


Setting up your Repository
-------------------------

First thing, we should probably have our repository which holds our Logstash and Elasticsearch
configs setup logically:

.. ::
    repository_root
    ├── README.md
    ├── elasticsearch
    │   └── templates
    │       └── template_name.json
    ├── logstash
    │   ├── conf.d
    │   │   ├── output.conf
    │   │   └── test_0001
    │   │       └── filter.conf
    │   └── logstash.yml

In this example we have our repo root with two directories, `elasticsearch` and
`logstash`. These two directories hold various configuration files related to each
service.

The logstash directory is deisgned around the concept of having a single `output.conf` and
having multple directories holding the configuration for each type of data source we
will be processing. AKA each pipeline.

The output.conf uses variables assigned via each pipeline to determine which index the data
gets indexed into.


Next we want to add our tests. I'm adding the logstash tests to the root of the directry.

First we need to add a `logstash_tests.yml` file. This file holds all the information about
all our tests.

.. code_block:: yaml

    test_0001:
      input: test_0001/input.log
      output: test_0001/output.txt
      query: test_0001/query.json
      pipeline: logstash/conf.d/test_0001/filter.conf
      output_conf: logstash/conf.d/output.conf
      config: logstash/logstash.yml
      template: elasticsearch/templates/template_name.json

The first line is our test name, `test_0001`.
Then block is the information for our test. We need to specify the location of our

1. input - the mock data to be processed by logstash
2. output - the desired output we well use to verify the correctness of our test.
3. query - the query we will use to query the data out of Elasticsearch to verify the output.
4. pipeline - the relative path (to the logstash_tests.yml) to the logstash conf pipeline we want to test.
5. output_conf - the output conf we want logstash to use when indexing data into Elasticsearch.
6. config - the config file we want logstash to use.
7. template - the template we want Elasticsearch to use when this data get indexed into ES.

Now our repository should look a little more like:

.. ::

    repository_root
    ├── README.md
    ├── elasticsearch
    │   └── templates
    │       └── template_name.json
    ├── logstash
    │   ├── conf.d
    │   │   ├── output.conf
    │   │   └── test_0001
    │   │       └── filter.conf
    │   └── logstash.yml
    ├── logstash_tests.yml
    ├── test_0001
    │   ├── input.log
    │   ├── output.txt
    │   └── query.json


Writing your test
-----------------

Now to write a test we need to have some data for Logstash to process. It is important
to note that `solit` is configured by default to process `json_lines` as the input data
format.

Why did I make this assumption? I've found that most people are using filebeats to
send data to Logstash for data enrichment. But if you want to change the way Logstash a
acceps input data you can overide the `command` in the `.solit.yml` file. But beweare
of dragons when going down this path. It can be difficult to get formatted correctly.

A very simple input.log would look like this:

.. code_block:: json

    {"message":"somemessage"}

Logstash would take this json_line and start processing it with your pipeline filter.

A more advanced message might look like this:

.. code_block:: json

    {"type":"message_type","message":"2017-08-24 13:49:29.2810|29587|DEBUG|Loq.Controllers.Attendant|8592|107|Entry attempt is Valid for guest e1cd6d63-8ce7-4c7b-85fa-4718c15d5a0d@example.com||"}

Here we have a `type` and a `message`. And our logstash config is specifically designed
to process a message body like this.

Now we want to write a query to get data out of Elasticsearch:

.. code_block:: json

    {
        "sort": [
            {"@timestamp": {"order": "asc"}}
        ],
        "_source":["logMessage", "type", "message", "logLevel", "operationId"],
        "query":{
            "match_all":{}
        }
    }

This query is designed to get the data back in ascending order on the timestamp field.
This is to ensure the data coming back from elasticsearch is in an expected order.

Next we only want to return the fields which are important to the test. In this example
those fields are `logMessage`, `type`, `message`, `logLevel` and `operationId`.

Finally we want to get back ALL the documents of this index.

After we have our query and our input source we need to create an output so we can verify
the results from our query match a desired output.

Our output file is a json file listing all the `hits` we expect to see:

.. code_block:: json

    {
      "hits" : [
        {
            "logLevel" : "DEBUG",
            "logMessage" : "Entry attempt is Valid for guest e1cd6d63-8ce7-4c7b-85fa-4718c15d5a0d@example.com  ",
            "operationId" : "Loq.Controllers.Attendant",
            "type" : "message_type",
            "message" : "2017-08-24 13:49:29.2810|29587|DEBUG|Loq.Controllers.Attendant|8592|107|Entry attempt is Valid for guest e1cd6d63-8ce7-4c7b-85fa-4718c15d5a0d@example.com||"
        }
    }

With these 3 files our tests can execute. The input will be fed into Logstash and processed
and finally indexed into Elasticsearch. After the logstash job has finished, `solit` will
query Elasticsearch for the indexed data and will compare the results it gets with the
output we provided. If we have an exact match the test will pass otherwise the test will fail.



