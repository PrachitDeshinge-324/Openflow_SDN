"""
Networks with more than one path between hosts, for the path-quality experiment
CS G525 Advanced Computer Networks - Project SA7

Every builder returns (Mininet Topo, link delays, switch labels):
  delays : {(switch name, switch name): one-way delay in ms}, used for TCLink
           delay= and written to the topology file for the proactive controller
  labels : {switch name: readable name}, e.g. 'edge p0-0' or 'Chicago'

  fattree(k=4)  - data-centre fat-tree (Al-Fares et al., SIGCOMM 2008):
                  k=4 gives 4 core, 8 aggregation, 8 edge switches, 16 hosts,
                  and 4 equal-length paths between hosts in different pods
  abilene()     - the Abilene / Internet2 US research backbone, 11 cities and
                  14 links, as in the Internet Topology Zoo (Abilene.gml)
  from_gml(f)   - any Internet Topology Zoo .gml file (e.g. Geant2012.gml from
                  topology-zoo.org), one host per city

ISP link delays are the straight-line distance between the two cities at the
speed of light in fibre (about 200 km per ms). Real fibre routes are longer,
so these delays are a lower bound.
"""

import math
import os
import re

from mininet.topo import Topo


def _dpid(n):
  return '%016x' % n


# ---------------------------------------------------------------- fat-tree

def fattree(k=4):
  if k % 2:
    raise ValueError("fat-tree k must be even")
  topo = Topo()
  labels = {}
  half = k // 2
  n = [0]

  def switch(label):
    n[0] += 1
    name = 's%d' % n[0]
    topo.addSwitch(name, dpid=_dpid(n[0]))
    labels[name] = label
    return name

  cores = [switch('core %d' % i) for i in range(half * half)]
  host_no = 0
  for pod in range(k):
    aggs = [switch('agg p%d-%d' % (pod, i)) for i in range(half)]
    edges = [switch('edge p%d-%d' % (pod, i)) for i in range(half)]
    for i, agg in enumerate(aggs):
      for j in range(half):              # aggregation i connects to cores i*k/2 .. i*k/2+k/2-1
        topo.addLink(agg, cores[i * half + j])
      for edge in edges:
        topo.addLink(agg, edge)
    for edge in edges:
      for _ in range(half):
        host_no += 1
        h = topo.addHost('h%d' % host_no)
        topo.addLink(h, edge)
  return topo, {}, labels


# ---------------------------------------------------------------- ISP maps

ABILENE_CITIES = [   # name, latitude, longitude
  ('Seattle', 47.61, -122.33), ('Sunnyvale', 37.37, -122.04), ('Los Angeles', 34.05, -118.24),
  ('Denver', 39.74, -104.99), ('Kansas City', 39.10, -94.58), ('Houston', 29.76, -95.37),
  ('Chicago', 41.88, -87.63), ('Indianapolis', 39.77, -86.16), ('Atlanta', 33.75, -84.39),
  ('Washington DC', 38.91, -77.04), ('New York', 40.71, -74.01),
]
ABILENE_LINKS = [
  ('Seattle', 'Sunnyvale'), ('Seattle', 'Denver'), ('Sunnyvale', 'Los Angeles'),
  ('Sunnyvale', 'Denver'), ('Los Angeles', 'Houston'), ('Denver', 'Kansas City'),
  ('Kansas City', 'Houston'), ('Kansas City', 'Indianapolis'), ('Houston', 'Atlanta'),
  ('Atlanta', 'Indianapolis'), ('Atlanta', 'Washington DC'), ('Indianapolis', 'Chicago'),
  ('Chicago', 'New York'), ('New York', 'Washington DC'),
]

FIBRE_KM_PER_MS = 200.0


def _km(a, b):
  (la1, lo1), (la2, lo2) = [(math.radians(x), math.radians(y)) for x, y in (a, b)]
  h = (math.sin((la2 - la1) / 2) ** 2
       + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
  return 2 * 6371.0 * math.asin(math.sqrt(h))


def _isp(cities, links, default_delay_ms=1.0):
  """cities: [(label, lat or None, lon or None)], links: [(label, label)]."""
  topo = Topo()
  name_of, coords, labels, delays = {}, {}, {}, {}
  for i, (label, lat, lon) in enumerate(cities, 1):
    sw = topo.addSwitch('s%d' % i, dpid=_dpid(i))
    h = topo.addHost('h%d' % i)
    topo.addLink(h, sw)
    name_of[label], labels[sw] = sw, label
    if lat is not None and lon is not None:
      coords[label] = (lat, lon)
  for a, b in links:
    if a in coords and b in coords:
      d = round(max(_km(coords[a], coords[b]) / FIBRE_KM_PER_MS, 0.1), 2)
    else:
      d = default_delay_ms
    delays[(name_of[a], name_of[b])] = d
    topo.addLink(name_of[a], name_of[b])
  return topo, delays, labels


def abilene():
  return _isp(ABILENE_CITIES, ABILENE_LINKS)


# ---------------------------------------------------------------- Topology Zoo GML

_TOKEN = re.compile(r'"[^"]*"|\[|\]|[^\s\[\]]+')


def _parse_gml(text):
  tokens = _TOKEN.findall(text)
  pos = [0]

  def block():
    items = []
    while pos[0] < len(tokens):
      t = tokens[pos[0]]
      pos[0] += 1
      if t == ']':
        break
      v = tokens[pos[0]]
      pos[0] += 1
      if v == '[':
        items.append((t, block()))
      else:
        items.append((t, v.strip('"')))
    return items

  return dict(block()).get('graph', [])


def from_gml(path):
  graph = _parse_gml(open(path).read())
  nodes, edges = {}, []
  for key, val in graph:
    if key == 'node':
      d = dict(val)
      lat, lon = d.get('Latitude'), d.get('Longitude')
      nodes[d['id']] = (d.get('label', 'n' + d['id']),
                        float(lat) if lat is not None else None,
                        float(lon) if lon is not None else None)
    elif key == 'edge':
      d = dict(val)
      edges.append((d['source'], d['target']))

  # Keep the largest connected part, drop self-loops and repeated links
  adj = {n: set() for n in nodes}
  for a, b in edges:
    if a != b:
      adj[a].add(b)
      adj[b].add(a)
  best, seen = set(), set()
  for n in sorted(nodes, key=int):
    if n in seen:
      continue
    comp, stack = set(), [n]
    while stack:
      u = stack.pop()
      if u not in comp:
        comp.add(u)
        stack.extend(adj[u] - comp)
    seen |= comp
    if len(comp) > len(best):
      best = comp
  keep = sorted(best, key=int)
  label = {}
  for n in keep:   # unique labels (some maps reuse a city name)
    l = nodes[n][0]
    label[n] = l if l not in label.values() else '%s (%s)' % (l, n)
  cities = [(label[n], nodes[n][1], nodes[n][2]) for n in keep]
  links = sorted({tuple(sorted((a, b), key=int)) for a, b in edges if a != b and a in best})
  return _isp(cities, [(label[a], label[b]) for a, b in links])


def gml_name(path):
  return 'zoo-' + os.path.splitext(os.path.basename(path))[0].lower()


BUILTIN = {
  'fattree-k4': lambda: fattree(4),
  'abilene': abilene,
}
