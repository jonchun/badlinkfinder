#!/usr/bin/env python3
# coding: utf-8

class SiteError:
    def __init__(self, graph, url, **kwargs):
        self._graph = graph
        self._url = url
        self._node = graph[url]
        self._type = kwargs.get('type', None)
        self._error_msg = kwargs.get('error_msg', None)
        self._include_inbound = kwargs.get('include_inbound', False)

    def __repr__(self):
        repr_str = '<SiteError '
        try:
            try:
                if self._type:
                    repr_str += '{} ({})'.format(self._type, self._url)
                elif self._node.status == 'error':
                    # Error loading the page
                    repr_str += 'load_fail ({})'.format(self._url)
                    self._error_msg = self._node.error
                elif self._node.status_code:
                    # make sure status_code is set
                    repr_str += '{} ({})'.format(self._node.status_code, self._url)
                else:
                    # Generic Error. Shouldn't ever get here.
                    raise Exception
            except Exception:
                repr_str += 'generic ({})'.format(self._url)

            if self._error_msg:
                repr_str += ': {}>'.format(self._error_msg)
            else:
                # Empty error message
                repr_str += '>'

            if self._include_inbound:
                # Find parent nodes
                repr_str += '\n  Referenced From:\n'
                for inbound_url in self._graph.get_inbound(self._url):
                    repr_str += '    - {}\n'.format(inbound_url)

            return repr_str
        except Exception:
            return 'Error displaying SiteError'