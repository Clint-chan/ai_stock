from setuptools import setup, find_packages

def read_requirements(filename='requirements.txt'):
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith('#')]

setup(
    name="ai_stock",
    version="0.1",
    packages=find_packages(),
    install_requires=read_requirements(),
    author="陈定钢",
    author_email="your.email@example.com",
    description="A stock analysis tool",
    keywords="stock, analysis, AI",
)
