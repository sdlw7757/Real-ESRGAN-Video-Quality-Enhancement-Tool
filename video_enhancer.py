import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import threading
import shutil
import signal
import psutil

class VideoEnhancerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-ESRGAN 视频画质增强工具")
        self.root.geometry("800x700")  # 增大窗口尺寸以容纳注释
        self.root.minsize(800, 700)    # 设置最小尺寸
        self.root.resizable(True, True)
        
        # 获取项目根目录
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        
        # 运行日志
        self.log_messages = []
        
        # 子进程列表
        self.processes = []
        
        # 创建界面元素
        self.create_widgets()
        
        # 初始化路径
        self.init_paths()
        
        # 绑定模型选择事件
        self.model_var.trace('w', self.on_model_change)
        
    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="Real-ESRGAN 视频画质增强工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 视频文件选择框
        video_frame = tk.Frame(self.root)
        video_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(video_frame, text="选择视频文件:").pack(anchor=tk.W)
        
        file_frame = tk.Frame(video_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        self.video_path_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.video_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(file_frame, text="浏览", command=self.browse_video).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 参数设置框
        params_frame = tk.LabelFrame(self.root, text="增强参数")
        params_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 模型选择
        model_frame = tk.Frame(params_frame)
        model_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(model_frame, text="增强模型:").pack(side=tk.LEFT)
        
        self.model_var = tk.StringVar(value="realesr-animevideov3")
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                  values=["realesr-animevideov3", "realesrgan-x4plus", "realesrgan-x4plus-anime"],
                                  state="readonly", width=25)
        model_combo.pack(side=tk.RIGHT)
        
        # 模型用途说明
        model_description_frame = tk.Frame(params_frame)
        model_description_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.model_description_label = tk.Label(model_description_frame, text="realesr-animevideov3 - 通用动漫视频增强模型", 
                                               font=("Arial", 8), fg="gray", wraplength=700, justify="left")
        self.model_description_label.pack(anchor=tk.W)
        
                # 缩放因子
        scale_frame = tk.Frame(params_frame)
        scale_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(scale_frame, text="缩放因子:").pack(side=tk.LEFT)
        
        self.scale_var = tk.StringVar(value="2")
        self.scale_combo = ttk.Combobox(scale_frame, textvariable=self.scale_var,
                                       values=["2", "3", "4"],
                                       state="readonly", width=25)
        self.scale_combo.pack(side=tk.RIGHT)
        
        # 输出格式
        format_frame = tk.Frame(params_frame)
        format_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT)
        
        self.format_var = tk.StringVar(value="jpg")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                   values=["jpg", "png"],
                                   state="readonly", width=25)
        format_combo.pack(side=tk.RIGHT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=20, pady=10)
        
        # 进度百分比标签
        self.progress_label = tk.Label(self.root, text="0%")
        self.progress_label.pack()
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, fg="blue")
        self.status_label.pack(pady=5)
        
        # 日志框
        log_frame = tk.LabelFrame(self.root, text="运行日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, state="disabled")  # 减小高度
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 日志操作按钮
        log_button_frame = tk.Frame(log_frame)
        log_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(log_button_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT)
        tk.Button(log_button_frame, text="复制日志", command=self.copy_log).pack(side=tk.LEFT, padx=5)
        
        # 控制按钮
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(button_frame, text="开始增强", command=self.start_enhancement, 
                                     bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                                     padx=20)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="退出", command=self.exit_application,
                 bg="#f44336", fg="white", font=("Arial", 10, "bold"),
                 padx=20).pack(side=tk.LEFT, padx=10)
        
    def init_paths(self):
        """初始化必要的路径"""
        self.tmp_frames_dir = os.path.join(self.project_root, "tmp_frames")
        self.out_frames_dir = os.path.join(self.project_root, "out_frames")
        
        # 创建必要的目录
        os.makedirs(self.tmp_frames_dir, exist_ok=True)
        os.makedirs(self.out_frames_dir, exist_ok=True)
        
    def on_model_change(self, *args):
        """当模型选择改变时的处理函数"""
        selected_model = self.model_var.get()
        
        # 更新模型用途说明
        model_descriptions = {
            "realesr-animevideov3": "通用动漫视频增强模型",
            "realesrgan-x4plus": "通用视频增强模型，适用于各种类型的视频",
            "realesrgan-x4plus-anime": "专门针对动漫图像优化的增强模型"
        }
        
        description = model_descriptions.get(selected_model, "")
        self.model_description_label.config(text=f"{selected_model} - {description}")
        
        if selected_model in ["realesrgan-x4plus", "realesrgan-x4plus-anime"]:
            # 固定缩放因子为4
            self.scale_var.set("4")
            # 禁用缩放因子选择
            self.scale_combo.config(state="disabled")
        else:
            # 启用缩放因子选择
            self.scale_combo.config(state="readonly")
            
    def exit_application(self):
        """退出应用程序并结束所有进程"""
        # 终止所有子进程
        for process in self.processes:
            try:
                # 尝试优雅地终止进程
                process.terminate()
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # 如果进程没有响应，强制终止
                process.kill()
            except Exception as e:
                self.log(f"终止进程时出错: {e}")
        
        # 查找并终止可能的残留进程
        try:
            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass
            
            # 等待进程结束
            gone, alive = psutil.wait_procs(children, timeout=3)
            for p in alive:
                try:
                    p.kill()
                except psutil.NoSuchProcess:
                    pass
        except Exception as e:
            self.log(f"清理进程时出错: {e}")
        
        # 退出应用
        self.root.quit()
        self.root.destroy()
        
    def log(self, message):
        """添加日志信息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        # 添加到日志列表
        self.log_messages.append(log_message)
        
        # 更新日志文本框
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, log_message + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)  # 滚动到最新日志
        
        # 更新状态标签
        self.status_var.set(message)
        self.root.update()
        
    def clear_log(self):
        """清空日志"""
        self.log_messages = []
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        
    def copy_log(self):
        """复制日志到剪贴板"""
        log_content = "\n".join(self.log_messages)
        self.root.clipboard_clear()
        self.root.clipboard_append(log_content)
        messagebox.showinfo("提示", "日志已复制到剪贴板")
        
    def browse_video(self):
        """浏览选择视频文件"""
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.video_path_var.set(file_path)
            
    def get_video_fps(self, video_path):
        """获取视频的FPS"""
        try:
            self.log("正在获取视频帧率...")
            
            cmd = [
                os.path.join(self.project_root, "ffmpeg.exe"),
                "-i", video_path
            ]
            
            # 创建子进程并添加到进程列表
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            
            # 修复：同时捕获stdout和stderr，并将它们组合起来进行分析
            stdout, stderr = process.communicate()
            # ffmpeg的详细信息通常输出到stderr，所以我们需要检查stderr
            output = (stdout.decode('utf-8', errors='ignore') + 
                     stderr.decode('utf-8', errors='ignore'))
            
            # 查找FPS信息 - 改进的模式匹配
            import re
            
            # 首先尝试匹配标准的fps模式
            fps_patterns = [
                r"(\d+(?:\.\d+)?)\s+fps",  # 标准fps模式，如 "23.98 fps"
                r"(\d+(?:\.\d+)?)\s*tbr",  # 平均帧率模式，如 "23.98 tbr"
                r"(\d+(?:\.\d+)?)\s+fps,",  # 带逗号的fps模式
                r",\s*(\d+(?:\.\d+)?)\s+fps",  # 逗号后的fps模式
                r"(\d+(?:\.\d+)?)\s+tbr,",  # 带逗号的tbr模式
                r",\s*(\d+(?:\.\d+)?)\s+tbr"   # 逗号后的tbr模式
            ]
            
            for pattern in fps_patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    fps = float(match.group(1))
                    self.log(f"检测到视频帧率: {fps} FPS")
                    return fps
            
            # 如果标准模式都未匹配，尝试更宽松的匹配
            # 匹配任何数字后跟fps或tbr的模式
            loose_patterns = [
                r"(\d+(?:\.\d+)?)\s*[fF][pP][sS]",
                r"(\d+(?:\.\d+)?)\s*[tT][bB][rR]"
            ]
            
            for pattern in loose_patterns:
                match = re.search(pattern, output)
                if match:
                    fps = float(match.group(1))
                    self.log(f"检测到视频帧率: {fps} FPS")
                    return fps
                
            self.log("未检测到帧率信息，使用默认值 30 FPS")
            return 30.0  # 默认值
        except Exception as e:
            self.log(f"获取帧率时出错: {e}，使用默认值 30 FPS")
            return 30.0
            
    def extract_frames(self, video_path):
        """从视频中提取帧"""
        try:
            self.log("正在提取视频帧...")
            
            # 清空临时帧目录
            for file in os.listdir(self.tmp_frames_dir):
                file_path = os.path.join(self.tmp_frames_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            # 提取帧 - 使用更兼容的参数
            cmd = [
                os.path.join(self.project_root, "ffmpeg.exe"),
                "-i", video_path,
                "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",  # 确保宽高为偶数
                "-q:v", "2",  # JPEG质量 (1-31, 1为最高质量)
                "-start_number", "0",  # 从0开始编号
                os.path.join(self.tmp_frames_dir, "frame%08d.jpg")
            ]
            
            self.log("执行帧提取命令...")
            # 创建子进程并添加到进程列表
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            
            _, stderr = process.communicate()
            if process.returncode != 0:
                # 如果上面的方法失败，尝试基本参数
                self.log("尝试备用帧提取方法...")
                cmd = [
                    os.path.join(self.project_root, "ffmpeg.exe"),
                    "-i", video_path,
                    "-q:v", "2",
                    os.path.join(self.tmp_frames_dir, "frame%08d.jpg")
                ]
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processes.append(process)
                
                _, stderr = process.communicate()
                if process.returncode != 0:
                    raise Exception(f"提取帧失败: {stderr.decode('utf-8', errors='ignore')}")
                
            self.log("视频帧提取完成")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"提取帧时出错: {str(e)}")
            self.log(f"提取帧时出错: {str(e)}")
            return False
            
    def enhance_frames(self):
        """使用Real-ESRGAN增强帧"""
        try:
            self.log("正在增强视频帧...")
            
            # 清空输出帧目录
            for file in os.listdir(self.out_frames_dir):
                file_path = os.path.join(self.out_frames_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            # 执行增强
            realesrgan_exe = os.path.join(self.project_root, "realesrgan-ncnn-vulkan.exe")
            if not os.path.exists(realesrgan_exe):
                raise Exception("未找到realesrgan-ncnn-vulkan.exe文件，请确保该文件在项目根目录中")
            
            # 构建命令参数
            cmd = [
                realesrgan_exe,
                "-i", self.tmp_frames_dir,
                "-o", self.out_frames_dir,
                "-n", self.model_var.get(),
                "-s", self.scale_var.get(),
                "-f", self.format_var.get()
            ]
            
            # 如果是jpg格式，添加额外参数提高兼容性
            if self.format_var.get() == "jpg":
                cmd.extend(["-g", "0"])  # 禁用GPU优化以提高兼容性
            
            self.log("执行帧增强命令...")
            # 创建子进程并添加到进程列表
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            
            _, stderr = process.communicate()
            if process.returncode != 0:
                # 尝试不带额外参数的基本命令
                self.log("尝试备用增强方法...")
                cmd = [
                    realesrgan_exe,
                    "-i", self.tmp_frames_dir,
                    "-o", self.out_frames_dir,
                    "-n", self.model_var.get(),
                    "-s", self.scale_var.get(),
                    "-f", self.format_var.get()
                ]
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processes.append(process)
                
                _, stderr = process.communicate()
                if process.returncode != 0:
                    raise Exception(f"增强帧失败: {stderr.decode('utf-8', errors='ignore')}")
                
            self.log("视频帧增强完成")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"增强帧时出错: {str(e)}")
            self.log(f"增强帧时出错: {str(e)}")
            return False
            
    def merge_frames(self, video_path):
        """将增强后的帧合并为视频"""
        try:
            self.log("正在合并视频帧...")
            
            # 获取原始视频的FPS
            fps = self.get_video_fps(video_path)
            
            # 获取桌面路径
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # 获取原始文件名和扩展名
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            ext = os.path.splitext(video_path)[1]
            
            # 生成带时间戳的文件名，确保唯一性
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_video_name = f"enhanced_{base_name}_{timestamp}{ext}"
            output_video_path = os.path.join(desktop_path, output_video_name)
            
            # 合并帧为视频 - 使用针对QQ播放器优化的参数
            # 首先尝试保留音频的版本
            cmd = [
                os.path.join(self.project_root, "ffmpeg.exe"),
                "-r", str(fps),
                "-i", os.path.join(self.out_frames_dir, "frame%08d.jpg"),
                "-i", video_path,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:a", "aac",  # 使用AAC音频编码提高兼容性
                "-c:v", "libx264",
                "-preset", "fast",  # 使用快速编码预设
                "-crf", "23",  # 视频质量控制
                "-r", str(fps),
                "-pix_fmt", "yuv420p",
                "-profile:v", "baseline",  # 使用baseline profile提高兼容性
                "-level", "3.0",  # 使用level 3.0提高兼容性
                "-movflags", "+faststart",  # 优化文件结构以便快速开始播放
                "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",  # 确保宽高为偶数
                "-g", "30",  # GOP大小
                "-bf", "0",  # 不使用B帧以提高兼容性
                output_video_path
            ]
            
            self.log("执行视频合并命令（带音频）...")
            # 创建子进程并添加到进程列表
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            
            _, stderr = process.communicate()
            if process.returncode != 0:
                # 如果上面的方法失败，尝试简化版本（仅视频）
                self.log("尝试仅视频合并...")
                cmd = [
                    os.path.join(self.project_root, "ffmpeg.exe"),
                    "-r", str(fps),
                    "-i", os.path.join(self.out_frames_dir, "frame%08d.jpg"),
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-crf", "23",
                    "-r", str(fps),
                    "-pix_fmt", "yuv420p",
                    "-profile:v", "baseline",
                    "-level", "3.0",
                    "-movflags", "+faststart",
                    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                    "-g", "30",
                    "-bf", "0",
                    output_video_path
                ]
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processes.append(process)
                
                _, stderr = process.communicate()
                if process.returncode != 0:
                    # 如果仍然失败，使用最基本的参数
                    self.log("尝试基本视频合并...")
                    cmd = [
                        os.path.join(self.project_root, "ffmpeg.exe"),
                        "-r", str(fps),
                        "-i", os.path.join(self.out_frames_dir, "frame%08d.jpg"),
                        "-c:v", "libx264",
                        "-pix_fmt", "yuv420p",
                        "-preset", "ultrafast",  # 使用最快编码速度
                        output_video_path
                    ]
                    
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.processes.append(process)
                    
                    _, stderr = process.communicate()
                    if process.returncode != 0:
                        raise Exception(f"合并视频失败: {stderr.decode('utf-8', errors='ignore')}")
            
            self.log(f"视频合并完成，输出文件: {output_video_path}")
            messagebox.showinfo("完成", f"视频增强完成！输出文件已保存到桌面:\n{output_video_path}")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"合并视频时出错: {str(e)}")
            self.log(f"合并视频时出错: {str(e)}")
            return False
            
    def update_progress(self, value):
        """更新进度条"""
        self.progress_var.set(value)
        self.progress_label.config(text=f"{int(value)}%")
        self.root.update()
            
    def enhancement_process(self):
        """执行完整的增强流程"""
        try:
            video_path = self.video_path_var.get()
            if not video_path:
                messagebox.showwarning("警告", "请先选择视频文件")
                self.log("请先选择视频文件")
                return
                
            if not os.path.exists(video_path):
                messagebox.showerror("错误", "选择的视频文件不存在")
                self.log("选择的视频文件不存在")
                return
                
            self.log("开始视频增强流程...")
            
            # 步骤1: 提取帧
            if not self.extract_frames(video_path):
                return
                
            # 更新进度
            self.update_progress(33)
            
            # 步骤2: 增强帧
            if not self.enhance_frames():
                return
                
            # 更新进度
            self.update_progress(66)
            
            # 步骤3: 合并帧
            if not self.merge_frames(video_path):
                return
                
            # 完成
            self.update_progress(100)
            self.log("视频增强流程完成")
            self.status_var.set("增强完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理过程中发生错误: {str(e)}")
            self.log(f"处理过程中发生错误: {str(e)}")
        finally:
            self.start_button.config(state="normal")
            
    def start_enhancement(self):
        """开始增强过程"""
        # 禁用开始按钮防止重复点击
        self.start_button.config(state="disabled")
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        
        # 在新线程中运行增强过程
        thread = threading.Thread(target=self.enhancement_process)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = VideoEnhancerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()