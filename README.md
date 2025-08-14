# neostella-JuanCamiloArcilaQAManager

This is an automated test using Playwright in Python. 
Im aimed to automate the process of inputting data from an Excel file into a web form, 
where the form fields change dynamically after each submission. 
The script must handle dynamic changes, log in to the website, and complete the task with 100%

PRE-Requisites:

1. Make sure the Environment variables for Python and playwright are allocated in the PATH

2. Configure environment variables for Python and install playwright in the project folder

C:\Users\juanc>cd C:\Test Automation\Python\playwright_python_test_neostella
C:\Test Automation\Python\playwright_python_test_neostella>python -m venv venv

C:\Test Automation\Python\playwright_practices>venv\Scripts\activate
(venv) C:\Test Automation\Python\playwright_python_test_neostella>pip install playwright

3. to run the test via terminal use this command in VS:
   slow motion: pytest .\tests\completing_form.py --headed --slowmo=1000
   regular speed: pytest .\tests\completing_form.py --headed


This is a Data Driven testing. 
I used 2 CSV files that will drive the execution of the test depending by the amount of 
rows (iterations) presents in the file:
  In the line 17 of the "completing_form.py" file  (with open("./ddt/ddt_50iterations.csv"...) you can change the file you want to use for the test case execution.
  In the ddt folder will be allocated the differnt files:
ddt_50iterations.csv   ---> This one have all the 50 rows available for the real test
ddt_5iterations.csv   ---> This one only have 5 rows. I use this just for rapid executions during test case creation
