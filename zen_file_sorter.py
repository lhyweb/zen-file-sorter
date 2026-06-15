import os
import shutil
import json
import re
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from collections import Counter

try:
    from pymediainfo import MediaInfo
except ImportError:
    MediaInfo = None

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    Image = None


# =====================全局常量【锁定】=====================
DEFAULT_CONFIG_NAME = "zen_config.ini"
VIDEO_FORMATS = (".mp4", ".mkv", ".avi", ".mov", ".flv", ".rmvb", ".wmv")
AUDIO_FORMATS = (".mp3", ".wav", ".flac", ".ape", ".ogg")
IMAGE_FORMATS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic", ".raw", ".webp")
ZIP_FORMATS = (".zip", ".rar", ".7z")
OTHER_DEFAULT_SUFFIX = ".doc;.docx;.pdf;.txt;.xls;.xlsx"
ADS_SUFFIX = ":zen_mv_data"
DEFAULT_MAX_ROW = 10
NORMAL_FONT = ("微软雅黑", 11)
SMALL_FONT = ("微软雅黑", 10)

DEFAULT_TAG_MAIN = [
    "动作",
    "喜剧",
    "爱情",
    "悬疑",
    "科幻",
    "仙侠",
    "刑侦",
    "纪实",
    "动画",
    "舞蹈",
]
DEFAULT_TAG_EXTRA = ["大陆", "大陆", "港台", "日韩", "欧美"]

MEDIA_MANAGER_TITLE = "媒体文件分类管理工具"
MEDIA_MANAGER_VERSON = "v2.1.7"
MEDIA_MANAGER_AUTHOR = "zen(lhywbe@mail.com)&doubao"
MEDIA_MANAGER_LOG = """
v2.1.7 
1、扫描目录的增加生效、禁用切换功能
2、优化布局、控件排版、文本，修复bug
3、整体代码优化、格式化

v2.1.6 基本稳定版本
1、修复多处BUG，提升整体运行稳定性
2、优化全局UI布局，统一所有控件排版、尺寸与字体样式
3、新增浅色/深色模式切换，支持日夜界面切换

v2.1.5 优化便捷操作
1、优化Treeview选中刷新机制，完善双击打开目录或打开文件
2、增设上一个/下一个快捷切换按钮，搭配独立勾选开关实现切完自动打开，适配单手批量处理流程
3、完善媒体扫描与列表刷新逻辑，尝试接入图片EXIF识别，因技术难度暂时简化适配
4、优化窗口焦点取回逻辑，解决播放器抢占焦点、快捷键失效问题

v2.1.4 优化便捷操作
1、优化NTFS-ADS标签写入逻辑，做到标签更新不改动文件原始修改时间
2、完善批量标签、星级编辑能力，全面支持单条/批量素材属性修改
3、修复部分特殊素材分辨率读取异常、信息缺失问题

v2.1.3 优化便捷操作
1、添加复合筛选体系，完善清晰度、星级、分类多条件联动检索
2、优化关键词模糊匹配算法，大幅提升素材检索精准度
3、新增全局键盘快捷键，支持快捷键快速评分、操作

v2.1.2
1、重写标签统计与盘点核心逻辑，可识别无效、游离标签，完善标签频次统计、标签规整清理功能
2、重构标签管理UI，实现界面组件复用，提升扩展性
v2.1.1
1、优化主界面布局，新增主界面快速重命名功能
2、升级批量打标重命名逻辑，强化容错机制，规避特殊字符、超长文件名报错
3、修复Toplevel弹窗残留问题，解决弹窗导致主窗口无法正常关闭的BUG
v2.1.0
1、新增快捷标签组 1-5、快捷移动目录 1-5，完善二次确认弹窗与执行逻辑
2、全局操作统一优化，全部功能支持单条操作与批量处理
3、新增ADS标签导出、备份与还原功能，解决跨分区、跨设备迁移难题
4、修复极端场景下文件标签数据丢失、读取异常的BUG

v2.0.0 架构重构版本
1、项目复杂度大幅提升，开发模式由面向豆包喊话转为面向电脑开发
2、全盘重构项目架构，优化全局代码逻辑与运行效率
3、磁盘IO全面优化，大量数据改用内存字典预加载，大幅提升扫描与检索速度
4、全新改版管理界面，统一功能布局，支持配置保存与快速切换
5、支持多场景方案切换，可快速切换不同目录组、标签组配置，适配多套素材库管理

v1.6.0
1、新增独立设置界面，全局配置统一收纳管理
2、优化软件整体界面布局与文字展示，统一交互逻辑，提升使用体验

v1.5.0
1、重构标签数据结构，旧题材/演员标签升级为【主内容标签+附加标签】、移除备注标签，
2、开发旧标签数据迁移兼容逻辑，完美兼容v1.0-v1.4历史素材数据
v1.4.0
1、软件定位升级：从小视频管理工具升级为多类型素材整理管理工具
2、新增音频、图片、压缩包、其他文档支持
3、新增目录管理模块，支持批量增删扫描目录
4、完善多格式文件识别、筛选、加载逻辑，统一全类型素材管理规范

v1.3.0
1、新增标签统计可视化和编辑面板，直观展示标签使用频次与分布
2、主界面组件支持自定义布局，界面可灵活定制适配个人习惯

v1.2.0
1、实现标签批量重命名，自动根据星级、标签拼接文件名
2、支持一键逆向还原原始文件名，方便文件迁移与分享
3、优化文件删除逻辑，增加校验与容错，规范素材删除流程

v1.1.0
1、新增多维度组合筛选功能，精准过滤素材库目标文件
2、标签存储体系升级为 NTFS-ADS 备用数据流方案
3、优化标签读写机制，不篡改文件本体、不改动文件属性，数据更安全稳定

v1.0.0 初始功能稳定版本
1、搭建软件基础运行框架，支持主流视频格式识别与解析
2、实现素材目录添加、手动重新扫描、列表刷新基础能力
3、标签体系：题材、演员、评分、备注四维度标签管理
"""
MEDIA_MANAGER_INFO = """
本工具是面向本地音视频、图集素材和额外文件的轻量化资源管理软件，依托 NTFS-ADS 备用数据流做标签存储。针对整理、分类的需求的打磨：方便归类、方便整理、方便打开、方便转移，展开说说
核心功能
1、自动遍历自定义本地目录，区分视频 / 音频 / 图片 / 压缩包 / 自定义文档，调用 MediaInfo、Pillow 自动读取视频图片分辨率进行记录。
2、多维度标签与星级管理：自定义分容分类、附属附加标签库，五星评分标记资源；支持单选 / 批量修改标签、星级，数据持久化存入 ADS 或附属标签文件。
4、复合条件筛选检索：关键词 + 文件类型 + 清晰度 + 星级 + 内容分类 + 附加分类六维联动筛选，精准过滤目标素材。
5、批量命名 ：一键批量将【星级 + 内容 + 附加】拼接为文件名后缀；随时一键逆向剔除标签后缀，还原文件初始名称，方便结合文件管理器搜索转移。
6、标签统计盘点：自动统计在用标签频次，区分系统标准标签、游离无效标签，快速清理不规范标签，统一资源库分类规范。
"""

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


# =====================全局函数【锁定】=====================
def cycle_theme():
    # 循环索引：0=浅色 1=护眼深色 2=VS深色 3=商务低饱和
    if not hasattr(cycle_theme, "idx"):
        cycle_theme.idx = 1

    cycle_theme.idx = (cycle_theme.idx + 1) % 4

    style = ttk.Style()
    style.theme_use("clam")  # 必须保留，否则颜色无效
    idx = cycle_theme.idx

    # ========== 四套配色方案 ==========
    if idx == 0:
        # 浅色清爽
        bg, fg, field, border, select, trough, bar, arrow, hover = (
            "#f7f8fa",
            "#222222",
            "#ffffff",
            "#d2d6dc",
            "#2574cc",
            "#e5e5e5",
            "#2574cc",
            "#333333",
            "#e0e0e0",
        )
    elif idx == 1:
        # 护眼柔和深色
        bg, fg, field, border, select, trough, bar, arrow, hover = (
            "#292c33",
            "#e9ecef",
            "#353942",
            "#4b5059",
            "#365b86",
            "#40444b",
            "#4a8fdb",
            "#cccccc",
            "#444444",
        )
    elif idx == 2:
        # VS Code 经典深色
        bg, fg, field, border, select, trough, bar, arrow, hover = (
            "#1e1e1e",
            "#d4d4d4",
            "#252526",
            "#3e3e42",
            "#094771",
            "#3c3c3c",
            "#007acc",
            "#cccccc",
            "#3a3a3a",
        )
    else:
        # 商务低饱和深色
        bg, fg, field, border, select, trough, bar, arrow, hover = (
            "#24272e",
            "#e2e8f0",
            "#2f333b",
            "#404652",
            "#235487",
            "#373c46",
            "#3182ce",
            "#cccccc",
            "#3d424b",
        )

    style = ttk.Style()
    # ========== 同步主窗口背景 ==========
    try:
        global root
        root.config(bg=bg)
        root.option_add("*Font", NORMAL_FONT)  # 字体
    except:
        pass

    # ========== 全局基础样式 ==========
    style.configure(".", background=bg, foreground=fg, bordercolor=border)
    style.configure("TFrame", background=bg)
    style.configure("TLabel", background=bg, foreground=fg)
    style.configure("TEntry", fieldbackground=field, foreground=fg, bordercolor=border)
    # ========== 字体换用雅黑==========
    style.configure("TLabel", font=NORMAL_FONT)
    style.configure("TButton", font=NORMAL_FONT)
    style.configure("TEntry", font=NORMAL_FONT)
    style.configure("TRadiobutton", font=NORMAL_FONT)
    style.configure("TCheckbutton", font=SMALL_FONT)
    style.configure("Vertical.TScrollbar", gripcount=0)

    # ========== 按钮 (关键：鼠标悬浮颜色) ==========
    style.configure("TButton", background=bg, foreground=fg, bordercolor=border)
    style.map(
        "TButton",
        background=[("active", hover)],
        foreground=[("active", "white" if idx != 0 else "black")],
    )

    # ========== 复选框 / 单选框 ==========
    style.configure("TCheckbutton", background=bg, foreground=fg)
    style.map("TCheckbutton", background=[("active", hover)])

    # ========== Treeview + 底部空白区域 ==========
    style.configure(
        "Treeview", background=bg, fieldbackground=bg, foreground=fg, bordercolor=border
    )
    style.map(
        "Treeview",
        background=[("selected", select)],
        foreground=[("selected", "white")],
    )

    # ========== 下拉框 Combobox ==========
    style.configure(
        "TCombobox",
        fieldbackground=field,
        background=bg,
        foreground=fg,
        arrowcolor=arrow,
        bordercolor=border,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", field)],
        background=[("active", hover)],
    )

    # ========== 进度条 ==========
    style.configure(
        "Horizontal.TProgressbar",
        troughcolor=trough,
        background=bar,
        bordercolor=border,
    )

    # ========== 滚动条 ==========
    style.configure(
        "Vertical.TScrollbar", background=select, troughcolor=field, bordercolor=border
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=select,
        troughcolor=field,
        bordercolor=border,
    )


def zen_msgbox(title, message):
    # 创建弹窗（自动继承主窗口字体）
    msg_win = tk.Toplevel()
    msg_win.title(title)
    msg_win.transient(root)  # 绑定主窗口
    msg_win.grab_set()  # 模态弹窗（必须关掉才能点主窗口）
    msg_win.resizable(False, False)

    # 文字靠左 + 自适应 + 全局字体
    label = tk.Label(
        msg_win,
        text=message,
        font=NORMAL_FONT,  # 自动用全局字体
        justify=tk.LEFT,  # 文字靠左 ✅
        wraplength=380,  # 最大宽度，超过自动换行
        anchor="w",  # 内容靠左
    )
    label.pack(expand=True, fill=tk.BOTH)

    # 按钮（全局字体 + 美观）
    btn = tk.Button(msg_win, text="确定", font=NORMAL_FONT, command=msg_win.destroy)
    btn.pack(pady=(0, 12))

    # 【核心：自适应大小】自动计算窗口尺寸 ✅
    msg_win.update_idletasks()
    w = msg_win.winfo_width()
    h = msg_win.winfo_height()

    # 居中显示
    x = root.winfo_x() + (root.winfo_width() // 2) - (w // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (h // 2)
    msg_win.geometry(f"+{x}+{y}")


# =====================弹窗类【锁定】=====================


class TagsManagerUI(tk.Toplevel):
    def __init__(self, master_root, app_obj, win_title, mode):
        super().__init__(master=master_root)
        self.root = master_root
        self.app = app_obj
        self.title(win_title)
        self.geometry("420x600")
        self.transient(self.root)
        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)
        self.grab_set()
        self.txt = tk.Text(self, padx=10, pady=10)
        self.txt2 = tk.Text(self, padx=10, pady=10)
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
        if not messagebox.askyesno("确认操作", msg):
            return  # 点取消就直接退出
        count_total, count_dict = self.app.scan_media(force_gen=True)
        messagebox.showinfo(
            "操作完成",
            f"文件扫描与数据刷新已执行完毕！\n\n"
            f"本次扫描总文件数：{count_total} 个\n"
            f"符合文件格式要求并完成数据更新：{count_dict} 个\n\n",
        )

    def build_ui(self):
        main_fr = ttk.Frame(self, padding=10)
        main_fr.pack(fill=tk.BOTH, expand=True)
        fr_cfg = ttk.LabelFrame(
            main_fr, text="⚙配置管理：实现对不同目录、文件类型、分类的分组设置"
        )
        fr_cfg.pack(fill=tk.X, pady=4)
        ttk.Button(fr_cfg, text="≣切换配置", command=self.open_config_sel).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(fr_cfg, text="🎨切换配色", command=cycle_theme).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            fr_cfg, text="↺重新扫描文件", command=self.force_refresh_all_file
        ).pack(side=tk.LEFT, padx=2)
        fr_dir = ttk.LabelFrame(main_fr, text="🗁扫描目录")
        fr_dir.pack(fill=tk.X, pady=4)
        self.dir_lb = tk.Listbox(fr_dir, height=4)
        self.dir_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
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
            text="★分类管理：显示设置以及备份、还原全部文件的ads标签，位置是每个目录的ads_tags.txt",
        )
        fr_tag.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(fr_tag, text="每列行数：").pack(side=tk.LEFT, padx=(15, 3))
        ttk.Entry(fr_tag, textvariable=self.str_max_row, width=6).pack(side=tk.LEFT)
        ttk.Button(
            fr_tag, text="批量备份ADStoTXT", command=self.backup_all_folder_ads
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            fr_tag, text="批量还原TXTtoADS", command=self.restore_all_folder_ads
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            fr_tag, text="删除备份TXT", command=self.clear_backup_folder_ads
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

    def toggle_scan_dir(self):
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
        all_folders = self.app.config_data.get("folders", [])
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
                    out_txt = os.path.join(root, "ads_tags.txt")
                    with open(out_txt, "w", encoding="utf-8") as f:
                        json.dump(save_dic, f, ensure_ascii=False, indent=2)
                    total += 1
        messagebox.showinfo("备份完成", f"共生成{total}个ads_tags.txt")

    def restore_all_folder_ads(self):
        all_folders = self.app.config_data.get("folders", [])
        total = 0
        for top_fd in all_folders:
            if not os.path.isdir(top_fd):
                continue
            for root, _, files in os.walk(top_fd):
                txt_path = os.path.join(root, "ads_tags.txt")
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
        messagebox.showinfo("还原完成", f"共读取{total}个目录备份")

    def clear_backup_folder_ads(self):
        all_folders = self.app.config_data.get("folders", [])
        total = 0
        for top_fd in all_folders:
            if not os.path.isdir(top_fd):
                continue
            for root, _, files in os.walk(top_fd):
                txt_path = os.path.join(root, "ads_tags.txt")
                if os.path.exists(txt_path):
                    os.remove(txt_path)
                    total += 1
        messagebox.showinfo("清除完成", f"共清除{total}个ads_tags.txt备份")


class ConfigSelectUI(tk.Toplevel):
    def __init__(self, master_root, app_obj):
        super().__init__(master=master_root)
        self.root, self.app = master_root, app_obj
        self.title("选择配置文件")
        self.geometry("360x300")
        self.resizable(0, 0)
        self.transient(self.root)
        self.grab_set()

        self.lb = tk.Listbox(self)
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
            messagebox.showwarning("提示", "请先选中配置文件")
            return None
        return self.lb.get(sel[0])

    def on_double_click(self, event):  # 新增：双击直接应用
        self.select_cfg()

    def create_new_cfg(self):
        name = simpledialog.askstring("新建配置", "输入配置名称：")
        if not name:
            return
        path = f"{name}_config.ini"
        if os.path.exists(path):
            messagebox.showwarning("提示", "配置已存在")
            return
        self.app.create_default_config(path)
        self.refresh_list()

    def copy_cfg(self):
        src = self._get_select()
        if not src:
            return
        new_name = simpledialog.askstring("复制配置", "新配置名称：")
        if not new_name:
            return
        dst = f"{new_name}_config.ini"
        if os.path.exists(dst):
            messagebox.showwarning("提示", "目标配置已存在")
            return
        shutil.copy2(src, dst)
        self.refresh_list()

    def rename_cfg(self):
        old = self._get_select()
        if not old:
            return
        new_name = simpledialog.askstring("重命名配置", "输入新名称：")
        if not new_name:
            return
        new = f"{new_name}_config.ini"
        if new == old or os.path.exists(new):
            messagebox.showwarning("提示", "名称重复或无修改")
            return
        os.rename(old, new)
        self.refresh_list()

    def del_cfg(self):
        cfg = self._get_select()
        if not cfg:
            return
        if messagebox.askyesno("删除确认", f"确定删除 {cfg} ?"):
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
        self.root.title("媒体分类管理器 V2.1")
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
        self.root.bind("0", lambda e: self.set_file_score(0))
        self.root.bind("1", lambda e: self.set_file_score(1))
        self.root.bind("2", lambda e: self.set_file_score(2))
        self.root.bind("3", lambda e: self.set_file_score(3))
        self.root.bind("4", lambda e: self.set_file_score(4))
        self.root.bind("5", lambda e: self.set_file_score(5))
        self.root.bind("7", lambda e: self.prev_item())
        self.root.bind("8", lambda e: self.next_item())
        # 刷新标签、媒体文件
        self.rebuild_all_checkbox()
        self.refresh_tags_list()
        self.scan_media()  # 的确需要

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
            "folders": [os.getcwd()],
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
        TagsManagerUI(self.root, self, "编辑分类标签", "EDIT")

    def open_calc_tag(self):
        TagsManagerUI(self.root, self, "统计分类标签", "CALC")

    def open_about(self):
        AboutUI(self.root)

    def build_main_ui(self):
        # 顶部按钮行
        top_fr = ttk.Frame(self.root)
        top_fr.pack(fill=tk.X, padx=5, pady=5)
        btns = [
            ("⚙设置", self.open_setting),
            ("𝒾 关于", self.open_about),
            ("▦标签统计", self.open_calc_tag),
            ("🖍标签编辑", self.open_edit_tag),
            ("▤文件名标记", self.batch_rename_files),
            ("↺标记还原", self.restore_original_name),
            ("🗁打开目录", self.open_folder_by_sel),
            # ("🗑删除文件", self.delete_selected_file),
        ]
        for txt, cmd in btns:
            ttk.Button(top_fr, text=txt, command=cmd).pack(side=tk.LEFT, padx=3)
        ttk.Label(top_fr, text="文件名：").pack(side=tk.LEFT, padx=(10, 2))
        self.rename_entry = ttk.Entry(top_fr, width=28)
        self.rename_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(top_fr, text="🖍执行改名", width=10, command=self.single_rename).pack(
            side=tk.LEFT
        )
        ##        ttk.Button(top_fr,text="⚙设置",width=9,command=self.open_setting).pack(side=tk.LEFT)
        ##        ttk.Button(top_fr,text="𝒾 关于",width=9,command=self.open_about).pack(side=tk.LEFT,padx=3)

        # 筛选+排序行
        filter_fr = ttk.Frame(self.root)
        filter_fr.pack(fill=tk.X, padx=5, pady=3)
        ttk.Label(filter_fr, text="筛选 关键字：").pack(side=tk.LEFT)
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
        self.cb_type["values"] = ["全部", "视频", "音频", "图片", "压缩包", "其他文档"]
        self.cb_type.pack(side=tk.LEFT)
        self.cb_type.bind("<<ComboboxSelected>>", lambda e: self.refresh_file_list())
        ttk.Button(filter_fr, text="清空筛选", command=self.clear_all_filter).pack(
            side=tk.LEFT, padx=5
        )
        # 排序下拉
        ttk.Label(filter_fr, text="排序：").pack(side=tk.LEFT, padx=(8, 2))
        self.cb_sort = ttk.Combobox(
            filter_fr, textvariable=self.var_sort, state="readonly", width=9
        )
        self.cb_sort["values"] = [
            "默认顺序",
            "文件名升序",
            "文件名降序",
            "大小升序",
            "大小降序",
            "星级升序",
            "星级降序",
        ]
        self.cb_sort.pack(side=tk.LEFT)
        self.cb_sort.bind("<<ComboboxSelected>>", lambda e: self.refresh_file_list())

        # 左右分割面板
        pan = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        pan.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_fr = ttk.Frame(pan)
        pan.add(left_fr, weight=4)
        right_fr = ttk.Frame(pan, width=320)
        pan.add(right_fr, weight=1)
        # 左侧列表+滚动条
        tree_wrap = ttk.Frame(left_fr)
        tree_wrap.pack(fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(tree_wrap, orient=tk.VERTICAL)
        self.file_tree = ttk.Treeview(
            tree_wrap,
            columns=("path", "size", "reso", "defi", "score"),
            show="headings",
            selectmode="extended",
            yscrollcommand=vsb.set,
        )
        vsb.config(command=self.file_tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_tree.heading("path", text="文件路径")
        self.file_tree.heading("size", text="文件大小(单击)")
        self.file_tree.heading("reso", text="分辨率")
        self.file_tree.heading("defi", text="清晰度")
        self.file_tree.heading("score", text="星级")
        self.file_tree.column("path", width=420, stretch=tk.YES)
        self.file_tree.column("size", width=100, stretch=tk.NO)
        self.file_tree.column("reso", width=80, stretch=tk.NO)
        self.file_tree.column("defi", width=60, stretch=tk.NO)
        self.file_tree.column("score", width=60, stretch=tk.NO)
        self.file_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.file_tree.bind("<ButtonRelease-1>", self.click_size_open_file)
        self.file_tree.bind("<Double-1>", self.click_tree_open)
        # 右侧面板
        rp = 5
        rp_line = rp + 10
        fr_nav = ttk.Frame(right_fr)
        fr_nav.pack(pady=3, anchor="w")
        ttk.Button(fr_nav, text="⬆上一个", width=8, command=self.prev_item).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(fr_nav, text="⬇下一个", width=8, command=self.next_item).pack(
            side=tk.LEFT, padx=2
        )
        self.auto_open_flag = tk.BooleanVar(value=True)
        ttk.Checkbutton(fr_nav, text="自动打开", variable=self.auto_open_flag).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=rp_line, pady=(1, 1)
        )  # 分割线
        ttk.Label(right_fr, text="★星级打分").pack(anchor=tk.W, padx=rp, pady=(1, 1))
        score_fr = ttk.Frame(right_fr)
        score_fr.pack(padx=rp, pady=1, fill=tk.X)
        self.score_btn_list = []
        for i in range(5):
            b = tk.Button(
                score_fr,
                text="★",
                width=3,
                font=("宋体", 11),
                fg="gray",
                command=lambda n=i + 1: self.set_file_score(n),
            )
            b.pack(side=tk.LEFT, padx=2)
            self.score_btn_list.append(b)

        lb_group = ttk.Label(right_fr, text="▤快捷分类组(左键应用/右键保存)")
        lb_group.pack(anchor=tk.W, padx=rp, pady=(1, 1))
        lb_group.bind("<Button-1>", self.show_all_presets)
        preset_fr = ttk.Frame(right_fr)
        preset_fr.pack(padx=rp, pady=2, fill=tk.X)
        for i in range(5):
            btn = ttk.Button(preset_fr, text=str(i + 1), width=3)
            btn.bind("<Button-1>", lambda e, idx=i: self.apply_preset(idx))
            btn.bind("<Button-3>", lambda e, idx=i: self.save_preset(idx))
            btn.pack(side=tk.LEFT, padx=2)
        if True:
            btn = ttk.Button(preset_fr, text="清除", width=5, command=self.clear_preset)
            btn.pack(side=tk.LEFT, padx=2)
        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=rp_line, pady=(1, 1)
        )  # 分割线
        ttk.Label(right_fr, text="⊟内容分类（题材、特色等）").pack(
            anchor=tk.W, padx=rp, pady=(1, 1)
        )
        self.tagm_inner = ttk.Frame(right_fr)
        self.tagm_inner.pack(padx=rp, pady=2, fill=tk.X)
        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=rp_line, pady=(1, 1)
        )  # 分割线
        ttk.Label(right_fr, text="⊟附加分类（演员、作者、自定义等）").pack(
            anchor=tk.W, padx=rp, pady=(1, 1)
        )
        self.tage_inner = ttk.Frame(right_fr)
        self.tage_inner.pack(padx=rp, pady=2, fill=tk.X)
        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=rp_line, pady=(1,)
        )  # 分割线
        lb_move = ttk.Label(right_fr, text="🗁快捷移动目录(左键应用/右键设置)")
        lb_move.pack(anchor=tk.W, padx=rp, pady=(1, 1))
        lb_move.bind("<Button-1>", self.show_move_dir)

        move_fr = ttk.Frame(right_fr)
        move_fr.pack(padx=rp, pady=2, fill=tk.X)
        for i in range(5):
            btn = ttk.Button(move_fr, text=str(i + 1), width=3)
            btn.bind("<Button-1>", lambda e, idx=i: self.move_to_dir(idx))
            btn.bind("<Button-3>", lambda e, idx=i: self.set_move_dir(idx))
            btn.pack(side=tk.LEFT, padx=2)
        if True:
            btn = ttk.Button(
                move_fr, text="🗑删除", width=6, command=self.delete_selected_file
            )
            btn.pack(side=tk.LEFT, padx=2)

    # 上一个条目
    def prev_item(self):
        s = self.file_tree.selection()
        if not s:
            return
        lst = self.file_tree.get_children()
        i = self.file_tree.index(s[0])
        if i > 0:
            self.file_tree.selection_set(lst[i - 1])
            self.file_tree.focus(lst[i - 1])
        s = self.file_tree.selection()
        if self.auto_open_flag.get():
            os.startfile(self.file_tree.item(s[0], "values")[0])

    # 下一个条目
    def next_item(self):
        s = self.file_tree.selection()
        if not s:
            return
        lst = self.file_tree.get_children()
        i = self.file_tree.index(s[0])
        if i + 1 < len(lst):
            it = lst[i + 1]
            self.file_tree.selection_set(it)
            self.file_tree.focus(it)
        s = self.file_tree.selection()
        if self.auto_open_flag.get():
            os.startfile(self.file_tree.item(s[0], "values")[0])

    def refresh_tags_list(self):
        self.cb_tagm["values"] = ["全部", "未分类"] + self.config_data.get(
            "tag_main", []
        )
        self.cb_tage["values"] = ["全部", "未分类"] + self.config_data.get(
            "tag_extra", []
        )

    def rebuild_all_checkbox(self):
        self.refresh_tagm_check()
        self.refresh_tage_check()

    def refresh_tagm_check(self):
        if not self.tagm_inner.winfo_exists():
            return
        for w in self.tagm_inner.winfo_children():
            w.destroy()
        self.tag_main_check_map.clear()
        ths = self.config_data.get("tag_main", [])
        rowcnt = self.config_data.get("tag_max_row", DEFAULT_MAX_ROW)
        import math

        col = math.ceil(len(ths) / rowcnt)
        idx = 0
        for c in range(col):
            for r in range(rowcnt):
                if idx >= len(ths):
                    break
                n = ths[idx]
                v = tk.BooleanVar()
                cb = ttk.Checkbutton(
                    self.tagm_inner,
                    text=n,
                    variable=v,
                    command=lambda x=n, var=v: self.toggle_tagm(x, var),
                )
                cb.grid(row=r, column=c, sticky="w")
                self.tag_main_check_map[n] = v
                idx += 1
        self.tagm_inner.update_idletasks()

    def refresh_tage_check(self):
        if not self.tage_inner.winfo_exists():
            return
        for w in self.tage_inner.winfo_children():
            w.destroy()
        self.tag_extra_check_map.clear()
        acs = self.config_data.get("tag_extra", [])
        rowcnt = self.config_data.get("tag_max_row", DEFAULT_MAX_ROW)
        import math

        col = math.ceil(len(acs) / rowcnt)
        idx = 0
        for c in range(col):
            for r in range(rowcnt):
                if idx >= len(acs):
                    break
                n = acs[idx]
                v = tk.BooleanVar()
                cb = ttk.Checkbutton(
                    self.tage_inner,
                    text=n,
                    variable=v,
                    command=lambda x=n, var=v: self.toggle_tage(x, var),
                )
                cb.grid(row=r, column=c, sticky="w")
                self.tag_extra_check_map[n] = v
                idx += 1
        self.tage_inner.update_idletasks()

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
        messagebox.showinfo("全部快捷目录", info.strip())

    def move_to_dir(self, idx):
        sel = self.file_tree.selection()
        if not sel:
            return
        dst = os.path.normpath(self.config_data.get(f"move_{idx+1}", ""))
        if not os.path.isdir(dst):
            messagebox.showwarning("提示", "目录未配置，右键按钮设置")
            return
        # 移动前确认
        if not messagebox.askyesno(
            "确认移动", f"确定要将选中文件移动到目录：\n【{dst}】\n吗？"
        ):
            return
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
            messagebox.showinfo("提示", "无需移动（文件已在目标目录）")
            return
        # 如果有需要覆盖的文件 → 列出来让用户确认
        if overwrite_list:
            files = "\n".join(overwrite_list[:10])
            if len(overwrite_list) > 10:
                files += f"\n...等 {len(overwrite_list)} 个文件"
            if not messagebox.askyesno(
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
                messagebox.showerror("移动失败", f"{os.path.basename(src)}\n{str(e)}")

        ##        self.scan_media()

        messagebox.showinfo("完成", f"成功移动 {success} 个文件")
        self.refresh_file_list()

    def save_preset(self, idx):
        if not self.current_select_path:
            messagebox.showinfo("提示", "请先选中一个文件再保存模板")
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
        if not messagebox.askyesno(
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
        info = "📋 当前全部快捷分类组模板：\n\n"
        for i in range(5):
            key = f"preset_{i+1}"
            preset = self.config_data.get(key, {})
            main = " | ".join(preset.get("tag_main", [])) or "空"
            extra = " | ".join(preset.get("tag_extra", [])) or "空"
            info += f"分类组{i+1}\n内容分类：[{main}]\n附加分类：[{extra}]\n\n"
        messagebox.showwarning("全部快捷分类组模板一览", info)

    def apply_preset(self, idx):
        sel = self.file_tree.selection()
        if not sel:
            return
        cnt = len(sel)
        if idx == "C":
            ths = []
            acs = []
            msg = f"确定对【{cnt}个文件】清空全部分类标签并重置评分？"
        else:
            preset = self.config_data.get(f"preset_{idx+1}", {})
            ths = preset.get("tag_main", [])
            acs = preset.get("tag_extra", [])
            if not ths and not acs:
                messagebox.showwarning(
                    "提示",
                    f"当前快捷分类模板{idx+1}为空，请设置内容分类和附加分类后以右键点击按钮保存分类组",
                )
                return
            main_str = " | ".join(ths) if ths else "无"
            extra_str = " | ".join(acs) if acs else "无"
            msg = f"确定要对【{cnt}个文件】批量设置标签吗？\n\n内容分类：{main_str}\n附加分类：{extra_str}"
        if not messagebox.askyesno("确认操作", msg):
            return
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            info = self.media_dict[p]
            info["tag_main"] = ths.copy()
            info["tag_extra"] = acs.copy()
            if idx == "C":
                info["score"] = 0
            self.save_file_meta(p, info)
        self.on_tree_select(None)

    def clear_preset(self):
        sel = self.file_tree.selection()
        if not sel:
            return
        cnt = len(sel)
        msg = f"确定对【{cnt}个文件】清空全部分类标签并重置评分？"
        if not messagebox.askyesno("确认操作", msg):
            return
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            info = self.media_dict[p]
            info["tag_main"] = []
            info["tag_extra"] = []
            info["score"] = 0
            self.save_file_meta(p, info)
        self.on_tree_select(None)

    def set_file_score(self, num):
        sel = self.file_tree.selection()
        if not sel:
            return
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            self.media_dict[p]["score"] = num
            self.save_file_meta(p, self.media_dict[p])
        self.on_tree_select(None)
        self.refresh_file_list(self.current_select_path)

    def toggle_tagm(self, name, var):
        sel = self.file_tree.selection()
        if not sel:
            var.set(False)
            return
        stat = var.get()
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            lst = self.media_dict[p]["tag_main"]
            if stat and name not in lst:
                lst.append(name)
            elif not stat and name in lst:
                lst.remove(name)
            self.save_file_meta(p, self.media_dict[p])
        # 切换分类不用刷新

    ##        self.refresh_file_list(self.current_select_path)
    def toggle_tage(self, name, var):
        sel = self.file_tree.selection()
        if not sel:
            var.set(False)
            return
        stat = var.get()
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            lst = self.media_dict[p]["tag_extra"]
            if stat and name not in lst:
                lst.append(name)
            elif not stat and name in lst:
                lst.remove(name)
            self.save_file_meta(p, self.media_dict[p])
        # 切换分类不用刷新

    ##        self.refresh_file_list(self.current_select_path)

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
        p = os.path.normpath(self.file_tree.item(sel[0], "values")[0])
        self.current_select_path = p
        info = self.media_dict[p]
        self.rename_entry.delete(0, tk.END)
        self.rename_entry.insert(0, os.path.splitext(info["name"])[0])
        for i in range(5):
            self.score_btn_list[i].config(fg="gold" if i < info["score"] else "gray")
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
            return {
                "score": 0,
                "tag_main": [],
                "tag_extra": [],
                "resolution": "",
                "definition": "",
            }

    def save_file_meta(self, p, data):
        fp = os.path.normpath(p)
        ads = fp + ADS_SUFFIX
        try:
            st = os.stat(fp) if os.path.exists(fp) else None
            with open(ads, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            if st:
                os.utime(ads, (st.st_atime, st.st_mtime))
        except Exception:
            pass

    # 竖屏取短边算清晰度【V2.1修订】
    def get_video_def_info(self, p):
        if not MediaInfo:
            return ("", "", "")
        try:
            mi = MediaInfo.parse(p)
            for tr in mi.tracks:
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
            return ("识别出错", "未知", "")
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
        ev = cfg.get("enable_video", True)
        ea = cfg.get("enable_audio", False)
        ei = cfg.get("enable_image", False)
        ez = cfg.get("enable_archive", False)
        eo = cfg.get("enable_other", False)
        o_suf = [
            x.strip().lower()
            for x in cfg.get("other_suffix", OTHER_DEFAULT_SUFFIX).split(";")
            if x.strip()
        ]
        file_count = 0
        # 针对folders新旧模式切换
        if cfg.get("folders", []):
            if isinstance(cfg["folders"], list):
                tmp = {}
                for item in cfg["folders"]:
                    if isinstance(item, str):
                        tmp[item] = True
                cfg["folders"] = tmp

        for dp in cfg.get("folders", {}):
            if not cfg["folders"][dp]:
                continue  # 不勾选就跳过
            dp = os.path.normpath(dp)
            if not os.path.isdir(dp):
                continue
            for root, _, files in os.walk(dp):
                for fn in files:
                    file_count += 1
                    full = os.path.normpath(os.path.join(root, fn))
                    ext = os.path.splitext(fn.lower())[-1]
                    ftype = ""
                    if ev and ext in VIDEO_FORMATS:
                        ftype = "视频"
                    elif ea and ext in AUDIO_FORMATS:
                        ftype = "音频"
                    elif ei and ext in IMAGE_FORMATS:
                        ftype = "图片"
                    elif ez and ext in ZIP_FORMATS:
                        ftype = "压缩包"
                    elif eo and ext in o_suf:
                        ftype = "其他文档"
                    if not ftype:
                        continue
                    sz = os.path.getsize(full)
                    meta = self.load_file_meta(full)
                    res, defi, info = None, None, None
                    if ftype == "视频":
                        # if ftype=="视频" :#用于手动处理，刷新清晰度
                        res, defi, info = (
                            meta.get("resolution", ""),
                            meta.get("definition", ""),
                            meta.get("video_info", ""),
                        )
                        meta = {
                            "name": fn,
                            "size": sz,
                            "type": ftype,
                            "score": meta["score"],
                            "tag_main": meta["tag_main"],
                            "tag_extra": meta["tag_extra"],
                            "resolution": res,
                            "definition": defi,
                            "video_info": info,
                        }
                        if not (res or defi or info) or force_gen:
                            (
                                meta["resolution"],
                                meta["definition"],
                                meta["video_info"],
                            ) = self.get_video_def_info(full)
                            self.save_file_meta(full, meta)
                        self.media_dict[full] = meta
                    elif ftype == "图片":
                        res, defi, info = (
                            meta.get("resolution", ""),
                            meta.get("definition", ""),
                            meta.get("image_info", ""),
                        )
                        meta = {
                            "name": fn,
                            "size": sz,
                            "type": ftype,
                            "score": meta["score"],
                            "tag_main": meta["tag_main"],
                            "tag_extra": meta["tag_extra"],
                            "resolution": res,
                            "definition": defi,
                            "image_info": info,
                        }
                        if not (res or defi or info) or force_gen:
                            (
                                meta["resolution"],
                                meta["definition"],
                                meta["image_info"],
                            ) = self.get_image_def_info(full)
                            self.save_file_meta(full, meta)
                        self.media_dict[full] = meta
                    else:
                        self.media_dict[full] = {
                            "name": fn,
                            "size": sz,
                            "type": ftype,
                            "score": meta["score"],
                            "tag_main": meta["tag_main"],
                            "tag_extra": meta["tag_extra"],
                            "resolution": "无",
                            "definition": "未知",
                        }
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
            mb = info["size"] / 1024 / 1024
            star = "★" * info["score"]
            iid = self.file_tree.insert(
                "",
                "end",
                values=(
                    p,
                    f"{mb:.2f} MB",
                    info["resolution"],
                    info["definition"],
                    star,
                ),
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

    def click_size_open_file(self, e):
        col = self.file_tree.identify_column(e.x)
        if col == "#2":
            sel = self.file_tree.selection()
            if sel:
                p = os.path.normpath(self.file_tree.item(sel[0], "values")[0])
                os.startfile(p)

    def click_tree_open(self, e):
        col = self.file_tree.identify_column(e.x)
        sel = self.file_tree.selection()
        if sel:
            p = os.path.normpath(self.file_tree.item(sel[0], "values")[0])
            if col == "#1" or col == "#2":
                os.startfile(p)
            else:
                os.startfile(os.path.dirname(p))

    def open_folder_by_sel(self):
        sel = self.file_tree.selection()
        if not sel:
            return
        p = os.path.normpath(self.file_tree.item(sel[0], "values")[0])
        os.startfile(os.path.dirname(p))

    def delete_selected_file(self):
        sel = self.file_tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("确认", "删除选中文件？"):
            return
        for item in sel:
            p = os.path.normpath(self.file_tree.item(item, "values")[0])
            try:
                os.remove(p)
                ads = p + ADS_SUFFIX
                if os.path.exists(ads):
                    os.remove(ads)
                if p in self.media_dict:
                    del self.media_dict[p]
            except Exception:
                pass
        self.refresh_file_list()

    # 【V2.1修订：改名成功自动选中新文件】
    def single_rename(self):
        if not self.current_select_path or len(self.file_tree.selection()) != 1:
            messagebox.showwarning("提示", "请单选一个文件")
            return
        new_name = self.rename_entry.get().strip()
        if not new_name:
            messagebox.showwarning("提示", "名称不能为空")
            return
        old_p = os.path.normpath(self.current_select_path)
        ext = os.path.splitext(old_p)[1]
        dir_p = os.path.dirname(old_p)
        new_full = os.path.normpath(os.path.join(dir_p, new_name + ext))
        idx = 1
        while os.path.exists(new_full):
            new_full = os.path.normpath(
                os.path.join(dir_p, f"{new_name}{idx:02d}{ext}")
            )
            idx += 1
        try:
            os.rename(old_p, new_full)
            ads_old = old_p + ADS_SUFFIX
            ads_new = new_full + ADS_SUFFIX
            if os.path.exists(ads_old):
                os.rename(ads_old, ads_new)
            self.media_dict[new_full] = self.media_dict.pop(old_p)
            # 刷新并选中新路径
            self.refresh_file_list(new_full)
        except Exception as e:
            messagebox.showerror("改名失败", str(e))

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
        messagebox.showinfo("批量完成", f"成功{cnt}个")

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
            ths = [x for x in rest if x in all_th]
            acs = [x for x in rest if x in all_ac]
            info = self.media_dict[p]
            info["score"] = sc
            info["tag_main"] = ths
            info["tag_extra"] = acs
            self.save_file_meta(p, info)
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
        messagebox.showinfo("还原完成", f"{cnt}个文件已去掉标签后缀")


if __name__ == "__main__":
    root = tk.Tk()
    app = MediaManagerApp(root)
    # cycle_theme()
    root.mainloop()
