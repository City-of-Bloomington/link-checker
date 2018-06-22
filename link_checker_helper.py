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

def check_page(driver, page, complete, todo, external, errors, lookups):
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
        # check for page response here
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
        # only need to process page if it's an internal page
        # otherwise checking the response code (previously) is sufficient
        if re.search('bloomington.in.gov', page):
            if not errors.has_key(page):
                errors[page] = {}

            driver.get(page)
            links = driver.find_elements_by_tag_name("a")
            
            for link in links:
                href = link.get_attribute('href')
                #print "Checking link: ", href
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
                    #catch them now and fix to prevent issues
                    raise ValueError, "Unknown link type"
                
                #https://calendar.google.com/calendar/embed?src=bloomington.in.gov_rm22gcl2hatcmjk0boh75d6pec@group.calendar.google.com&ctz=America/New_York

                # There are a lot of integrated systems
                # we don't want to scan those,
                # especially if they contain infinite recursions
                elif check_ignore(href, ['bloomington.in.gov/onboard', 'bloomington.in.gov/alpha/onboard', 'caslogin', 'utilities_forms', 'data.bloomington.in.gov', 'bloomingtontransit.com', '.xls', '.docx', '.doc', '.ppt', 'meetings', '/webtrac/', 'google.com/maps', 'mailto', 'interactive/maps', 'inroads', 'apps.bloomington.in.gov/kb/', 'apps.bloomington.in.gov/helpdesk/', 'bloomington.in.gov/open311-proxy', 'apps.bloomington.in.gov/directory', 'mail.google.com', 'helpdesk', 'resource://pdf.js/web/', 'legislation', 'webtrac.bloomington.in.gov', 'library.municode.com/in/bloomington/codes/', '/boards/innovation/report']):
                    print "ignoring: ", href
                    #pass

                elif re.match('mailto', href) or re.match('tel', href):
                    print "Skipping mailto/tel: ", href

                #see crawl_site()... this approach didn't work well
                ## elif href in previous_errors.keys():
                ##     cur_error = "previously bad link found"
                ##     element = link.get_attribute('outerHTML')
                    
                ##     if not errors[page].has_key(cur_error):
                ##         errors[page][cur_error] = []
                ##     if not element in errors[page][cur_error]:
                ##         errors[page][cur_error].append(element)

                else:
                    #skip checking anchors:
                    parts = href.split('#')
                    href = parts[0]
                    
                    print href
                    #TODO:
                    # get rid of leading http(s) ?
                    # would need to refactor final check below

                    #track where the link came from for later troubleshooting
                    if not lookups.has_key(href):
                        lookups[href] = [ page ]
                    if not page in lookups[href]:
                        lookups[href].append(page)

                    if re.search('bloomington.in.gov/alpha', href):
                        cur_error = "link to alpha site"
                        print "%s found" % (cur_error)
                        if not errors[page].has_key(cur_error):
                            errors[page][cur_error] = []
                        if not href in errors[page][cur_error]:
                            errors[page][cur_error].append(href)
                    
                    elif ( re.search('bloomington.in.gov/old', href) or
                           re.search('tarantula.bloomington.in.gov', href) ):
                        cur_error = "link to old site"
                        print "%s found" % (cur_error)
                        if not errors[page].has_key(cur_error):
                            errors[page][cur_error] = []
                        if not href in errors[page][cur_error]:
                            errors[page][cur_error].append(href)

                    elif ( re.search('bloomington.in.gov/code', href) ):
                        cur_error = "link to old host for muni code"
                        print "%s found" % (cur_error)
                        if not errors[page].has_key(cur_error):
                            errors[page][cur_error] = []
                        if not href in errors[page][cur_error]:
                            errors[page][cur_error].append(href)

                    elif re.search('node', href):
                        cur_error = "link with no alias"
                        print "%s found: %s" % (cur_error, href)
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

                    elif (not href in todo) and (not href in complete) and (href != page):
                        #all obvious problematic links removed...
                        #add this for scanning later
                        todo.append(href)



            #if re.search('business/zoning-districts', page):
            #    raise ValueError, "found expected page"

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
                cur_error = "Page contains an (old) markdown link"
                if not errors[page].has_key(cur_error):
                    errors[page][cur_error] = []
                if not href in errors[page][cur_error]:
                    errors[page][cur_error].append(href)

    if r:
        return r.status_code
    else:
        return None

def crawl_site(driver, base):
    start = datetime.now()

    # visit CAS logout link first...
    # don't want to be logged in for this crawl!!!
    todo_paths = ['/user/logout', '/']

    #possible to prioritize another path first:
    #todo_paths = ['/user/logout', '/business/zoning-districts', '/']
    
    todo = []
    for t in todo_paths:
        todo.append(base + t)
    print todo
    
    complete = []
    external = []
    errors = {}

    # this approach adds complexity, and in practice does not work reliably:
    # previous_errors = {}
    ## #load these errors from a saved json file from a previous scan
    ## loaded_errors = load_json(error_file)
    ## for item in loaded_errors.items():
    ##     bad_response = False
    ##     for key in item.keys():
    ##         if re.search('Response', key):
    ##             bad_response = True
    ##             if not previous_errors.has_key(cur_page):
    ##                 previous_errors[cur_page] = {}
    ##                 previous_errors[cur_page]["Bad Response"] = True

    # might be better to track what page a link is found on
    # then note that when the check fails
    lookups = {}
          
    while len(todo):
        print
        print "%04d complete. %s to go" % (len(complete), len(todo))
        cur_page = todo.pop(0)
        print cur_page
        result = check_page(driver, cur_page, complete, todo, external, errors, lookups)
        #print todo
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

    destination_dir = 'results'
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)


    ts = datetime.now()
    filename = ts.strftime("%Y%m%d%H%M") + '-errors' + '.json'
    dest = os.path.join(destination_dir, filename)
    save_json(dest, errors)

    lookup_file = ts.strftime("%Y%m%d%H%M") + '-lookups' + '.json'
    #same content as above, but will get overwritten each time
    lookup_dest = os.path.join(destination_dir, lookup_file)
    save_json(lookup_dest, lookups)

    print 'link_checker_helper.process_results("%s", "%s")' % (filename, lookup_dest) 

def process_results(filename, lookup_filename):
    lookups = load_json(lookup_filename)

    errors = load_json(filename)
    counter = 0
    for key, value in errors.items():
        if value:
            print
            #print '<a href="%s">%s</a>' % (key, key)
            print key
            for sub_key, sub_value in value.items():
                print "  %s" % sub_key
                if type(sub_value) == list:
                    for item in sub_value:
                        print "     ", item
                        #print '    <a href="%s">%s</a>' % (item, item)
                else:
                    #print "    ", sub_value
                    pass
            counter += 1

            if key in lookups.keys():
                print "Appears on:"
                for item in lookups[key][:10]:
                    print "     ", item
                    #print '       <a href="%s">%s</a>' % (item, item)
                    
                if len(lookups[key]) > 10:
                    additional = len(lookups[key]) - 10
                    print "     + %s additional pages" % additional
            
    #print "Total errors: ", len(errors.items())
    print "Total errors: ", counter

