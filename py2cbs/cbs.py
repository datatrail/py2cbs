#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright 2016, S. Declerck
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from odata import Resource
from collections import OrderedDict 
import json

class DataService(object):
    """Class respresenting a data service provided by CBS.

    Attributes:
        url (str): url identifying the service document of the data service
        collections ([str]): selection of (names of) collections exposed by the data service, default [] = all collections 
        feeds {collection, feed}: feeds (which consist of entries) exposed by the data service
    """

    def __init__(self, url, collections = [], query_options = {}):
        """Initialize CBS Open Data data service.

        Args:
            url (str): url that points to the service document of the data service
            collections (Optional[str]): subset of collections exposed by the data service, default [] = all collections
            query_options (optional{resource_path:filter}): collection specific query_options
        """
        self.url = url
        self.set_collection(collections)
        self.query_options = query_options
        self.feeds = {}

    def set_collection(self, collections):
        """Set collections as hold by the service document (default) or as specified by the user.

        Args:
            collections (Optional[str]): subset of collections exposed by the data service, default [] = all collections
        """
        if collections == []: 
            service_document = Resource(service_root = self.url)
            
            self.collections = [entry['name'] for entry in service_document.entries]
        else:
            self.collections = collections


    def set_feeds(self):
        """Set feeds (load data) for the selected collections."""
        self.feeds = {}
        for collection in self.collections:
            if collection in self.query_options:
                qo = self.query_options[collection]
            else:
                qo = None                
            feed = Resource(service_root = self.url, resource_path = collection, query_options = qo)
            self.feeds[collection] = feed

    def get_entries(self, collection):
        """Get the entries exposed by a feed/collection

        Args:
            collection (str): name of the feed

        Returns:
            List of entries, each containing an ordered dictionary of (property name, property value) pairs
        """
        return self.feeds[collection].entries


    def get_entry(self, collection, entry_id, primary_key):
        """Get a single entry from a feed/collection.

        Args:
            collection (str): name of the feed
            entry_id: unique identifier of an entry
            primary_key (str): name unique identifier

        Returns:
            Entry, an ordered dictionary of (property name, property value) pairs
        """
        return self.feeds[collection].get_entry(entry_id, primary_key)

    def get_property(self, collection, entry_id, primary_key,  property_name):
        """Get a property from an entry.

        Args:
            collection (str): name of the feed
            entry_id: unique identifier of an entry
            primary_key (str): name unique identifier
            property_name (str): name of the property

        Returns:
            Property value
        """
        return self.feeds[collection].get_property(entry_id, primary_key,  property_name)

    def query(self, collection, search_properties = {}, return_property_names = []):
        """Generic search function to query a collection/feed.

        Args:
            collection (str): name of the feed
            search_properties ({property_name:property_value}): name:value pairs to select  
            return_property_names ([property_name]): list of property_names returned from selected entries (default = all)

        Returns:
            List of entries, each containing an ordered dictionary of (property name, property value) pairs
        """

class Catalog(DataService):
    """Class respresenting CBS Open Data Catalog data service.

    Attributes:
        language (str): language catalog ('nl' = dutch, 'en' = english, default = None)
    """

    def __init__(self, collections = [], language = None): 
        """Initialize CBS Open Data Catalog data service.

        Args:
            collections (Optional[str]): subset of collections exposed by the data service, default [] = all collections
            language (str): language catalog ('nl' = dutch, 'en' = english, default = None)
        """

        url = 'http://opendata.cbs.nl/ODataCatalog'
        self.language = language
        if language is not None:
            qo_filter =  "$filter=Language eq '{0}'".format(language)
            query_options = {'Tables':qo_filter, 'Themes':qo_filter}
        else:
            query_options = {}
        super(Catalog, self).__init__(url = url, collections = collections, query_options = query_options)


class CatalogTree(Catalog):
    """Class respresenting navigation tree CBS Open Data Catalog data service.

    Attributes:
        language (str): language catalog ('nl' = dutch, 'en' = english, default = None)
    """

    def __init__(self, language = None):
        """Initialize navigation tree CBS Open Data Catalog data service.

        Args:
            language (str): language catalog ('nl' = dutch, 'en' = english, default = None)
        """

        self.language = language 
        collections = ['Tables', 'Themes', 'Tables_Themes']
        super(CatalogTree, self).__init__(collections = collections, language = language)

    def get_parents(self, theme_id):
        """Get the parents of a theme.

        Args:
            theme_id (int): unique identifier of a theme

        Returns:
            List of theme id's (parentnodes)
        """
        ids = [theme_id]
        parent_id = self.get_property('Themes', theme_id, 'ID', 'ParentID')
        while not (parent_id is None):
            ids.append(parent_id)
            parent_id = self.get_property('Themes', parent_id, 'ID', 'ParentID')
        ids.reverse()
        return ids

    def get_children(self, theme_id):
        """Get the direct children of a theme.

        Args:
            theme_id (int): unique identifier of a theme

        Returns:
            Dictionary of tables_themes and themes childnodes
            - tables_themes childnodes: {ID, TableID} from Tables_Themes
            - themes childnodes: {ID} from Themes
        """
        tables = self.feeds['Tables_Themes'].query(search_properties = {'ThemeID':theme_id}, return_property_names = ['ID', 'TableID'])
        themes = self.feeds['Themes'].query(search_properties = {'ParentID':theme_id}, return_property_names = ['ID'])
        return {'Tables_Themes':tables, 'Themes':themes}

class Table(DataService):
    """Class respresenting CBS Open Data Api or Feed data service.

    Attributes:
        identifier (str): unique identifier of a table
    """

    def __init__(self, identifier, collections = [], query_options = {}):
        """Initialize CBS Open Data Api/Feed data service.

        Args:
            collections (optional [str]): subset of collections exposed by the data service, default [] = all collections
            query_options (optional {collection:filter}): collection specific query_options

        """
        url = 'http://opendata.cbs.nl/ODataFeed/odata/' + identifier
        self.identifier = identifier
        super(Table, self).__init__(url = url, collections = collections, query_options = query_options)

    def get_dimensions_dataset(self):
        """Get the dimensions in the dataset.

        Returns:
            Dictionary of dimensions each containing an ordered dictionary of (value, label) pairs
        """
        dimensions = {}
        if 'DataProperties' in self.collections:
            entries = self.get_entries('DataProperties')
            for entry in entries:
                if 'Dimension' in entry['Type']:
                    dimensions[entry['Key']] = OrderedDict()
                    for dimension_entry in self.get_entries(entry['Key']):
                        dimensions[entry['Key']][dimension_entry['Key']]=dimension_entry['Title']
        return dimensions

    def get_variables_dataset(self):
        """Get the variables in the dataset.

        Returns:
            Ordered dictionary of (variable name, variable label) pairs
        """
        variables = OrderedDict()
        if 'DataProperties' in self.collections:
            variables['ID']='ID'
            entries = self.feeds['DataProperties'].entries
            for entry in entries:
                if entry['Type'] != 'TopicGroup':
                    variables[entry['Key']] = entry['Title']
        return variables

    def get_typed_dataset(self):
        """Get the typed data in the dataset.

        Returns:
            List of datarows
        """
        dataset = [entry.values() for entry in self.get_entries('TypedDataSet')]
        return dataset

    def get_untyped_dataset(self):
        """Get the untyped data in the dataset.

        Returns:
            List of datarows
        """
        dataset = [entry.values() for entry in self.get_entries('UntypedDataSet')]
        return dataset  