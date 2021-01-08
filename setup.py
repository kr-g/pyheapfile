import setuptools
import os
import re

with open("README.MD", "r") as fh:
    long_description = fh.read()


def find_version(fnam, version="VERSION"):
    with open(fnam) as f:
        cont = f.read()
    regex = f'{version}\s*=\s*["]([^"]+)["]'
    match = re.search(regex, cont)
    if match is None:
        raise Exception(
            f"version with spec={version} not found, use double quotes for version string"
        )
    return match.group(1)


def find_projectname():
    cwd = os.getcwd()
    name = os.path.basename(cwd)
    return name


projectname = find_projectname()
file = os.path.join(projectname, "__init__.py")

version = "v0.0.1"

setuptools.setup(
    name=projectname,
    version=version,
    author="k.r. goger",
    author_email=f"k.r.goger+{projectname}@gmail.com",
    description=f"{projectname} - python heap file storage memory management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/kr-g/{projectname}",
    packages=setuptools.find_packages(
        exclude=[
            "doc",
            "tests",
        ]
    ),
    keywords="heap file storage memory management",
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
    ],
    python_requires=">=3.6",
)
