import os
import platform

import docker


def pull_required_images(images):
    """
    Helper function to pull down required images used for testing.
    """

    client = docker.from_env()
    for _, image  in images.items():
        print("Pulling: {}".format(image))
        client.images.pull(image)


def construct_abs_path(path, base_path=None):
    if base_path is None:
        base_path = os.path.dirname(__file__)

    full_path = os.path.join(base_path, path)
    if platform.system() == "Windows":
        full_path = os.path.join(base_path, path)
        full_path = full_path.replace("C:", "//C").replace("\\", "/")
    return full_path


def create_network(network_name, docker_base_url="unix://var/run/docker.sock"):
    client = docker.APIClient(base_url=docker_base_url)
    return client.create_network(network_name)

def remove_network(network_name, docker_base_url="unix://var/run/docker.sock"):
    client = docker.APIClient(base_url=docker_base_url)
    return client.remove_network(network_name)

class Network(object):
    def __init__(self,
                 docker_base_url="unix://var/run/docker.sock",
                 network_name=None):
        self.client = docker.APIClient(base_url=docker_base_url)
        self.network_name = network_name
        self.network = self._create_network()

    def _create_network(self):
        return self.client.create_network(self.network_name)


class Container(object):
    def __init__(self,
                 docker_base_url="unix://var/run/docker.sock",
                 image_name=None,
                 image_tag=None,
                 command=None,
                 name=None,
                 environment=None,
                 ports=None,
                 volumes=None):
        self.client = docker.APIClient(base_url=docker_base_url)
        self.image_name = image_name
        self.tag = image_tag
        self.image = ":".join([self.image_name, self.tag])
        self.command = command
        self.container_name = name
        self.environment = environment
        self.ports = ports
        self.volumes = volumes
        self.container = self._create_container()
        self.container_id = self.container.get('Id')



    def _create_container(self):
        return self.client.create_container(
            self.image, command=self.command,
            name=self.container_name,
            environment=self.environment,
            ports=list(self.ports.keys()) if self.ports else None,
            host_config=self._create_host_config(),
        )

    def _create_host_config(self):
        return self.client.create_host_config(
            port_bindings=self.ports,
            binds=self.volumes,
        )


    def start(self):
        return self.client.start(container=self.container_id)


    def stop(self):
        return self.client.stop(container=self.container_id)

    def wait(self):
        return self.client.wait(container=self.container_id)

    def cleanup(self):
        self.client.remove_container(self.container_id)

    def logs(self):
        return self.client.logs(self.container_id)

    def connect_container_to_network(self, network):
        self.client.connect_container_to_network(self.container_id, network)


class ElasticsearchContainer(Container):
    def __init__(self,
                 image_name="docker.elastic.co/elasticsearch/elasticsearch",
                 image_tag="5.5.1",
                 name="elasticsearch",
                 environment=None,
                 ports=None):
        if environment is None:
            environment = {
                "ES_JAVA_OPTS":"-Xms512m -Xmx512m",
                "bootstrap.memory_lock": "false",
            }
        if ports is None:
            ports = {9200:9200}

        super(ElasticsearchContainer, self).__init__(
            image_name=image_name,
            image_tag=image_tag,
            name=name,
            environment=environment,
            ports=ports,
        )


class LogstashContainer(Container):
    def __init__(self,
                 image_name="docker.elastic.co/logstash/logstash",
                 image_tag="5.5.1",
                 name="logstash",
                 command="/usr/local/bin/run.sh",
                 environment=None,
                 volumes=None):
        super(LogstashContainer, self).__init__(
            image_name=image_name,
            image_tag=image_tag,
            name=name,
            command=command,
            environment=environment,
            volumes=volumes)
