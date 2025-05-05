from setuptools import setup, find_packages

setup(
    name="preventivi-cyberworks",
    version="0.1.0",
    description="CLI per generare e gestire preventivi in PDF",
    author="Amin",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "preventivi_cyberworks": [
            "templates/*.html",
            "templates/*.css",
            "branding/*/*.json",
            "branding/*/*.png",
        ],
    },
    install_requires=[
        "click==8.1.8",
        "reportlab==4.4.0",
        "pytest==8.3.5",
        "pdfminer.six>=20221105",
        "rich>=13.4.1",
        "Jinja2>=3.1.3",
        "WeasyPrint>=62.0",
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
