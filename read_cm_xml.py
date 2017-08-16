"""
Class reads cnf.xml file for Control Modules into an OrderDictionary / Lists for repeats

First level is MultiBlock

Second level has ErdbVersion (ignored) and
Block which contains the relevant information.

Third level contains:
    - Block Def with BlockName
    - Parameters - List of parameters
    - SymbolAttrs - Containing monitoring parameters for Control Module
    - EmBlocks - List of Blocks

Fourth Level
Each Block in the list contains:
    - BlockDef
    - Parameters list of Parameter
    - SymbolAttrs list of SymbolAttr
    - Connections list of Connection

Coordinate data organization:
    Based on segment, pairs of coordinates:
        [{Start:{x: , y: , block: , param: , direction: , arrow: ,},
          End:{see Start},
          orient: horiz/vert }]
"""
import argparse
import collections
import os
import xmltodict

class ReadCM():
    def __init__(self,filepath):
        self.fp = filepath
        self.cm_name = ''
        self.cm_data = {}
    def readFile(self):
        with open(self.fp,'rt',encoding='utf-16') as f:
            f.readline()
            file_data = f.readline()
            d1 = xmltodict.parse(file_data,encoding='utf-16')
            self.data = d1['MultiBlock']['Block']
            self.processMain()
            self.processEmbBlocks()
    def processMain(self):
        self.cm_name = self.data['BlockDef']['BlockName']
        self.cm_data['BlockDef'] = self.data['BlockDef']
        params = collections.OrderedDict()
        for x in self.data['Parameters']['Parameter']:
            params[x['ParamName']] = x['ParamValue']
        self.cm_data['Parameters'] = params
        symbolattr = {}
        for x in self.data['SymbolAttrs']['SymbolAttr']:
            param_name = x['ParamName'].split('.')[-1]
            attr_type = x['AttrType']
            if attr_type not in symbolattr:
                symbolattr[attr_type] = {}
            symbolattr[attr_type][param_name] = x
        self.cm_data['SymbolAttrs'] = symbolattr
    def processEmbBlocks(self):
        self.cm_data['Blocks'] = {}
        for x in self.data['EmbBlocks']['Block']:
            block_name = x['BlockDef']['BlockName'].split('.')[-1]
            self.cm_data['Blocks'][block_name] = {}
            self.cm_data['Blocks'][block_name]['BlockDef'] = x['BlockDef']
            params = {}
            for p in x['Parameters']['Parameter']:
                params[p['ParamName']] = p['ParamValue']
            self.cm_data['Blocks'][block_name]['Parameters'] = params
            symbolattr = {}
            for a in x['SymbolAttrs']['SymbolAttr']:
                pn = a['ParamName'].split('.')
                param_name = '.'.join(pn[2:])
                attr_type = a['AttrType']
                if attr_type not in symbolattr:
                    symbolattr[attr_type] = {}
                symbolattr[attr_type][param_name] = a
            self.cm_data['Blocks'][block_name]['SymbolAttrs'] = symbolattr
            if 'Connections' in x:
                self.cm_data['Blocks'][block_name]['Connections'] = {}
                if type(x['Connections']['Connection']) == collections.OrderedDict:
                    self.cm_data['Blocks'][block_name]['Connections'][x['Connections']['Connection']['BlockId']] = x['Connections']['Connection']
                else:
                    conn = {}
                    for c in x['Connections']['Connection']:
                        block_id = c['BlockId']
                        conn[block_id] = c
                    self.cm_data['Blocks'][block_name]['Connections'] = conn
    def getBlocks(self):
        self.boxes = {}
        coord_names = ['Top','Left','Bottom','Right']
        for x in self.cm_data['Blocks']:
            cds = {}
            coords = self.cm_data['Blocks'][x]['BlockDef']['Coord']
            for c in coord_names:
                cds[c] = float(coords[c])
            self.boxes[x] = cds
    def getSegments(self):
        self.segs = []
        for x in self.cm_data['Blocks']:
            if 'Connections' in self.cm_data['Blocks'][x]:
                coords = self.cm_data['Blocks'][x]['Connections']
                for c in coords:
                    vs = {}
                    ind = coords[c]['InputEnd'].split('.')
                    in_block = ind[1]
                    in_param = '.'.join(ind[2:])
                    outd = coords[c]['OutputEnd'].split('.')
                    out_block = outd[1]
                    out_param = '.'.join(outd[2:])
                    for i, v in enumerate(coords[c]['Vertex'][:-1]):
                        scoord = {'x':float(v['XVertex']),
                                  'y':float(v['YVertex']),
                                  'block': '', 'direct': '', 'arrow': '', 'param': ''}
                        vs['Start'] = scoord
                        scoord = {'x':float(coords[c]['Vertex'][i+1]['XVertex']),
                                  'y':float(coords[c]['Vertex'][i+1]['YVertex']),
                                  'block': '', 'direct': '', 'arrow': '', 'param': ''}
                        vs['End'] = scoord
                        if vs['Start']['x'] == vs['End']['x']:
                            vs['orient'] = 'vert'
                            if vs['Start']['y'] > vs['End']['y']:
                                vs['Start']['arrow'] = 'up'
                                vs['End']['arrow'] = 'down'
                            else:
                                vs['Start']['arrow'] = 'down'
                                vs['End']['arrow'] = 'up'
                        elif vs['Start']['y'] == vs['End']['y']:
                            vs['orient'] = 'horiz'
                            if vs['Start']['x'] > vs['End']['x']:
                                vs['Start']['arrow'] = 'right'
                                vs['End']['arrow'] = 'left'
                            else:
                                vs['Start']['arrow'] = 'left'
                                vs['End']['arrow'] = 'right'
                        else:
                            vs['orient'] = 'other'
                        in_box, xy_out = self.boxConnect(vs['Start'],in_block)
                        if in_box:
                            vs['Start']['block'] = in_block
                            vs['Start']['param'] = in_param
                            vs['Start']['x'] = xy_out['x']
                            vs['Start']['y'] = xy_out['y']
                            vs['Start']['direct'] = 'in'
                        in_box, xy_out = self.boxConnect(vs['Start'],out_block)
                        if in_box:
                            vs['Start']['block'] = out_block
                            vs['Start']['param'] = out_param
                            vs['Start']['x'] = xy_out['x']
                            vs['Start']['y'] = xy_out['y']
                            vs['Start']['direct'] = 'out'
                        in_box, xy_out = self.boxConnect(vs['End'],in_block)
                        if in_box:
                            vs['End']['block'] = in_block
                            vs['End']['param'] = in_param
                            vs['End']['x'] = xy_out['x']
                            vs['End']['y'] = xy_out['y']
                            vs['End']['direct'] = 'in'
                        in_box, xy_out = self.boxConnect(vs['End'],out_block)
                        if in_box:
                            vs['End']['block'] = out_block
                            vs['End']['param'] = out_param
                            vs['End']['x'] = xy_out['x']
                            vs['End']['y'] = xy_out['y']
                            vs['End']['direct'] = 'out'
                        self.segs.append(vs)
    def boxConnect(self, seg_pt, box_name):
        # Check the seg_end for all 4 box coordinates.  
        # If right or left, cut x coordinate.
        # If top or bottom, cut y coordinate.
        if seg_pt['x'] >= self.boxes[box_name]['Left'] and \
           seg_pt['x'] <= self.boxes[box_name]['Right'] and \
           seg_pt['y'] <= self.boxes[box_name]['Top'] and \
           seg_pt['y'] >= self.boxes[box_name]['Bottom']:
            in_box = True
        else:
            in_box = False
        xy_out = {'x': seg_pt['x'], 'y': seg_pt['y']}
        arrows = ['left', 'right', 'up', 'down']
        sides = ['Right', 'Left', 'Bottom', 'Top']
        coords = ['x', 'x', 'y', 'y']
        for a, s, c in zip(arrows, sides, coords):
            if a == seg_pt['arrow']:
                xy_out[c] = self.boxes[box_name][s]
        return in_box, xy_out


if __name__ == '__main__':
    #path = '/home/jmill/Documents/Work/1Ref_HDS/C300_20170630'
    path = '..'
    filename = '19FC103.cnf.xml'
    rc = ReadCM(os.path.join(path,filename))
    rc.readFile()
    print(rc.cm_name)
    print('*'*40)
    rc.getBlocks()
    print(' '*10 + '{0:>10}{1:>10}{2:>10}{3:>10}'.format('Top','Bottom','Left','Right'))
    print('-'*50)
    fmt_box = '{Top:>10}{Bottom:>10}{Left:>10}{Right:>10}'
    for x in rc.boxes:
        print('{:<10}'.format(x) + fmt_box.format(**rc.boxes[x]))
    print('*'*40)
    rc.getSegments()
    key_order = ['Start', 'End']
    seg_order = ['x', 'y', 'arrow', 'direct', 'block', 'param']
    fmt_hdr = '{0:^10}{1:^10}{2:^10}{3:^10}{4:^10}{5:^10}'
    fmt_seg = '{x:^10}{y:^10}{arrow:^10}{direct:^10}{block:^10}{param:^10}'
    print('        ' + fmt_hdr.format(*seg_order))
    print('-'*68)
    for x in rc.segs:
        print('Start:  ' + fmt_seg.format(**x['Start']))
        print('End:    ' + fmt_seg.format(**x['End']))
        print(' ')
