# -*- coding: utf-8 -*-
# 0-1分组背包问题求解器
# 界面布局完全匹配需求，功能完整：读取、排序、求解、导出、绘图

# 导入GUI库tkinter
import tkinter as tk
# 文件选择、消息提示、滚动文本框
from tkinter import filedialog, messagebox, scrolledtext
import turtle

# 默认背包容量（未读取文件时使用）
MAX_CAPACITY_DEFAULT = 100

# ===================== 数据加载模块 =====================
# 功能：从txt文件读取背包容量和物品组数据
def load_data(filepath):
    try:
        # 以UTF-8编码打开数据文件
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        # 第一行 = 背包总容量
        cap = int(lines[0])
        groups = []

        # 逐行解析物品组（每组3个物品，共6个数值：w1 v1 w2 v2 w3 v3）
        for line in lines[1:]:
            nums = list(map(int, line.split()))
            g = [(nums[0], nums[1]), (nums[2], nums[3]), (nums[4], nums[5])]
            groups.append(g)

        return cap, groups

    # 异常处理：文件格式错误、读取失败
    except Exception as e:
        print(f"加载错误: {e}")
        return None, None

# ===================== 背包算法模块 =====================
# 排序规则：按每组第三个物品的【价值/重量比】降序排序
def sort_groups(groups):
    def ratio(g):
        w, v = g[2]
        return v / w if w != 0 else 999  # 避免除零错误
    return sorted(groups, key=ratio, reverse=True)

# 动态规划求解0-1分组背包（每组只能选一个物品）
def solve_knapsack(capacity, groups):
    n = len(groups)
    # dp[w] 表示容量w时的最大价值
    dp = [0] * (capacity + 1)
    # path[w] 记录每个容量选择了哪个物品（用于回溯方案）
    path = [None] * (capacity + 1)

    # 遍历每一组
    for i in range(n):
        (w1, v1), (w2, v2), (w3, v3) = groups[i]
        # 逆序遍历容量，保证每个物品只选一次
        for w in range(capacity, -1, -1):
            # 尝试选组内第一个物品
            if w >= w1 and dp[w - w1] + v1 > dp[w]:
                dp[w] = dp[w - w1] + v1
                path[w] = (i, 0)
            # 尝试选组内第二个物品
            if w >= w2 and dp[w - w2] + v2 > dp[w]:
                dp[w] = dp[w - w2] + v2
                path[w] = (i, 1)
            # 尝试选组内第三个物品
            if w >= w3 and dp[w - w3] + v3 > dp[w]:
                dp[w] = dp[w - w3] + v3
                path[w] = (i, 2)

    # 回溯：从最大容量倒推选中的物品方案
    selected = []
    cur = capacity
    while cur > 0 and path[cur] is not None:
        g, idx = path[cur]
        selected.append((g + 1, idx + 1))  # 转为从1开始的编号
        cur -= groups[g][idx][0]

    # 返回最大价值与选中物品列表
    return dp[capacity], selected

# ===================== 结果导出模块 =====================
# 导出为TXT文件
def export_txt(result, filepath):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"背包容量：{result['cap']}\n")
            f.write(f"最大价值：{result['max_val']}\n")
            f.write(f"求解时间：{result['time']} 秒\n")
            f.write("选中物品：\n")
            for g, idx in result['selected']:
                f.write(f"第{g}组 第{idx}个\n")
        return True
    except:
        return False

# 导出为Excel文件（需要pandas库）
def export_excel(result, filepath):
    try:
        import pandas as pd
        df = pd.DataFrame([{
            "背包容量": result['cap'],
            "最大价值": result['max_val'],
            "求解时间(秒)": result['time'],
            "选中物品": "; ".join([f"第{g}组第{idx}个" for g, idx in result['selected']])
        }])
        df.to_excel(filepath, index=False)
        return True
    except:
        return False

# ===================== 散点图绘图模块 =====================
# 使用turtle绘制重量-价值散点图
def draw_scatter(groups):
    if not groups:
        messagebox.showwarning("提示", "请先加载数据")
        return

    # 收集所有点，确定坐标范围
    points = []
    max_w = 0
    max_v = 0
    for g in groups:
        for (w, v) in g:
            points.append((w, v))
            if w > max_w: max_w = w
            if v > max_v: max_v = v

    if not points:
        messagebox.showwarning("提示", "无物品数据可绘图")
        return

    # 初始化绘图窗口
    screen = turtle.Screen()
    screen.title("重量-价值散点图")
    screen.setup(width=800, height=600)
    screen.setworldcoordinates(-10, -10, max_w + 10, max_v + 10)

    # 画笔设置
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    colors = ["red", "blue", "green", "orange", "purple", "cyan"]

    # 绘制坐标轴
    t.penup()
    t.goto(0, 0)
    t.pendown()
    t.goto(max_w + 5, 0)    # X轴（重量）
    t.penup()
    t.goto(0, 0)
    t.pendown()
    t.goto(0, max_v + 5)    # Y轴（价值）

    # 坐标轴标注
    t.penup()
    t.goto(max_w + 5, -5)
    t.write("重量", font=("Arial", 12, "normal"))
    t.goto(-5, max_v + 5)
    t.write("价值", font=("Arial", 12, "normal"))

    # 绘制每个物品的散点
    for group_idx, group in enumerate(groups):
        color = colors[group_idx % len(colors)]
        t.pencolor(color)
        t.fillcolor(color)
        for item_idx, (w, v) in enumerate(group):
            t.penup()
            t.goto(w, v)
            t.pendown()
            t.begin_fill()
            t.circle(5)        # 画圆点
            t.end_fill()
            t.penup()
            t.goto(w + 2, v + 2)
            t.write(f"{group_idx+1}-{item_idx+1}", font=("Arial", 10, "normal"))

    messagebox.showinfo("成功", "散点图已打开，关闭窗口后继续操作")
    screen.mainloop()

# ===================== GUI主界面 =====================
# 主窗口类
class KnapsackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("D{0-1}背包问题求解器")  # 窗口标题
        self.geometry("1200x800")          # 窗口大小
        self.file_path = tk.StringVar()    # 文件路径变量
        self.capacity = 0                  # 背包容量
        self.groups = []                   # 物品组
        self.result = None                 # 求解结果
        self.create_widgets()              # 创建界面组件

    # 创建所有GUI组件
    def create_widgets(self):
        # 1. 数据文件选择行
        frame_file = tk.Frame(self)
        frame_file.pack(pady=10, anchor="w", padx=10)
        tk.Label(frame_file, text="数据文件：", font=("微软雅黑", 14)).pack(side=tk.LEFT)
        tk.Entry(frame_file, textvariable=self.file_path, width=80, font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_file, text="选择文件", font=("微软雅黑", 12), command=self.select_file).pack(side=tk.LEFT)

        # 2. 第一排功能按钮
        frame_btn1 = tk.Frame(self)
        frame_btn1.pack(pady=5, anchor="w", padx=10)
        tk.Button(frame_btn1, text="读取数据", font=("微软雅黑", 14), width=15, command=self.load_data).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btn1, text="排序物品组", font=("微软雅黑", 14), width=15, command=self.sort_groups).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btn1, text="求解最优解", font=("微软雅黑", 14), width=15, command=self.solve).pack(side=tk.LEFT, padx=10)

        # 3. 第二排功能按钮
        frame_btn2 = tk.Frame(self)
        frame_btn2.pack(pady=5, anchor="w", padx=10)
        tk.Button(frame_btn2, text="导出为TXT", font=("微软雅黑", 14), width=15, command=self.export_txt).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btn2, text="导出为Excel", font=("微软雅黑", 14), width=15, command=self.export_excel).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btn2, text="绘制散点图", font=("微软雅黑", 14), width=15, command=self.draw_plot).pack(side=tk.LEFT, padx=10)

        # 4. 求解结果显示区域
        tk.Label(self, text="求解结果：", font=("微软雅黑", 16)).pack(pady=5, anchor="w", padx=10)
        self.result_box = scrolledtext.ScrolledText(self, font=("微软雅黑", 12), height=25)
        self.result_box.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    # 选择数据文件
    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt")])
        if path:
            self.file_path.set(path)

    # 加载数据
    def load_data(self):
        if not self.file_path.get():
            messagebox.showwarning("提示", "请先选择数据文件")
            return
        cap, groups = load_data(self.file_path.get())
        if not groups:
            messagebox.showerror("错误", "数据格式错误，请检查文件")
            return
        self.capacity = cap
        self.groups = groups
        self.result_box.delete(1.0, tk.END)
        self.result_box.insert(tk.END, f"✅ 数据加载成功\n背包容量：{cap}\n物品组数：{len(groups)}\n每组3个物品")

    # 排序物品组
    def sort_groups(self):
        if not self.groups:
            messagebox.showwarning("提示", "请先加载数据")
            return
        self.groups = sort_groups(self.groups)
        self.result_box.delete(1.0, tk.END)
        self.result_box.insert(tk.END, "✅ 已按每组第3个物品的价值/重量比降序排序")

    # 求解背包最优解
    def solve(self):
        if not self.groups:
            messagebox.showwarning("提示", "请先加载数据")
            return
        import time
        start = time.time()
        max_val, selected = solve_knapsack(self.capacity, self.groups)
        cost = round(time.time() - start, 4)
        self.result = {
            "cap": self.capacity,
            "max_val": max_val,
            "selected": selected,
            "time": cost
        }
        self.result_box.delete(1.0, tk.END)
        self.result_box.insert(tk.END, f"🎯 求解完成\n背包容量：{self.capacity}\n最大价值：{max_val}\n求解耗时：{cost} 秒\n\n选中物品：\n")
        for g, idx in selected:
            self.result_box.insert(tk.END, f"第{g}组 第{idx}个\n")

    # 导出TXT
    def export_txt(self):
        if not self.result:
            messagebox.showwarning("提示", "请先求解最优解")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt")])
        if not path:
            return
        if export_txt(self.result, path):
            messagebox.showinfo("成功", "已导出为 TXT 文件")
        else:
            messagebox.showerror("失败", "导出 TXT 文件失败")

    # 导出Excel
    def export_excel(self):
        if not self.result:
            messagebox.showwarning("提示", "请先求解最优解")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel 文件", "*.xlsx")])
        if not path:
            return
        if export_excel(self.result, path):
            messagebox.showinfo("成功", "已导出为 Excel 文件")
        else:
            messagebox.showerror("失败", "导出 Excel 文件失败，请检查是否安装 pandas：pip install pandas openpyxl")

    # 打开散点图
    def draw_plot(self):
        if not self.groups:
            messagebox.showwarning("提示", "请先加载数据")
            return
        draw_scatter(self.groups)

# ===================== 程序入口 =====================
if __name__ == "__main__":
    app = KnapsackApp()
    app.mainloop()