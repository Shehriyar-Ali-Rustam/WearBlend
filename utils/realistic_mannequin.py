"""Realistic Mannequin Renderer for WearBlend"""

from PIL import Image, ImageDraw, ImageFilter
from typing import Dict, Tuple
import io
import math


class RealisticMannequin:
    CANVAS_SIZE = (800, 1100)

    BODY_PROPORTIONS = {
        "male": {"head_height": 85, "head_width": 65, "neck_height": 35, "neck_width": 45,
                 "shoulder_width": 220, "chest_width": 180, "waist_width": 150, "hip_width": 160,
                 "arm_length": 280, "arm_width": 35, "hand_length": 70, "hand_width": 35,
                 "leg_length": 420, "thigh_width": 65, "calf_width": 45, "foot_width": 45},
        "female": {"head_height": 80, "head_width": 60, "neck_height": 30, "neck_width": 38,
                   "shoulder_width": 180, "chest_width": 160, "waist_width": 120, "hip_width": 170,
                   "arm_length": 260, "arm_width": 28, "hand_length": 60, "hand_width": 28,
                   "leg_length": 400, "thigh_width": 60, "calf_width": 38, "foot_width": 38}
    }

    SKIN_TONES = {
        "light": {"base": (240, 223, 214), "highlight": (255, 245, 238), "shadow": (210, 190, 180)},
        "medium": {"base": (222, 195, 172), "highlight": (242, 220, 200), "shadow": (190, 165, 145)},
        "tan": {"base": (195, 158, 128), "highlight": (220, 185, 160), "shadow": (165, 130, 105)},
        "dark": {"base": (140, 100, 75), "highlight": (170, 130, 105), "shadow": (110, 75, 55)},
        "deep": {"base": (90, 60, 45), "highlight": (120, 85, 68), "shadow": (65, 42, 30)}
    }

    CLOTHING_ZONES = {
        "male": {"shirt": {"y_start": 0.165, "y_end": 0.44, "x_center": 0.5, "width_factor": 0.36},
                 "pants": {"y_start": 0.42, "y_end": 0.88, "x_center": 0.5, "width_factor": 0.26},
                 "jacket": {"y_start": 0.16, "y_end": 0.50, "x_center": 0.5, "width_factor": 0.40},
                 "shoes": {"y_start": 0.88, "y_end": 0.95, "x_center": 0.5, "width_factor": 0.22},
                 "tie": {"y_start": 0.175, "y_end": 0.40, "x_center": 0.5, "width_factor": 0.06},
                 "belt": {"y_start": 0.40, "y_end": 0.44, "x_center": 0.5, "width_factor": 0.20}},
        "female": {"shirt": {"y_start": 0.155, "y_end": 0.42, "x_center": 0.5, "width_factor": 0.32},
                   "pants": {"y_start": 0.40, "y_end": 0.86, "x_center": 0.5, "width_factor": 0.24},
                   "jacket": {"y_start": 0.15, "y_end": 0.48, "x_center": 0.5, "width_factor": 0.36},
                   "shoes": {"y_start": 0.86, "y_end": 0.93, "x_center": 0.5, "width_factor": 0.18},
                   "tie": {"y_start": 0.165, "y_end": 0.38, "x_center": 0.5, "width_factor": 0.05},
                   "belt": {"y_start": 0.38, "y_end": 0.42, "x_center": 0.5, "width_factor": 0.18}}
    }

    LAYER_ORDER = {"shoes": 0, "pants": 1, "shirt": 2, "belt": 3, "tie": 4, "jacket": 5}

    def __init__(self, gender="male", skin_tone="medium"):
        self.gender = gender.lower()
        self.skin_tone = skin_tone.lower()
        self._update_settings()

    def _update_settings(self):
        self.proportions = self.BODY_PROPORTIONS.get(self.gender, self.BODY_PROPORTIONS["male"])
        self.skin = self.SKIN_TONES.get(self.skin_tone, self.SKIN_TONES["medium"])
        self.zones = self.CLOTHING_ZONES.get(self.gender, self.CLOTHING_ZONES["male"])

    def create_mannequin(self):
        canvas = Image.new("RGBA", self.CANVAS_SIZE, (0, 0, 0, 0))
        w, h = self.CANVAS_SIZE
        cx = w // 2
        hy = int(h * 0.02)
        ny = hy + self.proportions["head_height"]
        sy = ny + self.proportions["neck_height"]
        wy = sy + 200
        hiy = wy + 60
        lsy = hiy + 60
        fy = lsy + self.proportions["leg_length"]
        self._draw_head(canvas, cx, hy)
        self._draw_neck(canvas, cx, ny)
        self._draw_torso(canvas, cx, sy, wy, hiy)
        self._draw_arms(canvas, cx, sy)
        self._draw_legs(canvas, cx, lsy, fy)
        return self._smooth(canvas)

    def _draw_head(self, c, cx, y):
        d = ImageDraw.Draw(c)
        hw, hh = self.proportions["head_width"], self.proportions["head_height"]
        d.ellipse([cx-hw//2, y, cx+hw//2, y+hh], fill=self.skin["base"]+(255,))
        hl = Image.new("RGBA", c.size, (0,0,0,0))
        ImageDraw.Draw(hl).ellipse([cx-hw//3, y+10, cx+hw//6, int(y+hh*0.6)], fill=self.skin["highlight"]+(60,))
        hl = hl.filter(ImageFilter.GaussianBlur(12))
        c.paste(Image.alpha_composite(Image.new("RGBA", c.size, (0,0,0,0)), hl), (0,0), hl)
        ey = y + int(hh * 0.38)
        es = int(hw * 0.22)
        d.ellipse([cx-es-6, ey, cx-es+6, ey+5], fill=self.skin["shadow"]+(30,))
        d.ellipse([cx+es-6, ey, cx+es+6, ey+5], fill=self.skin["shadow"]+(30,))
        d.line([cx, int(y+hh*0.55-3), cx+2, int(y+hh*0.55+10)], fill=self.skin["shadow"]+(20,), width=2)
        d.line([cx-10, int(y+hh*0.72), cx+10, int(y+hh*0.72)], fill=self.skin["shadow"]+(25,), width=1)

    def _draw_neck(self, c, cx, y):
        d = ImageDraw.Draw(c)
        nw, nh = self.proportions["neck_width"], self.proportions["neck_height"]
        d.polygon([(cx-nw//2+5, y), (cx+nw//2-5, y), (cx+nw//2+10, y+nh), (cx-nw//2-10, y+nh)], fill=self.skin["base"]+(255,))

    def _draw_torso(self, c, cx, sy, wy, hy):
        d = ImageDraw.Draw(c)
        sw = self.proportions["shoulder_width"]
        cw = self.proportions["chest_width"]
        ww = self.proportions["waist_width"]
        hw = self.proportions["hip_width"]
        pts = [(cx-sw//2, sy), (cx+sw//2, sy), (cx+cw//2, sy+80), (cx+ww//2, wy), (cx+hw//2, hy), (cx+hw//2-20, hy+70), (cx+20, hy+80), (cx, hy+85), (cx-20, hy+80), (cx-hw//2+20, hy+70), (cx-hw//2, hy), (cx-ww//2, wy), (cx-cw//2, sy+80)]
        d.polygon(pts, fill=self.skin["base"]+(255,))
        hl = Image.new("RGBA", c.size, (0,0,0,0))
        ImageDraw.Draw(hl).ellipse([cx-50, sy+30, cx+30, wy], fill=self.skin["highlight"]+(40,))
        hl = hl.filter(ImageFilter.GaussianBlur(25))
        c.paste(Image.alpha_composite(Image.new("RGBA", c.size, (0,0,0,0)), hl), (0,0), hl)

    def _draw_arms(self, c, cx, sy):
        d = ImageDraw.Draw(c)
        sw = self.proportions["shoulder_width"]
        al = self.proportions["arm_length"]
        aw = self.proportions["arm_width"]
        hw = self.proportions["hand_width"]
        hl = self.proportions["hand_length"]
        for s in ["left", "right"]:
            dr = -1 if s == "left" else 1
            ax = cx + dr * (sw//2 + 5)
            aty = sy + 10
            ey = sy + 10 + int(al * 0.45)
            wry = sy + 10 + al
            d.polygon([(ax-aw//2, aty), (ax+aw//2, aty), (ax+dr*15+int(aw//2*0.9), ey), (ax+dr*15-int(aw//2*0.9), ey)], fill=self.skin["base"]+(255,))
            fx = ax + dr * 15
            d.polygon([(fx-int(aw//2*0.85), ey-5), (fx+int(aw//2*0.85), ey-5), (fx+dr*5+int(aw//2*0.7), wry), (fx+dr*5-int(aw//2*0.7), wry)], fill=self.skin["base"]+(255,))
            hx = fx + dr * 5
            d.ellipse([hx-hw//2, wry-5, hx+hw//2, wry+hl-15], fill=self.skin["base"]+(255,))

    def _draw_legs(self, c, cx, lsy, fy):
        d = ImageDraw.Draw(c)
        tw = self.proportions["thigh_width"]
        cw = self.proportions["calf_width"]
        fw = self.proportions["foot_width"]
        ll = self.proportions["leg_length"]
        for s in ["left", "right"]:
            dr = -1 if s == "left" else 1
            lc = cx + dr * (20 + tw//2 - 15)
            ky = lsy + int(ll * 0.48)
            ay = fy - 20
            d.polygon([(lc-tw//2, lsy), (lc+tw//2, lsy), (lc+tw//2-8, ky), (lc-tw//2+8, ky)], fill=self.skin["base"]+(255,))
            d.polygon([(lc-tw//2+5, ky-5), (lc+tw//2-5, ky-5), (lc+cw//2, ay), (lc-cw//2, ay)], fill=self.skin["base"]+(255,))
            d.polygon([(lc-cw//2, ay-5), (lc+cw//2, ay-5), (lc+fw//2, fy), (lc-fw//2, fy)], fill=self.skin["base"]+(255,))

    def _smooth(self, c):
        r, g, b, a = c.split()
        a = a.filter(ImageFilter.GaussianBlur(1.5))
        return Image.merge("RGBA", (r.filter(ImageFilter.GaussianBlur(0.5)), g.filter(ImageFilter.GaussianBlur(0.5)), b.filter(ImageFilter.GaussianBlur(0.5)), a))

    def fit_clothing(self, clothing, clothing_type):
        ct = {"top": "shirt", "bottom": "pants", "trousers": "pants", "blazer": "jacket"}.get(clothing_type.lower(), clothing_type.lower())
        if ct not in self.zones:
            return clothing, (self.CANVAS_SIZE[0]//2 - clothing.width//2, 200)
        z = self.zones[ct]
        w, h = self.CANVAS_SIZE
        ys = int(h * z["y_start"])
        ye = int(h * z["y_end"])
        th = ye - ys
        tw = int(w * z["width_factor"])
        if clothing.mode != "RGBA":
            clothing = clothing.convert("RGBA")
        ow, oh = clothing.size
        asp = ow / oh
        if asp > (tw / th):
            nw, nh = tw, int(tw / asp)
        else:
            nh, nw = th, int(th * asp)
        clothing = clothing.resize((nw, nh), Image.Resampling.LANCZOS)
        clothing = self._add_depth(clothing)
        return clothing, (int(w * z["x_center"]) - clothing.width//2, ys + (th - clothing.height)//2)

    def _add_depth(self, clothing):
        if clothing.mode != "RGBA":
            clothing = clothing.convert("RGBA")
        w, h = clothing.size
        shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for x in range(w):
            fi = math.sin(x / w * math.pi * 3) * 0.5 + 0.5
            sa = int(15 * fi)
            for y in range(h):
                if clothing.getpixel((x, y))[3] > 50:
                    shadow.putpixel((x, y), (0, 0, 0, sa))
        shadow = shadow.filter(ImageFilter.GaussianBlur(6))
        return Image.alpha_composite(clothing, shadow)

    # Vertical stacking order (top → bottom) for flat-lay rendering
    FLATLAY_ORDER = ["jacket", "tie", "shirt", "belt", "pants", "shoes"]

    # Relative widths so items look proportional next to each other
    FLATLAY_WIDTH_FACTOR = {
        "jacket": 0.62,
        "shirt":  0.55,
        "tie":    0.10,
        "belt":   0.40,
        "pants":  0.42,
        "shoes":  0.38,
    }

    def render_outfit(self, clothing_items, background_color=(245, 245, 248)):
        """Flat-lay composition — clothing items stacked vertically, touching, no body."""
        return self.render_flatlay(clothing_items, background_color)

    def render_flatlay(self, clothing_items, background=(245, 245, 248)):
        canvas_w, canvas_h = self.CANVAS_SIZE
        bg = self._create_bg(background)

        if not clothing_items:
            return bg

        # Crop each item to its non-transparent bounding box, then scale to target width
        prepared = []
        for key in self.FLATLAY_ORDER:
            if key not in clothing_items:
                continue
            img = clothing_items[key]
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            bbox = img.getbbox()
            if bbox:
                img = img.crop(bbox)
            target_w = int(canvas_w * self.FLATLAY_WIDTH_FACTOR.get(key, 0.4))
            ratio = target_w / img.width
            new_size = (target_w, max(1, int(img.height * ratio)))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            prepared.append(img)

        total_h = sum(im.height for im in prepared)
        # Fit vertically into the canvas with a small top/bottom margin if needed
        max_h = int(canvas_h * 0.92)
        if total_h > max_h:
            scale = max_h / total_h
            prepared = [im.resize((max(1, int(im.width * scale)),
                                   max(1, int(im.height * scale))),
                                  Image.Resampling.LANCZOS) for im in prepared]
            total_h = sum(im.height for im in prepared)

        # Center the stack vertically and paste items touching each other
        y = (canvas_h - total_h) // 2
        for im in prepared:
            x = (canvas_w - im.width) // 2
            bg.paste(im, (x, y), im)
            y += im.height

        return bg

    def _create_bg(self, color):
        w, h = self.CANVAS_SIZE
        bg = Image.new("RGB", (w, h), color)
        d = ImageDraw.Draw(bg)
        for y in range(h):
            f = 1.0 - (y / h) * 0.08
            d.line([(0, y), (w, y)], fill=(int(min(255, color[0]*f)), int(min(255, color[1]*f)), int(min(255, color[2]*f))))
        return bg

    def _add_shadow(self, image):
        d = ImageDraw.Draw(image)
        w, h = image.size
        sy = h - 60
        for i in range(25):
            g = int(200 + (55 * (1 - i/25)))
            ew = 100 + i * 4
            d.ellipse([w//2 - ew, sy + i*1.5 - 8, w//2 + ew, sy + i*1.5 + 8], fill=(g, g, g))
        return image

    def get_image_bytes(self, image, format="PNG"):
        buf = io.BytesIO()
        image.save(buf, format=format, quality=95)
        buf.seek(0)
        return buf.getvalue()

    def set_gender(self, gender):
        self.gender = gender.lower()
        self._update_settings()

    def set_skin_tone(self, tone):
        self.skin_tone = tone.lower()
        self._update_settings()
