import os
import re
from tkinterdnd2 import *
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
import ctypes

from tv_ass_process import (
    TapAssParser,
    MergeMode,
    Config,
    SCRIPT_VERSION,
    SUPPORTED_EXTENSIONS,
)

ctypes.windll.shcore.SetProcessDpiAwareness(1)


def add_files():
    files = filedialog.askopenfilenames(filetypes=[("ASS files", ".ass")])
    existed_files = []
    for file in files:
        if file in file_list.get(0, tk.END):
            existed_files.append(file)
        else:
            file_list.insert(tk.END, file)
    if existed_files:
        messagebox.showwarning("警告", f"文件已存在列表中: \n{"\n".join(existed_files)}")


def remove_files():
    selected_files = file_list.curselection()
    for index in reversed(selected_files):
        file_list.delete(index)


def get_ass_files(path):
    result = []
    for element in path:
        if os.path.isfile(element):
            if element.endswith(".ass"):
                result.append(element)
        elif os.path.isdir(element):
            ass_files = [
                os.path.join(element, file)
                for file in os.listdir(element)
                if file.endswith(".ass") and not file.endswith("_processed.ass")
            ]
            if len(ass_files):
                result.extend(ass_files)
    return result


def get_config():
    mapping = {
        "actor": [False, True],
        "add_spaces": [True, False],
        "adjust_repeated_syllables": [True, False],
        "clean_mode": [True, False],
        "merge": ["auto", "none", "force"],
        "output_format": ["txt", "ass", "srt"],
    }
    user_config = {}
    for key, value in mapping.items():
        user_config[key] = value[variables[key].get()]
    user_config["ending_char"] = variables["ending_char"].get()
    return Config(user_config)

def get_replacement():
    replacement = {}
    invalid_lines = []
    for line in text_replace.get("1.0", "end-1c").splitlines():
        if not line:
            continue
        old, sep, new = line.partition("=")
        if sep:
            replacement[old] = new
        else:
            invalid_lines.append(line)
    if invalid_lines:
        messagebox.showwarning("警告", "以下替换行无效：\n" + "\n".join(invalid_lines))
    return replacement

def process_files():
    files = file_list.get(0, tk.END)
    ass_files = get_ass_files(files)
    if not ass_files:
        messagebox.showwarning("警告", "文件列表为空，无法处理")
        return
    user_config = get_config()
    replacement = get_replacement()
    failed_files = []
    for file in ass_files:
        try:
            output_file = file[:-4] + f"_processed.{user_config.output_format}"
            subs = TapAssParser(file).process(user_config)
            for _, line in subs:
                for old, new in replacement.items():
                    line.text = line.replace(old, new)
            subs.save(
                output_file, None, user_config.actor, user_config.ending_char
            )
            
        except:
            failed_files.append(file)
    message = f"成功处理 {len(ass_files) - len(failed_files)} 个文件"
    if failed_files:
        message += "\n\n处理失败：\n" + "\n".join(failed_files)
    messagebox.showinfo("处理文件", message)


def on_drop(event):
    files = root.tk.splitlist(event.data)
    invalid_files = []
    existed_files = []
    for file in files:
        if not file.lower().endswith(".ass"):
            invalid_files.append(file)
        elif file in file_list.get(0, tk.END):
            existed_files.append(file)
        else:
            file_list.insert(tk.END, file)
    messages = []
    if invalid_files:
        messages.append(f"文件不是ass格式: \n{"\n".join(invalid_files)}")
    if existed_files:
        messages.append(f"文件已存在列表中: \n{"\n".join(existed_files)}")
    if messages:
        messagebox.showwarning("警告", "\n\n".join(messages))


def file_exists(file_path):
    # 检查文件是否存在
    return os.path.isfile(file_path)

def disable_maximize():
    # 设置窗口的最小和最大尺寸相同，以防止最大化
    root.update_idletasks()  # 更新窗口大小
    width = root.winfo_width()
    height = root.winfo_height()
    root.minsize(width, height)
    root.maxsize(width, height)

# 主窗口
root = TkinterDnD.Tk()
root.title("Tap GUI 0.1.0")
root.geometry("800x600")
scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 75
root.tk.call("tk", "scaling", scale_factor)


# 创建Notebook（选项卡控件）
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# 创建“处理文件”选项卡
frame_file_processing = ttk.Frame(notebook)
notebook.add(frame_file_processing, text="处理文件")

# 文件列表框
file_list = tk.Listbox(frame_file_processing, selectmode=tk.EXTENDED)
file_list.pack(fill="both", expand=True, padx=10, pady=10)

# 添加拖放功能
file_list.drop_target_register(DND_FILES)
file_list.dnd_bind("<<Drop>>", on_drop)

# 按钮框架
button_frame = ttk.Frame(frame_file_processing)
button_frame.pack(fill="x", padx=10, pady=10)

# “添加”按钮
btn_add = ttk.Button(button_frame, text="添加", command=add_files)
btn_add.pack(side=tk.LEFT, padx=5)

# “移除”按钮
btn_remove = ttk.Button(button_frame, text="移除", command=remove_files)
btn_remove.pack(side=tk.LEFT, padx=5)

# “处理”按钮
btn_process = ttk.Button(button_frame, text="处理", command=process_files)
btn_process.pack(side=tk.LEFT, padx=5)

# 自定义替换选项卡
frame_custom_replace = ttk.Frame(notebook)
notebook.add(frame_custom_replace, text="自定义替换")

label_replace = ttk.Label(
    frame_custom_replace, text="只支持普通文本替换，每行都是 A=B 的形式"
)
label_replace.pack(padx=10, pady=10, anchor="w")

text_replace = tk.Text(frame_custom_replace, wrap=tk.WORD)
text_replace.pack(fill="both", expand=True, padx=10, pady=10)

# 选项选项卡
def create_option_frame(name, label_text, options):
    frame = ttk.Frame(frame_options)
    frame.pack(fill="x", padx=0, pady=15)

    label = ttk.Label(frame, text=label_text)
    label.pack(side=tk.LEFT, padx=10)

    variables[name] = tk.IntVar()
    variables[name].set(0)
    for i, option_text in enumerate(options):
        radiobutton = ttk.Radiobutton(frame, text=option_text, variable=variables[name], value=i)
        radiobutton.pack(side=tk.LEFT, padx=10)
    
    return frame


frame_options = ttk.Frame(notebook)
notebook.add(frame_options, text="选项")
variables = {}
# 添加单选选项
create_option_frame("actor", "输出说话人", ["关闭", "开启"])
create_option_frame("add_spaces", "中西文之间添加六分之一空格", ["开启", "关闭"])
create_option_frame("adjust_repeated_syllables", "整理重复音节", ["开启", "关闭"])
create_option_frame("clean_mode", "删除语气词", ["开启", "关闭"])
create_option_frame("merge", "合并时间重复行", ["自动", "关闭", "强制合并"])
create_option_frame("output_format", "输出格式", ["txt", "ass", "srt"])

# 添加填空选项
frame = ttk.Frame(frame_options)
frame.pack(fill="x", padx=0, pady=15)
label = ttk.Label(frame, text="行尾追加字符")
label.pack(side=tk.LEFT, padx=10)
variables["ending_char"] = tk.StringVar()
append_char_entry = ttk.Entry(frame, textvariable=variables["ending_char"])
append_char_entry.pack(side=tk.LEFT, padx=10)


root.mainloop()
