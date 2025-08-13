# neostellaJuanCamiloA

1. Make sure the Environment variables for Python are allocated in the PATH


2. Configure environment variables for Python and install playwright

C:\Users\juanc>cd C:\Test Automation\Python\playwright_practices

C:\Test Automation\Python\playwright_practices>python -m venv venv

C:\Test Automation\Python\playwright_practices>venv\Scripts\activate
(venv) C:\Test Automation\Python\playwright_practices>pip install playwright

3. to run the test via terminal use this command in VS:
   slow motion: pytest .\tests\reading_csv.py --headed --slowmo=1000
   regular speed: pytest .\tests\reading_csv.py --headed
