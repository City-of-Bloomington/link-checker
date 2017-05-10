# Link Checker

Link Checker uses selenium to crawl a website and look for problems. The results of the crawl can then be formatted and acted upon. 

Currently the script is tailored to our alpha website that is in development. All assumptions and requirements are specified in the script itself. 

The general pattern used is helpful for testing websites.  The main script (link_checker.py in this case) establishes the browser window. This can be run interactively with "python -i link_checker.py". Functions and tests can be developed in a separate script (link_cheker_helper.py in this case), and those can be reloaded with 'reload(link_checker_helper)' in the python interpreter. I find this shortens the time it takes to get to the right place in the site being tested, especially if there is any authentication that needs to happen. 
