#collectd-solr.py
#
# This program is free software; you can solrtribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; only version 2 of the License is applicable.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# Authors:
#   Denis Zhdanov <denis.zhdanov@gmail.com>
#   Garret Heaton <powdahound at gmail.com> (I used his solr-info.py as template of collectd plugin)
#   Distilled Media Ltd - author of Munin Solr plugins
#   Gasol Wu - another author of Solr Munin plugins
#
# About this plugin:
#   This plugin uses collectd's Python plugin to record Solr information.
#
# collectd:
#   http://collectd.org
# Solr:
#   http://lucene.apache.org/solr/
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml
# Distilled Media Ltd.
#   https://github.com/distilledmedia/munin-plugins/
# Gasol Wu
#   https://github.com/Gasol/munin-solr-plugins/
# powdahoud's solr-collectd-plugin
#   https://github.com/powdahound/solr-collectd-plugin/
#

import collectd
import sys, urllib2
try:
    import xml.etree.cElementTree as etree
except ImportError:
    try:
        import xml.etree.ElementTree as etree
    except ImportError:
        print 'python >= 2.5'
        sys.exit()

# Host to connect to. Override in config by specifying 'Host'.
SOLR_HOST = 'localhost'
# Port to connect on. Override in config by specifying 'Port'.
SOLR_PORT = 8080
# Solr URL. Override in config by specifying 'SolrURL'.
SOLR_URL = '/solr'
# Solr Admin URL. Override in config by specifying 'SolrAdminURL'.
SOLR_ADMIN_URL = 'admin/mbeans?stats=true'

VERBOSE_LOGGING = True

def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('solr_info plugin [verbose]: %s' % msg)


def get_cores():
    url = 'http://%s:%s/%s?action=status' % (SOLR_HOST, SOLR_PORT, SOLR_URL)
    try:
        log_verbose("Fetching %s" % url)
        f = urllib2.urlopen(url)
        xml = etree.fromstring(f.read())
        cores = [lst.attrib['name'].strip() for lst in xml.findall('./lst/lst')]
    except urllib2.HTTPError as e:
        log_verbose('collectd-solr plugin get_cores: can\'t get info, HTTP error: ' + str(e.code))
        log_verbose(url)
    except urllib2.URLError as e:
        log_verbose('collectd-solr plugin get_cores: can\'t get info: ' + str(e.reason))
        log_verbose(url)

    return cores


def fetch_info(core):
    """Connect to Solr stat page and and return XML object"""
    url = 'http://%s:%s/%s/%s/%s' % (SOLR_HOST, SOLR_PORT, SOLR_URL, core, SOLR_ADMIN_URL)
    xml = None
    try:
        f = urllib2.urlopen(url)
        #f = open('queues.xml', 'r')
        xml = etree.fromstring(f.read())
    except urllib2.HTTPError as e:
        log_verbose('collectd-solr plugin: can\'t get info, HTTP error: ' + e.code)
    except urllib2.URLError as e:
        log_verbose('collectd-solr plugin: can\'t get info: ' + e.reason)
    return xml


def configure_callback(conf):
    """Receive configuration block"""
    global SOLR_HOST, SOLR_PORT, SOLR_URL, SOLR_ADMIN_URL
    for node in conf.children:
        if node.key == 'Host':
            SOLR_HOST = node.values[0]
        elif node.key == 'Port':
            SOLR_PORT = int(node.values[0])
        if node.key == 'URL':
            SOLR_URL = node.values[0]
        if node.key == 'AdminURL':
            SOLR_ADMIN_URL = node.values[0]
        else:
            collectd.warning('collectd-solr plugin: Unknown config key: %s.' % node.key)
    log_verbose('Configured: host=%s, port=%s, url=%s, admin_url=%s' % (SOLR_HOST, SOLR_PORT, SOLR_URL, SOLR_ADMIN_URL))


def dispatch_value(instance, key, value, value_type):
    """Dispatch a value to collectd"""
    log_verbose('Sending value: %s.%s=%s' % (instance, key, value))
    val = collectd.Values(plugin='activemq_info')
    val.plugin_instance = instance
    val.type = value_type
    val.values = [value]
    val.dispatch()


def read_callback():
    log_verbose('solr-info plugin: Read callback called')
    cores = get_cores()
    log_verbose('solr-info plugin: Cores: ' + cores)
    for core in cores:
        info = fetch_info(core)
        if not info:
            collectd.error('solr-info plugin: No info received')
        # parse info
        dispatch_value(core, 'test1', 0, 'gauge')
        dispatch_value(core, 'test2', 0, 'bytes')
        dispatch_value(core, 'test3', 0, 'counter')

# register callbacks
collectd.register_config(configure_callback)
collectd.register_read(read_callback)
