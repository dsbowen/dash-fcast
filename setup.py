import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dash-fcast",
    version="0.0.3",
    author="Dillon Bowen",
    author_email="dsbowen@wharton.upenn.edu",
    description="High-level API for creating forecasting dashboards.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dsbowen.github.io/dash-fcast/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'dash>=1.16.0',
        'dash-bootstrap-components>=0.10.6',
        'pandas>=1.1.2',
        'smoother>=0.0.2'
    ]
)