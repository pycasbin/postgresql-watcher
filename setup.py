from setuptools import setup, find_packages, __version__


with open("README.md", "r") as readme_file:
    readme = readme_file.read()


setup(
    name="casbin-postgresql-watcher",
    author="hsluoyz",
    author_email="hsluoyz@gmail.com",
    description="Casbin role watcher to be used for monitoring updates to policies for PyCasbin",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/pycasbin/postgresql-watcher",
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    extras_require={
        'dev': [
            open('dev_requirements.txt').read().splitlines(),
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
    ],
)
