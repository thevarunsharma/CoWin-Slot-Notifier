from setuptools import setup, find_packages

setup(
    name="cowin_notifier",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        'Click',
        'requests',
        'diskcache'],
    entry_points='''
        [console_scripts]
        cowin-notifier=cowin_notifier.cowin_notifier:main
    ''',
    description="Sends E-Mail Notification for Available CoWin Slots"
)