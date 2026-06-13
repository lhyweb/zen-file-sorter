import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import re
from collections import Counter
try:
    from pymediainfo import MediaInfo
except ImportError:
    MediaInfo = None

# =====================全局常量【锁定】=====================
DEFAULT_CONFIG_NAME = "config.ini"
VIDEO_FORMATS = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.rmvb', '.wmv')
AUDIO_FORMATS = ('.mp3', '.wav', '.flac', '.ape', '.ogg')
IMAGE_FORMATS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
ZIP_FORMATS = ('.zip', '.rar', '.7z')
OTHER_DEFAULT_SUFFIX = ".doc;.txt;.pdf"
ADS_SUFFIX = ":zen_mv_data"
DEFAULT_MAX_ROW = 10

DEFAULT_THEMES = ["动作", "喜剧", "爱情", "悬疑", "科幻", "仙侠", "刑侦", "纪实", "动画"]
DEFAULT_ACTORS = ["大陆男星", "大陆女星", "港台男星", "港台女星", "欧美演员"]

# 清晰度：取画面短边判定，横竖屏通用【V2.1修订】
DEF_ALL = ["全部", "4K", "2K", "1080P", "720P", "SD", "LD", "未知", "非视频"]
def get_def_by_height(short_px):
    if short_px >= 2160:
        return "4K"
    elif 1440 < short_px < 2160:
        return "2K"
    elif 1080 < short_px <= 1440:
        return "1080P"
    elif 720 < short_px <= 1080:
        return "720P"
    elif 480 < short_px <= 720:
        return "SD"
    else:
        return "LD"

# =====================弹窗类【锁定】=====================
class TagEditWin(tk.Toplevel):
    def __init__(self, master_root, app_obj, win_title, cfg_key):
        super().__init__(master=master_root)
        self.root = master_root
        self.app = app_obj
        self.cfg_key = cfg_key
        self.title(win_title)
        self.geometry("450x400")
        self.minsize(300, 250)
        self.transient(self.root)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.save_and_close)
        self.txt = tk.Text(self)
        self.txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        data_list = self.app.config_data.get(cfg_key, [])
        self.txt.insert("1.0", "\n".join(data_list))
    def save_and_close(self):
        content = self.txt.get("1.0", tk.END).strip()
        new_list = [x.strip() for x in content.splitlines() if x.strip()]
        self.app.config_data[self.cfg_key] = new_list
        self.app.save_config()
        self.app.rebuild_all_checkbox()
        self.destroy()

class AboutWin(tk.Toplevel):
    def __init__(self, master_root):
        super().__init__(master=master_root)
        self.root = master_root
        self.title("关于本软件")
        self.geometry("520x320")
        self.resizable(False, False)
        self.transient(self.root)
        self.grab_set()
        txt = tk.Text(self, font=("微软雅黑",10))
        txt.pack(fill=tk.BOTH, expand=True, padx=12,pady=12)
        info = """媒体文件分类管理工具v2.1.3
本工具是面向本地音视频、图集素材的轻量化资源管理软件，依托 NTFS-ADS 备用数据流做标签存储。
核心功能
1、自动遍历自定义本地目录，区分视频 / 音频 / 图片 / 压缩包 / 自定义文档，调用 MediaInfo 自动读取视频分辨率，通过画面短边算法自动判定清晰度（4K/2K/1080P/720P 等）。
2、多维度标签与星级管理：自定义分容分类、附属附加标签库，五星评分标记资源；支持单选 / 批量修改标签、星级，数据持久化存入 ADS 或附属标签文件。
4、复合条件筛选检索：关键词 + 文件类型 + 清晰度 + 星级 + 题材 + 演员六维联动筛选，快速从成千上万杂乱资源里精准过滤目标素材。
5、批量命名 ：一键批量将【星级 + 题材 + 演员】拼接为文件名后缀；随时一键逆向剔除标签后缀，还原文件初始名称，整理零风险。
6、标签统计盘点：自动统计在用标签频次，区分系统标准标签、游离无效标签，快速清理不规范标签，统一资源库分类规范。
change log：
v2.1.3
1、完善全部界面文字
2、完善了筛选条件和逻辑
3、完善了标签统计
"""
        txt.insert("1.0",info)
        txt.config(state=tk.DISABLED)

class ConfigSelectWin(tk.Toplevel):
    def __init__(self, master_root, app_obj):
        super().__init__(master=master_root)
        self.root = master_root
        self.app = app_obj
        self.title("选择配置文件")
        self.geometry("360x300")
        self.resizable(False,False)
        self.transient(self.root)
        self.grab_set()
        self.lb = tk.Listbox(self)
        self.lb.pack(fill=tk.BOTH, expand=True, padx=10,pady=10)
        btn_fr = ttk.Frame(self)
        btn_fr.pack(pady=5)
        ttk.Button(btn_fr,text="新建配置",command=self.create_new_cfg).grid(row=0,column=0,padx=6)
        ttk.Button(btn_fr,text="选用配置",command=self.select_cfg).grid(row=0,column=1,padx=6)
        self.refresh_list()
    def refresh_list(self):
        self.lb.delete(0,tk.END)
        for f in os.listdir("."):
            if f.lower().endswith(".ini"):
                self.lb.insert(tk.END,f)
    def create_new_cfg(self):
        name = simpledialog.askstring("新建配置","配置名：")
        if not name:return
        fn=f"{name}.ini"
        if os.path.exists(fn):
            messagebox.showwarning("提示","文件已存在")
            return
        self.app.create_default_config(fn)
        self.refresh_list()
    def select_cfg(self):
        idx=self.lb.curselection()
        if not idx:return
        sel=self.lb.get(idx[0])
        self.app.config_file=sel
        self.app.config_data=self.app.load_config()
        if self.app.setting_win:self.app.setting_win.destroy()
        self.destroy()
        self.app.rebuild_all_checkbox()
        self.app.scan_media()

class SettingDialog(tk.Toplevel):
    def __init__(self, master_root, app_obj):
        super().__init__(master=master_root)
        self.root=master_root
        self.app=app_obj
        self.title("软件设置")
        self.geometry("720x460")
        self.minsize(680,420)
        self.transient(self.root)
        self.grab_set()
        self.var_video=tk.BooleanVar()
        self.var_audio=tk.BooleanVar()
        self.var_img=tk.BooleanVar()
        self.var_zip=tk.BooleanVar()
        self.var_other=tk.BooleanVar()
        self.str_other_suffix=tk.StringVar()
        self.str_max_row=tk.StringVar()
        self.build_ui()
        self.load_data()
    def open_edit_theme(self):TagEditWin(self.root,self.app,"编辑内容分类","themes")
    def open_edit_actor(self):TagEditWin(self.root,self.app,"编辑演员分类","actors")
    def open_config_sel(self):ConfigSelectWin(self.root,self.app)
    def open_about(self):AboutWin(self.root)
    def build_ui(self):
        main_fr=ttk.Frame(self,padding=10)
        main_fr.pack(fill=tk.BOTH,expand=True)
        fr_cfg=ttk.LabelFrame(main_fr,text="配置管理")
        fr_cfg.pack(fill=tk.X,pady=4)
        ttk.Button(fr_cfg,text="切换配置",command=self.open_config_sel).pack(side=tk.LEFT,padx=5)
        ttk.Button(fr_cfg,text="批量备份ADS",command=self.backup_all_folder_ads).pack(side=tk.LEFT,padx=5)
        ttk.Button(fr_cfg,text="批量还原ADS",command=self.restore_all_folder_ads).pack(side=tk.LEFT,padx=5)
        ttk.Button(fr_cfg,text="关于",command=self.open_about).pack(side=tk.LEFT,padx=5)
        fr_dir=ttk.LabelFrame(main_fr,text="扫描目录")
        fr_dir.pack(fill=tk.X,pady=4)
        self.dir_lb=tk.Listbox(fr_dir,height=4)
        self.dir_lb.pack(side=tk.LEFT,fill=tk.BOTH,expand=True,padx=5)
        dir_btn=ttk.Frame(fr_dir)
        dir_btn.pack(side=tk.RIGHT,padx=5)
        ttk.Button(dir_btn,text="添加目录",command=self.add_scan_dir).pack(fill=tk.X,pady=2)
        ttk.Button(dir_btn,text="删除选中",command=self.del_scan_dir).pack(fill=tk.X,pady=2)
        fr_type=ttk.LabelFrame(main_fr,text="扫描格式")
        fr_type.pack(fill=tk.X,pady=4)
        line1=ttk.Frame(fr_type)
        line1.pack(anchor=tk.W,pady=3)
        ttk.Checkbutton(line1,text="视频",var=self.var_video,command=self.save_now).pack(side=tk.LEFT,padx=5)
        ttk.Checkbutton(line1,text="音频",var=self.var_audio,command=self.save_now).pack(side=tk.LEFT,padx=5)
        ttk.Checkbutton(line1,text="图片",var=self.var_img,command=self.save_now).pack(side=tk.LEFT,padx=5)
        ttk.Checkbutton(line1,text="压缩包",var=self.var_zip,command=self.save_now).pack(side=tk.LEFT,padx=5)
        line2=ttk.Frame(fr_type)
        line2.pack(anchor=tk.W,pady=3)
        ttk.Checkbutton(line2,text="其他",var=self.var_other,command=self.save_now).pack(side=tk.LEFT,padx=5)
        ttk.Entry(line2,textvariable=self.str_other_suffix,width=38).pack(side=tk.LEFT,padx=3)
        ttk.Label(line2,text="后缀;分隔").pack(side=tk.LEFT)
        fr_tag=ttk.LabelFrame(main_fr,text="标签设置")
        fr_tag.pack(fill=tk.X,pady=(8,0))
        ttk.Button(fr_tag,text="编辑内容分类",command=self.open_edit_theme).pack(side=tk.LEFT,padx=5)
        ttk.Button(fr_tag,text="编辑附加分类",command=self.open_edit_actor).pack(side=tk.LEFT,padx=5)
        ttk.Label(fr_tag,text="标签每行数量：").pack(side=tk.LEFT,padx=(15,3))
        ttk.Entry(fr_tag,textvariable=self.str_max_row,width=6).pack(side=tk.LEFT)
    def load_data(self):
        cfg=self.app.config_data
        self.var_video.set(cfg.get("enable_video",True))
        self.var_audio.set(cfg.get("enable_audio",False))
        self.var_img.set(cfg.get("enable_image",False))
        self.var_zip.set(cfg.get("enable_archive",False))
        self.var_other.set(cfg.get("enable_other",False))
        self.str_other_suffix.set(cfg.get("other_suffix",OTHER_DEFAULT_SUFFIX))
        self.str_max_row.set(str(cfg.get("tag_max_row",DEFAULT_MAX_ROW)))
        self.dir_lb.delete(0,tk.END)
        for d in cfg.get("folders",[]):
            self.dir_lb.insert(tk.END,d)
    def add_scan_dir(self):
        d=filedialog.askdirectory()
        if not d:return
        dirs=self.app.config_data.get("folders",[])
        if d not in dirs:
            dirs.append(d)
            self.app.config_data["folders"]=dirs
            self.save_now()
            self.dir_lb.insert(tk.END,d)
    def del_scan_dir(self):
        s=self.dir_lb.curselection()
        if not s:return
        val=self.dir_lb.get(s[0])
        dirs=self.app.config_data.get("folders",[])
        if val in dirs:
            dirs.remove(val)
            self.app.config_data["folders"]=dirs
            self.save_now()
            self.dir_lb.delete(s[0])
    def save_now(self):
        cfg=self.app.config_data
        cfg["enable_video"]=self.var_video.get()
        cfg["enable_audio"]=self.var_audio.get()
        cfg["enable_image"]=self.var_img.get()
        cfg["enable_archive"]=self.var_zip.get()
        cfg["enable_other"]=self.var_other.get()
        cfg["other_suffix"]=self.str_other_suffix.get().strip()
        try:
            row=int(self.str_max_row.get())
            if row<1:row=DEFAULT_MAX_ROW
        except:row=DEFAULT_MAX_ROW
        cfg["tag_max_row"]=row
        self.app.save_config()
        self.app.rebuild_all_checkbox()
        self.app.scan_media()


        
    def backup_all_folder_ads(self):
        import json
        all_folders = self.app.config_data.get("folders", [])
        cnt = 0
        for fd in all_folders:
            if not os.path.isdir(fd):
                continue
            save_dic = {}
            for root, _, files in os.walk(fd):
                for fn in files:
                    fullpath = os.path.join(root, fn)
                    meta = self.app.load_file_meta(fullpath)
                    if meta["score"] or meta["themes"] or meta["actors"]:
                        save_dic[fn] = meta
            out_txt = os.path.join(fd, "ads_tags.txt")
            with open(out_txt, "w", encoding="utf-8") as f:
                json.dump(save_dic, f, ensure_ascii=False, indent=2)
            cnt += 1
        messagebox.showinfo("备份完成", f"共{cnt}个目录已生成ads_tags.txt")

    def restore_all_folder_ads(self):
        import json
        all_folders = self.app.config_data.get("folders", [])
        cnt = 0
        for fd in all_folders:
            txt_path = os.path.join(fd, "ads_tags.txt")
            if not os.path.exists(txt_path):
                continue
            try:
                with open(txt_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                continue
            for fname, meta in data.items():
                full = os.path.join(fd, fname)
                if os.path.isfile(full):
                    self.app.save_file_meta(full, meta)
            cnt += 1
        self.app.scan_media()
        self.app.refresh_file_list()
        messagebox.showinfo("还原完成", f"成功读取{cnt}个目录备份")

# =====================主程序【V2.1.3定稿锁定】=====================
class MediaManagerApp:
    def __init__(self, root_win):
        self.root=root_win
        self.root.title("媒体分类管理器 V2.1")
        self.config_file=DEFAULT_CONFIG_NAME
        self.config_data={}
        self.media_dict={}
        self.current_select_path=None
        self.setting_win=None
        self.theme_check_map={}
        self.actor_check_map={}
        self.theme_inner=None
        self.actor_inner=None
        self.theme_inner=None
        self.actor_inner=None
        self.check_and_init_config()
        #筛选+排序变量
        self.var_filter_name=tk.StringVar()
        self.var_filter_theme=tk.StringVar(value="全部")
        self.var_filter_actor=tk.StringVar(value="全部")
        self.var_filter_score=tk.StringVar(value="全部")
        self.var_filter_def=tk.StringVar(value="全部")
        self.var_filter_type=tk.StringVar(value="全部")
        self.var_sort=tk.StringVar(value="默认顺序")
        self.build_main_ui()
        self.rebuild_all_checkbox()
        self.refresh_theme_actor_list()
        self.scan_media()

    def check_and_init_config(self):
        has_cfg=any(f.lower().endswith(".ini") for f in os.listdir("."))
        if not has_cfg:
            self.create_default_config(self.config_file)
        self.config_data=self.load_config()

    def create_default_config(self,fn):
        move={f"move_{i+1}":"" for i in range(5)}
        preset={f"preset_{i+1}":{"themes":[],"actors":[],"score":0} for i in range(5)}
        cfg={
            "folders":[os.getcwd()],
            "themes":DEFAULT_THEMES.copy(),
            "actors":DEFAULT_ACTORS.copy(),
            "enable_video":True,"enable_audio":False,"enable_image":False,
            "enable_archive":False,"enable_other":False,"other_suffix":OTHER_DEFAULT_SUFFIX,
            "tag_max_row":DEFAULT_MAX_ROW,**move,**preset
        }
        with open(fn,"w",encoding="utf-8")as f:
            json.dump(cfg,f,ensure_ascii=False,indent=2)

    def load_config(self):
        try:
            with open(self.config_file,"r",encoding="utf-8")as f:
                return json.load(f)
        except:return {}
    def save_config(self):
        with open(self.config_file,"w",encoding="utf-8")as f:
            json.dump(self.config_data,f,ensure_ascii=False,indent=2)

    def build_main_ui(self):
        #顶部按钮行
        top_fr=ttk.Frame(self.root)
        top_fr.pack(fill=tk.X,padx=5,pady=5)
        btns=[("设置",self.open_setting),("标签统计",self.show_label_stat),("批量打标",self.batch_rename_files),
              ("还原原名",self.restore_original_name),("打开目录",self.open_folder_by_sel),("删除文件",self.delete_selected_file)]
        for txt,cmd in btns:
            ttk.Button(top_fr,text=txt,command=cmd).pack(side=tk.LEFT,padx=3)
        ttk.Label(top_fr,text="单文件改名：").pack(side=tk.LEFT,padx=(10,2))
        self.rename_entry=ttk.Entry(top_fr,width=28)
        self.rename_entry.pack(side=tk.LEFT,padx=2)
        self.btn_rename_single=ttk.Button(top_fr,text="执行改名",command=self.single_rename)
        self.btn_rename_single.pack(side=tk.LEFT)

        #筛选+排序行
        filter_fr=ttk.Frame(self.root)
        filter_fr.pack(fill=tk.X,padx=5,pady=3)
        ttk.Label(filter_fr,text="关键词：").pack(side=tk.LEFT)
        e=ttk.Entry(filter_fr,textvariable=self.var_filter_name,width=12)
        e.pack(side=tk.LEFT,padx=2)
        e.bind("<KeyRelease>",lambda e:self.refresh_file_list())
        ttk.Label(filter_fr,text="内容：").pack(side=tk.LEFT,padx=5)
        self.cb_theme=ttk.Combobox(filter_fr,textvariable=self.var_filter_theme,state="readonly",width=12)
        self.cb_theme.pack(side=tk.LEFT)
        self.cb_theme.bind("<<ComboboxSelected>>",lambda e:self.refresh_file_list())
        ttk.Label(filter_fr,text="附加：").pack(side=tk.LEFT,padx=5)
        self.cb_actor=ttk.Combobox(filter_fr,textvariable=self.var_filter_actor,state="readonly",width=12)
        self.cb_actor.pack(side=tk.LEFT)
        self.cb_actor.bind("<<ComboboxSelected>>",lambda e:self.refresh_file_list())
        ttk.Label(filter_fr,text="星级：").pack(side=tk.LEFT,padx=5)
        self.cb_score=ttk.Combobox(filter_fr,textvariable=self.var_filter_score,state="readonly",width=4)
        self.cb_score["values"]=["全部","0星","1星","2星","3星","4星","5星"]
        self.cb_score.pack(side=tk.LEFT)
        self.cb_score.bind("<<ComboboxSelected>>",lambda e:self.refresh_file_list())
        ttk.Label(filter_fr,text="清晰度：").pack(side=tk.LEFT,padx=5)
        self.cb_def=ttk.Combobox(filter_fr,textvariable=self.var_filter_def,state="readonly",width=6)
        self.cb_def["values"]=DEF_ALL
        self.cb_def.pack(side=tk.LEFT)
        self.cb_def.bind("<<ComboboxSelected>>",lambda e:self.refresh_file_list())
        ttk.Label(filter_fr,text="类型：").pack(side=tk.LEFT,padx=5)
        self.cb_type=ttk.Combobox(filter_fr,textvariable=self.var_filter_type,state="readonly",width=8)
        self.cb_type["values"]=["全部","视频","音频","图片","压缩包","其他文档"]
        self.cb_type.pack(side=tk.LEFT)
        self.cb_type.bind("<<ComboboxSelected>>",lambda e:self.refresh_file_list())
        ttk.Button(filter_fr,text="清空筛选",command=self.clear_all_filter).pack(side=tk.LEFT,padx=5)
        #排序下拉
        ttk.Label(filter_fr,text="排序：").pack(side=tk.LEFT,padx=(8,2))
        self.cb_sort=ttk.Combobox(filter_fr,textvariable=self.var_sort,state="readonly",width=9)
        self.cb_sort["values"]=["默认顺序","文件名升序","文件名降序","大小升序","大小降序","星级升序","星级降序"]
        self.cb_sort.pack(side=tk.LEFT)
        self.cb_sort.bind("<<ComboboxSelected>>",lambda e:self.refresh_file_list())

        #左右分割面板
        pan=ttk.PanedWindow(self.root,orient=tk.HORIZONTAL)
        pan.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)
        left_fr=ttk.Frame(pan)
        pan.add(left_fr,weight=4)
        right_fr=ttk.Frame(pan,width=320)
        pan.add(right_fr,weight=1)
        #左侧列表+滚动条
        tree_wrap=ttk.Frame(left_fr)
        tree_wrap.pack(fill=tk.BOTH,expand=True)
        vsb=ttk.Scrollbar(tree_wrap,orient=tk.VERTICAL)
        self.file_tree=ttk.Treeview(tree_wrap,columns=("path","size","score","defi"),show="headings",selectmode="extended",yscrollcommand=vsb.set)
        vsb.config(command=self.file_tree.yview)
        vsb.pack(side=tk.RIGHT,fill=tk.Y)
        self.file_tree.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
        self.file_tree.heading("path",text="文件路径")
        self.file_tree.heading("size",text="大小(点击打开)")
        self.file_tree.heading("score",text="星级")
        self.file_tree.heading("defi",text="清晰度")
        self.file_tree.column("path",width=420,stretch=tk.YES)
        self.file_tree.column("size",width=100,stretch=tk.NO)
        self.file_tree.column("score",width=60,stretch=tk.NO)
        self.file_tree.column("defi",width=60,stretch=tk.NO)
        self.file_tree.bind("<<TreeviewSelect>>",self.on_tree_select)
        self.file_tree.bind("<ButtonRelease-1>",self.click_size_open_file)
        #右侧面板
        rp=5
        ttk.Label(right_fr,text="星级打分").pack(anchor=tk.W,padx=rp,pady=(6,2))
        score_fr=ttk.Frame(right_fr)
        score_fr.pack(padx=rp,pady=2,fill=tk.X)
        self.score_btn_list=[]
        for i in range(5):
            b=tk.Button(score_fr,text="★",width=3,font=("宋体",11),fg="gray",command=lambda n=i+1:self.set_file_score(n))
            b.pack(side=tk.LEFT,padx=2)
            self.score_btn_list.append(b)

        ttk.Label(right_fr,text="快捷标签模板(左键应用/右键保存)").pack(anchor=tk.W,padx=rp,pady=(8,2))
        preset_fr=ttk.Frame(right_fr)
        preset_fr.pack(padx=rp,pady=2,fill=tk.X)
        for i in range(5):
            btn=ttk.Button(preset_fr,text=str(i+1),width=3)
            btn.bind("<Button-1>",lambda e,idx=i:self.apply_preset(idx))
            btn.bind("<Button-3>",lambda e,idx=i:self.save_preset(idx))
            btn.pack(side=tk.LEFT,padx=2)
        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(fill=tk.X,padx=rp,pady=(2,4))#分割线
        ttk.Label(right_fr,text="内容分类（题材、特色等）").pack(anchor=tk.W,padx=rp,pady=(8,6))
        self.theme_inner = ttk.Frame(right_fr)
        self.theme_inner.pack(padx=rp, pady=2, fill=tk.X)
        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(fill=tk.X,padx=rp,pady=(2,4))#分割线
        ttk.Label(right_fr,text="附加分类（演员、作者、自定义等）").pack(anchor=tk.W,padx=rp,pady=(8,6))
        self.actor_inner = ttk.Frame(right_fr)
        self.actor_inner.pack(padx=rp, pady=2, fill=tk.X)
        ttk.Separator(right_fr, orient=tk.HORIZONTAL).pack(fill=tk.X,padx=rp,pady=(2,4))#分割线
        ttk.Label(right_fr,text="快捷移动目录(左键应用/右键设置)").pack(anchor=tk.W,padx=rp,pady=(8,2))
        move_fr=ttk.Frame(right_fr)
        move_fr.pack(padx=rp,pady=2,fill=tk.X)
        for i in range(5):
            btn=ttk.Button(move_fr,text=str(i+1),width=3)
            btn.bind("<Button-1>",lambda e,idx=i:self.move_to_dir(idx))
            btn.bind("<Button-3>",lambda e,idx=i:self.set_move_path(idx))
            btn.pack(side=tk.LEFT,padx=2)

    def refresh_theme_actor_list(self):
        self.cb_theme["values"]=["全部","未分类"]+self.config_data.get("themes",[])
        self.cb_actor["values"]=["全部","未分类"]+self.config_data.get("actors",[])
    def rebuild_all_checkbox(self):
        self.refresh_theme_check()
        self.refresh_actor_check()
    def refresh_theme_check(self):
        if not self.theme_inner.winfo_exists():return
        for w in self.theme_inner.winfo_children():w.destroy()
        self.theme_check_map.clear()
        ths=self.config_data.get("themes",[])
        rowcnt=self.config_data.get("tag_max_row",DEFAULT_MAX_ROW)
        import math
        col=math.ceil(len(ths)/rowcnt)
        idx=0
        for c in range(col):
            for r in range(rowcnt):
                if idx>=len(ths):break
                n=ths[idx]
                v=tk.BooleanVar()
                cb=ttk.Checkbutton(self.theme_inner,text=n,variable=v,command=lambda x=n,var=v:self.toggle_theme(x,var))
                cb.grid(row=r,column=c,sticky="w")
                self.theme_check_map[n]=v
                idx+=1
        self.theme_inner.update_idletasks()
    def refresh_actor_check(self):
        if not self.actor_inner.winfo_exists():return
        for w in self.actor_inner.winfo_children():w.destroy()
        self.actor_check_map.clear()
        acs=self.config_data.get("actors",[])
        rowcnt=self.config_data.get("tag_max_row",DEFAULT_MAX_ROW)
        import math
        col=math.ceil(len(acs)/rowcnt)
        idx=0
        for c in range(col):
            for r in range(rowcnt):
                if idx>=len(acs):break
                n=acs[idx]
                v=tk.BooleanVar()
                cb=ttk.Checkbutton(self.actor_inner,text=n,variable=v,command=lambda x=n,var=v:self.toggle_actor(x,var))
                cb.grid(row=r,column=c,sticky="w")
                self.actor_check_map[n]=v
                idx+=1
        self.actor_inner.update_idletasks()

    def open_setting(self):self.setting_win=SettingDialog(self.root,self)
    def set_move_path(self,idx):
        k=f"move_{idx+1}"
        old=self.config_data.get(k,"")
        d=filedialog.askdirectory(initialdir=old if old else None)
        if not d:return
        self.config_data[k]=os.path.normpath(d)
        self.save_config()
    def move_to_dir(self,idx):
        sel=self.file_tree.selection()
        if not sel:return
        dst=os.path.normpath(self.config_data.get(f"move_{idx+1}",""))
        if not os.path.isdir(dst):
            messagebox.showwarning("提示","目录未配置，右键按钮设置")
            return
        for item in sel:
            src=os.path.normpath(self.file_tree.item(item,"values")[0])
            fn=os.path.basename(src)
            new_p=os.path.normpath(os.path.join(dst,fn))
            if os.path.exists(new_p):
                if not messagebox.askyesno("文件存在","覆盖？"):continue
            try:
                os.replace(src,new_p)
                ads_src=src+ADS_SUFFIX
                ads_new=new_p+ADS_SUFFIX
                if os.path.exists(ads_src):os.replace(ads_src,ads_new)
                self.media_dict[new_p]=self.media_dict.pop(src)
            except Exception as e:messagebox.showerror("错误",str(e))
        self.scan_media()
    def save_preset(self,idx):
        if not self.current_select_path:
            messagebox.showinfo("提示","先选中一个文件保存模板")
            return
        d=self.media_dict[self.current_select_path]
        self.config_data[f"preset_{idx+1}"]={"themes":d["themes"].copy(),"actors":d["actors"].copy(),"score":d["score"]}
        self.save_config()
        messagebox.showinfo("成功",f"模板{idx+1}已保存")
    def apply_preset(self,idx):
        sel=self.file_tree.selection()
        if not sel:return
        preset=self.config_data.get(f"preset_{idx+1}",{})
        ths=preset.get("themes",[])
        acs=preset.get("actors",[])
        sc=preset.get("score",0)
        if not ths and not acs and sc==0:
            messagebox.showwarning("提示","模板为空，右键保存标签")
            return
        for item in sel:
            p=os.path.normpath(self.file_tree.item(item,"values")[0])
            info=self.media_dict[p]
            info["themes"]=ths.copy()
            info["actors"]=acs.copy()
            info["score"]=sc
            self.save_file_meta(p,info)
        self.refresh_file_list(self.current_select_path)
        self.on_tree_select(None)
    def set_file_score(self,num):
        sel=self.file_tree.selection()
        if not sel:return
        for item in sel:
            p=os.path.normpath(self.file_tree.item(item,"values")[0])
            self.media_dict[p]["score"]=num
            self.save_file_meta(p,self.media_dict[p])
        self.on_tree_select(None)
        self.refresh_file_list(self.current_select_path)
    def toggle_theme(self,name,var):
        sel=self.file_tree.selection()
        if not sel:
            var.set(False)
            return
        stat=var.get()
        for item in sel:
            p=os.path.normpath(self.file_tree.item(item,"values")[0])
            lst=self.media_dict[p]["themes"]
            if stat and name not in lst:lst.append(name)
            elif not stat and name in lst:lst.remove(name)
            self.save_file_meta(p,self.media_dict[p])
        self.refresh_file_list(self.current_select_path)
    def toggle_actor(self,name,var):
        sel=self.file_tree.selection()
        if not sel:
            var.set(False)
            return
        stat=var.get()
        for item in sel:
            p=os.path.normpath(self.file_tree.item(item,"values")[0])
            lst=self.media_dict[p]["actors"]
            if stat and name not in lst:lst.append(name)
            elif not stat and name in lst:lst.remove(name)
            self.save_file_meta(p,self.media_dict[p])
        self.refresh_file_list(self.current_select_path)

    def on_tree_select(self,e):
        for v in self.theme_check_map.values():v.set(False)
        for v in self.actor_check_map.values():v.set(False)
        sel=self.file_tree.selection()
        if not sel:
            self.current_select_path=None
            self.rename_entry.delete(0,tk.END)
            for b in self.score_btn_list:b.config(fg="gray")
            return
        p=os.path.normpath(self.file_tree.item(sel[0],"values")[0])
        self.current_select_path=p
        info=self.media_dict[p]
        self.rename_entry.delete(0,tk.END)
        self.rename_entry.insert(0,os.path.splitext(info["name"])[0])
        for i in range(5):
            self.score_btn_list[i].config(fg="gold" if i<info["score"] else "gray")
        for t in info["themes"]:
            if t in self.theme_check_map:self.theme_check_map[t].set(True)
        for a in info["actors"]:
            if a in self.actor_check_map:self.actor_check_map[a].set(True)

    def load_file_meta(self,p):
        fp=os.path.normpath(p)
        ads=fp+ADS_SUFFIX
        try:
            with open(ads,"r",encoding="utf-8")as f:
                return json.load(f)
        except:
            return {"score":0,"themes":[],"actors":[],"resolution":"","definition":""}
    def save_file_meta(self,p,data):
        fp=os.path.normpath(p)
        ads=fp+ADS_SUFFIX
        try:
            st=os.stat(ads) if os.path.exists(ads) else None
            with open(ads,"w",encoding="utf-8")as f:
                json.dump(data,f,ensure_ascii=False,indent=1)
            if st:os.utime(ads,(st.st_atime,st.st_mtime))
        except Exception:pass

    #竖屏取短边算清晰度【V2.1修订】
    def get_video_def_info(self,p):
        if not MediaInfo:return ("","未知")
        try:
            mi=MediaInfo.parse(p)
            for tr in mi.tracks:
                if tr.track_type=="Video":
                    w=tr.width or 0
                    h=tr.height or 0
                    res=f"{w}×{h}"
                    short=min(w,h)
                    df=get_def_by_height(short)
                    return (res,df)
            return ("","未知")
        except:return ("","未知")

    def scan_media(self):
        self.media_dict.clear()
        cfg=self.config_data
        ev=cfg.get("enable_video",True)
        ea=cfg.get("enable_audio",False)
        ei=cfg.get("enable_image",False)
        ez=cfg.get("enable_archive",False)
        eo=cfg.get("enable_other",False)
        o_suf=[x.strip().lower() for x in cfg.get("other_suffix",OTHER_DEFAULT_SUFFIX).split(";") if x.strip()]
        for dp in cfg.get("folders",[]):
            dp=os.path.normpath(dp)
            if not os.path.isdir(dp):continue
            for root,_,files in os.walk(dp):
                for fn in files:
                    full=os.path.normpath(os.path.join(root,fn))
                    ext=os.path.splitext(fn.lower())[-1]
                    ftype=""
                    if ev and ext in VIDEO_FORMATS:ftype="视频"
                    elif ea and ext in AUDIO_FORMATS:ftype="音频"
                    elif ei and ext in IMAGE_FORMATS:ftype="图片"
                    elif ez and ext in ZIP_FORMATS:ftype="压缩包"
                    elif eo and ext in o_suf:ftype="其他文档"
                    if not ftype:continue
                    sz=os.path.getsize(full)
                    meta=self.load_file_meta(full)
                    res,defi=meta.get("resolution",""),meta.get("definition","")
                    if ftype=="视频" and (not res or not defi):
##                    if ftype=="视频" :#用于手动处理，刷新清晰度
                        res,defi=self.get_video_def_info(full)
                        meta["resolution"]=res
                        meta["definition"]=defi
                        self.save_file_meta(full,meta)
                    elif ftype!="视频":defi="非视频"
                    self.media_dict[full]={
                        "name":fn,"size":sz,"type":ftype,"score":meta["score"],
                        "themes":meta["themes"],"actors":meta["actors"],"resolution":res,"definition":defi
                    }
        self.refresh_file_list()

    def refresh_file_list(self,keep_path=None):
        self.file_tree.delete(*self.file_tree.get_children())
        kw=self.var_filter_name.get().lower()
        fth=self.var_filter_theme.get()
        fac=self.var_filter_actor.get()
        fsc=self.var_filter_score.get()
        fdf=self.var_filter_def.get()
        fty=self.var_filter_type.get()
        tmp=[]
        for p,info in self.media_dict.items():
            if kw and kw not in info["name"].lower():continue
            if fth!="全部" and ((fth=="未分类" and info["themes"]) and (fth not in info["themes"])):continue
            if fac!="全部" and ((fac=="未分类" and info["actors"]) and (fac not in info["actors"])):continue
            if fty!="全部" and info["type"]!=fty:continue
            if fsc!="全部" and info["score"]!=int(fsc[0]):continue
            if fdf!="全部" and info["definition"]!=fdf:continue
            tmp.append((p,info))
        #排序
        srt=self.var_sort.get()
        if srt=="文件名升序":tmp.sort(key=lambda x:x[1]["name"].lower())
        elif srt=="文件名降序":tmp.sort(key=lambda x:x[1]["name"].lower(),reverse=True)
        elif srt=="大小升序":tmp.sort(key=lambda x:x[1]["size"])
        elif srt=="大小降序":tmp.sort(key=lambda x:x[1]["size"],reverse=True)
        elif srt=="星级升序":tmp.sort(key=lambda x:x[1]["score"])
        elif srt=="星级降序":tmp.sort(key=lambda x:x[1]["score"],reverse=True)
        else:tmp.sort(key=lambda x:x[1]["size"],reverse=True)
##        elif srt=="清晰度升序":tmp.sort(key=lambda x:x[1]["definition"])
##        elif srt=="清晰度降序":tmp.sort(key=lambda x:x[1]["definition"],reverse=True)
        target=None
        for p,info in tmp:
            mb=info["size"]/1024/1024
            star="★"*info["score"]
            iid=self.file_tree.insert("","end",values=(p,f"{mb:.2f} MB",star,info["definition"]))
            if keep_path and os.path.normpath(p)==os.path.normpath(keep_path):
                target=iid
        if target:
            self.file_tree.selection_set(target)
            self.file_tree.focus(target)
            self.current_select_path=keep_path

    def clear_all_filter(self):
        self.var_filter_name.set("")
        self.var_filter_theme.set("全部")
        self.var_filter_actor.set("全部")
        self.var_filter_score.set("全部")
        self.var_filter_def.set("全部")
        self.var_filter_type.set("全部")
##        self.var_sort.set("默认顺序")
        self.refresh_file_list()

    def click_size_open_file(self,e):
        col=self.file_tree.identify_column(e.x)
        if col=="#2":
            sel=self.file_tree.selection()
            if sel:
                p=os.path.normpath(self.file_tree.item(sel[0],"values")[0])
                os.startfile(p)
    def open_folder_by_sel(self):
        sel=self.file_tree.selection()
        if not sel:return
        p=os.path.normpath(self.file_tree.item(sel[0],"values")[0])
        os.startfile(os.path.dirname(p))
    def delete_selected_file(self):
        sel=self.file_tree.selection()
        if not sel:return
        if not messagebox.askyesno("确认","删除选中文件？"):return
        for item in sel:
            p=os.path.normpath(self.file_tree.item(item,"values")[0])
            try:
                os.remove(p)
                ads=p+ADS_SUFFIX
                if os.path.exists(ads):os.remove(ads)
                if p in self.media_dict:del self.media_dict[p]
            except Exception:pass
        self.refresh_file_list()

    #【V2.1修订：改名成功自动选中新文件】
    def single_rename(self):
        if not self.current_select_path or len(self.file_tree.selection())!=1:
            messagebox.showwarning("提示","请单选一个文件")
            return
        new_name=self.rename_entry.get().strip()
        if not new_name:
            messagebox.showwarning("提示","名称不能为空")
            return
        old_p=os.path.normpath(self.current_select_path)
        ext=os.path.splitext(old_p)[1]
        dir_p=os.path.dirname(old_p)
        new_full=os.path.normpath(os.path.join(dir_p,new_name+ext))
        idx=1
        while os.path.exists(new_full):
            new_full=os.path.normpath(os.path.join(dir_p,f"{new_name}{idx:02d}{ext}"))
            idx+=1
        try:
            os.rename(old_p,new_full)
            ads_old=old_p+ADS_SUFFIX
            ads_new=new_full+ADS_SUFFIX
            if os.path.exists(ads_old):os.rename(ads_old,ads_new)
            self.media_dict[new_full]=self.media_dict.pop(old_p)
            #刷新并选中新路径
            self.refresh_file_list(new_full)
        except Exception as e:
            messagebox.showerror("改名失败",str(e))

    def batch_rename_files(self):
        sel=self.file_tree.selection()
        if not sel:return
        cnt=0
        reg=re.compile(r"【[^】]*】$")
        for item in sel:
            p=os.path.normpath(self.file_tree.item(item,"values")[0])
            info=self.media_dict[p]
            name,ext=os.path.splitext(os.path.basename(p))
            block=[]
            block.extend(info["actors"])
            block.extend(info["themes"])
            if info["score"]>0:block.append(f"{info['score']}星")
            if not block:continue
            tag=" ".join(block)
            new_name=reg.sub("",name)+f"【{tag}】"+ext
            new_p=os.path.normpath(os.path.join(os.path.dirname(p),new_name))
            if os.path.exists(new_p):continue
            try:
                os.rename(p,new_p)
                os.rename(p+ADS_SUFFIX,new_p+ADS_SUFFIX) if os.path.exists(p+ADS_SUFFIX) else None
                self.media_dict[new_p]=self.media_dict.pop(p)
                cnt+=1
            except Exception:pass
        self.scan_media()
        messagebox.showinfo("批量完成",f"成功{cnt}个")

    def restore_original_name(self):
        sel=self.file_tree.selection()
        if not sel:return
        cnt=0
        reg=re.compile(r"(.*)【([^】]+)】(\.\w+)$")
        all_th=set(self.config_data.get("themes",[]))
        all_ac=set(self.config_data.get("actors",[]))
        for item in sel:
            p=os.path.normpath(self.file_tree.item(item,"values")[0])
            fn=os.path.basename(p)
            m=reg.match(fn)
            if not m:continue
            raw=m.group(1)+m.group(3)
            tags=m.group(2).split()
            sc=0
            rest=[]
            if tags and re.fullmatch(r"\d+星",tags[0]):
                sc=int(tags[0][0])
                rest=tags[1:]
            else:rest=tags
            ths=[x for x in rest if x in all_th]
            acs=[x for x in rest if x in all_ac]
            info=self.media_dict[p]
            info["score"]=sc
            info["themes"]=ths
            info["actors"]=acs
            self.save_file_meta(p,info)
            new_p=os.path.normpath(os.path.join(os.path.dirname(p),raw))
            if os.path.exists(new_p):continue
            try:
                os.rename(p,new_p)
                os.rename(p+ADS_SUFFIX,new_p+ADS_SUFFIX) if os.path.exists(p+ADS_SUFFIX) else None
                self.media_dict[new_p]=self.media_dict.pop(p)
                cnt+=1
            except Exception:pass
        self.scan_media()
        messagebox.showinfo("还原完成",f"{cnt}个文件已去掉标签后缀")

    def show_label_stat(self):
        th_cnt=Counter()
        ac_cnt=Counter()
        free_th=Counter()
        free_ac=Counter()
        std_th=set(self.config_data.get("themes",[]))
        std_ac=set(self.config_data.get("actors",[]))
        for d in self.media_dict.values():
            for t in d["themes"]:
                if t in std_th:th_cnt[t]+=1
                else:free_th[t]+=1
            for a in d["actors"]:
                if a in std_ac:ac_cnt[a]+=1
                else:free_ac[a]+=1
        for t in std_th:
            if t not in th_cnt:th_cnt[t]=0
        for t in std_ac:
            if t not in ac_cnt:ac_cnt[t]=0
        
        win=tk.Toplevel(self.root)
        win.title("标签统计")
        win.geometry("420x600")
        win.transient(self.root)
        win.columnconfigure((0,1),weight=1)
        win.rowconfigure(0,weight=1)
        txt=tk.Text(win,padx=10,pady=10)
        txt2=tk.Text(win,padx=10,pady=10)
        txt.grid(row=0,column=0,padx=2,pady=2,sticky="nsew")
        txt2.grid(row=0,column=1,padx=2,pady=2,sticky="nsew")
        
        txt.insert("1.0","====内容分类统计====\n")

        
        for i in self.config_data.get("themes",[]):#不排序
            txt.insert(tk.END,f"{th_cnt[i]}	{i}\n")#不排序
            
        if free_th :
            txt.insert(tk.END,"\n====游离标签====\n")
            for k,v in free_th.items():txt.insert(tk.END,f"{v}	{k}\n")
        txt2.insert(tk.END,"====附加分类统计====\n")

        for i in self.config_data.get("actors",[]):#不排序
            txt2.insert(tk.END,f"{ac_cnt[i]}	{i}\n")#不排序
        if free_ac:
            txt2.insert(tk.END,"\n====游离标签====\n")
            for k,v in free_ac.items():txt2.insert(tk.END,f"{v}	{k}\n")

if __name__=="__main__":
    root=tk.Tk()
    app=MediaManagerApp(root)
    root.mainloop()
