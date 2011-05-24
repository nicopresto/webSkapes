import simplejson as json
from re import match
from urllib2 import urlopen
from BeautifulSoup import BeautifulStoneSoup

def sync():
    require_role (admin_role)
    if request.args[0] == 'geoserver':
        path = request.vars.get ('path')
        file = urlopen (path + '/wms?ERVICE=WMS&REQUEST=GetCapabilities')
        buffer = file.read ()
        soup = BeautifulStoneSoup (buffer)
        layers = soup.findAll (name = 'layer')
        results = []
        for l in layers:
            name = l.find ('title')
            id = l.find ('name')
            if name and id:
                text = name.string
                if not text:
                    text = id.string
                m = match ('^([^\:]+)\:(.+)$', id.string)
                if m:
                    p = m.group (1)
                    f = m.group (2)
                else:
                    p = '',
                    f = id.string
                id = dm.insert ('maps', prefix = p, filename = f, name = text, src = path, public = True)
                keywords = l.findAll (name = 'keyword')
                kw = []
                for k in keywords:
                    kw.append (k.string)
                dm.keywords ('maps', id, kw)
        return 'Ok'

def maps():
    file = urlopen (deployment_settings.geoserver.wms_capabilities ())
    buffer = file.read ()
    soup = BeautifulStoneSoup (buffer)
    layers = soup.findAll (name = 'layer')
    results = []
    for l in layers:
        name = l.find ('title')
        id = l.find ('name')
        if name and id:
            text = name.string
            if not text:
                text = id.string
            m = match ('^([^\:]+)\:(.+)$', id.string)
            if m:
                p = m.group (1)
                f = m.group (2)
            else:
                p = '',
                f = id.string
            results.append ({'prefix': p, 'filename': f, 'name': text, 'type': 'db'})
    return json.dumps (results)

def kw():
    from BeautifulSoup import BeautifulStoneSoup 
    from urllib2 import urlopen

    tmp_create_lit ()
    disease = request.vars.get ('d')
    result = db.executesql ('''
    SELECT keyword.kw, counts.count 
    FROM (SELECT keycount.kw_id, keycount.count 
          FROM (SELECT id 
                FROM disease 
                WHERE d = '%s') AS diseases
          INNER JOIN keycount
          ON keycount.d_id = diseases.id) AS counts
    INNER JOIN keyword
    ON keyword.id = counts.kw_id;
    ''' % (disease,))
    rList = []
    capabilities = urlopen (deployment_settings.geoserver.wms_capabilities ()).read ()
    soup = BeautifulStoneSoup (capabilities)
    keywords = soup.findAll (name = 'keyword')
    for r in result:
        words = []
        for k in keywords:
            if k.string == r[0]:
                words.append (k)
        mapList = []
        for w in words:
            layer = w.parent.parent
            id = layer.find ('name').string
            name = layer.find ('title').string
            mapList.append ({'filename': id, 'name': name, 'type': 'db'})
        d = dict (kw = r[0], count = r[1], numMaps = len (words), maps = mapList)
        rList.append (d)
    return json.dumps (rList)

def reset_maps():
    if not auth.user:
        raise HTTP (400)
    db (db.saved_maps.user_id == auth.user.id).update (json = '{}')
    return 'Ok'
    
def save_maps():
    if not auth.user:
        raise HTTP (400)
    mapList = request.vars.get ('data')
    if mapList is None:
        raise HTTP (400)
    db (db.saved_maps.user_id == auth.user.id).update (json = mapList)

'''def save_slice():
    if not auth.user:
        raise HTTP (400)
    filename = request.vars.get ('filename')
    name = request.vars.get ('name')
    subset = request.vars.get ('subset')'''
