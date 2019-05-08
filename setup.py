import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="reaction-scroll",
    version="0.0.1.dev0",
    author="Scubot Team",
    description="Scrollable Embeds for Discord bots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scubot/reaction-scroll",
    packages=setuptools.find_packages(),
    install_requires=[
        "discord"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


