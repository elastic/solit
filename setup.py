from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='solit',
      version='0.3',
      description='The Logstash Integration Test framework',
      long_description=readme(),
      classifiers=[
      ],
      url='http://github.com/elastic/solit',
      author='Nick Lang',
      author_email='nick.lang@elastic.co',
      license='Apache v2',
      packages=['solit'],
      install_requires=[
          "docker==2.5.1",
          "elasticsearch==5.4.0",
          "pyyaml==3.11",
          "pytest==3.2.1",
      ],
      tests_require=['pytest',],
      scripts=['bin/solit'],
      include_package_data=True,
      zip_safe=False
     )
