# -*- coding: utf-8 -*-
"""
D{0-1}背包问题求解
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import time
import os

# 全局常量
MAX_CAPACITY_DEFAULT = 100
RESULT_COLUMNS = ['总容量', '最大价值', '求解时间(秒)', '选择方案']


class DataLoader:
    """数据加载器"""
    @staticmethod
    def load_data(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            capacity = int(lines[0])
            groups = []
            for line in lines[1:]:
                parts = list(map(int, line.split()))
                if len(parts) != 6:
                    raise ValueError(f"数据格式错误：{line}（需6个数字）")
                group = [(parts[0], parts[1]), (parts[2], parts[3]), (parts[4], parts[5])]
                groups.append(group)
            return capacity, groups
        except Exception as e:
            messagebox.showerror("读取失败", f"数据文件读取错误：{str(e)}")
            return None, None


class KnapsackSolver:
    """背包问题求解器"""
    @staticmethod
    def sort_by_third_ratio(groups):
        try:
            def get_ratio(group):
                w, v = group[2]
                return v / w if w != 0 else float('inf')
            sorted_groups = sorted(groups, key=get_ratio, reverse=True)
            return sorted_groups
        except Exception as e:
            messagebox.showerror("排序失败", f"排序出错：{str(e)}")
            return groups

    @staticmethod
    def solve_dp(capacity, groups):
        start_time = time.time()
        n = len(groups)
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]
        path = [[None] * (capacity + 1) for _ in range(n + 1)]
        try:
            for i in range(1, n + 1):
                item1, item2, item3 = groups[i - 1]
                w1, v1 = item1
                w2, v2 = item2
                w3, v3 = item3
                for w in range(1, capacity + 1):
                    dp[i][w] = dp[i - 1][w]
                    if w >= w1 and dp[i - 1][w - w1] + v1 > dp[i][w]:
                        dp[i][w] = dp[i - 1][w - w1] + v1
                        path[i][w] = (i - 1, 0)
                    if w >= w2 and dp[i - 1][w - w2] + v2 > dp[i][w]:
                        dp[i][w] = dp[i - 1][w - w2] + v2
                        path[i][w] = (i - 1, 1)
                    if w >= w3 and dp[i - 1][w - w3] + v3 > dp[i][w]:
                        dp[i][w] = dp[i - 1][w - w3] + v3
                        path[i][w] = (i - 1, 2)
            selected = []
            current_w = capacity
            for i in range(n, 0, -1):
                if path[i][current_w] is not None:
                    group_idx, item_idx = path[i][current_w]
                    selected.append((group_idx + 1, item_idx + 1))
                    current_w -= groups[group_idx][item_idx][0]
            solve_time = round(time.time() - start_time, 6)
            selected = sorted(selected, key=lambda x: x[0])
            selected_str = "; ".join([f"第{g}组第{i}个" for g, i in selected]) or "无"
            return dp[n][capacity], selected_str, solve_time
        except Exception as e:
            messagebox.showerror("求解失败", f"动态规划求解出错：{str(e)}")
            return 0, "", 0


class ResultExporter:
    """结果导出器"""
    @staticmethod
    def export_result(result_data, file_type='txt'):
        try:
            file_ext = '.txt' if file_type == 'txt' else '.xlsx'
            save_path = filedialog.asksaveasfilename(
                defaultextension=file_ext,
                filetypes=[(f"{file_type.upper()}文件", f"*{file_ext}"), ("所有文件", "*.*")]
            )
            if not save_path:
                return False
            if file_type == 'txt':
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write("D{0-1}背包问题求解结果\n")
                    f.write("=" * 30 + "\n")
                    f.write(f"背包总容量：{result_data['capacity']}\n")
                    f.write(f"最大价值：{result_data['max_value']}\n")
                    f.write(f"求解时间：{result_data['solve_time']} 秒\n")
                    f.write(f"选择方案：{result_data['selected']}\n")
            else:
                import pandas as pd
                df = pd.DataFrame([{
                    '背包总容量': result_data['capacity'],
                    '最大价值': result_data['max_value'],
                    '求解时间(秒)': result_data['solve_time'],
                    '选择方案': result_data['selected']
                }])
                df.to_excel(save_path, index=False)
            messagebox.showinfo("导出成功", f"结果已保存至：{save_path}")
            return True
        except Exception as e:
            messagebox.showerror("导出失败", f"结果导出出错：{str(e)}")
            return False


class KnapsackGUI:
    """主界面类"""
    def __init__(self, root):
        self.root = root
        self.root.title("D{0-1}背包问题求解器")
        self.root.geometry("800x500")
        self.file_path = tk.StringVar()
        self.capacity = tk.IntVar(value=MAX_CAPACITY_DEFAULT)
        self.groups = None
        self.result_data = None
        self._create_widgets()

    def _create_widgets(self):
        frame_file = tk.Frame(self.root, padx=10, pady=10)
        frame_file.pack(fill=tk.X)
        tk.Label(frame_file, text="数据文件：", font=("Arial", 12)).pack(side=tk.LEFT)
        tk.Entry(frame_file, textvariable=self.file_path, width=60, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_file, text="选择文件", command=self._select_file, font=("Arial", 12)).pack(side=tk.LEFT)

        frame_buttons = tk.Frame(self.root, padx=10, pady=10)
        frame_buttons.pack(fill=tk.X)
        tk.Button(frame_buttons, text="读取数据", command=self._load_data, font=("Arial", 12), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_buttons, text="排序物品组", command=self._sort_groups, font=("Arial", 12), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_buttons, text="求解最优解", command=self._solve_knapsack, font=("Arial", 12), width=15).pack(side=tk.LEFT, padx=5)

        frame_export = tk.Frame(self.root, padx=10, pady=10)
        frame_export.pack(fill=tk.X)
        tk.Button(frame_export, text="导出为TXT", command=lambda: self._export_result('txt'), font=("Arial", 12), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_export, text="导出为Excel", command=lambda: self._export_result('excel'), font=("Arial", 12), width=15).pack(side=tk.LEFT, padx=5)

        frame_result = tk.Frame(self.root, padx=10, pady=10)
        frame_result.pack(fill=tk.BOTH, expand=True)
        tk.Label(frame_result, text="求解结果：", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.result_text = tk.Text(frame_result, font=("Arial", 12), wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        scrollbar = tk.Scrollbar(self.result_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)

    def _select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if file_path:
            self.file_path.set(file_path)

    def _load_data(self):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showwarning("警告", "请先选择有效的数据文件！")
            return
        capacity, groups = DataLoader.load_data(file_path)
        if capacity and groups:
            self.capacity.set(capacity)
            self.groups = groups
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"✅ 数据加载成功！\n")
            self.result_text.insert(tk.END, f"📦 背包容量：{capacity}\n")
            self.result_text.insert(tk.END, f"📝 物品组数量：{len(groups)}\n")

    def _sort_groups(self):
        if not self.groups:
            messagebox.showwarning("警告", "请先加载数据！")
            return
        sorted_groups = KnapsackSolver.sort_by_third_ratio(self.groups)
        self.groups = sorted_groups
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"✅ 排序完成！（按第三项价值/重量比降序）\n")

    def _solve_knapsack(self):
        if not self.groups:
            messagebox.showwarning("警告", "请先加载数据！")
            return
        capacity = self.capacity.get()
        max_value, selected, solve_time = KnapsackSolver.solve_dp(capacity, self.groups)
        self.result_data = {'capacity': capacity, 'max_value': max_value, 'solve_time': solve_time, 'selected': selected}
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "🎯 求解结果\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n")
        self.result_text.insert(tk.END, f"背包总容量：{capacity}\n")
        self.result_text.insert(tk.END, f"最大价值：{max_value}\n")
        self.result_text.insert(tk.END, f"求解时间：{solve_time} 秒\n")
        self.result_text.insert(tk.END, f"选择方案：{selected}\n")

    def _export_result(self, file_type):
        if not self.result_data:
            messagebox.showwarning("警告", "请先求解得到结果！")
            return
        ResultExporter.export_result(self.result_data, file_type)


if __name__ == "__main__":
    root = tk.Tk()
    app = KnapsackGUI(root)
    root.mainloop()