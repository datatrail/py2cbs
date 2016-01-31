#!/usr/bin/env python
"""Examples py2cbs"""

from py2cbs import Resource, Catalog, CatalogTree, Table
from pprint import pprint
import json

def example_odata():
    """Example OData"""

    # service document
    print '\n--- example module odata : Resource - service document ---\n'
    url = 'http://services.odata.org/V4/Northwind/Northwind.svc/' #
    service_document = Resource(url)
    print 'Url service document:', service_document.url
    print 'The service document contains {0} entries (collections/feeds), properties first entry:'.format(len(service_document.entries))
    print "- names:", service_document.property_names
    print "- values:", service_document.entries[0].values()

    # feed 
    print '\n--- example module odata : Resource - feed or collection ---\n'
    collection =  {'name':'Customers'} 
    url = service_document.url + collection['name']
    feed = Resource(url)
    print 'Url feed:', feed.url
    print 'The feed {0} contains {1} entries, properties first entry:'.format(collection['name'] , len(feed.entries))
    print "- names:", feed.property_names
    print "- values:", feed.entries[0].values()

    # methods  
    print '\n--- example module odata : Resource - methods ---\n'
    print "* method: query -> feed.query(search_properties = {'Country':'Germany'}, return_property_names = ['CustomerID', 'ContactName', 'City'])"
    for item in feed.query(search_properties = {'Country':'Germany'}, return_property_names = ['CustomerID', 'ContactName', 'City']):
        print '-', ' - '.join(item.values())

    print "\n* method get_entry -> feed.get_entry(entry_id = 'BLAUS', primary_key = 'CustomerID')"
    print '-', feed.get_entry(entry_id = 'BLAUS', primary_key = 'CustomerID').values()

    print "\n* method get_property -> feed.get_property(entry_id = 'BLAUS', primary_key = 'CustomerID', property_name = 'ContactName')"
    print '-', feed.get_property(entry_id = 'BLAUS', primary_key = 'CustomerID', property_name = 'ContactName')

def example_catalog():
    """Example Catalog"""

    print '\n--- example module cbs : Catalog - service document ---\n'
    
    # create catalog    
    catalog = Catalog(language = 'en')
    catalog.set_feeds()

    # service document 
    print 'Url service document:', catalog.url
    print 'The service exposes {0} collections:'.format(len(catalog.collections))
    for i, collection in enumerate(catalog.collections, 1):
        feed = catalog.feeds[collection] 
        print '-', collection, '->', len(feed.entries), 'entries'

    # feed
    print '\n--- example module cbs : Catalog - feed or collection ---\n'
    collection = catalog.collections[0]
    feed = catalog.feeds[collection]
    print 'Url feed:', feed.url
    print 'The feed {0} contains {1} entries, properties first entry:'.format(collection, len(feed.entries))
    print "- names:", feed.property_names
    print "- values:", feed.entries[0].values()

def example_catalog_tree():
    """Example CatalogTree"""

    print '\n--- example module cbs : CatalogTree ---\n'
    
    # create CatalogTree    
    ct = CatalogTree(language = 'en')
    ct.set_feeds()

    # service document 
    print 'Url service document:', ct.url
    print 'The service exposes {0} collections:'.format(len(ct.collections))
    for i, collection in enumerate(ct.collections, 1):
        feed = ct.feeds[collection] 
        print '-', collection, '->', len(feed.entries), 'entries'



    # methods  
    print '\n--- example module cbs : CatalogTree - methods ---'

    # get theme_id
    for entry in ct.get_entries('Themes'):
        if entry['ParentID'] is not None and entry['Language']=='en' \
        and ct.get_property('Themes', entry['ParentID'], 'ID', 'ParentID') is not None :
            theme_id = entry['ID']
            break

    theme_title = ct.get_property(collection = 'Themes', entry_id = theme_id, primary_key = 'ID', property_name = 'Title')
    print 'Theme id = {0}, title = {1}.'.format(theme_id, theme_title)

    # get parents theme
    print "\n* method: get_parents -> ct.get_parents(theme_id = {0})".format(theme_id)
    parents = ct.get_parents(theme_id = theme_id)
    for parent_id in parents[:-1]:
        print '- {0} ({1})'.format(ct.get_property('Themes', parent_id, 'ID', 'Title'), parent_id)

    # get children theme
    print "\n* method: get_children -> ct.get_children(theme_id = {0})".format(theme_id)
    children = ct.get_children(theme_id)
    for child in children['Tables_Themes']:
        print '- Table: {0} (id: {1})'.format(ct.get_property('Tables', child['TableID'], 'ID', 'Title'), child['TableID'])
    for child in children['Themes']:
        print '- Theme: {0} (id: {1})'.format(ct.get_property('Themes', child['ID'], 'ID', 'Title'), child['ID'])

def example_table():
    """Example Table"""

    print '\n--- example module cbs : Table - service document ---\n'
    identifier = '81162eng' # other examples: 82220ned, 70072ned, 03759NED, 82172ned
    table = Table(identifier = identifier, query_options = {'UntypedDataSet':'?$top=1'}) 
    table.set_feeds()
    
    # service document 
    print 'Url service document = ', table.url
    print 'The service exposes {0} collections:'.format(len(table.collections))
    for i, collection in enumerate(table.collections, 1):
        feed = table.feeds[collection] 
        print '-', collection, '->', len(feed.entries), 'entries'

    # feed
    print '\n--- example module cbs : Table - feed or collection ---\n'
    collection = 'DataProperties'
    feed = table.feeds[collection]
    print 'Url feed = ', feed.url
    print 'The Feed {0} contains {1} entries, properties first entry:'.format(collection, len(feed.entries))
    print "- names  = ", feed.property_names
    print "- values = ", feed.entries[0].values()

    # dimensions
    dimensions = table.get_dimensions_dataset()
    print '\nThe table has {0} dimensions:'.format(len(dimensions))
    for i, dimension in enumerate(dimensions, 1):
        print '-', dimension, '->', len(dimensions[dimension]), 'entries'

    dimension = list(dimensions)[0]
    print '\nDimension {0} contains {1} entries, key-value pairs:'.format(dimension, len(dimensions[dimension]))
    for key in list(dimensions[dimension])[0:3]:
        print '-', key, ':', dimensions[dimension][key]

    # variables
    variables = table.get_variables_dataset()
    print '\nThe table has {0} variables, top 3 variables:'.format(len(variables))
    for variable in variables[0:3]:
        print '-', ', '.join([variable['name'], variable['label'], variable['type']])

    # typed data set
    dataset = table.get_typed_dataset()
    print '\nThe table has {0} data entries, first entry (max top 5 variables):'.format(len(dataset))
    for variable, value in zip(variables, dataset[0])[0:5]:
        print '-', variable, '=', value, '(type={0})'.format(type(value))

    # untyped data set
    dataset = table.get_untyped_dataset()
    print '\nThe table has {0} data entries, first entry (max top 5 variables):'.format(len(dataset))
    for variable, value in zip(variables, dataset[0])[0:5]:
        print '-', variable, '=', value, '(type={0})'.format(type(value))

if __name__ == '__main__':
    nr = raw_input('Example 1 = OData, 2 = Catalog, 3 = CatalogTree, 4 = Table ? : ')
    if nr in ['1','2','3', '4']:
        if nr == '1':
            example_odata()
        elif nr == '2':
            example_catalog()
        elif nr == '3':
            example_catalog_tree()
        else:
            example_table()
