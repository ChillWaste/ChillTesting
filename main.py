from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from barnum import gen_data
from time import sleep

import names
import random
import string
import re

# install smua modulnya
# python maple.py

def js_fill(driver, xpath, value):
    """Bypass interactability exceptions by filling elements directly via JS DOM manipulation"""
    try:
        el = driver.find_element(By.XPATH, xpath)
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """, el, value)
    except Exception:
        pass

def js_click(driver, xpath):
    """Bypass interactability/overlay exceptions by triggering JS click events"""
    try:
        el = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", el)
    except Exception:
        pass

def makeCode():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.binary_location = "/usr/bin/google-chrome"
    pondev = webdriver.Chrome(options=options)
    
    pondev.implicitly_wait(10)
    
    letters = string.ascii_lowercase
    mailRand = ''.join(random.choice(letters) for i in range(6)) + '@mailsac.com'
    urlreg = 'https://www.maplesoft.com/products/maple/free-trial/'
    getlink = 'https://mailsac.com/inbox/'

    try:
        pondev.get(urlreg)
        sleep(3) 

        # --- STEP 1: Insert Email and Click "Get your Free Trial" ---
        js_fill(pondev, "//input[@type='email' or contains(@placeholder, 'Email') or contains(@id, 'Email')]", mailRand)
        sleep(1)
        
        pondev.execute_script("""
            var btns = document.querySelectorAll('button, a, input[type="submit"], input[type="button"]');
            for (var b of btns) {
                var txt = b.innerText || "";
                var val = b.value || "";
                if (txt.includes('Get your Free Trial') || val.includes('Get your Free Trial')) {
                    b.click();
                    break;
                }
            }
        """)
        js_click(pondev, "//button[contains(., 'Get your Free Trial')] | //input[@value='Get your Free Trial'] | //a[contains(., 'Get your Free Trial')]")
        
        print("Step 1 (Email) submitted. Waiting for form details page...")
        sleep(5)

        # --- STEP 2: Fill "Just a Few More Details!" Form ---
        js_fill(pondev, "//input[@id='FirstName'] | //input[contains(@placeholder, 'First Name')]", names.get_first_name())
        js_fill(pondev, "//input[@id='LastName'] | //input[contains(@placeholder, 'Last Name')]", names.get_last_name())
        js_fill(pondev, "//input[@id='Company'] | //input[contains(@placeholder, 'Institution') or contains(@placeholder, 'Company')]", gen_data.create_company_name())
        js_fill(pondev, "//input[@id='JobTitle'] | //input[contains(@placeholder, 'Job Title')]", gen_data.create_job_title())
        
        # Select Country ("United States")
        pondev.execute_script("""
            var selects = document.querySelectorAll('select');
            for (var s of selects) {
                if (s.id.includes('Country') || s.name.includes('Country') || (s.previousElementSibling && s.previousElementSibling.innerText.includes('Country'))) {
                    for (var i = 0; i < s.options.length; i++) {
                        if (s.options[i].text.includes('United States')) {
                            s.selectedIndex = i;
                            s.dispatchEvent(new Event('change', { bubbles: true }));
                            break;
                        }
                    }
                }
            }
        """)
        
        # Wait for the Region/State dropdown to dynamically appear after selecting US
        sleep(3) 

        # Select State/Region ("California")
        pondev.execute_script("""
            var selects = document.querySelectorAll('select');
            for (var s of selects) {
                if (s.id.toLowerCase().includes('state') || s.name.toLowerCase().includes('state') || 
                    s.id.toLowerCase().includes('region') || s.id.toLowerCase().includes('province')) {
                    for (var i = 0; i < s.options.length; i++) {
                        if (s.options[i].text.includes('California') || s.options[i].value === 'CA') {
                            s.selectedIndex = i;
                            s.dispatchEvent(new Event('change', { bubbles: true }));
                            break;
                        }
                    }
                }
            }
        """)
        sleep(1)

        # Select "Which best describes you?" ("Student")
        pondev.execute_script("""
            var selects = document.querySelectorAll('select');
            for (var s of selects) {
                for (var i = 0; i < s.options.length; i++) {
                    var text = s.options[i].text.toLowerCase();
                    if (text.includes('student') || text.includes('academic') || text.includes('commercial')) {
                        s.selectedIndex = i;
                        s.dispatchEvent(new Event('change', { bubbles: true }));
                        break;
                    }
                }
            }
        """)
        sleep(1)

        # Accept Terms & Conditions
        # Do NOT check every checkbox, because that also checks
        # the newsletter checkbox.

        terms = pondev.find_element(By.ID, "chkAgreeToGDPR")

        if not terms.is_selected():
            pondev.execute_script(
                "arguments[0].click();",
                terms
            )

        print("Terms checked:", terms.is_selected())

        sleep(2)

        # Scroll down slightly so the bottom of the form is visible
        pondev.execute_script("window.scrollBy(0, 350);")
        sleep(1)
        # Submit Form via Go! Button
        js_click(pondev, "//*[@id='SubmitButton']")

        print("Step 2 (Details & Terms) submitted.")
        sleep(5)

        print(f"Waiting for confirmation email in Mailsac inbox: {getlink}{mailRand}")
        
        # --- STEP 3: Inbox Polling & Activation ---
        pondev.get(getlink + mailRand)
        
        email_found = False
        for attempt in range(25):
            sleep(3) # Slightly longer poll wait for Maplesoft server to dispatch email
            rows = pondev.find_elements(By.XPATH, "//table//tbody/tr")
            for row in rows:
                if "Maplesoft" in row.text or "maplesoft" in row.text.lower():
                    email_found = True
                    break
            if email_found:
                break
            pondev.refresh()

        if not email_found:
            raise Exception("Timed out waiting for Maplesoft email in Mailsac inbox. Check 'site_after_signup.png' to verify if the form passed.")

        print("Email received!")
        js_click(pondev, "//table//tbody/tr[1]//a[contains(@href, '/inbox/')] | //table//tbody/tr[1]")
        sleep(4)

        # Extract activation link specifically filtering for Maplesoft endpoints
        maple_links = pondev.find_elements(By.XPATH, "//a[contains(@href, 'maplesoft.com')]")
        lastopen = None
        
        for link in maple_links:
            href = link.get_attribute("href")
            if href and ("eval" in href.lower() or "activate" in href.lower() or "trial" in href.lower()):
                lastopen = href
                break
                
        if not lastopen and maple_links:
            lastopen = maple_links[0].get_attribute("href")

        if not lastopen:
            src = pondev.page_source
            urls = re.findall(r'(https://www\.maplesoft\.com/[^\s"\'<>]+)', src)
            if urls:
                lastopen = urls[0]
            else:
                raise Exception("Could not locate Maplesoft activation link in email body.")

        print("Activation link:", lastopen)
        pondev.get(lastopen)
        sleep(5)

        Firstinstall = pondev.find_element(By.XPATH, "//a[contains(@href, 'download') or contains(@href, 'http')]").text
        exp = pondev.find_element(By.XPATH, "//*[@id='evaluationExpiry']").text
        Acode = pondev.find_element(By.XPATH, "//span[@id='evaluationPurchaseCode']").text
        
        print('\n')
        print('Download and Install Maple : ' + str(Firstinstall))
        print('Activation code : ' + Acode)
        from datetime import datetime, timedelta
        try:
            expiry_date = datetime.strptime(str(exp).strip(), "%B %d, %Y")
            days_left = (expiry_date.date() - datetime.now().date()).days
            print(f"Your evaluation will expire in {days_left} days ({expiry_date.strftime('%B %d, %Y')})")
        except ValueError:
            print('Your evaluation will expire: ' + str(exp))
        print('\n')
        print('If you are new to using this tool and have not installed Maple, you can use the direct download link above.')
        print('\n')
        
    except Exception as e:
        print("An error occurred:", e)
    finally:
        pondev.quit()

makeCode()