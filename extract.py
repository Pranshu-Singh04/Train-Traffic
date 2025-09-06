import json, csv, math
from shapely.geometry import Point, LineString, shape
# load your stations csv as list
stations = []
with open('stations.csv','r',newline='',encoding='utf8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        stations.append(r)

# load geojson from Overpass Turbo export
g = json.load(open('osm_raw.geojson','r',encoding='utf8'))

# collect nodes with railway station tags
nodes = []
for feat in g['features']:
    props = feat.get('properties',{})
    geom = feat.get('geometry',{})
    if geom and geom['type']=='Point':
        name = props.get('name','').strip()
        nodes.append({'name':name,'lat':geom['coordinates'][1],'lon':geom['coordinates'][0],'props':props})

# helper: find nearest node by name substring or fallback nearest by chainage estimate
def find_node_by_name(target):
    target_low = target.lower()
    for n in nodes:
        if n['name'] and target_low in n['name'].lower():
            return n
    return None

# match and write updated CSV
out = []
for s in stations:
    matched = find_node_by_name(s['station_name'])
    if matched:
        s['lat'] = matched['lat']
        s['lon'] = matched['lon']
    else:
        s['lat'] = ''
        s['lon'] = ''
    out.append(s)

# write back
with open('stations_with_coords.csv','w',newline='',encoding='utf8') as f:
    writer = csv.DictWriter(f, fieldnames=out[0].keys())
    writer.writeheader()
    writer.writerows(out)

print("Wrote data/lko_cnb/stations_with_coords.csv — review and manually fix unmatched stations.")
