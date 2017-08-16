import canvas
import os

from read_cm_xml import ReadCM

path = '..'
filename = '19FC103.cnf.xml'
rc = ReadCM(os.path.join(path,filename))
rc.readFile()

extremes = {'x':{'min':0,'max':0},'y':{'min':0,'max':0}}
trans = {'Left':'x', 'Right': 'x', 'Top': 'y', 'Bottom': 'y'}
hdr = 100
for b in rc.boxes:
    for c in b:
        if rc.boxes[b][c] < extremes[trans[c]]['min']:
            extremes[trans[c]]['min'] = rc.boxes[b][c]
        if rc.boxes[b][c] > extremes[trans[c]]['max']:
            extremes[trans[c]]['max'] = rc.boxes[b][c]
c_size = [extremes['x']['max']-extremes['x']['min'],
          extremes['y']['min']-extremes['y']['min']]
c_size[1] += hdr

canvas.unicode = bytes
canvas.set_size(*c_size)
canvas.translate(0,c_size[1]-hdr)
#canvas.set_size(768,1000)
#canvas.translate(0,900)
marglr=10
margtop=10
lspace=5
draw = True
fnt = 'Helvetica-Bold'
f_size = 40

coords = ['Top','Bottom','Left','Right']
arrows = {'up':[-2,-4,2,-4,1,-5],
          'down':[-2,4,2,4,1,5],
          'left':[4,-2,4,2,5,1],
          'right':[-4,-2,-4,2,-5,1]}
canvas.begin_updates()
canvas.draw_text(rc.cm_data['BlockDef']['BlockName'],10, 40, fnt, f_size)
fnt = 'Helvetica'
f_size = 30
canvas.draw_text(rc.cm_data['Parameters']['DESC'].strip('"') + '  --  ' + rc.cm_data['Parameters']['EUDESC'].strip('"'), 10, 10, fnt, f_size)
#
# Loop through the segments
#
for s in rc.segs:
    canvas.draw_line(s['Start'][x],s['Start']['y'],s['End']['x'],s['End']['y'])
    arrow_end = ''
    if s['Start']['direct'] == 'in':
        arrow_end = 'Start'
    elif s['End']['direct'] == 'in':
        arrow_end = 'End'
    if arrow_end:
        canvas.draw_line(s[arrow_end]['x'], s[arrow_end]['y'],
                         s[arrow_end][x] - arrows[s[arrow_end]['arrow']][0],
                         s[arrow_end][y] - arrows[s[arrow_end]['arrow']][1])
        canvas.draw_line(s[arrow_end]['x'], s[arrow_end]['y'],
                         s[arrow_end][x] - arrows[s[arrow_end]['arrow']][2],
                         s[arrow_end][y] - arrows[s[arrow_end]['arrow']][3])
    fs = 10
    if s['Start']['block']:
        ty = s['Start']['param']
        w, h = canvas.get_text_size(ty, fnt, fs)
        canvas.draw_text(ty, s['Start']['x'] - w - arrows[s['Start']['direct'][4]],
                         s['Start']['y'] - h - arrows[s['Start']['direct'][5]],
                         fnt, fs)
    if s['End']['block']:
        ty = s['End']['param']
        w, h = canvas.get_text_size(ty, fnt, fs)
        canvas.draw_text(ty, s['End']['x'] - w - arrows[s['End']['direct'][4]],
                         s['End']['y'] - h - arrows[s['End']['direct'][5]],
                         fnt, fs)

"""
for x in rc.cm_data['Blocks']:
    if 'Connections' in rc.cm_data['Blocks'][x]:
        conns = rc.cm_data['Blocks'][x]['Connections']
        for y in conns:
            xy = zip(conns[y]['Vertex'][:-1], conns[y]['Vertex'][1:])
            for z in xy:
                canvas.draw_line(float(z[0]['XVertex']),float(z[0]['YVertex']), float(z[1]['XVertex']),float(z[1]['YVertex']))
"""
for x in rc.cm_data['Blocks']:
    #print('\n' + x)
    #print('-'*20)
    c = {}
    #print(rc.cm_data['Blocks'][x]['BlockDef'])
    for y in rc.cm_data['Blocks'][x]['BlockDef']['Coord']:
        if y in coords:
            c[y]=float(rc.cm_data['Blocks'][x]['BlockDef']['Coord'][y])
    if draw:
        canvas.set_fill_color(.8,.8,.8)
        canvas.fill_rect(c['Left'], c['Top'], c['Right'], c['Bottom'])
        fnt = 'Helvetica-Bold'
        f_size = 30
        w, h = canvas.get_text_size(x, fnt, f_size)
        curr_l = c['Left']+marglr
        curr_b = c['Top']-h-margtop
        canvas.draw_text(x, curr_l, curr_b, fnt, f_size)
        ty = rc.cm_data['Blocks'][x]['BlockDef']['ClassName']
        fnt = 'Helvetica'
        f_size = 16
        w, h = canvas.get_text_size(ty, fnt, f_size)
        curr_b += -(h)
        canvas.draw_text(ty, curr_l, curr_b, fnt, f_size)
        attrs = []
        at = rc.cm_data['Blocks'][x]['SymbolAttrs']['ConfigBlockSymbol']
        for attr in at:
            n = []
            n.append(float(at[attr]['AttrOrder']))
            n.append(attr)
            attrs.append(n)
        curr_b += -20
        pars = rc.cm_data['Blocks'][x]['Parameters']

        for attr in sorted(attrs):
           w, h = canvas.get_text_size(attr[1],fnt,f_size)
           curr_b += -h
           canvas.draw_text(attr[1], curr_l, curr_b, fnt, f_size)
           #print(attr[1])
           paramv = '----'
           if attr[1] in pars:
               paramv = pars[attr[1]]
           elif attr[1] == 'IOP':
               paramv = rc.cm_data['Blocks'][x]['BlockDef']['AssignedTo']
           elif attr[1] == 'CHANNUM':
               paramv = str(int(pars['BLKLSTIDX']) + 1)
           w, h = canvas.get_text_size(paramv, fnt, f_size)
           curr_r = c['Right'] - w + marglr 
           canvas.draw_text(paramv, curr_r, curr_b, fnt, f_size)
canvas.end_updates()
#canvas.save_png('19FC103.png')
