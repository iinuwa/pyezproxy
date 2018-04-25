from setuptools import setup

setup(name='pyezproxy',
      version='0.1',
      url='https://github.com/iinuwa/pyezproxy/',
      author='Isaiah Inuwa',
      author_email='isaiah.inuwa@gmail.com',
      license='MIT',
      packages=['pyezproxy'],
      install_requires=[
        'flask',
        'requests',
        'beautifulsoup4'
      ],
      zip_safe=False)
