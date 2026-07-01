import os, shutil, time, subprocess,ctypes
from collections import Counter
import json, re
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from datetime import datetime

try:
    from pymediainfo import MediaInfo
except ImportError:
    MediaInfo = None

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    Image = None
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

# =====================全局常量【锁定】=====================
DEFAULT_CONFIG_NAME = "zen_config.ini"
ZEN_THEME = {
    "name":"默认配色",# 配色名字
    "base_theme": "vista",  # 这里用 vista
    "bg_main": "#f0f0f0",  # 窗口/控件 背景
    "fg_main": "#000000",  # 文字颜色
    "bg_field": "#ffffff",  # 输入框/列表背景
    "border": "#7f9db9",  # 控件边框
    "select": "#3399ff",  # 选中高亮
    "trough": "#e6e6e6",  # 进度条凹槽
    "bar": "#3399ff",  # 进度条填充
    "arrow": "#000000",  # 下拉箭头
    "hover": "#e5f3ff",  # 按钮/控件 hover
}
ZEN_FONT=["Microsoft YaHei",11]
ZEN_FONT_S=["Microsoft YaHei",11]
VIDEO_FORMATS = (".mp4", ".mkv", ".avi", ".mov", ".flv", ".rmvb", ".wmv")
AUDIO_FORMATS = (".mp3", ".wav", ".flac", ".ape", ".ogg")
IMAGE_FORMATS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic", ".raw", ".webp")
ZIP_FORMATS = (".zip", ".rar", ".7z")
OTHER_DEFAULT_SUFFIX = ".doc;.docx;.pdf;.txt;.xls;.xlsx"
ADS_SUFFIX = ":zen_mv_data"
DEFAULT_MAX_ROW = 10
UI_MAIN_BT_PADX = 1
DEFAULT_TAG_MAIN = [
    # 视频影视类
    "动作", "喜剧", "爱情", "悬疑", "动画", "舞蹈", "科幻", "恐怖",
    # 图片图像类
    "风景", "人像", "壁纸", "原画", "写真",
    # 音频音效类
    "配乐", "音效","人声", "纯音", "伴奏",
    # 文档文稿类
    "教程", "素材", "报告", "小说",
]
DEFAULT_TAG_EXTRA = ["国产", "港台", "日韩", "欧美","学习","聚会","工作","旅行","抖音","下载","自制","收藏", "分享","存档"]
HOTKEY_TAG_MAIN=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
        "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]

HOTKEY_TAG_EXTRA=["q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
        "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'",
        "z", "x", "c", "v", "b", "n", "m"]


# =====================版本信息备忘【锁定】=====================
MEDIA_MANAGER_TITLE = "媒体文件分类管理工具"
MEDIA_MANAGER_VERSON = "v2.2 202606"
MEDIA_MANAGER_AUTHOR = "zen(lhywbe@mail.com)&doubao"
MEDIA_MANAGER_LOG = """
远期计划TODO:
1、【202607】全面重构代码，整合重复代码，拆分可复用组件，提高代码健壮性。
2、【202607】增加重复、相似照片、视频的自动标记
3、【202608】接入本地AI实现照片、视频的自动分类标签标记
4、【看心情】增加http服务器，提供远程html查看列表和局域网远程播放功能
5、【看心情】增加linux和android的适配


V2.2.1 更新备忘
1、修复逻辑bug
2、重构zen_toast、把tagcheck的refresh、toggle合二为一重构了
3、优化windwos的DPI处理，解决系统缩放导致的文字模糊
4、右侧打分、内容、附加分类右键点击都会调整筛选的条件，更方便使用
5、增加了ads标签里date的属性，存储文件创建时间，重写scan_media
6、分类标签增加了sep行，自动换列，显示优化
7、去除掉兼容旧版本属性标签的版本代码，优化自动创建config的bug
8、打包exe
9、大容量媒体文件识别较慢，优化仅识别视频头，加快效率

V2.2 优化使用版本:代码量约2500。
1.重新划分快捷键：F键+数字键控制主标签，字母键控制附加标签，按键分工更清晰（v2.2.0）
2.适配单手键盘操作：上下键切换文件、±键打分、回车键打开文件；精简界面下左右键可控制播放器进退（v2.2.0）
3.支持根据白天黑夜自动切换深浅色模式；自制弹窗提示框，解决原生弹窗不兼容深色模式的问题（v2.2.0）
4.自动清除文件只读属性，避免文件权限问题导致无法修改标签（v2.2.0）
5.新增文件锁定标签，锁定后的文件无法修改评分和分类，防止误操作改（v2.2.0）


V2.1 功能迭代版本：代码量2000。
1.增加5组快捷标签、5组快捷移动文件夹功能，操作前增加二次确认；所有功能都支持单个文件和批量文件处理（v2.1.0）
2.支持标签数据导出、备份和恢复，方便跨硬盘、跨电脑迁移标签数据（v2.1.0）
3.主界面直接增加文件重命名框和按钮，方便操作（v2.1.1）
4.统计标签使用次数，可以检测无效和游离标签（v2.1.2）
5.支持按清晰度、评分、分类组合筛选文件，新增全局快捷键操作（v2.1.3）
6.添加上一个/下一个素材切换按钮，可设置切换后自动打开文件，适合单手批量处理文件（v2.1.5）
7.支持手动切换浅色、深色两种显示模式（v2.1.6）
8.可以单独开启或关闭某一个扫描文件夹，不用删除目录（v2.1.7）
9.增加精简模式，小窗口置顶浮在播放器上面，快速切换、打分（v2.1.8）
10.支持自定义软件字体、配色；新增极简置顶透明小界面；右键文件可直接修改标签（v2.1.9）

V2.0 重构版本：重写软件底层代码，优化运行速度，代码量接近900行。
1.把大部分文件数据加载到内存运行，减少频繁读取硬盘，提升软件运行速度（v2.0.0）
2.重新设计软件主界面，支持保存自己的界面配置，一键切换配置（v2.0.0）
3.支持多套配置快速切换，可分别管理不同的素材文件夹和标签分组（v2.0.0）

V1.0 初代版本：完成软件基础功能开发，实现素材管理、标签分类、多格式文件支持，代码量约400行
1.完成软件基础框架开发，支持主流视频识别，可添加素材目录、手动刷新文件列表，自带题材、演员、评分、备注四类标签（v1.0.0）
2.改用NTFS-ADS数据流保存标签，不改动原文件，同时增加多条件文件筛选功能（v1.1.0）
3.支持按评分、标签批量修改文件名，也可以一键恢复文件原始名称（v1.2.0）
4.增加标签使用统计面板，支持直接编辑标签，主界面布局可以自由调整（v1.3.0）
5.软件不再只支持视频，新增图片、音频、压缩包、文档等文件支持；可批量添加和删除扫描文件夹（v1.4.0）
6.修改标签格式，分为主标签和附加标签，旧版本所有标签数据可以直接迁移使用（v1.5.0）
7.新增独立设置页面，统一存放软件所有配置项（v1.6.0）

"""
MEDIA_MANAGER_INFO = """
1、zen-file-sorter 是一款轻量化本地媒体文件分类管理工具，能方便完成文件筛选、素材归类、星级打分、批量整理、文件转移等日常整理工作。
2、该小工具无联网、无捆绑、无后台，同时搭配单手操作、全局快捷键、置顶小窗口等快捷操作。
3、设计初衷：换手机剩下的大量视频照片、微信文件、抖音无水印短视频以及多年下载的电影，在电脑里散乱无分类需要整理，没找到合适的软件，所以花了点时间自制了这个工具。依托NTFS分区自带的ADS备用数据流储存全部标签与评分数据，标签信息直接挂载在文件本体上，不会生成额外的配置文件，同时也不会修改文件内容和改动文件原始修改时间，最大程度保留原文件原始状态。
4、项目完全开源免费，欢迎大家点Star收藏，提交Issue反馈问题、提交PR参与代码共建：https://github.com/lhyweb/zen-file-sorter 。
5、使用过程中遇到bug或有功能建议，请加入QQ群：463960874交流。
"""
# =====================全局函数【锁定】=====================
# 清晰度：取画面短边判定，横竖屏通用【V2.1修订】
DEF_ALL = ["全部", "8K", "6K", "4K", "2K", "1080P", "720P", "SD", "LD", "未知"]
def get_def_by_height(short_px):
    if short_px >= 4320:
        return "8K"
    elif 3240 <= short_px < 4320:
        return "6K"
    elif 2160 <= short_px < 3240:
        return "4K"
    elif 1440 <= short_px < 2160:
        return "2K"
    elif 1080 <= short_px <= 1440:
        return "1080P"
    elif 720 < short_px <= 1080:
        return "720P"
    elif 480 < short_px <= 720:
        return "SD"
    else:
        return "LD"


def cycle_theme():
    """极简：循环切换系统自带主题 + 应用全局字体"""
    # 拿到当前主题索引
    style = ttk.Style()
    theme_list = ["classic", "clam", "alt", "default"]
    if style.theme_use() == "vista":
        ZEN_THEME["base_theme"] = "alt"
    else:
        ZEN_THEME["base_theme"] = theme_list[
            (theme_list.index(style.theme_use()) + 1) % len(theme_list)
        ]
    style.theme_use(ZEN_THEME["base_theme"])
    ZEN_THEME["base_theme"] = style.theme_use()
    ZEN_THEME["bg_main"] = style.lookup("TFrame", "background")
    ZEN_THEME["fg_main"] = style.lookup("TLabel", "foreground")
    ZEN_THEME["bg_field"] = style.lookup("TEntry", "fieldbackground")
    ZEN_THEME["border"] = style.lookup("TCombobox", "bordercolor")
    ZEN_THEME["select"] = style.lookup("Treeview", "background", ("selected",))
    ZEN_THEME["trough"] = style.lookup("TScrollbar", "troughcolor")
    ZEN_THEME["bar"] = style.lookup("TScrollbar", "background")
    ZEN_THEME["arrow"] = style.lookup("TCombobox", "arrowcolor")
    ZEN_THEME["hover"] = style.lookup("TButton", "background", ("active",))

    # 应用 ZEN_THEME 里的全局字体
    font_size_adjust()


def font_size_adjust(step=0,mode=""):
    if step>0:
        if ZEN_FONT[1]>15:return
        elif ZEN_FONT_S[1]>15:return
    elif step<0:
        if ZEN_FONT[1]<8:return
        elif ZEN_FONT_S[1]<8:return

    if mode=="BOTH":
        ZEN_FONT_S[1]+= step
        ZEN_FONT[1]+= step
    elif mode=="RESET":
        ZEN_FONT_S[1] = 10
        ZEN_FONT[1] = 11
    elif mode=="A":
        ZEN_FONT[1]+= step
    elif mode=="T":
        ZEN_FONT_S[1]+= step
    else:
        return
    if mode:
        zen_toast(f"正常字体：{ZEN_FONT[1]}号\n列表字体：{ZEN_FONT_S[1]}号\n弹窗字体：{ZEN_FONT[1]+6}号")
    root.option_add("*Font", ZEN_FONT)
    # root.option_add("*TCombobox*Listbox.font", ZEN_FONT)
    style = ttk.Style()
    widgets_n = [
        ".",
        "TButton",
        "TCheckbutton",
        "TRadiobutton",
        "TLabel",
        "TEntry",
        "TCombobox",
        "TSpinbox",
        "TScale",
        "TFrame",
        "TLabelFrame",
        "TScrollbar",
    ]
    for widget in widgets_n:
        style.configure(widget, font=ZEN_FONT)
    widgets_s = [
        "Treeview.Heading",
        "Treeview",
    ]
    for widget in widgets_s:
        style.configure(widget, font=ZEN_FONT_S)


def cycle_color():

    # ===================== 主题方案 =====================
    theme_presets = [
    {"name":"复古茶棕","bg_main":"#f3ede0","fg_main":"#4b3f2e","bg_field":"#faf5eb","border":"#c9b99e","select":"#a67c52","trough":"#e9dfcc","bar":"#a67c52","arrow":"#705e43","hover":"#e8dcc5"},
    {"name":"基础浅灰","bg_main":"#f7f8fa","fg_main":"#222222","bg_field":"#ffffff","border":"#d2d6dc","select":"#2574cc","trough":"#e5e5e5","bar":"#2574cc","arrow":"#333333","hover":"#e0e0e0"},
    {"name":"深蓝灰","bg_main":"#292c33","fg_main":"#e9ecef","bg_field":"#353942","border":"#4b5059","select":"#365b86","trough":"#40444b","bar":"#4a8fdb","arrow":"#cccccc","hover":"#444444"},
    {"name":"VS经典深色","bg_main":"#1e1e1e","fg_main":"#d4d4d4","bg_field":"#252526","border":"#3e3e42","select":"#094771","trough":"#3c3c3c","bar":"#007acc","arrow":"#cccccc","hover":"#3a3a3a"},
    {"name":"极客深色","bg_main":"#24272e","fg_main":"#e2e8f0","bg_field":"#2f333b","border":"#404652","select":"#235487","trough":"#373c46","bar":"#3182ce","arrow":"#cccccc","hover":"#3d424b"},
    {"name":"马卡龙浅紫","bg_main":"#f8f5fc","fg_main":"#3c314e","bg_field":"#ffffff","border":"#cbbde2","select":"#927bcc","trough":"#efeaf7","bar":"#927bcc","arrow":"#6b5b87","hover":"#ede4f7"},
   {"name":"深海冷调","bg_main":"#f2f7fa","fg_main":"#1f364d","bg_field":"#ffffff","border":"#9cb8cc","select":"#1890ff","trough":"#e4edf3","bar":"#1890ff","arrow":"#406482","hover":"#dcecf7"},
    {"name":"暖调日系米白","bg_main":"#faf7f0","fg_main":"#3a3731","bg_field":"#fffdf8","border":"#d9d2c3","select":"#c7a87e","trough":"#f0ebe0","bar":"#c7a87e","arrow":"#6e6655","hover":"#f5efe0"},
    {"name":"暗夜青灰","bg_main":"#24292e","fg_main":"#d1d9e0","bg_field":"#2f363d","border":"#444c56","select":"#4ea3ff","trough":"#373e47","bar":"#4ea3ff","arrow":"#8b98a4","hover":"#303841"},
    {"name":"高对比橙白","bg_main":"#f9f9f9","fg_main":"#1a1a1a","bg_field":"#ffffff","border":"#b0b0b0","select":"#ff7d00","trough":"#eaeaea","bar":"#ff7d00","arrow":"#333333","hover":"#fff0e0"},
    {"name":"轻奢烟灰","bg_main":"#eef0f2","fg_main":"#2c3137","bg_field":"#f8f9fa","border":"#a9b0b8","select":"#59718a","trough":"#e0e3e7","bar":"#59718a","arrow":"#474f59","hover":"#e2e6eb"},
    {"name":"浆果红棕","bg_main":"#f7f2f2","fg_main":"#482c2c","bg_field":"#fdf8f8","border":"#cba3a3","select":"#b74c4c","trough":"#ede4e4","bar":"#b74c4c","arrow":"#7a4f4f","hover":"#f3e8e8"}
]
    style = ttk.Style()
        # 初始化主题索引
    if not hasattr(cycle_color, "theme_idx"):
        cycle_color.theme_idx = 6
        cycle_color.listbox_items = []
        cycle_color.text_items = []
    
    # 切换底层主题
    if style.theme_use() == "vista":ZEN_THEME["base_theme"] = "alt"
    style.theme_use(ZEN_THEME["base_theme"])
    
    cycle_color.theme_idx = (cycle_color.theme_idx + 1) % len(theme_presets)
    current = theme_presets[cycle_color.theme_idx]
    # zen_toast(root,ZEN_THEME["base_theme"]+current["name"],3000)
    # 同步到全局 ZEN_THEME
    for k, v in current.items():
        ZEN_THEME[k] = v

    # ===================== 统一生成字体 =====================

    # 简化变量
    bg_main = ZEN_THEME["bg_main"]
    fg_main = ZEN_THEME["fg_main"]
    bg_field = ZEN_THEME["bg_field"]
    border = ZEN_THEME["border"]
    select = ZEN_THEME["select"]
    trough = ZEN_THEME["trough"]
    bar = ZEN_THEME["bar"]
    arrow = ZEN_THEME["arrow"]
    hover = ZEN_THEME["hover"]
    base_theme = ZEN_THEME["base_theme"]

    # ===================== 全局样式 =====================
    root.option_add("*Font", ZEN_FONT)
    root.config(bg=bg_main)

    style.configure(
        ".",
        background=bg_main,
        foreground=fg_main,
        bordercolor=border,
        focusthickness=0,
        focuscolor="none",
    )

    style.configure("TFrame", background=bg_main)
    style.configure("TLabel", background=bg_main, foreground=fg_main)
    style.configure(
        "TEntry",
        fieldbackground=bg_field,
        foreground=fg_main,
        bordercolor=border,
    )

    # 按钮
    style.configure(
        "TButton",
        background=bg_main,
        foreground=fg_main,
        relief="flat",
        borderwidth=0,
        padding=(8, 3),
    )
    style.map(
        "TButton",
        background=[("active", hover)],
        foreground=[("active", "white" if bg_main != "#f7f8fa" else "black")],
    )

    # 复选框 / 单选框
    style.configure("TCheckbutton", background=bg_main, foreground=fg_main)
    style.map(
        "TCheckbutton",
        background=[("active", hover)],
        indicatorcolor=[("selected", select), ("!selected", border)],
    )
    style.configure("TRadiobutton", background=bg_main, foreground=fg_main)
    style.map(
        "TRadiobutton",
        background=[("active", hover)],
        indicatorcolor=[("selected", select), ("!selected", border)],
    )

    # 滚动条
    style.configure(
        "Vertical.TScrollbar",
        background=select,
        troughcolor=bg_field,
        width=8,
        arrowsize=0,
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=select,
        troughcolor=bg_field,
        height=8,
        arrowsize=0,
    )

    # 下拉框
    style.configure(
        "TCombobox",
        fieldbackground=bg_field,
        background=bg_field,
        foreground=fg_main,
        arrowcolor=arrow,
        bordercolor=border,
        lightcolor=bg_field,
        darkcolor=border,
    )
    style.map(
        "TCombobox",
        selectbackground=[("focus", select)],
        selectforeground=[("focus", "white")],
        fieldbackground=[("readonly", bg_field), ("focus", bg_field)],
    )
    root.option_add("*TCombobox*Listbox.background", bg_field)
    root.option_add("*TCombobox*Listbox.foreground", fg_main)
    root.option_add("*TCombobox*Listbox.selectBackground", select)
    root.option_add("*TCombobox*Listbox.selectForeground", "white")

    # 进度条 / 滑动条
    style.configure(
        "Horizontal.TProgressbar",
        troughcolor=trough,
        background=bar,
        bordercolor=border,
    )
    style.configure(
        "Horizontal.TScale",
        background=bg_main,
        troughcolor=bg_field,
        slidercolor=select,
        bordercolor=border,
        lightcolor=select,
        darkcolor=select,
    )

    # 表格
    style.configure(
        "Treeview",
        background=bg_main,
        foreground=fg_main,
        fieldbackground=bg_main,
        bordercolor=border,
        rowheight=24,
    )
    style.configure(
        "Treeview.Heading",
        background=bg_field,
        foreground=fg_main,
        bordercolor=border,
        relief="flat",
    )
    style.map(
        "Treeview.Heading",
        background=[("active", bg_field)],
        foreground=[("active", bg_main)],
    )
    style.map(
        "Treeview",
        background=[("selected", select)],
        foreground=[("selected", "white")],
    )

    # ===================== 1. 应用样式并添加Listbox =====================
    def apply_listbox(lb: tk.Listbox):
        lb.config(
            bg=bg_field,
            fg=fg_main,
            selectbackground=select,
            selectforeground="white",
            font=ZEN_FONT,
        )
        if lb not in cycle_color.listbox_items:
            cycle_color.listbox_items.append(lb)

    # ===================== 2. 应用样式并添加Text =====================
    def apply_text(txt: tk.Text):
        txt.config(bg=bg_field, fg=fg_main, insertbackground=fg_main, font=ZEN_FONT)
        if txt not in cycle_color.text_items:
            cycle_color.text_items.append(txt)

    # ===================== 3. 统一刷新（完全复用上面两个函数） =====================
    def refresh_widgets():
        # 刷新 Listbox
        for i in reversed(range(len(cycle_color.listbox_items))):
            try:
                apply_listbox(cycle_color.listbox_items[i])
            except Exception:
                del cycle_color.listbox_items[i]

        # 刷新 Text
        for i in reversed(range(len(cycle_color.text_items))):
            try:
                apply_text(cycle_color.text_items[i])
            except Exception:
                del cycle_color.text_items[i]

    # 暴露函数给外部使用
    cycle_color.apply_listbox = apply_listbox
    cycle_color.apply_text = apply_text
    cycle_color.refresh_widgets = refresh_widgets
    # 切换主题后自动刷新
    refresh_widgets()
    font_size_adjust()
    


def set_win_title_color(win):

    DWMWA_CAPTION_COLOR = 35
    DWMWA_TEXT_COLOR = 36

    # 十六进制 #RRGGBB 转 Windows BGR 整型
    def hex2bgr(hex_color):
        h = hex_color.lstrip("#")
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        return b | (g << 8) | (r << 16)

    hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
    # 标题栏背景
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd, DWMWA_CAPTION_COLOR,
        ctypes.byref(ctypes.c_int(hex2bgr(ZEN_THEME["bg_main"]))), 4
    )
    # 标题文字
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd, DWMWA_TEXT_COLOR,
        ctypes.byref(ctypes.c_int(hex2bgr(ZEN_THEME["fg_main"]))), 4
    )



# ===================== 自定义主题弹窗 =====================
def zen_msgbox(title,text):
    win=_zen_msg_pre(title,text)
    # 按钮
    ttk.Button(win, text="确定", command=win.destroy).pack(pady=(0, 18))
    win.bind("<Return>", lambda e: win.destroy())
    _zen_msg_after(win)
def zen_toast(text,duration=2000):
    transp = "#010101"
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.attributes("-transparentcolor", transp)
    toast.config(bg=transp)


    # 算出亮度，直接判断输出颜色
    h = ZEN_THEME["bg_main"].lstrip("#")
    bright = (int(h[0:2],16)*299 + int(h[2:4],16)*587 + int(h[4:6],16)*114) / 1000
    toast_fg = "#ff7733" if bright<130 else "#25033B"


    # 文本标签，自动换行、自适应宽高
    lab = ttk.Label(toast,text=text,background=transp,foreground=toast_fg,font=[ZEN_FONT[0],ZEN_FONT[1]+6,"bold"],wraplength=350)
    lab.pack(padx=25, pady=20)
    # 按钮
    ttk.Button(toast, text="确定", command=toast.destroy).pack(pady=(0, 18))
    toast.bind("<Return>", lambda e: toast.destroy())
    _zen_msg_after(toast,duration)

def _zen_msg_pre(title=None,text=None):
    win = tk.Toplevel(root)
    if title:win.title(title)
    win.configure(bg=ZEN_THEME["bg_main"])
    win.transient(root)
    win.grab_set()
    if text:ttk.Label(win,text=text,foreground=ZEN_THEME["fg_main"],font=ZEN_FONT,wraplength=600).pack(padx=50, pady=60)
    return win
def _zen_msg_after(win,duration=0):
    win.update_idletasks()
    # 窗口自身宽、高
    w = win.winfo_width()
    h = win.winfo_height()
    # 屏幕宽、高
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w - w) // 2
    y = (screen_h - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")
    win.bind("<Escape>", lambda e: win.destroy())
    if duration:
        win.after(duration, lambda: win.destroy())
    else:
        win.focus()
        root.wait_window(win)
        
def zen_askyesno(title, text):
    """是/否 确认框，返回 True(是) / False(否)"""
    win = _zen_msg_pre(title,text)
    result = [False]
    # 按钮容器
    btn_frame = ttk.Frame(win)
    btn_frame.pack(pady=(0, 18))
    def on_yes():
        result[0] = True
        win.destroy()
    def on_no():
        result[0] = False
        win.destroy()
    # 是、否按钮
    ttk.Button(btn_frame, text="是", command=on_yes).grid(row=0, column=0, padx=15)
    ttk.Button(btn_frame, text="否", command=on_no).grid(row=0, column=1, padx=15)
    # 回车默认触发「是」
    win.bind("<Return>", lambda e: on_yes())
    win.focus_force()
    # 自适应大小、禁止缩放
    _zen_msg_after(win)
    return result[0]
def zen_askstring(title, text, default=""):
    win = _zen_msg_pre(title,text)
    # 存储结果
    result = [None]
    # 输入框
    entry_var = tk.StringVar(value=default)
    entry = ttk.Entry(win, textvariable=entry_var, font=ZEN_FONT)
    entry.pack(fill="x", padx=25)
    # 按钮容器
    btn_frame = ttk.Frame(win)
    btn_frame.pack(pady=(15, 18))
    def on_ok():
        result[0] = entry_var.get()
        win.destroy()
    def on_cancel():
        result[0] = None
        win.destroy()
    ttk.Button(btn_frame, text="确定", command=on_ok).grid(row=0, column=0, padx=15)
    ttk.Button(btn_frame, text="取消", command=on_cancel).grid(row=0, column=1, padx=15)
    # 快捷键：回车确认，ESC取消
    win.bind("<Return>", lambda e: on_ok())
    # 输入框优先聚焦
    entry.focus()
    _zen_msg_after(win)
    return result[0]

# =====================弹窗类【锁定】=====================


class TagsManagerUI(tk.Toplevel):
    def __init__(self, master_root, app_obj, win_title, mode):
        super().__init__(master=master_root)
        self.root = master_root
        self.app = app_obj
        self.title(win_title)
        self.geometry("700x760")
        self.transient(self.root)
        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)
        self.grab_set()
        self.txt = tk.Text(self, padx=10, pady=10)
        self.txt2 = tk.Text(self, padx=10, pady=10)
        cycle_color.apply_text(self.txt)
        cycle_color.apply_text(self.txt2)
        self.txt.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        self.txt2.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")
        if mode == "EDIT":
            self.protocol("WM_DELETE_WINDOW", self.save_and_close)
            self.show()
        else:

            self.protocol("WM_DELETE_WINDOW", self.destroy)
            self.calc_show()


    def show(self):
        tagm_list = self.app.config_data.get("tag_main", [])
        self.txt.insert("1.0", "\n".join(tagm_list))
        tage_list = self.app.config_data.get("tag_extra", [])
        self.txt2.insert("1.0", "\n".join(tage_list))

    def save_and_close(self):
        content = self.txt.get("1.0", tk.END).strip()
        self.app.config_data["tag_main"] = [
            x.strip() for x in content.splitlines() if x.strip()
        ]
        content2 = self.txt2.get("1.0", tk.END).strip()
        self.app.config_data["tag_extra"] = [
            x.strip() for x in content2.splitlines() if x.strip()
        ]
        self.app.save_config()
        self.app.rebuild_all_checkbox()
        self.app.refresh_tags_list()
        self.destroy()

    def calc_show(self):
        tagm_count_dict = {item: 0 for item in self.app.config_data.get("tag_main", [])}
        tage_count_dict = {
            item: 0 for item in self.app.config_data.get("tag_extra", [])
        }
        tagm_free_count_dict = Counter()
        tage_free_count_dict = Counter()
        for d in self.app.media_dict.values():
            for t in d["tag_main"]:
                if t in tagm_count_dict:
                    tagm_count_dict[t] += 1
                else:
                    tagm_free_count_dict[t] += 1
            for a in d["tag_extra"]:
                if a in tage_count_dict:
                    tage_count_dict[a] += 1
                else:
                    tage_free_count_dict[a] += 1
        self.txt.insert("1.0", "====内容分类统计====\n")
        for i in tagm_count_dict:
            self.txt.insert(tk.END, f"{tagm_count_dict[i]}	{i}\n")
        if tagm_free_count_dict:
            self.txt.insert(tk.END, "\n====游离标签====\n")
            for k, v in tagm_free_count_dict.items():
                self.txt.insert(tk.END, f"{v}	{k}\n")
        self.txt2.insert(tk.END, "====附加分类统计====\n")
        for i in tage_count_dict:
            self.txt2.insert(tk.END, f"{tage_count_dict[i]}	{i}\n")
        if tage_free_count_dict:
            self.txt2.insert(tk.END, "\n====游离标签====\n")
            for k, v in tage_free_count_dict.items():
                self.txt2.insert(tk.END, f"{v}	{k}\n")


class AboutUI(tk.Toplevel):
    def __init__(self, master_root):
        super().__init__(master=master_root)
        self.root = master_root
        self.title("关于本软件")
        self.geometry("720x600")
        self.resizable(False, False)
        self.transient(self.root)
        self.grab_set()
        txt = tk.Text(self, font=("微软雅黑", 10))
        cycle_color.apply_text(txt)
        txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        txt.insert(
            "1.0",
            MEDIA_MANAGER_TITLE
            + MEDIA_MANAGER_VERSON
            + MEDIA_MANAGER_INFO
            + MEDIA_MANAGER_LOG,
        )
        txt.config(state=tk.DISABLED)


class SettingUI(tk.Toplevel):
    def __init__(self, master_root, app_obj):
        super().__init__(master=master_root)
        self.root = master_root
        self.app = app_obj
        self.title("软件设置")
        self.geometry("720x460")
        self.minsize(680, 420)
        self.transient(self.root)
        self.grab_set()
        self.var_video = tk.BooleanVar()
        self.var_audio = tk.BooleanVar()
        self.var_img = tk.BooleanVar()
        self.var_zip = tk.BooleanVar()
        self.var_other = tk.BooleanVar()
        self.str_other_suffix = tk.StringVar()
        self.str_max_row = tk.StringVar()
        self.prefix_yes = "✓ "
        self.prefix_no = "☐ "
        self.build_ui()
        self.load_data()
        self.update_idletasks()
        # 自动适配内容尺寸，去掉固定宽高限制
        self.geometry("")
    def open_edit_tag(self):
        TagsManagerUI(self.root, self.app, "编辑分类标签：按行区分，直接修改好退出即保存生效", "EDIT")
    def open_calc_tag(self):
        TagsManagerUI(self.root, self.app, "统计分类标签", "CALC")
    def open_config_sel(self):
        ConfigSelectUI(self.root, self.app)

    def force_refresh_all_file(self):
        msg = (
            "确定要执行【重新扫描并刷新文件】吗？\n\n"
            "• 本功能会重新扫描目录内所有文件\n"
            "• 原有评分、分类标签均会保留，不会丢失\n"
            "• 视频、图片将通过 pymediainfo、Pillow 重新解析分辨率、EXIF、拍摄参数等元数据并更新\n"
            "• 文件数量较多时耗时较久，请耐心等待完成提示，请勿中途关闭程序\n"
        )
        if not zen_askyesno("确认操作", msg):
            return  # 点取消就直接退出
        count_total, count_dict = self.app.scan_media(force_gen=True)
        zen_msgbox(
            "操作完成",
            f"文件扫描与数据刷新已执行完毕！\n\n"
            f"本次扫描总文件数：{count_total} 个\n"
            f"符合文件格式要求并完成数据更新：{count_dict} 个\n\n",
        )

    def build_ui(self):
        main_fr = ttk.Frame(self, padding=10)
        main_fr.pack(fill=tk.BOTH, expand=True)
        fr_cfg = ttk.LabelFrame(
            main_fr, text="⚙配置管理：设定组（总体设置）、界面配色、字体大小设置"
        )
        fr_cfg.pack(fill=tk.X, pady=4)
        ttk.Button(fr_cfg, text="≣切换配置", command=self.open_config_sel).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(fr_cfg,text="🎨切换主题",command=lambda: (cycle_theme(), self.app.refresh_file_list()),).pack(side=tk.LEFT, padx=2)
        ttk.Button(fr_cfg,text="🎨切换配色",command=lambda: (cycle_color(), self.app.refresh_file_list()),).pack(side=tk.LEFT, padx=2)
        ttk.Button(fr_cfg, text="A+", command=lambda: font_size_adjust(1,"A"), width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(fr_cfg, text="A-", command=lambda: font_size_adjust(-1,"A"), width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(fr_cfg, text="T+", command=lambda: font_size_adjust(1,"T"), width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(fr_cfg, text="T-", command=lambda: font_size_adjust(-1,"T"), width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(fr_cfg, text="RST", command=lambda: font_size_adjust(0,"RESET"), width=3).pack(side=tk.LEFT, padx=2)


        fr_dir = ttk.LabelFrame(main_fr, text="🗁扫描目录")
        fr_dir.pack(fill=tk.X, pady=4)
        v_scroll = ttk.Scrollbar(fr_dir, orient="vertical")
        
        self.dir_lb = tk.Listbox(fr_dir,yscrollcommand=v_scroll.set)
        self.dir_lb.bind("<Double-1>", self.toggle_scan_dir)  # 新增：双击绑定
        cycle_color.apply_listbox(self.dir_lb)
        self.dir_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        v_scroll.pack(side="left", fill="y")
        v_scroll.config(command=self.dir_lb.yview)
        dir_btn = ttk.Frame(fr_dir)
        dir_btn.pack(side=tk.RIGHT, padx=5)
        ttk.Button(dir_btn, text="添加目录", command=self.add_scan_dir).pack(
            fill=tk.X, pady=2
        )
        ttk.Button(dir_btn, text="删除目录", command=self.del_scan_dir).pack(
            fill=tk.X, pady=2
        )
        ttk.Button(dir_btn, text="切换选中", command=self.toggle_scan_dir).pack(
            fill=tk.X, pady=2
        )
        fr_type = ttk.LabelFrame(
            main_fr, text="⊟扫描格式：其他格式的文本框改动后要切换勾选后才能生效保存"
        )
        fr_type.pack(fill=tk.X, pady=4)
        line1 = ttk.Frame(fr_type)
        line1.pack(anchor=tk.W, pady=3)
        ttk.Checkbutton(
            line1, text="▶视频", var=self.var_video, command=self.save_now
        ).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(
            line1, text="♪音频", var=self.var_audio, command=self.save_now
        ).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(
            line1, text="□图片", var=self.var_img, command=self.save_now
        ).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(
            line1, text="⊡压缩包", var=self.var_zip, command=self.save_now
        ).pack(side=tk.LEFT, padx=5)
        line2 = ttk.Frame(fr_type)
        line2.pack(anchor=tk.W, pady=3)
        ttk.Checkbutton(
            line2, text="▤其他", var=self.var_other, command=self.save_now
        ).pack(side=tk.LEFT, padx=5)
        ttk.Entry(line2, textvariable=self.str_other_suffix, width=38).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Label(line2, text="后缀名用;分隔").pack(side=tk.LEFT)
        fr_tag = ttk.LabelFrame(
            main_fr,
            text="★标签管理",
        )
        fr_tag.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(fr_tag, text="每列行数：").pack(side=tk.LEFT, padx=(15, 3))
        ttk.Entry(fr_tag, textvariable=self.str_max_row, width=6).pack(side=tk.LEFT)
        ttk.Button(
            fr_tag, text="▦标签统计", command=self.open_calc_tag
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            fr_tag, text="🖍标签编辑", command=self.open_edit_tag
        ).pack(side=tk.LEFT, padx=2)

        fr_tool = ttk.LabelFrame(
            main_fr,
            text="🛠文件工具：显示设置以及备份、还原全部文件的ads标签，位置是每个目录的ads_tags.txt",
        )        

        fr_tool.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(
            fr_tool, text="↺重新识别文件参数", command=self.force_refresh_all_file
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            fr_tool, text="🛠备份ADStoTXT", command=self.backup_all_folder_ads
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            fr_tool, text="🛠还原TXTtoADS", command=self.restore_all_folder_ads
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            fr_tool, text="🛠删除备份TXT", command=self.clear_backup_folder_ads
        ).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        cfg = self.app.config_data
        self.var_video.set(cfg.get("enable_video", True))
        self.var_audio.set(cfg.get("enable_audio", False))
        self.var_img.set(cfg.get("enable_image", False))
        self.var_zip.set(cfg.get("enable_archive", False))
        self.var_other.set(cfg.get("enable_other", False))
        self.str_other_suffix.set(cfg.get("other_suffix", OTHER_DEFAULT_SUFFIX))
        self.str_max_row.set(str(cfg.get("tag_max_row", DEFAULT_MAX_ROW)))
        self.dir_lb.delete(0, tk.END)
        # 针对folders新旧模式切换

        if cfg.get("folders", []):
            if isinstance(cfg["folders"], list):
                tmp = {}
                for item in cfg["folders"]:
                    if isinstance(item, str):
                        tmp[item] = True
                cfg["folders"] = tmp
        for item in cfg["folders"]:
            if cfg["folders"][item]:
                self.dir_lb.insert(tk.END, self.prefix_yes + item)
            else:
                self.dir_lb.insert(tk.END, self.prefix_no + item)

    def add_scan_dir(self):
        d = filedialog.askdirectory()
        if not d:
            return
        dirs = self.app.config_data.get("folders", {})
        if d not in dirs:
            dirs[d] = True
            self.app.config_data["folders"] = dirs
            self.save_now()
            self.dir_lb.insert(tk.END, self.prefix_yes + d)

    def del_scan_dir(self):
        s = self.dir_lb.curselection()
        if not s:
            return
        val = self.dir_lb.get(s[0])[2:]
        dirs = self.app.config_data.get("folders", {})
        if val in dirs:
            dirs.pop(val)
            self.app.config_data["folders"] = dirs
            self.save_now()
            self.dir_lb.delete(s[0])

    def toggle_scan_dir(self,event=None):
        s = self.dir_lb.curselection()
        if not s:
            return
        val = self.dir_lb.get(s[0])[2:]
        dirs = self.app.config_data.get("folders", {})
        if val in dirs:
            dirs[val] = not dirs[val]
            self.app.config_data["folders"] = dirs
            self.save_now()
            self.dir_lb.delete(s[0])
            if dirs[val]:
                self.dir_lb.insert(s[0], self.prefix_yes + val)
            else:
                self.dir_lb.insert(s[0], self.prefix_no + val)

    def save_now(self):
        cfg = self.app.config_data
        cfg["enable_video"] = self.var_video.get()
        cfg["enable_audio"] = self.var_audio.get()
        cfg["enable_image"] = self.var_img.get()
        cfg["enable_archive"] = self.var_zip.get()
        cfg["enable_other"] = self.var_other.get()
        cfg["other_suffix"] = self.str_other_suffix.get().strip()
        try:
            row = int(self.str_max_row.get())
            if row < 1:
                row = DEFAULT_MAX_ROW
        except:
            row = DEFAULT_MAX_ROW
        cfg["tag_max_row"] = row
        self.app.save_config()
        self.app.rebuild_all_checkbox()
        self.app.scan_media()  # 的确需要

    def backup_all_folder_ads(self):
        all_folders = [k for k, v in self.app.config_data.get("folders", {}).items() if v is True]
        total = 0
        for top_fd in all_folders:
            if not os.path.isdir(top_fd):
                continue
            for root, _, files in os.walk(top_fd):
                save_dic = {}
                for fn in files:
                    fullpath = os.path.join(root, fn)
                    meta = self.app.load_file_meta(fullpath)
                    ##迁移旧格式的ads标签,备份一次，再还原回去就转化了
                    if "themes" in meta:
                        meta["tag_main"] = meta.pop("themes")
                    if "actors" in meta:
                        meta["tag_extra"] = meta.pop("actors")
                    if "tag_ext" in meta:
                        meta["tag_extra"] = meta.pop("tag_ext")
                    save_dic[fn] = meta
                if save_dic:
                    out_txt = os.path.join(root, "_ads_tags.txt")
                    with open(out_txt, "w", encoding="utf-8") as f:
                        json.dump(save_dic, f, ensure_ascii=False, indent=2)
                    total += 1
        zen_msgbox("备份完成", f"共生成{total}个ads_tags.txt")

    def restore_all_folder_ads(self):
        all_folders = [k for k, v in self.app.config_data.get("folders", {}).items() if v is True]
        total = 0
        for top_fd in all_folders:
            if not os.path.isdir(top_fd):
                continue
            for root, _, files in os.walk(top_fd):
                txt_path = os.path.join(root, "_ads_tags.txt")
                if not os.path.exists(txt_path):
                    continue
                try:
                    with open(txt_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except:
                    continue
                for fname, meta in data.items():
                    full = os.path.join(root, fname)
                    if os.path.isfile(full):
                        self.app.save_file_meta(full, meta)
                total += 1
        self.app.scan_media()  # 的确需要
        self.app.refresh_file_list()
        zen_msgbox("还原完成", f"共读取{total}个目录备份")

    def clear_backup_folder_ads(self):
        all_folders = [k for k, v in self.app.config_data.get("folders", {}).items() if v is True]
        total = 0
        for top_fd in all_folders:
            if not os.path.isdir(top_fd):
                continue
            for root, _, files in os.walk(top_fd):
                txt_path = os.path.join(root, "_ads_tags.txt")
                if os.path.exists(txt_path):
                    os.remove(txt_path)
                    total += 1
        zen_msgbox("清除完成", f"共清除{total}个ads_tags.txt备份")


class ConfigSelectUI(tk.Toplevel):
    def __init__(self, master_root, app_obj):
        super().__init__(master=master_root)
        self.root, self.app = master_root, app_obj
        self.title("选择配置文件")
        # self.geometry("360x300")
        self.resizable(False, False)
        self.resizable(0, 0)
        self.transient(self.root)
        self.grab_set()
        self.lb = tk.Listbox(self)
        cycle_color.apply_listbox(self.lb)
        self.lb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.lb.bind("<Double-1>", self.on_double_click)  # 新增：双击绑定

        btn_fr = ttk.Frame(self)
        btn_fr.pack(pady=5)
        btn_list = [
            ("新建配置", self.create_new_cfg),
            ("复制配置", self.copy_cfg),
            ("删除配置", self.del_cfg),
            ("重命名", self.rename_cfg),
            ("应用配置", self.select_cfg),
        ]
        for col, (text, func) in enumerate(btn_list):
            ttk.Button(btn_fr, text=text, width=8, command=func).grid(
                row=0, column=col, padx=3
            )

        self.refresh_list()

    def refresh_list(self):
        self.lb.delete(0, tk.END)
        files = []
        for f in os.listdir("."):
            if f.casefold().endswith("config.ini"):
                files.append((-os.path.getmtime(f), f))
        for _, name in sorted(files):
            self.lb.insert(tk.END, name)

    def _get_select(self):
        sel = self.lb.curselection()
        if not sel:
            zen_msgbox("提示", "请先选中配置文件")
            return None
        return self.lb.get(sel[0])

    def on_double_click(self, event):  # 新增：双击直接应用
        self.select_cfg()

    def create_new_cfg(self):
        name = zen_askstring("新建配置", "输入配置名称：")
        if not name:
            return
        path = f"{name}_config.ini"
        if os.path.exists(path):
            zen_msgbox("提示", "配置已存在")
            return
        self.app.create_default_config(path)
        self.refresh_list()

    def copy_cfg(self):
        src = self._get_select()
        if not src:
            return
        new_name = zen_askstring("复制配置", "新配置名称：")
        if not new_name:
            return
        dst = f"{new_name}_config.ini"
        if os.path.exists(dst):
            zen_msgbox("提示", "目标配置已存在")
            return
        shutil.copy2(src, dst)
        self.refresh_list()

    def rename_cfg(self):
        old = self._get_select()
        if not old:
            return
        new_name = zen_askstring("重命名配置", "输入新名称：")
        if not new_name:
            return
        new = f"{new_name}_config.ini"
        if new == old or os.path.exists(new):
            zen_msgbox("提示", "名称重复或无修改")
            return
        os.rename(old, new)
        self.refresh_list()

    def del_cfg(self):
        cfg = self._get_select()
        if not cfg:
            return
        if zen_askyesno("删除确认", f"确定删除 {cfg} ?"):
            os.remove(cfg)
            self.refresh_list()

    def select_cfg(self):
        idx = self.lb.curselection()
        if not idx:
            return
        sel = self.lb.get(idx[0])
        self.app.config_file = sel
        self.app.config_data = self.app.load_config()
        if self.app.setting_win:
            self.app.setting_win.destroy()
        self.destroy()
        self.app.refresh_tags_list()
        self.app.rebuild_all_checkbox()
        self.app.scan_media()  # 的确需要


# =====================主程序【V2.1.3定稿锁定】=====================
class MediaManagerApp:
    def __init__(self, root_win):

        self.root = root_win
        self.root.title(MEDIA_MANAGER_TITLE+MEDIA_MANAGER_VERSON)
        self.config_file = DEFAULT_CONFIG_NAME
        self.config_data = {}
        self.media_dict = {}
        self.current_select_path = None
        self.setting_win = None
        self.tag_main_check_map = {}
        self.tag_extra_check_map = {}
        self.tagm_inner = None
        self.tage_inner = None
        self.tagm_inner = None
        self.tage_inner = None
        self.check_and_init_config()
        # 筛选+排序变量
        self.var_filter_name = tk.StringVar()
        self.var_filter_tagm = tk.StringVar(value="全部")
        self.var_filter_tage = tk.StringVar(value="全部")
        self.var_filter_score = tk.StringVar(value="全部")
        self.var_filter_def = tk.StringVar(value="全部")
        self.var_filter_type = tk.StringVar(value="全部")
        self.var_sort = tk.StringVar(value="默认顺序")
        self.build_main_ui()
        # 快捷键打分
        self.root.bind("<Key>", self.on_key_event)
        self.hotkey_dict={}
        # 刷新标签、媒体文件
        self.rebuild_all_checkbox()
        self.refresh_tags_list()
        self.scan_media()  # 的确需要



    def control_player_seek(self, go_forward: bool = True, count: int = 2):
        if not self.switch_slim_mode_flag.get():
            return
        user32 = ctypes.windll.user32
        VK_ALT = 0x12
        VK_ESC = 0x1B
        VK_RIGHT = 0x27
        VK_LEFT = 0x25
        KEY_DOWN = 0x0000
        KEY_UP = 0x0002

        target_key = VK_RIGHT if go_forward else VK_LEFT

        user32.keybd_event(VK_ALT, 0, KEY_DOWN, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_ESC, 0, KEY_DOWN, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_ESC, 0, KEY_UP, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_ALT, 0, KEY_UP, 0)
        time.sleep(0.1)

        # 单键步进5秒，计算按压次数
        for _ in range(count):
            user32.keybd_event(target_key, 0, KEY_DOWN, 0)
            time.sleep(0.02)
            user32.keybd_event(target_key, 0, KEY_UP, 0)
            time.sleep(0.02)

        self.root.focus_force()
    def startfile(self):
        sel = self.file_tree.selection()
        if sel:
            p = os.path.normpath(self.file_tree.item(sel[0], "values")[0])
            os.startfile(p)

    def on_key_event(self,event):
        focus_widget = self.root.focus_get()
        widget_type = str(type(focus_widget))
        if "Entry" in widget_type or "Text" in widget_type:
            if focus_widget is self.rename_entry:
                if event.keysym=="Return":
                    self.single_rename()
            return
        if event.keysym=="Up":self.nav_item(-1)
        elif event.keysym=="Down":self.nav_item(1)
        elif event.keysym=="minus":self.set_file_score_setp(-1)
        elif event.keysym=="plus":self.set_file_score_setp(1)
        elif event.keysym in self.hotkey_dict:self.hotkey_dict[event.keysym]()
        elif event.keysym=="BackSpace":self.clear_preset()
        elif event.keysym=="Delete":self.delete_selected_file()
        elif event.keysym=="Right":self.control_player_seek(True,1)
        elif event.keysym=="Left":self.control_player_seek(False)
        elif event.keysym=="Return":self.startfile()
        elif event.keysym=="Escape":self.clear_all_filter()
        elif event.keysym=="Tab":self.root.after_idle(lambda: (self.rename_entry.focus_force(),self.rename_entry.selection_range(0, tk.END),self.rename_entry.icursor(tk.END)))
        elif event.keysym=="Alt_L":pass
        else:print("key press:",event.keysym)
    def check_and_init_config(self):
        cfg_files = [f for f in os.listdir(".") if f.lower().endswith("config.ini")]
        if not cfg_files:
            self.create_default_config(self.config_file)
        else:
            self.config_file = max(cfg_files, key=os.path.getmtime)
        self.config_data = self.load_config()

    def create_default_config(self, fn):
        move = {f"move_{i+1}": "" for i in range(5)}
        preset = {
            f"preset_{i+1}": {"tag_main": [], "tag_extra": [], "score": 0}
            for i in range(5)
        }
        cfg = {
            "folders": {os.getcwd():True},
            "tag_main": DEFAULT_TAG_MAIN.copy(),
            "tag_extra": DEFAULT_TAG_EXTRA.copy(),
            "enable_video": True,
            "enable_audio": False,
            "enable_image": False,
            "enable_archive": False,
            "enable_other": False,
            "other_suffix": OTHER_DEFAULT_SUFFIX,
            "tag_max_row": DEFAULT_MAX_ROW,
            **move,
            **preset,
        }
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

    def load_config(self):
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, ensure_ascii=False, indent=2)

    def open_setting(self):
        self.setting_win = SettingUI(self.root, self)

    def open_edit_tag(self):
        TagsManagerUI(self.root, self, "编辑分类标签：按行区分，直接修改好退出即保存生效", "EDIT")
    def open_calc_tag(self):
        TagsManagerUI(self.root, self, "统计分类标签", "CALC")
    def open_about(self):
        AboutUI(self.root)

    def switch_slim_mode(self):
        if self.switch_slim_mode_flag.get():
            self.switch_auto_open_flag.set(True)
            self.pan.forget(self.left_fr)
            self.pan.forget(self.right_fr)
            self.pan.add(self.right_fr,weight=0)
            self.root.attributes("-topmost", True)
            self.root.attributes("-alpha", 0.8)
            # 3. 恢复原始大小
            self.root.state("normal")
            self.root.after(50, lambda: self.root.geometry(
                f"+{self.root.winfo_screenwidth() - self.root.winfo_width()}+0"
            ))
            
        else:
            self.pan.pack_forget()
            self.pan.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.pan.forget(self.right_fr)
            self.pan.add(self.left_fr,weight=1)
            self.pan.add(self.right_fr,weight=0)
            self.root.attributes("-topmost", False)
            self.root.attributes("-alpha", 1)
            self.root.state("zoomed")
            self.root.geometry("+0+0")

        # if self.slim_mode_flag:
        #     for w in self.hide_list:
        #         w.pack()
        # else:
        #     for w in self.hide_list:
        #         w.pack_forget()

        # for w in self.root.winfo_children():
        #     if "hide" in w.winfo_name():
        #         w.pack()  # 恢复显示

    # 1. 全选
    def file_select_all(self):
        items = self.file_tree.get_children()
        self.file_tree.selection_set(items)
    # 3. 反选
    def file_invert_select(self):
        tree = self.file_tree
        all_items = tree.get_children()
        selected = set(tree.selection())
        
        to_select = []
        to_deselect = []
        
        for item in all_items:
            if item in selected:
                to_deselect.append(item)
            else:
                to_select.append(item)
        tree.selection_remove(to_deselect)
        tree.selection_set(to_select)

    def build_main_ui(self):
        # 左右分割面板
        pan = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        pan.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_fr = ttk.Frame(pan)
        pan.add(left_fr, weight=1)
        right_fr = ttk.Frame(pan, width=320)
        
        pan.add(right_fr, weight=0)
        self.pan=pan
        self.left_fr=left_fr
        self.right_fr=right_fr

        # 顶部按钮行
        left_top_fr = ttk.Frame(left_fr)
        left_top_fr.pack(fill=tk.X, padx=5, pady=5)
        btns = [
            ("⚙设置", self.open_setting),

            ("📝文件名标记", self.batch_rename_files),
            ("↩标记还原", self.restore_original_name),
            ("↺刷新列表", self.refresh_file_list),
            ("🛠扫描文件", self.scan_media),
            # ("🗁打开目录", self.open_folder_by_sel),
            # ("🗑删除文件", self.delete_selected_file),
            # ("𝒾 关于", self.open_about),
            # ("▦标签统计", self.open_calc_tag),
            # ("🖍标签编辑", self.open_edit_tag),
        ]
        for txt, cmd in btns:
            ttk.Button(left_top_fr, text=txt, width=len(txt) * 2, command=cmd).pack(
                side=tk.LEFT, padx=UI_MAIN_BT_PADX
            )

        # 靠右筛选
        
        self.cb_sort = ttk.Combobox(
            left_top_fr, textvariable=self.var_sort, state="readonly", width=9
        )
        self.cb_sort["values"] = [
            "默认顺序",
            "文件名升序",
            "文件名降序",
            "大小升序",
            "大小降序",
            "星级升序",
            "星级降序",]
        self.cb_sort.pack(side=tk.RIGHT)
        self.cb_sort.bind("<<ComboboxSelected>>", lambda e: self.refresh_file_list())
        ttk.Label(left_top_fr, text="排序：").pack(side=tk.RIGHT, padx=(8, 2))
        #靠右按钮
        btns_right = [
            ("反选", self.file_invert_select),
            ("全选", self.file_select_all),
            ("重置筛选条件", self.clear_all_filter),
        ]
        for txt, cmd in btns_right:
            ttk.Button(left_top_fr, text=txt, width=len(txt) * 2, command=cmd).pack(side=tk.RIGHT, padx=UI_MAIN_BT_PADX)



        # 筛选+排序行
        filter_fr = ttk.Frame(left_fr)
        filter_fr.pack(fill=tk.X, padx=5, pady=3)
        ttk.Label(filter_fr, text="▤筛选 文件名：").pack(side=tk.LEFT)
        e = ttk.Entry(filter_fr, textvariable=self.var_filter_name, width=12)
        e.pack(side=tk.LEFT, padx=2)
        e.bind("<KeyRelease>", lambda e: self.refresh_file_list())
        ttk.Label(filter_fr, text="内容：").pack(side=tk.LEFT, padx=5)
        self.cb_tagm = ttk.Combobox(
            filter_fr, textvariable=self.var_filter_tagm, state="readonly", width=12
        )
        self.cb_tagm.pack(side=tk.LEFT)
        self.cb_tagm.bind("<<ComboboxSelected>>", lambda e: self.refresh_file_list())
        ttk.Label(filter_fr, text="附加：").pack(side=tk.LEFT, padx=5)
        self.cb_tage = ttk.Combobox(
            filter_fr, textvariable=self.var_filter_tage, state="readonly", width=12
        )
        self.cb_tage.pack(side=tk.LEFT)
        self.cb_tage.bind("<<ComboboxSelected>>", lambda e: self.refresh_file_list())
        ttk.Label(filter_fr, text="星级：").pack(side=tk.LEFT, padx=5)
        self.cb_score = ttk.Combobox(
            filter_fr, textvariable=self.var_filter_score, state="readonly", width=4
        )
        self.cb_score["values"] = ["全部", "0星", "1星", "2星", "3星", "4星", "5星"]
        self.cb_score.pack(side=tk.LEFT)
        self.cb_score.bind("<<ComboboxSelected>>", lambda e: self.refresh_file_list())
        ttk.Label(filter_fr, text="清晰度：").pack(side=tk.LEFT, padx=5)
        self.cb_def = ttk.Combobox(
            filter_fr, textvariable=self.var_filter_def, state="readonly", width=6
        )
        self.cb_def["values"] = DEF_ALL
        self.cb_def.pack(side=tk.LEFT)
        self.cb_def.bind("<<ComboboxSelected>>", lambda e: self.refresh_file_list())
        ttk.Label(filter_fr, text="类型：").pack(side=tk.LEFT, padx=5)
        self.cb_type = ttk.Combobox(
            filter_fr, textvariable=self.var_filter_type, state="readonly", width=8
        )
        self.cb_type["values"] = ["全部", "视频", "音频", "图片", "压缩", "其他"]
        self.cb_type.pack(side=tk.LEFT)
        self.cb_type.bind("<<ComboboxSelected>>", lambda e: self.refresh_file_list())

        # 左侧列表+滚动条
        tree_wrap = ttk.Frame(left_fr)
        tree_wrap.pack(fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(tree_wrap, orient=tk.VERTICAL)
        self.file_tree = ttk.Treeview(
            tree_wrap,
            columns=("path", "tags", "size", "reso", "defi", "score"),
            show="headings",
            selectmode="extended",
            yscrollcommand=vsb.set,
        )
        vsb.config(command=self.file_tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_tree.heading(
            "path",
            text="文件路径（双击路径打开所在文件夹，单击大小或双击右侧列打开文件| 按Ctrl多选文件进行批量操作）",
        )
        self.file_tree.heading("tags", text="标签")  # 新增标签
        self.file_tree.heading("size", text="文件大小")
        self.file_tree.heading("reso", text="分辨率")
        self.file_tree.heading("defi", text="清晰度")
        self.file_tree.heading("score", text="星级")
        self.file_tree.column("path", width=420, stretch=tk.YES)
        self.file_tree.column("tags", width=140, stretch=tk.NO)  # 新增标签
        self.file_tree.column("size", width=100, stretch=tk.NO)
        self.file_tree.column("reso", width=110, stretch=tk.NO)
        self.file_tree.column("defi", width=70, stretch=tk.NO)
        self.file_tree.column("score", width=80, stretch=tk.NO)
        self.file_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.file_tree.bind("<ButtonRelease-1>", self.click_size_open_file)
        # self.file_tree.bind("<ButtonRelease-3>", self.click_tree_open_properties)
        self.file_tree.bind("<Double-1>", self.find_file_by_col_path)
        # 右侧面板
        rp = 5
        rp_line = rp + 10
        right_fr_switch= ttk.Frame(right_fr)
        right_fr_switch.pack(fill=tk.X, padx=5, pady=5)
        self.switch_auto_open_flag = tk.BooleanVar(value=False)
        self.switch_slim_mode_flag = tk.BooleanVar(value=False)
        self.switch_auto_score_next = tk.BooleanVar(value=False)
        ttk.Checkbutton(right_fr_switch, text="精简模式", variable=self.switch_slim_mode_flag,command=self.switch_slim_mode).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(right_fr_switch, text="自动打开", variable=self.switch_auto_open_flag).pack(side=tk.LEFT, padx=2)

        ttk.Button(right_fr_switch, text="𝒾 关于", width=5, command=self.open_about).pack(side=tk.LEFT, padx=2)
        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=rp_line, pady=(1, 1))  # 分割线
        fr_nav = ttk.Frame(right_fr)
        fr_nav.pack(pady=3, anchor="w")
        ttk.Button(fr_nav, text="⬆上一个", width=8, command=lambda:self.nav_item(-1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(fr_nav, text="⬇下一个", width=8, command=lambda:self.nav_item(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(fr_nav, text="🖍执行改名", width=10, command=self.single_rename).pack(side=tk.LEFT)
        right_fr_name= ttk.Frame(right_fr)
        right_fr_name.pack(fill=tk.X, padx=5, pady=5)
        self.rename_label=ttk.Label(right_fr_name, text="文件名：")
        self.rename_label.pack(side=tk.LEFT, padx=(10, 2))
        self.rename_label.bind("<Button-1>", lambda e:self.open_file())
        self.rename_entry = ttk.Entry(right_fr_name, width=28)
        self.rename_entry.pack(side=tk.LEFT, padx=(1, rp_line))

        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=rp_line, pady=(1, 1)
        )  # 分割线
        ttk.Label(right_fr, text="★星级打分 (快捷键⬅➡)").pack(anchor=tk.W, padx=rp, pady=(1, 1))
        score_fr = ttk.Frame(right_fr)
        score_fr.pack(padx=rp, pady=1, fill=tk.X)
        self.score_btn_list = []
        for i in range(5):
            b = tk.Button(
                score_fr,
                text="★",
                width=3,
                font=("Times New Roman",ZEN_FONT[1]+3),
                fg="gray",
                bg=ZEN_THEME["bg_main"],
                command=lambda n=i + 1: self.set_file_score(n),
            )
            b.pack(side=tk.LEFT)
            b.bind("<Button-3>", lambda e, score=i+1: (
                self.var_filter_score.set("全部") if self.var_filter_score.get() == score else self.var_filter_score.set(score),self.refresh_file_list()))
            self.score_btn_list.append(b)
        # ttk.Checkbutton(score_fr, text="自动下移", variable=self.switch_auto_score_next).pack(side=tk.LEFT, padx=2)
        self.switch_file_locked_flag= tk.BooleanVar(value=False)
        ttk.Checkbutton(score_fr, text="锁定", variable=self.switch_file_locked_flag,command=self.switch_file_locked).pack(side=tk.LEFT, padx=2)
        lb_group = ttk.Label(right_fr, text="▤批量分类组(左键应用/右键保存)")
        lb_group.pack(anchor=tk.W, padx=rp, pady=(1, 1))
        lb_group.bind("<Button-1>", self.show_all_presets)
        preset_fr = ttk.Frame(right_fr)
        preset_fr.pack(padx=rp, pady=2, fill=tk.X)
        for i in range(5):
            btn = ttk.Button(preset_fr, text=str(i + 1), width=1)
            btn.bind("<Button-1>", lambda e, idx=i: self.apply_preset(idx))
            btn.bind("<Button-3>", lambda e, idx=i: self.save_preset(idx))
            btn.pack(side=tk.LEFT)
        if True:
            btn = ttk.Button(preset_fr, text="清除", width=5, command=self.clear_preset)
            btn.pack(side=tk.LEFT, padx=5)
        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=rp_line, pady=(1, 1)
        )  # 分割线
        lb_main=ttk.Label(right_fr, text="⊟内容标签（左键统计/右键编辑）")
        lb_main.pack(anchor=tk.W, padx=rp, pady=(1, 1))
        lb_main.bind("<Button-3>", lambda e =i: self.open_edit_tag())
        lb_main.bind("<Button-2>", lambda e =i: self.open_calc_tag())
        lb_main.bind("<Button-1>", lambda e =i: self.refresh_tagcheck_list("tag_main",True))
        self.tagm_inner = ttk.Frame(right_fr)
        self.tagm_inner.pack(padx=rp, pady=2, fill=tk.X)
        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=rp_line, pady=(1, 1)
        )  # 分割线
        lb_extra=ttk.Label(right_fr, text="⊟附加标签（左键统计/右键编辑）")
        lb_extra.pack(anchor=tk.W, padx=rp, pady=(1, 1))
        lb_extra.bind("<Button-3>", lambda e =i: self.open_edit_tag())
        lb_extra.bind("<Button-2>", lambda e =i: self.open_calc_tag())
        lb_extra.bind("<Button-1>", lambda e =i: self.refresh_tagcheck_list("tag_extra",True))
        self.tage_inner = ttk.Frame(right_fr)
        self.tage_inner.pack(padx=rp, pady=2, fill=tk.X)
        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=rp_line, pady=(1,)
        )  # 分割线
        lb_move = ttk.Label(right_fr, text="🗁批量移动目录(左键应用/右键设置)")
        lb_move.pack(anchor=tk.W, padx=rp, pady=(1, 1))
        lb_move.bind("<Button-1>", self.show_move_dir)

        move_fr = ttk.Frame(right_fr)
        move_fr.pack(padx=rp, pady=2, fill=tk.X)
        for i in range(5):
            btn = ttk.Button(move_fr, text=str(i + 1), width=1)
            btn.bind("<Button-1>", lambda e, idx=i: self.move_to_dir(idx))
            btn.bind("<Button-3>", lambda e, idx=i: self.set_move_dir(idx))
            btn.pack(side=tk.LEFT)
        ttk.Button(move_fr, text="🗑删除", width=6, command=self.delete_selected_file).pack(side=tk.LEFT, padx=4)
        self.switch_move_confirm_flag= tk.BooleanVar(value=True)
        ttk.Checkbutton(move_fr, text="确认", variable=self.switch_move_confirm_flag).pack(side=tk.LEFT, padx=0)


    def nav_item(self, step=0):
        s = self.file_tree.selection()
        if not s:
            return
        lst = self.file_tree.get_children()
        i = self.file_tree.index(s[0])
        if step>0:
            if i==len(lst)-1:
                zen_toast("当前选择的是最后一个文件")
                return
        elif step<0:
            if i==0:
                zen_toast("当前选择的是第一个文件")
                return
        
        target_i = i + step
        target = lst[target_i]
        self.file_tree.selection_set(target)
        self.file_tree.focus(target)
        if self.switch_auto_open_flag.get():
            s = self.file_tree.selection()
            os.startfile(self.file_tree.item(s[0], "values")[0])
            if self.switch_slim_mode_flag.get():
                self.root.after(300, lambda: self.root.focus_force())

    def refresh_tags_list(self):
        self.cb_tagm["values"] = ["全部", "未分类"] + self.config_data.get(
            "tag_main", []
        )
        self.cb_tage["values"] = ["全部", "未分类"] + self.config_data.get(
            "tag_extra", []
        )

    def rebuild_all_checkbox(self):
        self.refresh_tagcheck_list("tag_main")
        self.refresh_tagcheck_list("tag_extra")


    def refresh_tagcheck_list(self, tag_type: str, tag_count: bool = False):
        # 自动匹配对应资源
        if tag_type == "tag_main":
            container = self.tagm_inner
            tag_list = self.config_data.get("tag_main", [])
            hotkeys = HOTKEY_TAG_MAIN
            check_map = self.tag_main_check_map
            tag_filter=self.var_filter_tagm
        elif tag_type == "tag_extra":
            container = self.tage_inner
            tag_list = self.config_data.get("tag_extra", [])
            hotkeys = HOTKEY_TAG_EXTRA
            check_map = self.tag_extra_check_map
            tag_filter=self.var_filter_tage
        else:
            return
        # 统计标签计数
        tag_counter = Counter()
        if tag_count:
            for media in self.media_dict.values():
                for tag in media[tag_type]:
                    tag_counter[tag] += 1

        # 容器不存在直接退出
        if not container.winfo_exists():return
        # 清空旧控件
        for widget in container.winfo_children():widget.destroy()
        check_map.clear()
        #生成checkbox
        rowcnt = self.config_data.get("tag_max_row", DEFAULT_MAX_ROW)
        sep_switch_threshold = 2
        tag_cursor = 0
        hotkey_cursor=0

        checkbox_col = 0       # 当前列
        checkbox_curren_row = 0   # 当前列已占用行数
        while tag_cursor < len(tag_list):
            tag_raw = tag_list[tag_cursor]
            # 处理分隔行
            if "sep" in tag_raw:
                # 当前列行数超过2/3阈值，先切下一列再放分隔符
                if checkbox_curren_row >= sep_switch_threshold:
                    checkbox_col += 1
                    checkbox_curren_row = 0
                ttk.Label(container,text=f"⋆{tag_raw.replace('sep', '')}⋆ ").grid(row=checkbox_curren_row, column=checkbox_col, sticky="w")
                checkbox_curren_row += 1
                tag_cursor += 1
                continue

            # 下面是你原来普通标签完整逻辑，一字没改
            display_text = tag_raw
            hotkey = hotkeys[hotkey_cursor] if tag_cursor < len(hotkeys) else None
            var = tk.BooleanVar()
            # 绑定热键
            if hotkey:
                display_text = f"[{hotkey.upper()}]{display_text}"
                hotkey_cb = lambda x=tag_raw, v=var: (v.set(not v.get()),self.toggle_tag(x, v,tag_type))
                self.hotkey_dict[hotkey] = hotkey_cb
            # 追加统计数量
            if tag_count and tag_counter.get(tag_raw, 0):
                display_text += f"({tag_counter[tag_raw]})"
            # 复选框左键回调
            cmd = lambda x=tag_raw, v=var: self.toggle_tag(x, v,tag_type)
            cb = ttk.Checkbutton(container,text=display_text,variable=var,command=cmd)
            cb.grid(row=checkbox_curren_row, column=checkbox_col, sticky="w")
            # 右键绑定
            cb.bind("<Button-3>", lambda e, tag=tag_raw: (
                tag_filter.set("全部") if tag_filter.get() == tag else tag_filter.set(tag),self.refresh_file_list()))
            check_map[tag_raw] = var

            checkbox_curren_row += 1
            tag_cursor += 1
            hotkey_cursor+=1

            # 当前列填满最大行数，切换下一列、行归零
            if checkbox_curren_row >= rowcnt:
                checkbox_col += 1
                checkbox_curren_row = 0





    def set_move_dir(self, idx):
        k = f"move_{idx+1}"
        old = self.config_data.get(k, "")
        d = filedialog.askdirectory(initialdir=old if old else None)
        if not d:
            return
        self.config_data[k] = os.path.normpath(d)
        self.save_config()

    def show_move_dir(self, e):
        info = "📋 快捷移动目录一览\n\n"
        for i in range(5):
            key = f"move_{i+1}"
            path = self.config_data.get(key, "未设置")
            info += f"目录{i+1}：{path}\n"
        zen_msgbox("全部快捷目录", info.strip())

    def move_to_dir(self, idx):
        sel = self.file_tree.selection()
        if not sel:
            return
        dst = os.path.normpath(self.config_data.get(f"move_{idx+1}", ""))
        if not os.path.isdir(dst):
            zen_msgbox("提示", "目录未配置，右键按钮设置")
            return
        # 移动前确认
        if self.switch_move_confirm_flag.get():
            if not zen_askyesno("确认移动", f"确定要将选中文件移动到目录：\n【{dst}】\n吗？"):return
        # 先收集所有要移动的文件（去重、判断是否同文件、判断是否覆盖）
        move_list = []
        overwrite_list = []
        same_file_list = []
        for item in sel:
            src = os.path.normpath(self.file_tree.item(item, "values")[0])
            fn = os.path.basename(src)
            new_p = os.path.normpath(os.path.join(dst, fn))
            # 如果 源文件 == 目标文件（位置一样）→ 跳过
            if src == new_p:
                same_file_list.append(fn)
                continue
            # 目标已存在 → 需要确认覆盖
            if os.path.exists(new_p):
                overwrite_list.append(fn)
            move_list.append((src, new_p))
        # 如果完全没东西要移动
        if not move_list:
            zen_msgbox("提示", "无需移动（文件已在目标目录）")
            return
        # 如果有需要覆盖的文件 → 列出来让用户确认
        if overwrite_list:
            files = "\n".join(overwrite_list[:10])
            if len(overwrite_list) > 10:
                files += f"\n...等 {len(overwrite_list)} 个文件"
            if not zen_askyesno(
                "文件已存在", f"以下文件将被覆盖：\n{files}\n\n确定继续吗？"
            ):
                return
        # 开始真正移动
        success = 0
        for src, new_p in move_list:
            try:
                os.replace(src, new_p)
                ads_src = src + ADS_SUFFIX
                ads_new = new_p + ADS_SUFFIX
                if os.path.exists(src):
                    os.replace(src, new_p)
                if os.path.exists(ads_src):
                    os.replace(ads_src, ads_new)
                if src in self.media_dict:
                    self.media_dict[new_p] = self.media_dict.pop(src)
                success += 1
            except Exception as e:
                zen_msgbox("移动失败", f"{os.path.basename(src)}\n{str(e)}")

        ##        self.scan_media()

        zen_msgbox("完成", f"成功移动 {success} 个文件")
        self.refresh_file_list()

    def save_preset(self, idx):
        if not self.current_select_path:
            zen_msgbox("提示", "请先选中一个文件再保存模板")
            return

        d = self.media_dict[self.current_select_path]
        key = f"preset_{idx+1}"

        # 新标签
        new_main = " | ".join(d["tag_main"]) or "空"
        new_extra = " | ".join(d["tag_extra"]) or "空"

        # 旧标签
        old = self.config_data.get(key, {})
        old_main = " | ".join(old.get("tag_main", [])) or "空"
        old_extra = " | ".join(old.get("tag_extra", [])) or "空"

        # 超简洁确认
        if new_main == "空" and new_extra == "空":
            zen_msgbox(
                "保存分组模板",
                f"新分组：内容分类[{new_main}] 附加分类[{new_extra}]\n\n" f"请重新设置",
            )
            return

        if not zen_askyesno(
            "保存分组模板",
            f"模板{idx+1}\n"
            f"旧分组：内容分类[{old_main}] 附加分类[{old_extra}]\n"
            f"新分组：内容分类[{new_main}] 附加分类[{new_extra}]\n\n"
            "确定覆盖保存？",
        ):
            return

        self.config_data[key] = {
            "tag_main": d["tag_main"].copy(),
            "tag_extra": d["tag_extra"].copy(),
        }
        self.save_config()

    def show_all_presets(self, e):
        info = "📋 当前全部快捷分类组模板：❎\n\n"
        for i in range(5):
            key = f"preset_{i+1}"
            preset = self.config_data.get(key, {})
            main = " | ".join(preset.get("tag_main", [])) or "空"
            extra = " | ".join(preset.get("tag_extra", [])) or "空"
            info += f"分类组{i+1}\n内容分类：[{main}]\n附加分类：[{extra}]\n\n"
        zen_msgbox("全部快捷分类组模板一览", info)

    def apply_preset(self, idx):
        sel = self.file_tree.selection()
        if not sel:
            return
        cnt = len(sel)
        preset = self.config_data.get(f"preset_{idx+1}", {})
        ths = preset.get("tag_main", [])
        acs = preset.get("tag_extra", [])
        if not ths and not acs:
            zen_msgbox("提示",f"当前快捷分类模板{idx+1}为空，请设置内容分类和附加分类后以右键点击按钮保存分类组",)
            return
        main_str = " | ".join(ths) if ths else "无"
        extra_str = " | ".join(acs) if acs else "无"
        msg = f"确定要对【{cnt}个文件】批量设置标签吗？\n\n内容分类：{main_str}\n附加分类：{extra_str}"

        if cnt > 3:
            if not zen_askyesno("确认操作", msg):
                return
        for item in sel:
            
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            if self.media_dict[p]["locked"]:continue #如果文件时锁定则跳过
            info = self.media_dict[p]
            info["tag_main"] = ths.copy()
            info["tag_extra"] = acs.copy()
            self.media_dict[p]=info
            self.save_file_meta(p, info)
            self.refresh_file_row(p, item)
        self.on_tree_select(None)

    def clear_preset(self):
        sel = self.file_tree.selection()
        if not sel:
            return
        cnt = len(sel)
        msg = f"确定对【{cnt}个文件】清空全部分类标签？"
        if cnt > 3:
            if not zen_askyesno("确认操作", msg):
                return
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            if self.media_dict[p]["locked"]:continue #如果文件时锁定则跳过
            info = self.media_dict[p]
            info["tag_main"] = []
            info["tag_extra"] = []
            self.media_dict[p]=info
            self.save_file_meta(p, info)
            self.refresh_file_row(p, item)
        self.on_tree_select(None)

    def switch_file_locked(self):
        sel = self.file_tree.selection()
        if not sel:
            return
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            info = self.media_dict[p]
            if self.switch_file_locked_flag.get():
                info["locked"] = True
            else:
                info["locked"] = False
            self.media_dict[p]=info
            self.save_file_meta(p, info)
        self.on_tree_select(None)


    def refresh_file_row(self, p, target_row=None):
        info = self.media_dict[p]
        mb = info["size"] / 1024 / 1024
        star = "★" * info["score"]
        values = (
            p,
            info["tag_main"] + info["tag_extra"],  # 新增标签
            f"{mb:.2f} MB",
            info["resolution"],
            info["definition"],
            star,
        )
        if target_row:
            self.file_tree.item(target_row, values=values)
        else:
            return values
        

    def set_file_score_setp(self,step):
        sel = self.file_tree.selection()
        if not sel:return
        single= len(sel)==1
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            if self.media_dict[p]["locked"]:continue #如果文件时锁定则跳过
            score= self.media_dict[p]["score"]
            if single and score==0:
                if step>0:
                    score=3
                else:
                    score=2
            else:
                score=max(0,min(5,score+step))
                if self.media_dict[p]["score"] == score: continue#如果分数不变则跳过
            self.media_dict[p]["score"] = score
            self.save_file_meta(p, self.media_dict[p])
            self.refresh_file_row(p, item)
        self.on_tree_select(None)


    def set_file_score(self, num):
        sel = self.file_tree.selection()
        if not sel:
            return
        # 判断第一个当前评分是否和新评分一致，如是则新评分置0
        p_tmp = os.path.normpath(self.file_tree.item(sel[0], "values")[0])
        if self.media_dict[p_tmp]["score"] == num:
            num = 0
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            if self.media_dict[p]["locked"]:continue #如果文件时锁定则跳过
            self.media_dict[p]["score"] = num
            self.save_file_meta(p, self.media_dict[p])
            self.refresh_file_row(p, item)
        self.on_tree_select(None)

    def toggle_tag(self, name, var,tag_type):
        sel = self.file_tree.selection()
        if not sel:
            var.set(False)
            return
        stat = var.get()
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            if self.media_dict[p]["locked"]:var.set(not stat);continue #如果文件时锁定则跳过
            lst = self.media_dict[p][tag_type]
            
            if stat and name not in lst:
                lst.append(name)
            elif not stat and name in lst:
                lst.remove(name)
            self.save_file_meta(p, self.media_dict[p])
            # 切换分类刷新对应行
            self.refresh_file_row(p, item)


    def on_tree_select(self, e):
        for v in self.tag_main_check_map.values():
            v.set(False)
        for v in self.tag_extra_check_map.values():
            v.set(False)
        sel = self.file_tree.selection()
        if not sel:
            self.current_select_path = None
            self.rename_entry.delete(0, tk.END)
            for b in self.score_btn_list:
                b.config(fg="gray")
            return
        fullname = os.path.normpath(self.file_tree.item(sel[0], "values")[0])
        basename=os.path.basename(fullname)
        self.current_select_path = fullname
        info = self.media_dict[fullname]
        self.rename_entry.delete(0, tk.END)
        self.rename_entry.insert(0, os.path.splitext(basename)[0])
        self.switch_file_locked_flag.set(info["locked"])
        
        for i in range(5):
            self.score_btn_list[i].config(
                fg="gold" if i < info["score"] else "gray", bg=ZEN_THEME["bg_main"]
            )

        for t in info["tag_main"]:
            if t in self.tag_main_check_map:
                self.tag_main_check_map[t].set(True)
        for a in info["tag_extra"]:
            if a in self.tag_extra_check_map:
                self.tag_extra_check_map[a].set(True)

    def load_file_meta(self, p):
        fp = os.path.normpath(p)
        ads = fp + ADS_SUFFIX
        try:
            with open(ads, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}


    def _do_save_keep_time(self, fp, ads, data):
        st = os.stat(fp) if os.path.exists(fp) else None
        with open(ads, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        st and os.utime(ads, (st.st_atime, st.st_mtime))
    def save_file_meta(self, p, data):
        fp, ads = os.path.normpath(p), os.path.normpath(p) + ADS_SUFFIX
        try:
            self._do_save_keep_time(fp, ads, data)
        except:
            try: os.chmod(fp, 0o666); self._do_save_keep_time(fp, ads, data)
            except: pass

    # 竖屏取短边算清晰度【V2.1修订】
    def get_video_def_info(self, p):
        if not MediaInfo:
            return ("", "", "")
        try:            
            mi = MediaInfo.parse(p,parse_speed=0)
            video_tracks = mi.video_tracks
            if not video_tracks:
                return ("无视频", "未知", "")
            for tr in video_tracks:
                if tr.track_type == "Video":
                    w = tr.width or 0
                    h = tr.height or 0
                    res = f"{w}×{h}"
                    short = min(w, h)
                    df = get_def_by_height(short)
                    info = {}
                    info["duration"] = tr.duration  # 时长
                    info["width"] = tr.width  # 宽
                    info["height"] = tr.height  # 高
                    info["frame_rate"] = tr.frame_rate  # 帧率
                    info["bit_rate"] = tr.bit_rate  # 视频码率 bps
                    return (res, df, info)
        except:
            return ("识别出错", "未知", "")

    def get_image_def_info(self, img_path):
        try:
            with Image.open(img_path) as img:
                w = img.width or 0
                h = img.height or 0
                res = f"{w}×{h}"
                short = min(w, h)
                df = get_def_by_height(short)
                info = {"width": w, "height": h}
                try:
                    exif = img._getexif()
                except:
                    exif = img.getexif()
                exif_data = {TAGS.get(k, k): v for k, v in exif.items()} if exif else {}

                # for i in exif_data:
                #     info[i]=exif_data[i]
                # # 时间信息 → 统一格式 YYYYMMDD_hhmmss
                # tmp_time=""
                # if "DateTimeOriginal" in exif_data:
                #     s = exif_data["DateTimeOriginal"][:19]
                #     ts = time.strptime(s, "%Y:%m:%d %H:%M:%S")
                #     tmp_time = time.strftime("%Y%m%d_%H%M%SE#", ts)
                #     try:
                #         ts = time.strptime(s, "%Y:%m:%d %H:%M:%S")
                #         tmp_time = time.strftime("%Y%m%d_%H%M%SE#", ts)
                #     except ValueError:
                #         m = re.search(r"\d{4}:\d{1,2}:\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}", s)
                #         if m:
                #             ts = time.strptime(m.group(), "%Y:%m:%d %H:%M:%S")
                #             tmp_time = time.strftime("%Y%m%d_%H%M%S", ts)
                #     if tmp_time:info["time_exif"]=tmp_time
                # try:
                #     tmp_time=0
                #     tmp_time = min(os.path.getctime(img_path),os.path.getmtime(img_path))
                #     info["time_file"] = datetime.fromtimestamp(tmp_time).strftime("%Y%m%d_%H%M%S")
                # except:
                #     pass
                # info = {}
                # # 相机、镜头
                # info["相机品牌"] = exif_data.get("Make", "")
                # info["相机型号"] = exif_data.get("Model", "")
                # info["镜头型号"] = exif_data.get("LensModel", "")

                # # 拍摄参数
                # info["光圈"] = exif_data.get("FNumber", "")
                # info["快门"] = exif_data.get("ExposureTime", "")
                # info["ISO"] = exif_data.get("ISOSpeedRatings", "")
                # info["焦距"] = exif_data.get("FocalLength", "")
                # info["拍摄时间"] = exif_data.get("DateTimeOriginal", "")

                # # 简化GPS
                # gps = exif_data.get("GPSInfo")
                # if gps:
                #     g = {GPSTAGS[k]: v for k, v in gps.items()}
                #     def dms2deg(dms, ref):
                #         if not dms:
                #             return ""
                #         d = dms[0] + dms[1]/60 + dms[2]/3600
                #         return -d if ref in ("S", "W") else d
                #     info["纬度"] = dms2deg(g.get("GPSLatitude"), g.get("GPSLatitudeRef"))
                #     info["经度"] = dms2deg(g.get("GPSLongitude"), g.get("GPSLongitudeRef"))
                # else:
                #     info["纬度"] = info["经度"] = ""
                return (res, df, exif_data)

        except:
            return ("识别出错", "未知", "")

    def scan_media(self, force_gen=False):
        self.media_dict.clear()
        cfg = self.config_data
        enable_video = cfg.get("enable_video", True)
        enable_audio = cfg.get("enable_audio", False)
        enable_image = cfg.get("enable_image", False)
        enable_archive = cfg.get("enable_archive", False)
        enable_other = cfg.get("enable_other", False)
        o_suf = [x.strip().lower() for x in cfg.get("other_suffix", OTHER_DEFAULT_SUFFIX).replace("*","").split(";") if x.strip()]

        file_count = 0
        rebuild_toast=True
        for dp in cfg.get("folders", {}):
            if not cfg["folders"][dp]:
                continue  # 不勾选就跳过
            dp = os.path.normpath(dp)
            if not os.path.isdir(dp):
                continue
            for root, _, files in os.walk(dp):
                for filename_base in files:
                    file_count += 1
                    filename_full = os.path.normpath(os.path.join(root, filename_base))
                    filename_ext = os.path.splitext(filename_base.lower())[-1]
                    filename_type = ""
                    if enable_video and filename_ext in VIDEO_FORMATS:
                        filename_type = "视频"
                    elif enable_audio and filename_ext in AUDIO_FORMATS:
                        filename_type = "音频"
                    elif enable_image and filename_ext in IMAGE_FORMATS:
                        filename_type = "图片"
                    elif enable_archive and filename_ext in ZIP_FORMATS:
                        filename_type = "压缩"
                    elif enable_other and filename_ext in o_suf:
                        filename_type = "其他"
                    if not filename_type:
                        continue
                    meta = self.load_file_meta(filename_full)
                    #判断是否需要重建
                    need_rebuild = True
                    if meta and not force_gen:
                        if filename_type == "视频":
                            need_rebuild = not bool(meta.get("resolution") and meta.get("definition") and meta.get("video_info"))
                        elif filename_type == "图片":
                            need_rebuild = not bool(meta.get("resolution") and meta.get("definition") and meta.get("image_info"))
                        else:
                            need_rebuild = False
                        if not bool(meta.get("name") and meta.get("size") and meta.get("date")):
                            need_rebuild = True

                            
                    if need_rebuild :
                        if rebuild_toast:rebuild_toast=False;zen_toast("正在新建/重建部分文件媒体信息，请稍后")
                        stat = os.stat(filename_full)
                        meta={
                            "name": filename_base,
                            "size": stat.st_size,
                            "type": filename_type,
                            "date": datetime.fromtimestamp(min(stat.st_mtime,stat.st_birthtime)).strftime("%Y%m%d"),
                            "score": meta.get("score",0),
                            "tag_main": meta.get("tag_main",""),
                            "tag_extra": meta.get("tag_extra",""),
                            "resolution": meta.get("resolution",""),
                            "definition": meta.get("definition",""),
                            "locked":meta.get("locked",False),
                        }
                        if filename_type == "视频":
                            (meta["resolution"],meta["definition"],meta["video_info"],) = self.get_video_def_info(filename_full)
                        elif filename_type == "图片":
                            (meta["resolution"],meta["definition"],meta["image_info"],) = self.get_image_def_info(filename_full)
                        self.save_file_meta(filename_full, meta)
                    self.media_dict[filename_full] = meta

        self.refresh_file_list()
        return file_count, len(self.media_dict)

    def refresh_file_list(self, keep_path=None):
        self.file_tree.delete(*self.file_tree.get_children())
        kw = self.var_filter_name.get().lower()
        fth = self.var_filter_tagm.get()
        fac = self.var_filter_tage.get()
        fsc = self.var_filter_score.get()
        fdf = self.var_filter_def.get()
        fty = self.var_filter_type.get()
        tmp = []
        for p, info in self.media_dict.items():
            if keep_path:
                if p == keep_path:
                    tmp.append((p, info))
                    continue

            if kw and kw not in info["name"].lower():
                continue

            if fth != "全部":
                if fth == "未分类":
                    if info["tag_main"]:
                        continue
                else:
                    if fth not in info["tag_main"]:
                        continue
            if fac != "全部":
                if fac == "未分类":
                    if info["tag_extra"]:
                        continue
                else:
                    if fac not in info["tag_extra"]:
                        continue
            if fty != "全部" and info["type"] != fty:
                continue
            if fsc != "全部" and info["score"] != int(fsc[0]):
                continue
            if fdf != "全部" and info["definition"] != fdf:
                continue
            tmp.append((p, info))
        # 排序
        srt = self.var_sort.get()
        if srt == "文件名升序":
            tmp.sort(key=lambda x: x[1]["name"].lower())
        elif srt == "文件名降序":
            tmp.sort(key=lambda x: x[1]["name"].lower(), reverse=True)
        elif srt == "大小升序":
            tmp.sort(key=lambda x: x[1]["size"])
        elif srt == "大小降序":
            tmp.sort(key=lambda x: x[1]["size"], reverse=True)
        elif srt == "星级升序":
            tmp.sort(key=lambda x: x[1]["score"])
        elif srt == "星级降序":
            tmp.sort(key=lambda x: x[1]["score"], reverse=True)
        else:
            tmp.sort(key=lambda x: x[1]["size"], reverse=True)
        ##        elif srt=="清晰度升序":tmp.sort(key=lambda x:x[1]["definition"])
        ##        elif srt=="清晰度降序":tmp.sort(key=lambda x:x[1]["definition"],reverse=True)
        target = None
        for p, info in tmp:
            iid = self.file_tree.insert(
                "",
                "end",
                values=self.refresh_file_row(p),
            )
            if keep_path:
                if os.path.normpath(p) == os.path.normpath(keep_path):
                    target = iid
            elif not target:
                target = iid

        if target:
            self.file_tree.selection_set(target)
            self.file_tree.focus(target)
            self.current_select_path = keep_path

    def clear_all_filter(self):
        self.var_filter_name.set("")
        self.var_filter_tagm.set("全部")
        self.var_filter_tage.set("全部")
        self.var_filter_score.set("全部")
        self.var_filter_def.set("全部")
        self.var_filter_type.set("全部")
        ##        self.var_sort.set("默认顺序")
        self.refresh_file_list()



    def open_file(self):
        sel = self.file_tree.selection()
        if sel:
            p = os.path.normpath(self.file_tree.item(sel[0], "values")[0])
            os.startfile(p)
    def open_folder(self):
        sel = self.file_tree.selection()
        if  sel:
            p = os.path.normpath(self.file_tree.item(sel[0], "values")[0])
            os.startfile(os.path.dirname(p))
    def find_file_by_col_path(self, e):
        col = self.file_tree.identify_column(e.x)
        sel = self.file_tree.selection()
        if sel:
            p = os.path.normpath(self.file_tree.item(sel[0], "values")[0])
            if col == "#1":
                try:
                    subprocess.Popen(r'explorer.exe /select,"' + p + '"')
                except:
                    os.startfile(os.path.dirname(p))

            else:
                os.startfile(p)
    def click_size_open_file(self, e):
        col = self.file_tree.identify_column(e.x)
        if col == "#3":
            self.open_file()

    def click_tree_open_properties(self, e):
        sel = self.file_tree.selection()
        if sel:
            p = os.path.normpath(self.file_tree.item(sel[0], "values")[0])
            if os.path.exists(p):

                # 方法1不行
                # os.startfile(p, operation="properties")
                # 方法2也不行
                # import ctypes
                # ctypes.windll.shell32.ShellExecuteExW(None, "properties", p, None, None, 5)
                # 方法3也不行
                # subprocess.Popen(['cmd', '/c', 'start', '', p, '/properties'],shell=True)
                pass





    def delete_selected_file(self):
        sel = self.file_tree.selection()
        sel_id= self.file_tree.index(sel[0])  

        if not sel:
            return
        if self.switch_move_confirm_flag.get(): 
            if not zen_askyesno("确认", "删除选中文件？"):return
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            try:
                os.remove(p)
                ads = p + ADS_SUFFIX
                if os.path.exists(ads):
                    os.remove(ads)
                if p in self.media_dict:
                    del self.media_dict[p]
                self.file_tree.delete(item)
            except Exception:
                pass
        lst = self.file_tree.get_children()
        target = lst[min(sel_id, len(lst)-1)]
        self.file_tree.selection_set(target)
        self.file_tree.focus(target)
        self.nav_item()

        # self.refresh_file_list()
    def rename(self,old_fullname,new_fullname):
        try:
            os.rename(old_fullname, new_fullname)
            info=self.media_dict.pop(old_fullname)
            info["name"] = os.path.basename(new_fullname)
            self.media_dict[new_fullname] = info
            self.save_file_meta(new_fullname,info)
            return True
        except Exception as e:
            zen_msgbox("改名失败", str(e))
            return False

    # 【V2.1.8修订：改名成功自动选中新文件】

    def single_rename(self):
        count_select_file=len(self.file_tree.selection())

        if count_select_file==0:
            zen_msgbox("提示", "请选择至少一个文件")
            return
        elif count_select_file==1:
            new_name = self.rename_entry.get().strip()
            if not new_name:return
            old_p = os.path.normpath(self.current_select_path)
            ext = os.path.splitext(old_p)[1]
            dir_p = os.path.dirname(old_p)
            new_full = os.path.normpath(os.path.join(dir_p, new_name + ext))
            if new_full == self.current_select_path:return
            idx = 1
            while os.path.exists(new_full):
                new_full = os.path.normpath(os.path.join(dir_p, f"{new_name}_{idx:02d}{ext}"))
                idx += 1
            if self.rename(old_p, new_full):
                # 刷新并选中
                self.refresh_file_row(new_full, self.file_tree.selection()[0])
                self.current_select_path = new_full
        elif count_select_file > 1:
            new_name = self.rename_entry.get().strip()
            confirm = zen_askyesno("批量改名", f"已选中 {count_select_file} 个文件，确定批量改名吗？")
            if not confirm:
                return
            dir_p = None
            idx = 1
            # 遍历所有选中文件逐个改名
            for item in self.file_tree.selection():
                old_p = os.path.normpath(self.file_tree.item(item, "values")[0])
                ext = os.path.splitext(old_p)[1]
                dir_p = os.path.dirname(old_p)
                # 拼接新路径，重复则累加序号
                new_full = os.path.normpath(os.path.join(dir_p, f"{new_name}_{idx:02d}{ext}"))
                while os.path.exists(new_full):
                    idx += 1
                    new_full = os.path.normpath(os.path.join(dir_p, f"{new_name}_{idx:02d}{ext}"))
                
                if self.rename(old_p, new_full):# 执行重命名
                    self.refresh_file_row(new_full, item)# 刷新行
                idx += 1

            # 清空输入框
            self.rename_entry.delete(0, tk.END)
            self.current_select_path = ""
            return

    def batch_rename_files(self):
        sel = self.file_tree.selection()
        if not sel:
            return
        cnt = 0
        reg = re.compile(r"【[^】]*】$")
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            info = self.media_dict[p]
            name, ext = os.path.splitext(os.path.basename(p))
            block = []
            block.extend(info["tag_extra"])
            block.extend(info["tag_main"])
            if info["score"] > 0:
                block.append(f"{info['score']}星")
            if not block:
                continue
            tag = " ".join(block)
            new_name = reg.sub("", name) + f"【{tag}】" + ext
            new_p = os.path.normpath(os.path.join(os.path.dirname(p), new_name))
            if os.path.exists(new_p):
                continue
            try:
                os.rename(p, new_p)
                (
                    os.rename(p + ADS_SUFFIX, new_p + ADS_SUFFIX)
                    if os.path.exists(p + ADS_SUFFIX)
                    else None
                )
                self.media_dict[new_p] = self.media_dict.pop(p)
                cnt += 1
            except Exception:
                pass
        self.refresh_file_list()
        zen_msgbox("批量完成", f"成功{cnt}个")

    def restore_original_name(self):
        sel = self.file_tree.selection()
        if not sel:
            return
        cnt = 0
        reg = re.compile(r"(.*)【([^】]+)】(\.\w+)$")
        all_th = set(self.config_data.get("tag_main", []))
        all_ac = set(self.config_data.get("tag_extra", []))
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            fn = os.path.basename(p)
            m = reg.match(fn)
            if not m:
                continue
            raw = m.group(1) + m.group(3)
            tags = m.group(2).split()
            sc = 0
            rest = []
            if tags and re.fullmatch(r"\d+星", tags[0]):
                sc = int(tags[0][0])
                rest = tags[1:]
            else:
                rest = tags
            new_p = os.path.normpath(os.path.join(os.path.dirname(p), raw))
            if os.path.exists(new_p):
                continue
            try:
                os.rename(p, new_p)
                (
                    os.rename(p + ADS_SUFFIX, new_p + ADS_SUFFIX)
                    if os.path.exists(p + ADS_SUFFIX)
                    else None
                )
                self.media_dict[new_p] = self.media_dict.pop(p)
                cnt += 1
            except Exception:
                pass
        self.refresh_file_list()
        zen_msgbox("还原完成", f"{cnt}个文件已去掉标签后缀")


if __name__ == "__main__":
    root = tk.Tk()
    font_size_adjust()
    cycle_color()
    if 18 <= datetime.now().hour or datetime.now().hour < 7:
        cycle_color()#如果是夜晚初始主题为深色
    app = MediaManagerApp(root)
    root.mainloop()
