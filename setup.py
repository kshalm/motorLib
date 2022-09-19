from setuptools import setup

setup(name='bellMotors',
      version='0.2',
      description='Modularized bell_motors control.',
      url='https://github.com/kshalm/motorLib',
      author='Krister Shalm',
      packages=['bellMotors', 'bellMotors.pyAPT'],
      install_requires=['pyzmq',
                        'zaber.serial',
                        'pylibftdi']
      )
