from setuptools import setup, find_packages
import io

def read_requirements(path):
    # prova a leggere in utf-8-sig, altrimenti utf-16
    for encoding in ("utf-8-sig", "utf-16"):
        try:
            with io.open(path, encoding=encoding) as f:
                return [
                    r.strip() for r in f
                    if r.strip() and not r.startswith("#")
                ]
        except UnicodeError:
            continue
    raise RuntimeError(f"Impossibile decodificare {path}")

install_requires = read_requirements("requirements.txt")

setup(
    name="preventivi-cyberworks",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "preventivi=preventivi_cyberworks.cli:cli",
        ],
    },
    author="Amin",
    author_email="support@cybergraf.it",
    description="CLI per la gestione dei preventivi di Cyberworks",
    long_description="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
