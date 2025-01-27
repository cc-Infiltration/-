import requests
import tkinter as tk
from tkinter import ttk
from threading import Thread
import os
from PIL import Image, ImageTk
from tkinter import messagebox, simpledialog, Menu, font

def get_video():
    try:
        response = requests.get("https://yuapi.karpov.cn/api/luoli.php?type=json")
        data = response.json()
        video_url = data.get("data")
        if video_url:
            download_video(video_url)
        return video_url
    except:
        return None

def download_video(video_url):
    if video_url:
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            # 检查当前目录是否有 YiRan_webvideo 文件夹
            folder_path = os.path.join(os.getcwd(), "YiRan_webvideo")
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # 获取当前目录下的所有文件，找到最大的编号
            files = [f for f in os.listdir(folder_path) if f.startswith("downloaded_video_") and f.endswith(".mp4")]
            max_num = 0
            for f in files:
                num = int(f.split('_')[-1].split('.')[0])
                if num > max_num:
                    max_num = num
            filename = os.path.join(folder_path, f"downloaded_video_{max_num + 1:03d}.mp4")
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            text_editor.insert(tk.END, f"视频已下载到 {filename}\n")
            text_editor.see(tk.END)
        except Exception as e:
            text_editor.insert(tk.END, f"Error downloading video: {e}\n")
            text_editor.see(tk.END)

def get_videos(count):
    def update_progress(downloaded, total):
        progress_var.set(downloaded)
        progress_label.config(text=f"已下载: {downloaded}/{total} 未下载: {total - downloaded}")
        root.update_idletasks()

    def download_thread():
        threads = []
        for _ in range(count):
            thread = Thread(target=get_video)
            thread.start()
            threads.append(thread)
        for i, thread in enumerate(threads):
            thread.join()
            update_progress(i + 1, count)
        messagebox.showinfo("下载完成", f"已下载 {count} 个视频")

    progress_var.set(0)
    progress_bar.config(maximum=count)
    progress_label.config(text=f"已下载: 0/{count} 未下载: {count}")
    Thread(target=download_thread).start()

def prompt_for_count():
    count = simpledialog.askinteger("输入数量", "请输入要获取的视频数量：", minvalue=1, maxvalue=100)
    if count:
        get_videos(count)

def set_theme(theme):
    global current_theme
    current_theme = theme
    if theme == "light":
        root.config(bg="white")
        text_editor.config(bg="white", fg="black")
        for window in open_windows:
            window.config(bg="white")
        for widget in root.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                widget.config(bg="white", fg="black")
        for widget in text_editor.winfo_children():
            widget.config(bg="white", fg="black")
    elif theme == "dark":
        root.config(bg="black")
        text_editor.config(bg="black", fg="white")
        for window in open_windows:
            window.config(bg="black")
        for widget in root.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                widget.config(bg="black", fg="white")
        for widget in text_editor.winfo_children():
            widget.config(bg="black", fg="white")

def set_threads(num):
    global thread_count
    thread_count = num

def set_font(font_name, font_size, font_color):
    text_editor.config(font=(font_name, font_size), fg=font_color)
    if 'font_preview_label' in globals():
        font_preview_label.config(font=(font_name, font_size), fg=font_color)
    for window in open_windows:
        for widget in window.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(font=(font_name, font_size), fg=font_color)
            if isinstance(widget, tk.Button):
                widget.config(font=(font_name, font_size), fg=font_color)

def apply_settings():
    set_theme(current_theme)
    set_threads(thread_var.get())
    set_font(font_var.get(), font_size_var.get(), font_color_var.get())

def open_settings():
    global font_preview_label, thread_var, font_var, font_size_var, font_color_var
    settings_window = tk.Toplevel(root)
    settings_window.title("设置")
    settings_window.geometry("300x400")
    open_windows.append(settings_window)

    theme_label = tk.Label(settings_window, text="模式切换")
    theme_label.pack(pady=5)

    theme_var = tk.StringVar(value=current_theme)
    light_theme = tk.Radiobutton(settings_window, text="白天模式", variable=theme_var, value="light", command=lambda: set_theme("light"))
    light_theme.pack()
    dark_theme = tk.Radiobutton(settings_window, text="黑夜模式", variable=theme_var, value="dark", command=lambda: set_theme("dark"))
    dark_theme.pack()

    thread_label = tk.Label(settings_window, text="线程数")
    thread_label.pack(pady=5)

    thread_var = tk.IntVar(value=thread_count)
    thread_menu = ttk.Combobox(settings_window, textvariable=thread_var, values=list(range(1, os.cpu_count() + 1)))
    thread_menu.pack()

    font_label = tk.Label(settings_window, text="字体设置")
    font_label.pack(pady=5)

    available_fonts = list(font.families())
    font_var = tk.StringVar(value=available_fonts[0])
    font_menu = ttk.Combobox(settings_window, textvariable=font_var, values=available_fonts)
    font_menu.pack()

    font_size_label = tk.Label(settings_window, text="字体大小")
    font_size_label.pack(pady=5)

    font_size_var = tk.IntVar(value=12)
    font_size_menu = ttk.Combobox(settings_window, textvariable=font_size_var, values=list(range(8, 33)))
    font_size_menu.pack()

    font_color_label = tk.Label(settings_window, text="字体颜色")
    font_color_label.pack(pady=5)

    font_color_var = tk.StringVar(value="black")
    font_color_menu = ttk.Combobox(settings_window, textvariable=font_color_var, values=["black", "red", "green", "blue", "yellow", "purple"])
    font_color_menu.pack()

    font_preview_label = tk.Label(settings_window, text="字体预览", font=(font_var.get(), font_size_var.get()), fg=font_color_var.get())
    font_preview_label.pack(pady=5)

    font_menu.bind("<<ComboboxSelected>>", lambda event: font_preview_label.config(font=(font_var.get(), font_size_var.get())))
    font_size_menu.bind("<<ComboboxSelected>>", lambda event: font_preview_label.config(font=(font_var.get(), font_size_var.get())))
    font_color_menu.bind("<<ComboboxSelected>>", lambda event: font_preview_label.config(fg=font_color_var.get()))

    apply_button = tk.Button(settings_window, text="应用", command=lambda: [apply_settings(), settings_window.destroy()])
    apply_button.pack(pady=10)

def check_connection():
    try:
        response = requests.get("https://yuapi.karpov.cn/api/luoli.php?type=json")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        return e.response.status_code if e.response else "无法连接"

def show_loading_window():
    loading_window = tk.Toplevel(root)
    loading_window.title("检查连接")
    loading_window.geometry("300x100")
    tk.Label(loading_window, text="正在检查网络连接，请稍候...").pack(pady=20)
    root.update_idletasks()
    return loading_window

def start_application():
    loading_window = show_loading_window()
    status = check_connection()
    loading_window.destroy()
    if status is True:
        root.deiconify()  # 显示主窗口
        create_main_window()
    else:
        messagebox.showerror("网络错误", f"无法连接到服务器，状态码: {status}")
        root.destroy()

def create_main_window():
    global root, text_editor, current_theme, open_windows, font_preview_label, thread_count
    root.title("随机萝莉")
    root.geometry("300x400")  # 设置窗口大小为300x400

    current_theme = "light"
    open_windows = []
    thread_count = os.cpu_count()

    menu_bar = Menu(root)
    settings_menu = Menu(menu_bar, tearoff=0)
    settings_menu.add_command(label="设置", command=open_settings)
    menu_bar.add_cascade(label="设置", menu=settings_menu)
    root.config(menu=menu_bar)

    video_label = tk.Label(root, text="随机萝莉视频下载工具")
    video_label.pack(expand=True)  # 设置标签在窗口中央显示

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var)
    progress_bar.pack(fill=tk.X, padx=10, pady=10)

    progress_label = tk.Label(root, text="已下载: 0/0 未下载: 0")
    progress_label.pack()

    change_button = tk.Button(root, text="获取视频", command=prompt_for_count)
    change_button.pack()

    # 添加带有纵向滚动条的文本编辑器
    text_frame = tk.Frame(root)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 30))  # 调整底部填充，避免遮挡
    text_scroll = tk.Scrollbar(text_frame)
    text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    text_editor = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=text_scroll.set)
    text_editor.pack(fill=tk.BOTH, expand=True)
    text_scroll.config(command=text_editor.yview)

    # 添加底部正中央的标签
    footer_label = tk.Label(root, text="亿染工作室制作", anchor='center')
    footer_label.pack(side=tk.BOTTOM, pady=5)

    root.mainloop()

root = tk.Tk()
root.withdraw()  # 隐藏主窗口，直到检查连接完成
start_application()
