import canvas
import os

from read_cm_xml import ReadCM

canvas.unicode = bytes
canvas.set_size(768,1000)
canvas.translate(0,900)
marglr=10
margtop=10
lspace=5
draw = True
fnt = 'Helvetica-Bold'
f_size = 40

path = '..'
filename = '19FC103.cnf.xml'
rc = ReadCM(os.path.join(path,filename))
rc.readFile()
#print(rc.cm_name)
#print('*'*40)
#print(rc.cm_data['BlockDef'])
#print('*'*40)
coords = ['Top','Bottom','Left','Right']

canvas.begin_updates()
canvas.draw_text(rc.cm_data['BlockDef']['BlockName'],10, 40, fnt, f_size)
fnt = 'Helvetica'
f_size = 30
canvas.draw_text(rc.cm_data['Parameters']['DESC'].strip('"') + '  --  ' + rc.cm_data['Parameters']['EUDESC'].strip('"'), 10, 10, fnt, f_size)
for x in rc.cm_data['Blocks']:
    if 'Connections' in rc.cm_data['Blocks'][x]:
        conns = rc.cm_data['Blocks'][x]['Connections']
        for y in conns:
            xy = zip(conns[y]['Vertex'][:-1], conns[y]['Vertex'][1:])
            for z in xy:
                canvas.draw_line(float(z[0]['XVertex']),float(z[0]['YVertex']), float(z[1]['XVertex']),float(z[1]['YVertex']))
                
for x in rc.cm_data['Blocks']:
    #print('\n' + x)
    #print('-'*20)
    c = {}
    #print(rc.cm_data['Blocks'][x]['BlockDef'])
    for y in rc.cm_data['Blocks'][x]['BlockDef']['Coord']:
        if y in coords:
            c[y]=float(rc.cm_data['Blocks'][x]['BlockDef']['Coord'][y])
            #print('{:<10}{:>10}'.format(y, rc.cm_data['Blocks'][x]['BlockDef']['Coord'][y]))
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
