from setuptools import setup, find_packages

setup(
    name="preventivi-cyberworks",
    version="0.1.0",
    description="CLI per generare e gestire preventivi in PDF",
    author="Amin",
    python_requires=">=3.10",
    # IMPORTANTE: src-layout
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "click==8.1.8",
        "reportlab==4.4.0",
        "pytest==8.3.5",
    ],
    entry_points={
        "console_scripts": [
            "preventivi=preventivi_cyberworks.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
