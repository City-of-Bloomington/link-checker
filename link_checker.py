"""
sudo apt-get install python-pip
sudo pip install selenium

sudo pip install requests

#browse for latest:
wget https://github.com/mozilla/geckodriver/releases/

wget https://github.com/mozilla/geckodriver/releases/download/v0.14.0/geckodriver-v0.14.0-linux64.tar.gz

tar zxvf geckodriver-v0.11.1-linux32.tar.gz
sudo mv geckodriver /usr/local/bin/

python -i link_checker.py 

"""
from selenium import webdriver


#base = "http://rogue.bloomington.in.gov/alpha"
#base = "http://alpha.bloomington.in.gov"
base = "https://bloomington.in.gov/alpha"

#driver = webdriver.PhantomJS()
driver = webdriver.Firefox()

driver.set_window_size(1120, 550)
driver.get(base)
#driver.find_element_by_id('search_form_input_homepage').send_keys("realpython")
#driver.find_element_by_id("search_button_homepage").click()
print driver.current_url
#driver.quit()

import link_checker_helper
reload(link_checker_helper)

print "reload(link_checker_helper)"

# may need to enter username and password at this point:

## details = { "username": "test" }


## TODO:
# check pages for the old link syntax, for example:
#[Pet Behavior Consulting Online Form|https://docs.google.com/a/bloomington.in.gov/forms/d/12Q_Dp_Sy0oH_kKr0TS_z0mrM7wZcepyUa1vWsDqvx_I/viewform]
# on: https://rogue.bloomington.in.gov/alpha/node/185/edit
# then convert that to an actual working link


#link_checker_helper.cas_login(driver, base)

#link_checker_helper.admin_aliases(driver, base)

#link_checker_helper.crawl_site(driver, base)

#link_checker_helper.process_results(filename)
