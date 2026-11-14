"""Create an original geometric G mark and outlined wordmarks; no stock assets."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent/'brand'
ROOT.mkdir(exist_ok=True)
FONT=Path('C:/Windows/Fonts/segoeuib.ttf')
if not FONT.exists():raise SystemExit('Run once on the authoring Windows host with Segoe UI Bold installed.')
font=TTFont(FONT);glyphs=font.getGlyphSet();cmap=font.getBestCmap();upem=font['head'].unitsPerEm

def text_paths(text,size,x,y,fill,spacing=0):
    scale=size/upem;pieces=[]
    for char in text:
        name=cmap.get(ord(char),'space');pen=SVGPathPen(glyphs);glyphs[name].draw(pen)
        if pen.getCommands():pieces.append(f'<path transform="translate({x:.3f} {y}) scale({scale:.7f} {-scale:.7f})" d="{pen.getCommands()}" fill="{fill}"/>')
        x+=glyphs[name].width*scale+spacing
    return ''.join(pieces)

mark='<rect width="64" height="64" rx="12" fill="#17231f"/><path d="M47 21a20 20 0 1 0 2 17v-6H33" fill="none" stroke="#e1e9e1" stroke-width="6" stroke-linecap="square"/><circle cx="49" cy="15" r="4" fill="#9fc7ae"/>'
(ROOT/'mark.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img"><title>SEO Geniuses Philippines G monogram</title>'+mark+'</svg>',encoding='utf-8')
for variant,background,ink in [('dark','#101518','#edf0eb'),('light','#f4f5ef','#17231f')]:
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 88" role="img"><title>SEO Geniuses Philippines</title><rect width="400" height="88" fill="'+background+'"/><g transform="translate(12 12)">'+mark+'</g>'+text_paths('SEO Geniuses',32,94,43,ink,-.7)+text_paths('PHILIPPINES',11,96,65,ink,2.4)+'</svg>'
    (ROOT/f'logo-{variant}.svg').write_text(svg,encoding='utf-8')

def raster_mark(size):
    im=Image.new('RGBA',(size,size),(0,0,0,0));d=ImageDraw.Draw(im);s=size/64
    d.rounded_rectangle((0,0,size-1,size-1),radius=round(12*s),fill='#17231f')
    # Same open circular G and terminal used by the vector mark.
    box=tuple(round(v*s) for v in (12,12,52,52))
    d.arc(box,start=18,end=327,fill='#e1e9e1',width=round(6*s))
    d.line([(49*s,38*s),(49*s,32*s),(33*s,32*s)],fill='#e1e9e1',width=round(6*s))
    d.ellipse(tuple(round(v*s) for v in (45,11,53,19)),fill='#9fc7ae')
    return im

icon=raster_mark(512)
icon.save(ROOT/'icon-512.png')
icon.resize((180,180),Image.Resampling.LANCZOS).save(ROOT/'apple-touch-icon.png')
icon.save(ROOT/'favicon.ico',sizes=[(16,16),(32,32),(48,48),(64,64)])
social=Image.new('RGB',(1200,630),'#101518');social_icon=raster_mark(104);social.paste(social_icon,(80,78),social_icon)
d=ImageDraw.Draw(social)
d.text((80,240),'SEO Geniuses',font=ImageFont.truetype(str(FONT),83),fill='#edf0eb')
d.text((84,350),'PHILIPPINES',font=ImageFont.truetype(str(FONT),29),fill='#9fc7ae')
d.line((84,430,1116,430),fill='#46534d',width=2)
d.text((84,474),'Technical SEO. Content. Local search.',font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',31),fill='#c2c9c3')
social.save(ROOT/'social-card.png',optimize=True)
print('Created original SVG logos, SVG/ICO favicon, touch icon and social card.')
