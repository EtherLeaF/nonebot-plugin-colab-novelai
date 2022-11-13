import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nonebot_plugin_colab_novelai",
    version="0.1.1",
    author="T_EtherLeaF",
    author_email="thetapilla@gmail.com",
    keywords=["pip", "nonebot2", "nonebot", "nonebot_plugin", "NovelAI", "Colaboratory", "QQ-bot", "chatbot"],
    description="""NoneBot2 由Colab驱动的AI作画插件""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EtherLeaF/nonebot-plugin-colab-novelai",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    platforms="any",
    install_requires=[
        'nonebot-adapter-onebot>=2.1.5',
        'nonebot2>=2.0.0b4',
        'asyncer>=0.0.2',
        'selenium>=4.6.0',
        'av>=10.0.0',
        'pyyaml>=6.0',
        'httpx>=0.23.0',
        'webdav4>=0.9.8',
        'webdriver-manager>=3.8.4',
        'selenium-stealth>=1.0.6',
        'nonebot-plugin-apscheduler>=0.1.4',
        'packaging>=21.3'
    ],
    python_requires=">=3.8"
)
