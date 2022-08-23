import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="getpass_asterisk",
    version="1.0.1",
    author="Muhammad Akbar | Secursive",
    author_email="akbar@secursive.com",
    description="An alternative implementation for getpass that echoes masked password (such as asterisks)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/secursive/getpass_asterisk",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
