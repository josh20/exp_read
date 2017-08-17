import canvas
import os

from read_cm_xml import ReadCM

path = '..'
filename = '19FC103.cnf.xml'
rc = ReadCM(os.path.join(path,filename))
rc.readFile()
rc.getBlocks()
rc.getSegments()

extremes = {'x':{'min':0,'max':0},'y':{'min':0,'max':0}}
trans = {'Left':'x', 'Right': 'x', 'Top': 'y', 'Bottom': 'y'}
hdr = 100
for b in rc.boxes:
    for c in rc.boxes[b]:
        if rc.boxes[b][c] < extremes[trans[c]]['min']:
            extremes[trans[c]]['min'] = rc.boxes[b][c]
        if rc.boxes[b][c] > extremes[trans[c]]['max']:
            extremes[trans[c]]['max'] = rc.boxes[b][c]
c_size = [extremes['x']['max']-extremes['x']['min'],
          extremes['y']['max']-extremes['y']['min']]
c_size[1] += hdr
c_size[0] += 50
#print(extremes)
#print(c_size)


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
arrows = {'up':[-4,8,4,8,0,-1,2,-8],
          'down':[-4,-8,4,-8,0,0,2,8],
          'left':[-8,-4,-8,4,0,0,8,0],
          'right':[8,-4,8,4,-1,0,-8,0]}
canvas.begin_updates()
canvas.draw_text(rc.cm_data['BlockDef']['BlockName'],10, 40, fnt, f_size)
fnt = 'Helvetica'
f_size = 30
canvas.draw_text(rc.cm_data['Parameters']['DESC'].strip('"') + '  --  ' + rc.cm_data['Parameters']['EUDESC'].strip('"'), 10, 10, fnt, f_size)


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
        #print(c['Left'], c['Top'], c['Right'], c['Bottom'])
        xcorner = min(c['Left'],c['Right'])
        ycorner = min(c['Top'],c['Bottom'])
        width = abs(c['Left']-c['Right'])
        height = abs(c['Top']-c['Bottom'])
        canvas.fill_rect(xcorner,ycorner,width,height)
        #canvas.fill_rect(c['Left'], c['Top'], c['Right'], c['Bottom'])
        fnt = 'Helvetica-Bold'
        f_size = 20
        w, h = canvas.get_text_size(x, fnt, f_size)
        curr_l = c['Left']+marglr
        curr_b = c['Top']-h-margtop
        canvas.draw_text(x, curr_l, curr_b, fnt, f_size)
        ty = rc.cm_data['Blocks'][x]['BlockDef']['ClassName']
        fnt = 'Helvetica'
        f_size = 14
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
               paramv = pars[attr[1]].strip('"')
           elif attr[1] == 'IOP':
               paramv = rc.cm_data['Blocks'][x]['BlockDef']['AssignedTo']
           elif attr[1] == 'CHANNUM':
               paramv = str(int(pars['BLKLSTIDX']) + 1)
           w, h = canvas.get_text_size(paramv, fnt, f_size)
           curr_r = c['Right'] - w - marglr 
           canvas.draw_text(paramv, curr_r, curr_b, fnt, f_size)
#
# Loop through the segments
#
for s in rc.segs:
    canvas.draw_line(s['Start']['x'],s['Start']['y'],s['End']['x'],s['End']['y'])
    arrow_end = ''
    if s['Start']['direct'] == 'in':
        arrow_end = 'Start'
    elif s['End']['direct'] == 'in':
        arrow_end = 'End'
    if arrow_end:
        canvas.draw_line(s[arrow_end]['x'], s[arrow_end]['y'],
                         s[arrow_end]['x'] - arrows[s[arrow_end]['arrow']][0],
                         s[arrow_end]['y'] - arrows[s[arrow_end]['arrow']][1])
        canvas.draw_line(s[arrow_end]['x'], s[arrow_end]['y'],
                         s[arrow_end]['x'] - arrows[s[arrow_end]['arrow']][2],
                         s[arrow_end]['y'] - arrows[s[arrow_end]['arrow']][3])
    fs = 16
    if s['Start']['block']:
        ty = s['Start']['param']
        w, h = canvas.get_text_size(ty, fnt, fs)
        canvas.draw_text(ty, s['Start']['x'] + arrows[s['Start']['arrow']][4] * w + arrows[s['Start']['arrow']][6],
                         s['Start']['y'] + arrows[s['Start']['arrow']][5] * h + arrows[s['Start']['arrow']][7],
                         fnt, fs)
    if s['End']['block']:
        ty = s['End']['param']
        w, h = canvas.get_text_size(ty, fnt, fs)
        canvas.draw_text(ty, s['End']['x'] + arrows[s['End']['arrow']][4] * w + arrows[s['End']['arrow']][6],
                         s['End']['y'] + arrows[s['End']['arrow']][5] * h + arrows[s['End']['arrow']][7],
                         fnt, fs)
canvas.end_updates()
canvas.save_png('19FC103.png')
