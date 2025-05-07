from setuptools import setup


setup(
    name="mintf",
    description="Minimalist Python spatial transformation utils.",
    version="0.1.0",
    packages=["mintf"],
    include_package_data=True,
    install_requires=[
        "numpy",
        "numpy-quaternion",
    ],
    extras_require={
        "plt": ["matplotlib"],
        "test": ["pytest", "scipy"],
    },
    python_requires=">=3.10",
    author="yanghn2002",
    url="https://github.com/yanghn2002/mintf",
)