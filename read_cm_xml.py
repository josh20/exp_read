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

if __name__ == '__main__':
    #path = '/home/jmill/Documents/Work/1Ref_HDS/C300_20170630'
    path = '..'
    filename = '19FC103.cnf.xml'
    rc = ReadCM(os.path.join(path,filename))
    rc.readFile()
    print(rc.cm_name)
    print('*'*40)
    print(rc.cm_data['Blocks']['19FT103']['BlockDef'])
    print('*'*40)
    tp = rc.cm_data['Blocks']['DACA']['SymbolAttrs']['ViewPinLabels']
    for x in sorted(tp.keys()):
    	if 'hist' not in x.lower() and 'hcmd' not in x.lower():
    		print(x,tp[x])
    print('*'*40)
    """
    coords = ['Top','Bottom','Left','Right']
    for x in rc.cm_data['Blocks']:
        print('\n' + x)
        print('-'*20)
        #print(rc.cm_data['Blocks'][x]['SymbolAttrs']['ConfigBlockSymbol'])
        for y in rc.cm_data['Blocks'][x]['BlockDef']['Coord']:
            if y in coords:
                print('{:<10}{:>10}'.format(y, rc.cm_data['Blocks'][x]['BlockDef']['Coord'][y]))
    """
