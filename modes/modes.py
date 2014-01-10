import random
import math
from .base import BaseMode
from .mixins import FixedColorMixin


class RandomFlashMode(FixedColorMixin, BaseMode):
    last = 0

    def calc_next_step(self):
        self.colors[self.last] = (0,0,0)
        self.last = random.randint(0,len(self.colors)-1)
        if self.fixed_color:
            self.colors[self.last] = self.fixed_color
        else:
            self.colors[self.last] = (
                random.randint(0,254),
                random.randint(0,254),
                random.randint(0,254)
            )


class FillUpMode(FixedColorMixin, BaseMode):
    last = 0
    pos = 0
    fill = 1
    color = (0, 0, 254)
    clear_last = 0

    def __init__(self, *args, **kwargs):
        super(FillUpMode, self).__init__(*args, **kwargs)
        self.last = self.led_count - 1

    def calc_next_step(self):
        if self.clear_last:
            self.colors[self.last] = (0,0,0)
        if self.fill:
            self.last -= 1
            self.colors[self.last] = self.fixed_color if self.fixed_color else self.color
            if self.last > self.pos:
                self.clear_last = 1
            else:
                self.last = self.led_count - 1
                self.pos += 1
                self.clear_last = 0
                if self.pos == self.led_count:
                    self.pos = 0
                    self.fill = 0
                    self.last = 0
                    self.clear_last = 1
        else:
            self.clear_last = 1
            self.last -= 1
            if self.last < 0:
                self.pos += 1
                self.last = self.pos
                if self.pos == self.led_count:
                    self.pos = 0
                    self.fill = 1
                    self.clear_last = 0
                    self.color = (0, 0, 0)
                    while self.color == (0, 0, 0):
                        self.color = (
                            random.randint(0, 1) * 254,
                            random.randint(0, 1) * 254,
                            random.randint(0, 1) * 254
                        )
            if not self.fill:
                self.colors[self.last] = self.fixed_color if self.fixed_color else self.color


class FlashMode(FixedColorMixin, BaseMode):
    on = 0
    color = (0, 0, 254)

    def calc_next_step(self):
        if self.on:
            self.on = 0
            for i in range(self.led_count):
                self.colors[i] = (0, 0, 0)
        else:
            self.on = 1
            for i in range(self.led_count):
                self.colors[i] = self.fixed_color if self.fixed_color else self.color


class PoliceMode(BaseMode):
    last = 0
    color_seq = [
        ((0, 0, 254), 10),
        ((0, 0, 0), 30),
        ((0, 0, 254), 10),
        ((0, 0, 0), 30),
        ((254, 254, 254), 10),
        ((254, 0, 0), 10),
        ((0, 0, 0), 30),
        ((254, 0, 0), 10),
        ((0, 0, 0), 30),
    ]

    def calc_next_step(self):
        for i in range(self.led_count):
            self.colors[i] = self.color_seq[self.last][0]
        self.fps = self.color_seq[self.last][1]
        self.last += 1
        if self.last >= len(self.color_seq):
            self.last = 0


class PoliceMode2(BaseMode):
    step = 0
    mid_left = 0
    max_steps = 4
    fps = 40
    mid_width = 20

    def calc_next_step(self):
        if self.step % 4 == 0:
            if self.mid_left:
                for i in range(self.led_count/2-self.mid_width/2, self.led_count/2):
                    self.colors[i] = (0, 0, 0)
                for i in range(self.led_count/2, self.led_count/2+self.mid_width/2):
                    self.colors[i] = (0, 0, 254)
                self.mid_left = 0
            else:
                for i in range(self.led_count/2-self.mid_width/2, self.led_count/2):
                    self.colors[i] = (254, 0, 0)
                for i in range(self.led_count/2, self.led_count/2+self.mid_width/2):
                    self.colors[i] = (0, 0, 0)
                self.mid_left = 1
        if self.step <= 1:
            for i in range(self.led_count/2-self.mid_width/2):
                self.colors[i] = (0, 0, 0)
            for i in range(self.led_count/2+self.mid_width/2, self.led_count):
                self.colors[i] = (0, 0, 0)
        else:
            for i in range(self.led_count/2-self.mid_width/2):
                self.colors[i] = (0, 0, 254)
            for i in range(self.led_count/2+self.mid_width/2, self.led_count):
                self.colors[i] = (254, 0, 0)

        self.step += 1
        if self.step >= self.max_steps:
            self.step = 0


class BinaryClockMode(BaseMode):
    fps = 4

    def calc_next_step(self):
        pass


class UnicolorAmbiTapeMode(BaseMode):
    fps = 60
    col = [0, 0, 0]
    fade_speed = 0.3
    scale_brightness = 0.5
    min_change = 1

    def __init__(self, *args, **kwargs):
        super(UnicolorAmbiTapeMode, self).__init__(*args, **kwargs)

    def calc_next_step(self):
        import gtk.gdk
        from PIL import Image
        from PIL import ImageStat
        self.w = gtk.gdk.get_default_root_window()
        self.sz = self.w.get_size()
        pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, self.sz[0], self.sz[1])
        pb = pb.get_from_drawable(self.w, self.w.get_colormap(), 0, 0, 0, 0, self.sz[0], self.sz[1])
        if not pb:
            print('Error: cannot capture screen')
            return False
        width, height = pb.get_width(), pb.get_height()
        img = Image.frombytes("RGB", (width, height), pb.get_pixels())
        s = ImageStat.Stat(img)
        avg = s.median
        for i in range(3):
            self.col[i] *= 1.0 - self.fade_speed
            c = int(max(avg[i]*self.scale_brightness, 10) * self.fade_speed)
            if not self.col[i] == avg[i] * self.scale_brightness and c < self.min_change:
                c = self.min_change
            self.col[i] += c
            self.col[i] = int(self.col[i])
        for ind in range(len(self.colors)):
            self.colors[ind] = (int(self.col[0]), int(self.col[1]), int(self.col[2]))


class MulticolorAmbiTapeMode(BaseMode):
    fps = 200
    current_colors = list()
    target_colors = list()
    fade_speed = 0.1
    scale_brightness = 0.5
    min_brightness = 0
    min_change = 1
    left_led_count = 14
    top_led_count = 32
    right_led_count = 14
    grid_height = 8
    grid_width = 16
    masks = list()
    frame_count = 10

    def __init__(self, *args, **kwargs):
        import gtk.gdk
        from PIL import Image
        super(MulticolorAmbiTapeMode, self).__init__(*args, **kwargs)
        for i in range(self.led_count):
            self.current_colors.append([0, 0, 0])
            self.target_colors.append([0, 0, 0])
        self.w = gtk.gdk.get_default_root_window()
        self.sz = self.w.get_size()
        box_width = int(self.sz[0] / self.grid_width)
        box_height = int(self.sz[1] / self.grid_height)
        h_overlay = Image.new('1', (box_width*2, box_height), color='white')
        v_overlay = Image.new('1', (box_width, box_height*2), color='white')
        for idx in range(self.grid_height):
            img = Image.new('1', self.sz, color='black')
            x = 0
            y = box_height * (self.grid_height - idx - 1)
            img.paste(
                h_overlay, box=(x, y)
            )
            self.masks.append(img)
        for idx in range(self.grid_width):
            img = Image.new('1', self.sz, color='black')
            x = (self.sz[0] / self.grid_width) * idx
            y = 0
            img.paste(
                v_overlay, box=(x, y)
            )
            self.masks.append(img)
        for idx in range(self.grid_height):
            img = Image.new('1', self.sz, color='black')
            x = self.sz[0] - (self.sz[0] / self.grid_width)
            y = (self.sz[1] / self.grid_height) * idx
            img.paste(
                h_overlay, box=(x, y)
            )
            self.masks.append(img)

    def calc_next_step(self):
        self.frame_count += 1
        if self.frame_count >= 10:
            self.frame_count = 0
            # capture screenshot
            import gtk.gdk
            from PIL import Image
            from PIL import ImageStat
            pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, self.sz[0], self.sz[1])
            pb = pb.get_from_drawable(self.w, self.w.get_colormap(), 0, 0, 0, 0, self.sz[0], self.sz[1])
            if not pb:
                print('Error: cannot capture screen')
                return False
            width, height = pb.get_width(), pb.get_height()
            img = Image.frombytes("RGB", (width, height), pb.get_pixels())
            for idx in range(self.grid_height * 2 + self.grid_width):
                s = ImageStat.Stat(img, self.masks[idx])
                self.target_colors[idx] = s.median

        def next_fade_step(block):
            try:
                for i in range(3):
                    self.current_colors[block][i] *= 1.0 - self.fade_speed
                    c = max(self.target_colors[block][i] * self.scale_brightness, self.min_brightness) * self.fade_speed
                    # if not self.current_colors[block][i] == self.target_colors[block][i] * self.scale_brightness and \
                    #         c < self.min_change:
                    #     c = self.min_change
                    # if self.current_colors[block][i] > self.target_colors[block][i] * self.scale_brightness and \
                    #         c > self.min_change * -1:
                    #     c = -1
                    self.current_colors[block][i] += c
                    self.current_colors[block][i] = self.current_colors[block][i]
            except IndexError:
                pass

                # left
        leds_per_box = int(math.ceil(self.left_led_count / float(self.grid_height)))
        for idx in range(self.grid_height):
            next_fade_step(idx)
            for led in range(leds_per_box):
                self.colors[idx * leds_per_box + led] = tuple([
                    int(self.current_colors[idx][0]),
                    int(self.current_colors[idx][1]),
                    int(self.current_colors[idx][2]),
                ])

        # top
        leds_per_box = int(math.ceil(self.top_led_count / float(self.grid_width)))
        led_offset = self.left_led_count
        box_offset = self.grid_height
        for idx in range(self.grid_width):
            next_fade_step(idx + box_offset)
            for led in range(leds_per_box):
                self.colors[led_offset + idx * leds_per_box + led] = tuple([
                    int(self.current_colors[idx + box_offset][0]),
                    int(self.current_colors[idx + box_offset][1]),
                    int(self.current_colors[idx + box_offset][2]),
                ])

        # right
        leds_per_box = int(math.ceil(self.right_led_count / float(self.grid_height)))
        led_offset = self.left_led_count + self.top_led_count
        box_offset = self.grid_height + self.grid_width
        for idx in range(self.grid_height):
            next_fade_step(idx + box_offset)
            for led in range(leds_per_box):
                try:
                    self.colors[led_offset + idx * leds_per_box + led] = tuple([
                        int(self.current_colors[idx + box_offset][0]),
                        int(self.current_colors[idx + box_offset][1]),
                        int(self.current_colors[idx + box_offset][2]),
                    ])
                except IndexError:
                    pass