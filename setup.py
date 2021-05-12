from setuptools import setup, find_packages

setup(
    name="cowin_notifier",
    version="0.4",
    packages=find_packages(),
    install_requires=[
        'Click',
        'requests',
        'diskcache'],
    entry_points='''
        [console_scripts]
        cowin-notifier=cowin_notifier.__init__:main
    ''',
    description="Sends E-Mail Notification for Available CoWin Slots"
)
