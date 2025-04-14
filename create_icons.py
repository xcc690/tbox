from PIL import Image, ImageDraw
import os
from math import sin, cos, radians

def create_icon(size, color, shape_func):
    """创建基本图标"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    shape_func(draw, size, color)
    return img

def create_settings_icon():
    """创建设置图标（齿轮）"""
    def draw_gear(draw, size, color):
        center = size // 2
        radius = size // 3
        # 绘制齿轮主体
        draw.ellipse((center - radius, center - radius, 
                     center + radius, center + radius), 
                    fill=color)
        # 绘制齿轮齿
        for i in range(8):
            angle = i * 45
            x1 = center + int(radius * 0.7 * cos(radians(angle)))
            y1 = center + int(radius * 0.7 * sin(radians(angle)))
            x2 = center + int(radius * 1.3 * cos(radians(angle)))
            y2 = center + int(radius * 1.3 * sin(radians(angle)))
            draw.line((x1, y1, x2, y2), fill=color, width=2)
    
    return create_icon(32, (100, 100, 100, 255), draw_gear)

def create_minimize_icon():
    """创建最小化图标（横线）"""
    def draw_line(draw, size, color):
        y = size // 2
        draw.line((size//4, y, size*3//4, y), fill=color, width=2)
    
    return create_icon(32, (100, 100, 100, 255), draw_line)

def create_maximize_icon():
    """创建最大化图标（方框）"""
    def draw_square(draw, size, color):
        margin = size // 4
        draw.rectangle((margin, margin, size-margin, size-margin), 
                      outline=color, width=2)
    
    return create_icon(32, (100, 100, 100, 255), draw_square)

def create_restore_icon():
    """创建还原图标（重叠的方框）"""
    def draw_overlap_squares(draw, size, color):
        margin = size // 4
        # 绘制大框
        draw.rectangle((margin, margin, size-margin, size-margin), 
                      outline=color, width=2)
        # 绘制小框
        small_margin = size // 3
        draw.rectangle((small_margin, small_margin, 
                       size-small_margin, size-small_margin), 
                      outline=color, width=2)
    
    return create_icon(32, (100, 100, 100, 255), draw_overlap_squares)

def create_close_icon():
    """创建关闭图标（X）"""
    def draw_x(draw, size, color):
        margin = size // 4
        # 绘制对角线
        draw.line((margin, margin, size-margin, size-margin), 
                 fill=color, width=2)
        draw.line((margin, size-margin, size-margin, margin), 
                 fill=color, width=2)
    
    return create_icon(32, (100, 100, 100, 255), draw_x)

def main():
    # 确保icons目录存在
    if not os.path.exists('icons'):
        os.makedirs('icons')
    
    # 创建并保存图标
    create_settings_icon().save('icons/settings.png')
    create_minimize_icon().save('icons/minimize.png')
    create_maximize_icon().save('icons/maximize.png')
    create_restore_icon().save('icons/restore.png')
    create_close_icon().save('icons/close.png')

if __name__ == '__main__':
    main() 