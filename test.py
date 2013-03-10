#!/usr/bin/python

import sys
import urllib2
try:
    import xml.etree.cElementTree as etree
except ImportError:
    try:
        import xml.etree.ElementTree as etree
    except ImportError:
        print 'python >= 2.5'
        sys.exit()

SOLR_HOST = 'localhost'
SOLR_PORT = 8983
SOLR_URL = '/solr'

def get_cores():
    return ['core']
    url = 'http://%s:%s/%s/admin/cores?action=status' % (SOLR_HOST, SOLR_PORT, SOLR_URL)
    f = urllib2.urlopen(url)
    xml = etree.fromstring(f.read())
    cores = [lst.attrib['name'].strip() for lst in xml.findall('./lst/lst')]
    return cores

for core in get_cores():
    url = 'http://%s:%s/%s/%s/admin/mbeans?stats=true' % (SOLR_HOST, SOLR_PORT, SOLR_URL, core)
    #f = urllib2.urlopen(url)
    f = open('stats.xml', 'r')
    root = etree.fromstring(f.read())

    # numDocs
    core = root.findall('./response/lst/')
    print core, dir(core)
    for entry in core[0].xpath('entry'):
        if entry[0].text.strip() == 'searcher':
            stats = entry.xpath('stats')
            for stat in stats[0]:
                if stat.get("name") in ["numDocs"]:
                    print "docs.value", stat.text.strip()

    core = root.xpath('/solr/solr-mbeans/CACHE')
    stat_list = []
    for entry in core[0].xpath('entry'):
        if entry[0].text.strip() == 'documentCache' or \
            entry[0].text.strip() == 'filterCache' or entry[0].text.strip() == 'queryResultCache':
                 description = entry.xpath('description')
                 match = re.findall(r'maxSize=([0-9]+)', description[0].text.strip())
                 maxsize = match[0]
                 stats = entry.xpath('stats')
                 for stat in stats[0]:
                     if stat.get('name') in ['lookups', 'hits', 'inserts', 'evictions', 'size']:
                        stat_list.append(stat.get('name') + '.value ' + stat.text.strip())
                 for i in stat_list:
                     print i

    core = root.xpath('/solr/solr-mbeans/QUERYHANDLER')
    for entry in core[0].xpath('entry'):
        if entry[0].text.strip() == 'standard':
            stats = entry.xpath('stats')
            for stat in stats[0]:
                if stat.get('name') == 'avgRequestsPerSecond':
                    print 'qps' + '.value', stat.text.strip()
                if stat.get('name') == 'avgTimePerRequest':
                    print 'qtime' + '.value', stat.text.strip()
        elif entry[0].text.strip() == '/update':
            stats = entry.xpath('stats')
            for stat in stats[0]:
                if stat.get("name") == 'avgRequestsPerSecond':
                    print "ups.value", stat.text.strip()

