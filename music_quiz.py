import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import os
from pathlib import Path
import datetime

class MusicQuiz:
    def __init__(self, root):
        self.root = root
        self.root.title("看谱识曲练习")
        self.root.geometry("800x600")
        
        # 添加答题状态标志
        self.answered = False
        
        # 绑定键盘事件
        self.root.bind('a', lambda e: self.handle_shortcut(0))
        self.root.bind('b', lambda e: self.handle_shortcut(1))
        self.root.bind('c', lambda e: self.handle_shortcut(2))
        self.root.bind('d', lambda e: self.handle_shortcut(3))
        # 添加左右方向键绑定
        self.root.bind('<Left>', lambda e: self.prev_question())
        self.root.bind('<Right>', lambda e: self.next_question())
        
        # 初始化数据
        self.songs_dir = Path("songs")
        self.song_files = list(self.songs_dir.glob("*.jpg")) + list(self.songs_dir.glob("*.png"))
        
        # 确保result文件夹存在
        self.result_dir = Path("result")
        self.result_dir.mkdir(exist_ok=True)
        
        # 添加答题记录
        self.question_states = {}  # 用于记录每题的答题状态
        
        # 显示设置界面
        self.show_settings()

    def show_settings(self):
        # 清空现有界面
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 创建主框架并设置样式
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        settings_frame = ttk.Frame(self.main_frame)
        settings_frame.pack(expand=True)
        
        # 标题
        title_label = ttk.Label(
            settings_frame,
            text="看谱识曲练习设置",
            font=("Microsoft YaHei UI", 24, "bold")
        )
        title_label.pack(pady=30)
        
        # 创建内容框架
        content_frame = ttk.Frame(settings_frame, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 题目数量选择标题
        ttk.Label(
            content_frame,
            text="练习题目数量",
            font=("Microsoft YaHei UI", 14)
        ).pack(pady=(0,15))
        
        # 创建题目数量选择框
        question_frame = ttk.Frame(content_frame)
        question_frame.pack(pady=10)
        
        self.question_count = tk.StringVar(value="20")
        
        # 预设选项按钮,使用更现代的样式
        presets = ["10", "15", "20", "30"]
        for count in presets:
            btn = ttk.Radiobutton(
                question_frame,
                text=count+"题",
                value=count,
                variable=self.question_count,
                style='TRadiobutton'
            )
            btn.pack(side=tk.LEFT, padx=15)
            
        # 自定义数量输入框
        custom_frame = ttk.Frame(content_frame)
        custom_frame.pack(pady=20)
        
        ttk.Label(
            custom_frame,
            text="自定义题目数量：",
            font=("Microsoft YaHei UI", 12)
        ).pack(side=tk.LEFT, padx=5)
        
        self.custom_entry = ttk.Entry(custom_frame, width=8, font=("Microsoft YaHei UI", 12))
        self.custom_entry.pack(side=tk.LEFT, padx=5)
        
        # 总题目数显示
        total_songs = len(self.song_files)
        ttk.Label(
            content_frame,
            text=f"题库总题数：{total_songs}",
            font=("Microsoft YaHei UI", 12),
            foreground='#666666'
        ).pack(pady=15)
        
        # 开始按钮
        start_btn = ttk.Button(
            content_frame,
            text="开始练习",
            command=self.start_quiz,
            style='Accent.TButton',
            width=20
        )
        start_btn.pack(pady=30)
        
        # 添加按钮样式
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Microsoft YaHei UI', 12))

    def start_quiz(self):
        # 获取选择的题目数量
        custom_value = self.custom_entry.get().strip()
        if custom_value.isdigit():
            self.questions_per_round = int(custom_value)
        else:
            self.questions_per_round = int(self.question_count.get())
        
        # 验证题目数量
        if self.questions_per_round < 1:
            self.questions_per_round = 1
        

        # 初始化练习数据
        self.current_index = 0
        self.total_count = 0
        self.correct_count = 0
        self.total_count = 0
        self.wrong_answers = []

        # 重新组织题目文件
        song_groups = {}
        for song_file in self.song_files:
            # 检查文件名是否包含 "-数字" 的模式
            base_name = song_file.stem
            if "-" in base_name:
                # 尝试分离基础名称和编号
                name_parts = base_name.rsplit("-", 1)
                if len(name_parts) == 2 and name_parts[1].isdigit():
                    base_name = name_parts[0]
            
            # 将相同基础名称的文件分组
            if base_name not in song_groups:
                song_groups[base_name] = []
            song_groups[base_name].append(song_file)
        
        # 从每个组中随机选择一个文件
        available_songs = []
        for group in song_groups.values():
            available_songs.append(random.choice(group))
        
        # 随机选择题目
        total_songs = len(available_songs)
        if self.questions_per_round <= total_songs:
            # 如果题目数量不超过可用题目，直接随机选择
            self.current_questions = random.sample(available_songs, self.questions_per_round)
        else:
            # 如果题目数量超过可用题目，需要重复选择
            self.current_questions = []
            full_rounds = self.questions_per_round // total_songs
            remaining_questions = self.questions_per_round % total_songs
            
            # 添加完整轮次的题目
            for _ in range(full_rounds):
                shuffled_songs = random.sample(available_songs, total_songs)
                self.current_questions.extend(shuffled_songs)
            
            # 添加剩余题目
            if remaining_questions > 0:
                shuffled_songs = random.sample(available_songs, remaining_questions)
                self.current_questions.extend(shuffled_songs)
        
        # 创建练习界面
        self.setup_ui()
        self.show_question()

    def start_new_round(self):
        # 返回设置界面
        self.show_settings()

    def setup_ui(self):
        # 清空现有界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # 顶部信息框架
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X)

        # 左侧进度显示
        progress_frame = ttk.Frame(top_frame)
        progress_frame.pack(side=tk.LEFT)
        self.progress_label = ttk.Label(
            progress_frame,
            text=f"第 {self.current_index + 1}/{self.questions_per_round} 题",
            font=("Arial", 12, "bold")
        )
        self.progress_label.pack(side=tk.LEFT)

        # 右侧正确率显示
        score_frame = ttk.Frame(top_frame)
        score_frame.pack(side=tk.RIGHT)
        self.score_label = ttk.Label(
            score_frame,
            text="正确率: 0%",
            font=("Arial", 12, "bold")
        )
        self.score_label.pack()

        # 中间内容区域
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(expand=True, fill=tk.BOTH, pady=20)

        # 题号显示
        self.number_label = ttk.Label(
            content_frame,
            text=f"#{self.current_index + 1}",
            font=("Arial", 14, "bold")
        )
        self.number_label.pack(anchor='w', padx=5)

        # 图片显示区域
        image_frame = ttk.Frame(content_frame)
        image_frame.pack(expand=True)

        # 左箭头按钮
        prev_btn = ttk.Button(
            image_frame,
            text="←",
            command=self.prev_question,
            width=3
        )
        prev_btn.pack(side=tk.LEFT, padx=10)

        # 图片标签
        self.image_label = tk.Label(image_frame)
        self.image_label.pack(side=tk.LEFT, padx=20)

        # 右箭头按钮
        next_btn = ttk.Button(
            image_frame,
            text="→", 
            command=self.next_question,
            width=3
        )
        next_btn.pack(side=tk.LEFT, padx=10)

        # 选项区域
        options_frame = ttk.Frame(self.main_frame)
        options_frame.pack(fill=tk.X, pady=20)

        # 创建两行选项按钮
        self.option_buttons = []
        labels = ['A', 'B', 'C', 'D']  # 添加选项标签
        for i in range(2):
            row_frame = ttk.Frame(options_frame)
            row_frame.pack(fill=tk.X, pady=5)
            for j in range(2):
                # 创建选项容器
                option_container = ttk.Frame(row_frame)
                option_container.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
                
                # 添加选项标签
                idx = i * 2 + j
                ttk.Label(
                    option_container,
                    text=labels[idx],
                    font=("Arial", 12, "bold")
                ).pack(side=tk.LEFT, padx=(0, 10))
                
                # 添加选项按钮
                btn = ttk.Button(option_container)
                btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
                self.option_buttons.append(btn)

        # 底部控制区域
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        # 上一题/下一题按钮
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack()
        ttk.Button(nav_frame, text="上一题", command=self.prev_question).pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="下一题", command=self.next_question).pack(side=tk.LEFT, padx=10)

        # 反馈信息
        self.feedback_label = ttk.Label(self.main_frame, text="", font=("Arial", 12))
        self.feedback_label.pack(pady=10)

    def show_question(self):
        # 重置答题状态（仅对未答过的题）
        current_song = self.current_questions[self.current_index]
        if current_song not in self.question_states:
            self.answered = False
        else:
            self.answered = True
        
        # 启用所有按钮并重置样式
        if hasattr(self, 'option_buttons'):
            style = ttk.Style()
            for btn in self.option_buttons:
                btn['state'] = 'normal' if not self.answered else 'disabled'
                btn['style'] = 'TButton'  # 重置为默认样式
            
        # 清除反馈信息
        if hasattr(self, 'feedback_label'):
            self.feedback_label.configure(text="")
        
        # 更新进度显示
        self.progress_label.configure(text=f"第 {self.current_index + 1}/{self.questions_per_round} 题")
        if self.total_count > 0:
            accuracy = (self.correct_count / self.total_count) * 100
            self.score_label.configure(text=f"正确率: {accuracy:.1f}%")

        # 更新序号显示
        self.number_label.configure(text=f"#{self.current_index + 1}")
        
        # 获取当前题目
        current_song = self.current_questions[self.current_index]
        
        # 显示图片
        image = Image.open(current_song)
        image = image.resize((600, 300), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo

        # 如果这题已经答过，使用保存的选项
        if current_song in self.question_states:
            state = self.question_states[current_song]
            options = state['options']
            correct_answer = state['correct']
        else:
            # 生成新的选项
            correct_answer = current_song.stem
            # 移除正确答案中的数字后缀
            if "-" in correct_answer:
                name_parts = correct_answer.rsplit("-", 1)
                if len(name_parts) == 2 and name_parts[1].isdigit():
                    correct_answer = name_parts[0]

            # 获取所有可能的选项，并移除数字后缀
            all_songs = []
            for f in self.song_files:
                name = f.stem
                if "-" in name:
                    name_parts = name.rsplit("-", 1)
                    if len(name_parts) == 2 and name_parts[1].isdigit():
                        name = name_parts[0]
                if name not in all_songs:  # 避免重复选项
                    all_songs.append(name)

            wrong_options = [s for s in all_songs if s != correct_answer]
            options = random.sample(wrong_options, 3) + [correct_answer]
            random.shuffle(options)

        # 更新按钮
        for i, button in enumerate(self.option_buttons):
            button.configure(
                text=options[i],
                command=lambda x=options[i], btn=button: self.check_answer(x, correct_answer, btn)
            )
            
            # 如果题目已经答过，显示正确和错误状态
            if current_song in self.question_states:
                state = self.question_states[current_song]
                if options[i] == state['selected']:  # 用户选择的选项
                    button.configure(style='Wrong.TButton' if state['selected'] != state['correct'] else 'Correct.TButton')
                elif options[i] == state['correct']:  # 正确答案
                    button.configure(style='Correct.TButton')
                button['state'] = 'disabled'  # 禁用已答过的题目的按钮

        # 更新进度
        self.progress_label.configure(text=f"count: {self.total_count + 1}/{self.questions_per_round}")

    def check_answer(self, selected, correct, selected_button):
        # 如果已经回答过，直接返回
        if self.answered:
            return
        
        self.answered = True
        self.total_count += 1
        
        # 保存答题状态
        current_song = self.current_questions[self.current_index]
        self.question_states[current_song] = {
            'selected': selected,
            'correct': correct,
            'options': [btn['text'] for btn in self.option_buttons]  # 保存所有选项
        }
        
        # 禁用所有按钮
        for btn in self.option_buttons:
            btn['state'] = 'disabled'
        
        # 设置按钮样式
        style = ttk.Style()
        style.configure('Correct.TButton', background='green')
        style.configure('Wrong.TButton', background='red')
        
        # 找到正确答案的按钮
        correct_button = None
        for btn in self.option_buttons:
            if btn['text'] == correct:
                correct_button = btn
                break

        if selected == correct:
            self.correct_count += 1
            selected_button.configure(style='Correct.TButton')
            self.feedback_label.configure(text="回答正确！", foreground="green")
        else:
            selected_button.configure(style='Wrong.TButton')
            correct_button.configure(style='Correct.TButton')
            self.feedback_label.configure(text=f"回答错误！正确答案是：{correct}", foreground="red")
            # 记录错误答案
            self.wrong_answers.append((correct, selected))

        # 更新正确率
        accuracy = (self.correct_count / self.total_count) * 100
        self.score_label.configure(text=f"正确率: {accuracy:.1f}%")

        # 检查是否完成本轮
        if self.total_count >= self.questions_per_round:
            self.show_round_complete()
        else:
            # 延迟1.5秒后进入下一题
            self.root.after(1500, self.next_question)

    def show_round_complete(self):
        # 保存结果到文件
        self.save_result()
        
        # 显示本轮结果
        for widget in self.root.winfo_children():
            widget.destroy()
        
        result_frame = ttk.Frame(self.root)
        result_frame.pack(expand=True)
        
        # 创建结果显示的文本框
        result_text = tk.Text(result_frame, width=50, height=20, font=("Arial", 12))
        result_text.pack(pady=20)
        
        # 添加结果信息
        wrong_count = len(self.wrong_answers)
        accuracy = (self.correct_count/self.questions_per_round)*100
        
        result_text.insert('end', f"本轮练习完成！\n\n")
        result_text.insert('end', f"总题数：{self.questions_per_round}\n")
        result_text.insert('end', f"正确数：{self.correct_count}\n")
        result_text.insert('end', f"错误数：{wrong_count}\n")
        result_text.insert('end', f"正确率：{accuracy:.1f}%\n\n")
        
        if wrong_count > 0:
            result_text.insert('end', "错误题目列表：\n")
            for correct, selected in self.wrong_answers:
                result_text.insert('end', f"正确答案：{correct} - 你的答案：{selected}\n")
        
        result_text.configure(state='disabled')  # 设置为只读
        
        # 添加新一轮按钮
        ttk.Button(
            result_frame,
            text="开始新一轮",
            command=self.start_new_round
        ).pack(pady=20)

    def save_result(self):
        # 获取当前时间
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # 创建结果文件
        result_file = self.result_dir / f"quiz_result_{current_time}.txt"
        
        with result_file.open('w', encoding='utf-8') as f:
            # 写入基本信息
            accuracy = (self.correct_count/self.questions_per_round)*100
            f.write(f"时间：{current_time}\n")
            f.write(f"正确率：{accuracy:.1f}%\n")
            f.write(f"错误数：{len(self.wrong_answers)}\n")
            f.write("\n错误的歌曲：\n")
            
            # 写入错误答案
            for correct, selected in self.wrong_answers:
                f.write(f"正确答案：{correct} - 错误选择：{selected}\n")

    def next_question(self):
        if self.total_count < self.questions_per_round:
            self.current_index = (self.current_index + 1) % self.questions_per_round
            self.show_question()

    def prev_question(self):
        if self.total_count < self.questions_per_round:
            self.current_index = (self.current_index - 1) % self.questions_per_round
            self.show_question()

    def handle_shortcut(self, index):
        # 如果已经回答过或者不在答题界面，则返回
        if hasattr(self, 'answered') and self.answered:
            return
        if hasattr(self, 'option_buttons') and len(self.option_buttons) > index:
            button = self.option_buttons[index]
            if button['state'] != 'disabled':
                button.invoke()

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicQuiz(root)
    root.mainloop() 