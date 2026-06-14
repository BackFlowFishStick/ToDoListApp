from setuptools import setup, find_packages

setup(
    name="todolist",
    version="1.0.0",
    description="A modern, borderless To-Do List desktop app",
    packages=find_packages(),
    install_requires=["PyQt5>=5.15.0"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "todolist=src.main:main",
        ],
    },
)
