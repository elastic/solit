from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='lit',
      version='0.1',
      description='The Logstash Integration Test framework',
      long_description=readme(),
      classifiers=[
      ],
      url='http://github.com/fxdgear/lit',
      author='Nick Lang',
      author_email='nick@nicklang.com',
      license='MIT',
      packages=['lit'],
      install_requires=[
          "docker==2.5.1",
          "elasticsearch==5.4.0",
          "pyyaml==3.11",
          "pytest==3.2.1",
      ],
      tests_require=['pytest',],
      scripts=['bin/lit'],
      include_package_data=True,
      zip_safe=False
     )
