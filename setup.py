import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PRISMBot-ShrapGnoll",
    version="0.1.0b1",
    author="ShrapGnoll",
    author_email="ShrapGnoll@gmail.com",
    description="A Discord bot for Project Reality's PRISM rcon management tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ShrapGnoll/PRISMBot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)