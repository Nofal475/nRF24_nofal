from setuptools import setup, find_packages

setup(
    name='nrf24_op',
    version='0.2.0',
    author='Nofal Elahi',
    license='MIT',
    description='Python package for interacting with NRF24 wireless module',
    packages=find_packages(include=['nrf24_op']),
    install_requires=['spidev', 'OPi.GPIO']
)
