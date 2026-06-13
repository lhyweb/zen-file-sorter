import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pymediainfo import MediaInfo

# ==================== 全局配置 ====================
VIDEO_FORMATS = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.rmvb', '.wmv', '.m4v', '.ts', '.m2ts')
CONFIG_FILE = "tags_config.txt"
ADS_STREAM = ":zen_mv_info"
COLUMN_MAX_ROW = 10

# 清晰度：取短边计算
def get_quality(width, height):
    short_side = min(width, height)
    if short_side <= 0:
        return ""
    elif short_side <= 480:
        return "480P-"
    elif short_side <= 720:
        return "720P"
    elif short_side <= 1080:
        return "1080P"
    else:
        return "4K+"

# 正确使用 pymediainfo 获取分辨率
def get_video_resolution(path):
    try:
        info = MediaInfo.parse(path)
        for track in info.tracks:
            if track.track_type == "Video":
                return (track.width or 0, track.height or 0)
        return (0, 0)
    except:
        return (0, 0)

# 文件时间戳保持
def save_file_times(path):
    try:
        return os.path.getatime(path), os.path.getmtime(path)
    except:
        return None

def restore_file_times(path, times):
    try:
        if times:
            os.utime(path, times)
    except:
        pass

# ==================== 标签编辑弹窗 ====================
class TagEditDialog(tk.Toplevel):
    def __init__(self, parent, title, current_list):
        super().__init__(parent)
        self.title(f"管理{title}")
        self.parent = parent
        self.tag_type = title

        self.text = tk.Text(self, width=40, height=10)
        self.text.pack(padx=10, pady=10)
        self.text.insert("1.0", "\n".join(current_list))

        bf = tk.Frame(self)
        bf.pack(pady=5)
        ttk.Button(bf, text="保存", command=self.on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=5)
        self.grab_set()

    def on_save(self):
        content = self.text.get("1.0", tk.END).strip()
        new_list = [x.strip() for x in content.splitlines() if x.strip()]
        self.parent.config[self.tag_type] = new_list
        self.parent.save_config()
        self.parent.refresh_tag_controls()
        self.destroy()

# ==================== 目录管理弹窗 ====================
class FolderManagerDialog(tk.Toplevel):
    def __init__(self, parent, folders):
        super().__init__(parent)
        self.title("管理目录")
        self.parent = parent
        self.folders = folders.copy()

        tk.Label(self, text="已添加的视频目录").pack(pady=2)
        self.listbox = tk.Listbox(self, width=60, height=10)
        self.listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        for f in self.folders:
            self.listbox.insert(tk.END, f)

        frm = tk.Frame(self)
        frm.pack(pady=5)
        ttk.Button(frm, text="添加目录", command=self.add_folder).pack(side=tk.LEFT, padx=3)
        ttk.Button(frm, text="删除选中", command=self.delete_selected).pack(side=tk.LEFT, padx=3)
        ttk.Button(frm, text="保存并关闭", command=self.save_and_close).pack(side=tk.LEFT, padx=3)
        self.grab_set()

    def add_folder(self):
        path = filedialog.askdirectory()
        if path and path not in self.folders:
            self.folders.append(path)
            self.listbox.insert(tk.END, path)

    def delete_selected(self):
        idx = self.listbox.curselection()
        if idx:
            self.listbox.delete(idx)
            self.folders.pop(idx[0])

    def save_and_close(self):
        self.parent.config["folders"] = self.folders
        self.parent.save_config()
        self.parent.scan_videos()
        self.destroy()

# ==================== 标签统计弹窗 ====================
class TagStatDialog(tk.Toplevel):
    def __init__(self, parent, video_map):
        super().__init__(parent)
        self.title("标签统计")
        self.geometry("500x600")

        theme_cnt = {}
        actor_cnt = {}
        for v in video_map.values():
            for t in v.get("题材", []):
                theme_cnt[t] = theme_cnt.get(t, 0) + 1
            for a in v.get("演员", []):
                actor_cnt[a] = actor_cnt.get(a, 0) + 1

        tk.Label(self, text="题材统计", font=("黑体", 12, "bold")).pack()
        t1 = tk.Text(self, height=12)
        t1.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
        for k,c in sorted(theme_cnt.items(), key=lambda x:-x[1]):
            t1.insert(tk.END, f"{k} — {c}个\n")
        t1.config(state=tk.DISABLED)

        tk.Label(self, text="演员统计", font=("黑体", 12, "bold")).pack()
        t2 = tk.Text(self, height=12)
        t2.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
        for k,c in sorted(actor_cnt.items(), key=lambda x:-x[1]):
            t2.insert(tk.END, f"{k} — {c}个\n")
        t2.config(state=tk.DISABLED)

# ==================== 主程序 ====================
class VideoManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("视频管理器")
        self.geometry("1300x700")
        self.config = self.load_config()
        self.video_map = {}
        self.current_video_path = None
        self.selected_paths = []  # 保存所有选中的文件路径

        self.filter_theme = tk.StringVar()
        self.filter_quality = tk.StringVar()
        self.filter_actor = tk.StringVar()
        self.sort_var = tk.StringVar(value="文件名")

        self.theme_vars = {}
        self.actor_vars = {}
        self.create_ui()
        self.refresh_all()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"folders": [], "题材": [], "演员": []}

    def save_config(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def read_video_info(self, path):
        try:
            with open(path + ADS_STREAM, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"题材": [], "演员": [], "评分":0, "备注":"", "分辨率":[0,0]}

    def write_video_info(self, path, data):
        try:
            t = save_file_times(path)
            with open(path + ADS_STREAM, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            restore_file_times(path, t)
        except:
            pass

    def scan_videos(self):
        self.video_map.clear()
        for folder in self.config.get("folders", []):
            if not os.path.isdir(folder): continue
            for name in os.listdir(folder):
                if not name.lower().endswith(VIDEO_FORMATS): continue
                p = os.path.abspath(os.path.join(folder, name))
                try:
                    info = self.read_video_info(p)
                    w, h = info.get("分辨率", [0,0])
                    if w == 0 and h == 0:
                        w, h = get_video_resolution(p)
                        info["分辨率"] = [w, h]
                        self.write_video_info(p, info)
                    self.video_map[p] = {
                        "path": p, "name": name, "folder": folder, "size": os.path.getsize(p),
                        "题材": info["题材"], "演员": info["演员"], "评分": info["评分"],
                        "备注": info["备注"], "分辨率": [w, h], "清晰度文本": get_quality(w, h)
                    }
                except:
                    continue
        self.refresh_list()

    def create_ui(self):
        # 顶部按钮
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(top, text="管理目录", command=self.manage_folders).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="重新扫描", command=self.scan_videos).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="修改文件名", command=self.rename_file).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="删除文件", command=self.delete_file).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="打开目录", command=self.open_folder).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="标签统计", command=self.show_tag_stat).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="批量优化文件名", command=self.batch_optimize_filename).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="还原选中文件名", command=self.batch_restore_filename).pack(side=tk.LEFT, padx=3)

        # 筛选栏
        f_row = tk.Frame(self)
        f_row.pack(fill=tk.X, padx=5, pady=3)
        tk.Label(f_row, text="题材:").pack(side=tk.LEFT)
        self.cb_theme = ttk.Combobox(f_row, textvariable=self.filter_theme, width=12)
        self.cb_theme.pack(side=tk.LEFT, padx=2)
        tk.Label(f_row, text="清晰度:").pack(side=tk.LEFT)
        self.cb_quality = ttk.Combobox(f_row, textvariable=self.filter_quality, values=["","480P-","720P","1080P","4K+"], width=12)
        self.cb_quality.pack(side=tk.LEFT, padx=2)
        tk.Label(f_row, text="演员:").pack(side=tk.LEFT)
        self.cb_actor = ttk.Combobox(f_row, textvariable=self.filter_actor, width=12)
        self.cb_actor.pack(side=tk.LEFT, padx=2)
        tk.Label(f_row, text="排序:").pack(side=tk.LEFT)
        self.cb_sort = ttk.Combobox(f_row, textvariable=self.sort_var, values=["文件名","大小","评分"], width=12)
        self.cb_sort.pack(side=tk.LEFT, padx=2)
        ttk.Button(f_row, text="筛选", command=self.refresh_list).pack(side=tk.LEFT, padx=5)

        # 主面板
        main = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)

        # 视频列表（支持多选）
        lf = tk.Frame(main)
        main.add(lf, width=900)
        self.tree = ttk.Treeview(lf, columns=["path","q","size","score"], show="headings", selectmode="extended")
        self.tree.heading("path", text="文件路径")
        self.tree.heading("q", text="清晰度")
        self.tree.heading("size", text="大小")
        self.tree.heading("score", text="评分")
        self.tree.column("path", width=550)
        self.tree.column("q", width=80)
        self.tree.column("size", width=80)
        self.tree.column("score", width=80)
        self.tree.pack(fill=tk.BOTH, expand=1)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", lambda e: os.startfile(self.current_video_path) if self.current_video_path else None)

        # 右侧面板
        rf = tk.Frame(main)
        main.add(rf, width=380)

        tk.Label(rf, text="评分（批量应用到所有选中文件）").pack(anchor=tk.W)
        sf = tk.Frame(rf)
        sf.pack(anchor=tk.W)
        self.stars = []
        for i in range(5):
            b = tk.Button(sf, text="★", fg="gray", font=("", 14), command=lambda v=i+1:self.set_score(v))
            b.pack(side=tk.LEFT)
            self.stars.append(b)

        tk.Label(rf, text="题材（批量应用到所有选中文件）").pack(anchor=tk.W, pady=(5,0))
        self.theme_frame = tk.Frame(rf)
        self.theme_frame.pack(fill=tk.X)
        ttk.Button(rf, text="管理题材", command=lambda:self.manage_tags("题材")).pack(anchor=tk.W)

        tk.Label(rf, text="演员（批量应用到所有选中文件）").pack(anchor=tk.W, pady=(5,0))
        self.actor_frame = tk.Frame(rf)
        self.actor_frame.pack(fill=tk.X)
        ttk.Button(rf, text="管理演员", command=lambda:self.manage_tags("演员")).pack(anchor=tk.W)

        tk.Label(rf, text="备注（仅应用到第一个选中文件）").pack(anchor=tk.W, pady=(5,0))
        self.note = tk.Text(rf, height=4)
        self.note.pack(fill=tk.X)
        ttk.Button(rf, text="保存备注", command=self.save_note).pack(fill=tk.X, pady=5)

        self.refresh_tag_controls()

    def render_tags(self, frame, tags, var_dict, cmd):
        for w in frame.winfo_children(): w.destroy()
        var_dict.clear()
        r, c = 0, 0
        for t in tags:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(frame, text=t, variable=var, command=lambda x=t:cmd(x))
            cb.grid(row=r, column=c, sticky="w", padx=3, pady=1)
            var_dict[t] = var
            r += 1
            if r >= COLUMN_MAX_ROW:
                r = 0
                c += 1

    def refresh_tag_controls(self):
        themes = self.config.get("题材", [])
        actors = self.config.get("演员", [])
        self.render_tags(self.theme_frame, themes, self.theme_vars, self.on_theme_toggle)
        self.render_tags(self.actor_frame, actors, self.actor_vars, self.on_actor_toggle)
        self.cb_theme["values"] = [""] + themes
        self.cb_actor["values"] = [""] + actors

        if self.current_video_path and self.current_video_path in self.video_map:
            v = self.video_map[self.current_video_path]
            # 显示第一个选中文件的标签状态
            for t, var in self.theme_vars.items(): var.set(t in v["题材"])
            for a, var in self.actor_vars.items(): var.set(a in v["演员"])
            for i, b in enumerate(self.stars): b.config(fg="gold" if i < v["评分"] else "gray")
            self.note.delete("1.0", tk.END)
            self.note.insert("1.0", v.get("备注", ""))

    # 题材标签批量应用到所有选中文件
    def on_theme_toggle(self, tag):
        if not self.selected_paths: return
        current_state = self.theme_vars[tag].get()
        for path in self.selected_paths:
            if path not in self.video_map: continue
            v = self.video_map[path]
            current = set(v["题材"])
            if current_state:
                current.add(tag)
            else:
                current.discard(tag)
            v["题材"] = sorted(list(current))
            data = self.read_video_info(path)
            data["题材"] = v["题材"]
            self.write_video_info(path, data)

    # 演员标签批量应用到所有选中文件
    def on_actor_toggle(self, tag):
        if not self.selected_paths: return
        current_state = self.actor_vars[tag].get()
        for path in self.selected_paths:
            if path not in self.video_map: continue
            v = self.video_map[path]
            current = set(v["演员"])
            if current_state:
                current.add(tag)
            else:
                current.discard(tag)
            v["演员"] = sorted(list(current))
            data = self.read_video_info(path)
            data["演员"] = v["演员"]
            self.write_video_info(path, data)

    # 评分批量应用到所有选中文件
    def set_score(self, s):
        if not self.selected_paths: return
        for path in self.selected_paths:
            if path not in self.video_map: continue
            v = self.video_map[path]
            v["评分"] = s
            data = self.read_video_info(path)
            data["评分"] = s
            self.write_video_info(path, data)
        # 更新评分按钮显示
        for i, b in enumerate(self.stars): b.config(fg="gold" if i < s else "gray")

    def save_note(self):
        if not self.current_video_path: return
        txt = self.note.get("1.0", tk.END).strip()
        v = self.video_map[self.current_video_path]
        v["备注"] = txt
        data = self.read_video_info(self.current_video_path)
        data["备注"] = txt
        self.write_video_info(self.current_video_path, data)
        messagebox.showinfo("成功", "备注已保存")

    def open_folder(self):
        if self.current_video_path:
            os.startfile(os.path.dirname(self.current_video_path))

    def manage_folders(self):
        FolderManagerDialog(self, self.config.get("folders", []))

    def manage_tags(self, title):
        TagEditDialog(self, title, self.config.get(title, []))

    def show_tag_stat(self):
        TagStatDialog(self, self.video_map)

    # ✅ 已修改：全部使用空格分隔标签
    def batch_optimize_filename(self):
        if not self.video_map:
            messagebox.showwarning("提示", "无视频可处理")
            return
        if not messagebox.askyesno("确认", "批量优化文件名？\n格式：名称【评分 题材1 题材2 演员1 演员2】\n\n所有选中的标签都会完整写入"):
            return

        cnt = 0
        for path, v in self.video_map.items():
            score = v["评分"]
            themes = v["题材"]
            actors = v["演员"]
            parts = []
            if score > 0:
                parts.append(f"{score}星")
            # 确保所有题材标签都被添加
            parts.extend(themes)
            # 确保所有演员标签都被添加
            parts.extend(actors)
            if not parts:
                continue
            base, ext = os.path.splitext(v["name"])
            if "【" in base:
                base = base.split("【")[0]
            # 使用空格连接所有部分
            new_name = f"{base}【{' '.join(parts)}】{ext}"
            new_path = os.path.join(v["folder"], new_name)
            if path == new_path or os.path.exists(new_path):
                continue
            try:
                t = save_file_times(path)
                os.rename(path, new_path)
                if os.path.exists(path + ADS_STREAM):
                    os.rename(path + ADS_STREAM, new_path + ADS_STREAM)
                restore_file_times(new_path, t)
                cnt += 1
            except Exception as e:
                print(f"重命名失败: {e}")
                continue
        messagebox.showinfo("完成", f"优化完成：{cnt} 个文件\n所有标签已完整写入文件名")
        self.scan_videos()

    # 仅还原选中文件
    def batch_restore_filename(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选中要还原的文件")
            return
        if not messagebox.askyesno("确认", "确定还原选中文件的文件名？"):
            return

        cnt = 0
        for item in selected:
            p = self.tree.item(item)["values"][0]
            if p not in self.video_map: continue
            v = self.video_map[p]
            name = v["name"]
            if "【" not in name: continue
            base, ext = os.path.splitext(name)
            base = base.split("【")[0]
            new_path = os.path.join(v["folder"], base + ext)
            if p == new_path or os.path.exists(new_path): continue
            try:
                t = save_file_times(p)
                os.rename(p, new_path)
                if os.path.exists(p + ADS_STREAM):
                    os.rename(p + ADS_STREAM, new_path + ADS_STREAM)
                restore_file_times(new_path, t)
                cnt += 1
            except:
                continue
        messagebox.showinfo("完成", f"已还原：{cnt} 个文件")
        self.scan_videos()

    def rename_file(self):
        if not self.current_video_path: return
        old = self.current_video_path
        folder = os.path.dirname(old)
        name = os.path.basename(old)
        new_name = simpledialog.askstring("重命名", "新文件名", initialvalue=name)
        if not new_name: return
        new_path = os.path.join(folder, new_name)
        if os.path.exists(new_path):
            messagebox.showerror("错误", "文件已存在")
            return
        try:
            t = save_file_times(old)
            os.rename(old, new_path)
            if os.path.exists(old + ADS_STREAM):
                os.rename(old + ADS_STREAM, new_path + ADS_STREAM)
            restore_file_times(new_path, t)
            messagebox.showinfo("成功", "文件名已修改")
            self.scan_videos()
        except:
            messagebox.showerror("错误", "重命名失败")

    def delete_file(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选中要删除的文件")
            return
        if not messagebox.askyesno("确认", f"确定删除选中的 {len(selected)} 个文件？\n删除后不可恢复！"):
            return
        cnt = 0
        for item in selected:
            p = self.tree.item(item)["values"][0]
            try:
                if os.path.exists(p + ADS_STREAM):
                    os.remove(p + ADS_STREAM)
                os.remove(p)
                cnt += 1
            except:
                continue
        messagebox.showinfo("完成", f"已删除：{cnt} 个文件")
        self.current_video_path = None
        self.scan_videos()

    # 保存所有选中的文件路径
    def on_select(self, e):
        sel = self.tree.selection()
        self.selected_paths = [self.tree.item(item)["values"][0] for item in sel]
        if self.selected_paths:
            self.current_video_path = self.selected_paths[0]
        else:
            self.current_video_path = None
        self.refresh_tag_controls()

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        ft = self.filter_theme.get()
        fq = self.filter_quality.get()
        fa = self.filter_actor.get()
        st = self.sort_var.get()
        vs = list(self.video_map.values())
        out = []
        for v in vs:
            if ft and ft not in v["题材"]: continue
            if fq and v["清晰度文本"] != fq: continue
            if fa and fa not in v["演员"]: continue
            out.append(v)
        if st == "大小": out.sort(key=lambda x:x["size"], reverse=True)
        elif st == "评分": out.sort(key=lambda x:x["评分"], reverse=True)
        else: out.sort(key=lambda x:x["name"].lower())
        for v in out:
            self.tree.insert("", "end", values=(v["path"], v["清晰度文本"], f"{v['size']//1024//1024}MB", "★"*v["评分"]))

    def refresh_all(self):
        self.scan_videos()
        self.refresh_list()

if __name__ == "__main__":
    app = VideoManager()
    app.mainloop()
