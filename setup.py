from setuptools import setup

setup(
    name='nrf24_op',
    version='0.1.0',
    description='Python package for interacting with NRF24 wireless module',
    packages=['nrf24_op'],
    install_requires=['spidev', 'OPi.GPIO']
)
