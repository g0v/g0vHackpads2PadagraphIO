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
GRAPHNAME = "G0V Hackpads network"
DESCRIPTION = "a graph or inter-linked Hackpads"
TAGS = ["pads", "g0v-tw"]


NodePad = NodeType("pad","", {"id": Text(),
                            "label": Text(),
                            "url": Text()})


EdgeLink = EdgeType("link to", "", {}) 



bot = Botagraph(PDG_HOST, PDG_KEY)
bot.create_graph(GRAPHNAME, {'description': DESCRIPTION, "tags": TAGS, "image":"https://avatars3.githubusercontent.com/u/2668086?v=3&s=200"})


# Posting Nodes and Edges Types

nodetypes_uuids = {}
edgetypes_uuids = {}
for nt in [NodePad]:
    nodetypes_uuids[nt.name] = bot.post_nodetype(GRAPHNAME, nt.name, nt.description, nt.properties)

for et in [EdgeLink]:
    edgetypes_uuids[et.name] = bot.post_edgetype(GRAPHNAME, et.name, et.description, et.properties)





re_link = re.compile("g0v.hackpad.com\\/(.*)$")
nodes_uuid = {}
pad_nodetype = nodetypes_uuids[NodePad.name]
link_edgetype = edgetypes_uuids[EdgeLink.name]

def getNodeIterator():
    for f in glob.glob("./hackpad-backup-g0v/*.html"):
        page_id = f.rsplit("/",1)[-1][:-5]
        print page_id
        url = "https://g0v.hackpad.com/%s.html" % (page_id,)
        with open(f) as F:
            html = open(f).read()
            bs = BS(html)
            title = bs.body.children.next().text
            print title
            body = bs.body.text
            props = {'id': page_id,
                     'label': title,
                     'url': url}
            yield {'nodetype': pad_nodetype,
                    'properties': props}

def getEdgeIterator(node_idx):
    for f in glob.glob("./hackpad-backup-g0v/*.html"):
        page_id = node_idx[f.rsplit("/",1)[-1][:-5]]
        with open(f) as F:
            html = open(f).read()
            bs = BS(html)
            for url in [x['href'] for x in bs.findAll("a")]:
                m = re_link.search(url)
                if m:
                    link = m.group(1)
                    target_id = node_idx.get(link,None)
                    if target_id is not None:
                        yield { 'edgetype': link_edgetype,
                                'source': page_id,
                                'target': target_id,
                                'properties': {}}
# Posting Nodes
node_idx = {}
for node, uuid in bot.post_nodes(GRAPHNAME, getNodeIterator()):
    nid = node['properties']['id']
    node_idx[nid] = uuid

# Posting Edges

list(bot.post_edges(GRAPHNAME, getEdgeIterator(node_idx)))

