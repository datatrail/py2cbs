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

import urllib
import json
from collections import OrderedDict

class Resource(object):
    """Class representing an OData resource exposed by a web service.
    
    Attributes:
        url : url identifying the resource
        entries [{name: value}]: data hold by the resource    
    """
    
    def __init__(self, service_root, resource_path = None, query_options = None):
        """Instantiate a new ODdata Resource object.

        Args:
            service_root (str): url identifying the service document
            resource_path (str): path pointing to the resource (collection/feed)
            query_options (str): parameters applied to the query the resource
        """
        self.set_url(service_root = service_root, resource_path = resource_path, query_options = query_options)
        self.set_entries()
        self.set_property_names()

    def set_url(self, service_root, resource_path, query_options):
        """Compose url out of service_root, resource_path and query_options.

        Args:
            service_root (str): url identifying the service document
            resource_path (str): path pointing to the resource (collection/feed)
            query_options (str): parameters applied to the query the resource
        """
        url = service_root
        if resource_path is not None:
            url += '/' + resource_path
        if query_options is not None:
            url += '?' + query_options
        self.url = url

    def read_json_data(self, url):
        """Read JSON data hold by the resource.

        Args:
            url (str): url identifying the resource

        Returns:
            An ordered dictionary contaning the data hold by the resource
        """
        # force the resource output into JSON-format
        if '$format=json' not in url: 
            if '?' in url:
                url += '&$format=json'
            else:
                url += '?$format=json'

        response = urllib.urlopen(url)
        data =  json.load(response, object_pairs_hook=OrderedDict)
        return data

    def set_entries(self):
        """Set entries."""
        entries = []
        next_link = self.url
        while True:
            entries_iteration = self.read_json_data(next_link)
            entries += entries_iteration['value']
            if 'odata.nextLink' in entries_iteration.keys():
                next_link = entries_iteration['odata.nextLink']
            else:
                break
        self.entries = entries

    def set_property_names(self):
        """Set property names"""  
        if len(self.entries)>0:
            self.property_names = self.entries[0].keys()
        else:
            self.property_names = []

    def query(self, search_properties = {}, return_property_names = []):
        """Generic search function to query a resource.

        Args:
            search_properties ({property_name:property_value}): name:value pairs to select  
            return_property_names ([property_name]): list of property_names returned from selected entries (default = all)

        Returns:
            List of entries, each containing an ordered dictionary of (property name, property value) pairs
        """
        if return_property_names == []:
            return_property_names = self.property_names
        result = []
        for entry in self.entries:
            if search_properties == {}:
                tmp_entry = OrderedDict()
                for return_property_name in return_property_names:
                    tmp_entry[return_property_name] = entry[return_property_name]
                    result.append(tmp_entry)
            else:
                if all( [ entry[search_property_name] == search_properties[search_property_name] for search_property_name in search_properties.keys()]):
                    tmp_entry = OrderedDict()
                    for return_property_name in return_property_names:
                        tmp_entry[return_property_name] = entry[return_property_name]
                    result.append(tmp_entry)
        return result

    def get_entry(self, entry_id, primary_key):
        """Get a single entry.

        Args:
            entry_id: unique identifier of an entry
            primary_key (str): property name unique identifier

        Returns:
            Entry, ordered dictionary of (property name, property value) pairs
        """
        return self.query(search_properties = {primary_key:entry_id})[0]

    def get_property(self, entry_id, primary_key,  property_name):
        """Get a property.

        Args:
            entry_id: unique identifier of an entry
            primary_key (str): property name unique identifier
            property_name (str): name of the property

        Returns:
            Property value
        """
        entry = self.get_entry(entry_id, primary_key)
        if entry is not None:
            return entry[property_name]
        else:
            return None