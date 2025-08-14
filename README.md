# neostella - Juan Camilo Arcila QA Manager


# Dynamic Form Automation Test with Playwright (Python)

## 📌 Objective
This project automates the process of filling out a dynamic form on  
[**The Automation Challenge**](https://www.theautomationchallenge.com/).  

The challenge:
- The form contains **8 input fields** that **change their locators, position, and labels** every time the **Submit** button is clicked.
- The script must **dynamically identify** each field based on its **visible label** (not fixed selectors).
- Data is read from a CSV file and entered into the correct fields for **each row** in the file.
- The test runs **full-screen** for visual clarity.

### 🎯 Goals
1. **Data-driven execution**: Read multiple sets of input from a CSV file.
2. **Dynamic element handling**: Fill fields correctly even when selectors change.
3. **Iterative submission**: Repeat the process for all rows in the dataset.
4. **Scalable structure**: Use Page Object Model (POM) and utility modules for maintainability.

---

Before running the test, make sure you have:

- **Python 3.8+** installed  
- **pip** package manager  
- **Playwright** and **pytest** installed  
- Chromium browsers installed via Playwright

IMPORTANT:
- Make sure the Environment variables for Python and playwright are allocated in the PATH
- Configure environment variables for Python and install playwright in the project folder

C:\Users\juanc>cd C:\Test Automation\Python\playwright_python_test_neostella
C:\Test Automation\Python\playwright_python_test_neostella>python -m venv venv
C:\Test Automation\Python\playwright_practices>venv\Scripts\activate
(venv) C:\Test Automation\Python\playwright_python_test_neostella>

This is a Data Driven testing. 
I used 2 CSV files that will drive the execution of the test depending by the amount of 
rows (iterations) presents in the file:
  In the line 17 of the "completing_form.py" file  (with open("./ddt/ddt_50iterations.csv"...) you can change the file you want to use for the test case execution.
  In the ddt folder will be allocated the differnt files:
ddt_50iterations.csv   ---> This one have all the 50 rows available for the real test
ddt_5iterations.csv   ---> This one only have 5 rows. I use this just for rapid executions during test case creation


-  to run the test via terminal use this command in VS:
   slow motion: pytest .\tests\completing_form.py --headed --slowmo=1000
   regular speed: pytest .\tests\completing_form.py --headed

