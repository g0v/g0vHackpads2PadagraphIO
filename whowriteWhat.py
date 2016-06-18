import os
import glob
import re
from collections import namedtuple
from bs4 import BeautifulSoup as BS


from botapi import Botagraph, BotApiError
from reliure.types import Text

NodeType = namedtuple("NodeType", "name description properties")
EdgeType = namedtuple("EdgeType", "name description properties")

# Graph Definition

PDG_HOST = "http://g0v-tw.padagraph.io"
PDG_KEY = ""
GRAPHNAME = "G0V Who Writes What"
DESCRIPTION = "a graph or pads and authors"
TAGS = ["pads", "g0v-tw"]


NodePad = NodeType("pad","", {"id": Text(),
                            "label": Text()})

NodeAuthor = NodeType("author", "", {"id": Text(), "label": Text()})

EdgeLink = EdgeType("writes", "", {}) 



bot = Botagraph(PDG_HOST, PDG_KEY)
bot.create_graph(GRAPHNAME, {'description': DESCRIPTION, "tags": TAGS, "image":"https://avatars3.githubusercontent.com/u/2668086?v=3&s=200"})


# Posting Nodes and Edges Types

nodetypes_uuids = {}
edgetypes_uuids = {}
for nt in [NodePad, NodeAuthor]:
    nodetypes_uuids[nt.name] = bot.post_nodetype(GRAPHNAME, nt.name, nt.description, nt.properties)

for et in [EdgeLink]:
    edgetypes_uuids[et.name] = bot.post_edgetype(GRAPHNAME, et.name, et.description, et.properties)





re_link = re.compile("g0v.hackpad.com\\/(.*)$")
nodes_uuid = {}
pad_nodetype = nodetypes_uuids[NodePad.name]
author_nodetype = nodetypes_uuids[NodeAuthor.name]
link_edgetype = edgetypes_uuids[EdgeLink.name]

data = BS(open("group_index.rss").read())

def getNodeIterator():
    for entry in data.findAll("entry"):
        pad_id = entry.findAll("id")[0].text
        title = entry.findAll("title")[0].text
        props = {'id': pad_id,
                 'label': title}
        yield {'nodetype': pad_nodetype,
                'properties': props}
    names = set([n.strip() for names in data.findAll("name") for n in names.text.split(",")])
    for n in names:
        yield {'nodetype': author_nodetype,
                'properties': {'label': n,
                                'id': n}}

def getEdgeIterator(node_idx):
    for entry in data.findAll("entry"):
        pad_id = node_idx[entry.findAll("id")[0].text]
        names = set([n.strip() for n in entry.findAll("name")[0].text.split(",")])
        for n in names:
            nid = node_idx[n]
            yield { 'edgetype': link_edgetype,
                    'source': pad_id,
                    'target': nid,
                    'properties': {}}
# Posting Nodes
node_idx = {}
for node, uuid in bot.post_nodes(GRAPHNAME, getNodeIterator()):
    nid = node['properties']['id']
    node_idx[nid] = uuid

# Posting Edges

list(bot.post_edges(GRAPHNAME, getEdgeIterator(node_idx)))
bot.star_nodes(GRAPHNAME, node_idx.values())
