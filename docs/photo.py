import cgi
import json

from google.appengine.ext import ndb
from PIL import Image
from StringIO import StringIO

from palette import extract_colors
from models import range_names, rgb_hls
from palette import rgb_to_hex
from handlers import BaseHandler


class Palette(BaseHandler):
    """
    Palette(
        colors=[
            Color(value=(211, 73, 74), prominence=0.27075757575757575),
            Color(value=(69, 101, 103), prominence=0.08575757575757575),
            Color(value=(69, 1, 2), prominence=0.06818181818181818),
            Color(value=(88, 57, 60), prominence=0.0353030303030303)],
        bgcolor=
            Color(value=(164, 14, 12), prominence=0.4356060606060606))
    """
    def get(self, safe_key):
        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.abort(404)
        img = Image.open(StringIO(obj.buffer))
        img.thumbnail((100, 100), Image.ANTIALIAS)
        palette = extract_colors(img)
        if palette.bgcolor:
            colors = [palette.bgcolor] + palette.colors
        else:
            colors = palette.colors

        data = {'active': {'color': obj.rgb,
                           'hls': rgb_hls(obj.rgb),
                           'hex': obj.hex,
                           'class': obj.color},
                'palette': [
                    {'prominence': '%.1f%%' % (100 * c.prominence,),
                     'color': c.value,
                     'hls': rgb_hls(c.value),
                     'hex': rgb_to_hex(c.value),
                     'class': range_names(c.value)} for c in colors]}

        self.render_json(data)

    def post(self, safe_key):
        def characterise(hue, lum, sat):
            if lum in ('dark', 'light',) or sat == 'monochrome':
                return lum
            else:
                return hue

        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.render_json({'success': False})
        new_rgb = json.loads(self.request.get('rgb'))
        new_range_names = range_names(new_rgb)
        new_color = characterise(*new_range_names)
        if new_rgb != obj.rgb or new_color != obj.color:
            # decr_count('Photo', 'color', obj.color)
            obj.rgb = new_rgb
            obj.hue, obj.lum, obj.sat = new_range_names
            obj.put()
            # incr_count('Photo', 'color', obj.color)
            self.render_json({
                'success': True,
                'similar_url': self.uri_for('photo_all_filter', field='color', value=obj.color)
            })
        else:
            self.render_json({'success': False})
