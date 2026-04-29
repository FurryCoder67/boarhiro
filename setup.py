from setuptools import setup, find_packages

setup(
    name="boarhiro",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich",
        "requests",
        "torch",
        "watchdog"
    ],
    entry_points={
        'console_scripts': [
            'boarhiro=src.interface:run_cli',
        ],
    },
)