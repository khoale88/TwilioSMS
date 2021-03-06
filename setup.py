from setuptools import setup

setup(
    name='twilio_sms',
    packages=['controllers', 'repository', 'twilio_app', 'gsheet'],
    include_package_data=True,
    install_requires=[
        'flask',
        'twilio',
        'google-api-python-client',
        'gspread',
    ],
)
