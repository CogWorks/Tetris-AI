from setuptools import setup, find_packages

setup(
    name='Tetris-AI',
    version='2.0.dev',
    packages=find_packages(),
    install_requires=[
        'numpy~=1.14',
    ],
    python_requires='~=2.7',

)
