from setuptools import setup, find_packages

setup(
    name="llm-documentation-modifier",
    version="0.1.0",
    url="https://github.com/mberk06/llm-documentation-modifier",
    author="Michael Berk",
    author_email="michaelberk99@gmail.com",
    description="LLM-based modification for a documentation in a code repository/file.",
    packages=find_packages(),
    install_requires=["pydantic", "yaml", "lanchain"],
)
