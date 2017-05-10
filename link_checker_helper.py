from datetime import datetime
import requests
import re
import regex
import codecs, json, os

def save_json(destination, json_objects):
    json_file = codecs.open(destination, 'w', encoding='utf-8', errors='ignore')
    json_file.write(json.dumps(json_objects))
    json_file.close()    

def load_json(source_file, create=False):
    if not os.path.exists(source_file):
        json_objects = {}
        if create:
            print "CREATING NEW JSON FILE: %s" % source_file
            json_file = codecs.open(source_file, 'w', encoding='utf-8', errors='ignore')
            #make sure there is something there for subsequent loads
            json_file.write(json.dumps(json_objects))
            json_file.close()
        else:
            raise ValueError, "JSON file does not exist: %s" % source_file
    else:
        json_file = codecs.open(source_file, 'r', encoding='utf-8', errors='ignore')

        try:
            json_objects = json.loads(json_file.read())
        except:
            raise ValueError, "No JSON object could be decoded from: %s" % source_file
        json_file.close()
    return json_objects

def check_ignore(item, ignores=[]):
    """
    take a string (item)
    and see if any of the strings in ignores list are in the item
    if so ignore it.
    """
    ignore = False
    for i in ignores:
        if i and re.search(i, item):
            #print "ignoring item: %s for ignore: %s" % (item, i)
            ignore = True
    return ignore

def cas_login(driver, base):
    ## TODO:
    # navigate to CAS login
    cas_login = base + '/' + 'caslogin'
    driver.get(cas_login)
    # (manually log in)

def admin_aliases(driver, base):
    # assumes cas_login completed already
    # use admin interface to convert taxonomy terms to nodes
    admin_base = base + '/' + 'admin/config/search/path'
    driver.get(admin_base)

def check_page(driver, base, page, complete, todo, external, errors):
    """
    load a page
    scan for links and other checks

    go through the current page
    parse out all links
    determine if they are internal links or external links
    (or integrated systems)
    
    check links to make sure they return a valid response
    recurse in to any internal links, repeating the above steps    
    """

    r = None
    try:
        #check for page response here
        r = requests.get(page)
        print r.status_code
    except:
        errors[page] = {}
        cur_error = "Connection Error"
        if not errors[page].has_key(cur_error):
            errors[page][cur_error] = []
        if not page in errors[page][cur_error]:
            errors[page][cur_error].append(page)

    else:
        if re.search('bloomington.in.gov', page):
            #only need to process page if it's an internal page
            #otherwise checking a response code is sufficient
            driver.get(page)

            links = driver.find_elements_by_tag_name("a")
            if not errors.has_key(page):
                errors[page] = {}

            for link in links:
                href = link.get_attribute('href')
                print "Checking link: ", href
                if not href:
                    #for example
                    #<a id="main-content" tabindex="-1"></a>

                    cur_error = "page contains empty link"

                    element = link.get_attribute('outerHTML')
                    #skipping this one... seems to be everywhere?
                    #if not errors[page].has_key(cur_error):
                    #    errors[page][cur_error] = []
                    #if not element in errors[page][cur_error]:
                    #    errors[page][cur_error].append(element)

                elif re.match('internal', href):
                    print href
                    #these can show up if people put a '/'
                    #in front of an external link in a link field in drupal
                    #catch them now to prevent issues
                    raise ValueError, "Unknown link type"


                elif check_ignore(href, ['bloomington.in.gov/onboard', 'caslogin', 'utilities_forms', 'data.bloomington.in.gov', 'bloomingtontransit.com' ]):
                    #print "Skipping mailto/tel: ", href
                    pass

                elif re.match('mailto', href) or re.match('tel', href):
                    print "Skipping mailto/tel: ", href

                else:
                    #skip checking anchors:
                    parts = href.split('#')
                    href = parts[0]

                    if re.search('shelter-services', href):
                        raise ValueError, "Found shelter-services link"

                    cur_error = "links to old site"
                    if not re.search(base, href):
                        print base, href
                        print "Didn't match main root url that we're scanning"
                        if re.search('//bloomington.in.gov/', href):
                            print "%s found" % (cur_error)
                            if not errors[page].has_key(cur_error):
                                errors[page][cur_error] = []
                            if not href in errors[page][cur_error]:
                                errors[page][cur_error].append(href)

                        elif not re.search('bloomington.in.gov/', href):
                            # must be an external link
                            if not href in external:
                                external.append(href)
                            if (not href in todo) and (not href in complete):
                                todo.append(href)

                    else:
                        #must be an internal link...
                        cur_error = "links with no alias"
                        if re.search('node', href):
                            print "%s found: %s" % (cur_error, href)
                            if not errors[page].has_key(cur_error):
                                errors[page][cur_error] = []
                            if not href in errors[page][cur_error]:
                                errors[page][cur_error].append(href)

                        if (not href in todo) and (not href in complete) and (href != page):
                            todo.append(href)



            #TODO
            #scan source for old markdown style links that were not converted
            source = driver.page_source.encode("utf-8")
            #re
            #print source
            #via: http://stackoverflow.com/questions/25109307/how-can-i-find-all-markdown-links-using-regular-expressions#25109573
            pattern = '(?|(?<txt>(?<url>(?:ht|f)tps?://\S+(?<=\P{P})))|\(([^)]+)\)\[(\g<url>)\])'
            result = regex.search(pattern, source)
            if result:
                print
                print str(result)
                print "Markdown Link found!!"
                print

    if r:
        return r.status_code
    else:
        return None

def crawl_site(driver, base):
    start = datetime.now()

    # visit CAS logout link first...
    # don't want to be logged in for this crawl!!!
            
    todo_paths = ['/user/logout', '/']
    todo = []
    for t in todo_paths:
        todo.append(base + t)
    print todo
    
    complete = []
    external = []
    errors = {}
    
    while len(todo):
        print
        print "Number of pages to scan: ", len(todo)
        cur_page = todo.pop(0)
        print cur_page
        result = check_page(driver, base, cur_page, complete, todo, external, errors)
        print todo
        if result != 200:
            print "Expected 200: ", result
            cur_error = "Response %s" % result
            if not errors.has_key(cur_page):
                errors[cur_page] = {}
                errors[cur_page][cur_error] = True


        if cur_page in complete:
            #this shouldn't happen if we check complete before adding
            #print "WARNING: scanned page that was already in complete: %s" % cur_page
            raise ValueError, "scanned page that was already in complete: %s" % cur_page
        
        complete.append(cur_page)

    end = datetime.now()
    print "Started: ", start
    print "Finished: ", end
    print "Scanned %s pages" % (len(complete))

    ts = datetime.now()
    filename = ts.strftime("%Y%m%d%H%M") + '.json'
    print 'link_checker_helper.process_results("%s")' % filename
    save_json(filename, errors)
        
    #return (complete, external, errors)

def process_results(filename):
    #(complete, external, errors) = crawl_site(driver, base)
    errors = load_json(filename)
    counter = 0
    for key, value in errors.items():
        if value:
            print
            print key
            for sub_key, sub_value in value.items():
                print "  %s" % sub_key
                if type(sub_value) == list:
                    for item in sub_value:
                        print "    ", item
                else:
                    #print "    ", sub_value
                    pass
            counter += 1
            
    #print "Total errors: ", len(errors.items())
    print "Total errors: ", counter

