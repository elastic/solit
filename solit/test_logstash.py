import os
import time
import json
from collections import namedtuple

from yaml import load
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError

from solit.utils import (
    ElasticsearchContainer, LogstashContainer, construct_abs_path,
    pull_required_images, create_network, remove_network
)


def _get_config():
    COMMAND = 'bash -c "/usr/share/logstash/bin/logstash -e \\"input{stdin{codec=>json_lines}}\\" < /data/input.log"'

    with open('.solit.yml') as stream:
        config = load(stream)

    CONFIG = {
        "images": {
            "logstash": config.get("logstash", "docker.elastic.co/logstash/logstash:5.5.1"),
            "elasticsearch": config.get("elasticsearch", "docker.elastic.co/elasticsearch/elasticsearch:5.5.1"),
        },
        "elastic_user": config.get("elastic_user", "elastic"),
        "elastic_pass": config.get("elastic_pass", "changeme"),
        "network_name": config.get("network_name", "lsnet"),
        "command": config.get("command", COMMAND)
    }
    return CONFIG


CONFIG = _get_config()

Containers = namedtuple('Containers', ['elastic_container', 'logstash_container'])


def get_test_parameters():
    print("Gathering logstash tests...")
    with open("logstash_tests.yml", "r") as stream:
        _tests = load(stream)

    test_tuples = []
    for test_name, data in _tests.items():
        test_tuples.append(
            (
                test_name, data['config'], data['input'], data['pipeline'],
                data.get('command'), data['query'], data['output'], data.get('auto_remove', True)
            )
        )
    return test_tuples


class TestClass(object):
    @classmethod
    def setup_class(cls):
        """
        First step is to get Elasticearch running in a docker container using docker-compose.

        When Elasticsearch is up and running we can start running the tests
        """
        # Next Pull images needed for the test
        pull_required_images(CONFIG.get("images"))
        network = create_network(CONFIG.get('network_name'))
        Containers.elastic_container = ElasticsearchContainer(
            image_name=CONFIG['images']['elasticsearch'].split(":")[0],
            image_tag=CONFIG['images']['elasticsearch'].split(":")[1]
        )
        Containers.elastic_container.connect_container_to_network(CONFIG.get('network_name'))
        Containers.elastic_container.start()
        # create an Elasticsearch instance to check for alive-ness
        es_client = Elasticsearch(
            'http://localhost:9200',
            http_auth=(CONFIG['elastic_user'], CONFIG['elastic_pass'])
        )
        resp = {}
        while not resp.get('name', False):
            # Wait till Elasticsearch is ready
            try:
                resp = es_client.info()
            except ESConnectionError:
                print("Elasticsearch is not up yet...")
                time.sleep(2)

        print("Elasticsearch is ready!")

    @classmethod
    def teardown_class(cls):
        """
        Need to tear down the docker-ized instance of Elasticsearch and remove any containers
        so the next time the tests run there's no lingering artifacts.
        """
        print("tearing down...")
        Containers.elastic_container.stop()
        Containers.elastic_container.cleanup()
        Containers.logstash_container.stop()
        Containers.logstash_container.cleanup()
        remove_network(CONFIG['network_name'])


    @classmethod
    def setup_method(cls):
        pass


    @classmethod
    def teardown_method(cls):
        pass


    def test_logstash_config(self, testname, testpath):
        if testpath is None:
            testpath = os.getcwd()

        with open(os.path.join(testpath, "logstash_tests.yml"), "r") as stream:
            test_data = load(stream)

        if not testname:
            testnames = test_data.keys()
        else:
            testnames = [testname]

        for name in testnames:
            data = test_data[name]
            self._test_logstash(
                name,
                os.path.join(testpath, data['config']),
                os.path.join(testpath, data['input']),
                os.path.join(testpath, data['pipeline']),
                os.path.join(testpath, data['output_conf']),
                data.get('command', CONFIG.get("command")),
                os.path.join(testpath, data['query']),
                os.path.join(testpath, data['output']),
                os.path.join(testpath, data.get('template')),
            )

    def test_elasticsearch_is_up(self):
        """
        Simple test to check for the aliveness of elasticsearch
        """
        print("Test elasticsearch is up")
        es_client = Elasticsearch('http://localhost:9200', http_auth=(CONFIG.get('elastic_user'), CONFIG.get('elastic_pass')))
        output = es_client.info()
        assert output['tagline'] == 'You Know, for Search'

    def _test_logstash(
            self, test_name, config, test_input, pipeline,
            output_conf, command, query, output, template):
        """
        docker run -it --network lsnet --rm
        -v `pwd`/logstash/config:/usr/share/logstash/config/
        -v `pwd`/example:/data
        -v `pwd`/logstash/pipeline:/usr/share/logstash/pipeline
        docker.elastic.co/logstash/logstash:5.5.1
        """
        print("## Running: {}".format(test_name))
        es_client = Elasticsearch(
            'http://localhost:9200',
            http_auth=(CONFIG['elastic_user'], CONFIG.get("elastic_pass"))
        )

        with open(template) as template_file:
            template_body = json.load(template_file)
        # load the elasticsearch template
        es_client.indices.put_template(name=test_name, body=template_body)
        Containers.logstash_container = LogstashContainer(
            image_name=CONFIG["images"]['logstash'].split(":")[0],
            image_tag=CONFIG["images"]['logstash'].split(":")[1],
            command=CONFIG.get('command'),
            environment={
                "LS_SETTINGS_DIR": "/usr/share/logstash/config",
                "MONITORING_HOST": "elasticsearch",
                "MONITORING_PORT": "9200",
                "MONITORING_USER": "logstash_system",
                "MONITORING_PASSWORD": CONFIG.get('elastic_pass'),
                "INDEX_NAME": test_name,
                "LOGSTASH_USER": CONFIG.get('elastic_user'),
                "LOGSTASH_PASS": CONFIG.get('elastic_pass'),
                "ES_HOST_1": "elasticsearch:9200",
                "ES_HOST_2": "elasticsearch:9200",
                "ES_HOST_3": "elasticsearch:9200",
                "ES_HOST_4": "elasticsearch:9200",
            },
            volumes={
                construct_abs_path(config): {
                    'bind': '/usr/share/logstash/config/logstash.yml', 'mode': 'ro'
                },
                construct_abs_path(test_input): {
                    'bind': '/data/input.log', 'mode': 'ro'
                },
                construct_abs_path(pipeline): {
                    'bind': '/etc/logstash/conf.d/{}/filter.conf'.format(test_name), 'mode': 'ro'
                },
                construct_abs_path(output_conf): {
                    'bind': '/etc/logstash/conf.d/{}/output.conf'.format(test_name), 'mode': 'ro'
                },
            }
        )
        Containers.logstash_container.connect_container_to_network(CONFIG.get('network_name'))
        print("\tStarting logstash container...")
        Containers.logstash_container.start()
        print("\tAwaiting results...")
        results = Containers.logstash_container.wait()
        print(Containers.logstash_container.logs().decode('utf-8'))
        es_client.indices.refresh(index="{}-*".format(test_name))
        with open(query) as data_file:
            query = json.load(data_file)
        print("\tFetching data from Elasticsearch...")
        results = es_client.search(index='{}-*'.format(test_name), body=query)

        with open(output) as data_file:
            output = json.load(data_file)

        print("\tComparing results...")
        counter = 0
        print(results)
        print("\n")
        print(output)
        for hit in output['hits']:
            assert results['hits']['hits'][counter]['_source'] == hit
            counter += 1


if __name__ == "__main__":
    print([test[0] for test in get_test_parameters()])
