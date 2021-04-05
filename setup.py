from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["casbin==0.8.4", "psycopg2-binary==2.8.6", "black==20.8b1"]

setup(
    name="postgresql-watcher",
    version="0.0.1",
    author="hsluoyz",
    author_email="hsluoyz@gmail.com",
    description="Casbin role watcher to be used for monitoring updates to casbin policies for PyCasbin",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/pycasbin/postgresql-watcher",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
    ],
)