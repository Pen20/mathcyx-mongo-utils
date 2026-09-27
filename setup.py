from setuptools import find_packages, setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()     

__version__ = "0.0.1"
REPO_NAME = "mathcyx-mongo-utils"
PKG_NAME= "databaseautomation"
AUTHOR_USER_NAME = "Pen20"
AUTHOR_EMAIL = "wastalasdassise@gmail.com"

setup(
    name=PKG_NAME,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="A python package for connecting with database.",
    long_description=long_description,
    long_description_content="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    # Keep build metadata self-contained: requirements.txt is not guaranteed to
    # be present when pip builds a wheel from the source distribution.
    install_requires=["pymongo", "dnspython", "pandas", "numpy", "ensure"],
    )


