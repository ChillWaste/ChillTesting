#!/usr/bin/env bash
set -e

python - <<'PY'
from pathlib import Path

p = Path("main.py")
s = p.read_text()

# Modern Chrome configuration for GitHub Codespaces
old = 'pondev = webdriver.Chrome("C:/Users/PC/Downloads/chromedriver_win32/chromedriver")'

new = '''options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.binary_location = "/usr/bin/google-chrome"
    pondev = webdriver.Chrome(options=options)'''

if old in s:
    s = s.replace(old, new)

# Modern Selenium 4 API
s = s.replace(
    ".find_element_by_xpath(",
    ".find_element(By.XPATH, "
)

# Back up the current file before writing
backup = Path("main.py.backup")
backup.write_text(p.read_text())

p.write_text(s)

print("Updated main.py")
print("Backup saved as main.py.backup")
PY
