# -*- coding: utf-8 -*-
"""
D{0-1}背包问题求解程序
核心功能：
1. 读取自定义格式的背包数据文件
2. 按第三项物品的价值/重量比排序物品组
3. 动态规划(DP)求解0-1背包最优解
4. 导出求解结果为TXT/Excel格式
5. 提供简单的TKinter图形界面交互
"""

import tkinter as tk
from tkinter import filedialog, messagebox  # GUI文件选择和消息提示
import time  # 计算求解耗时
import os  # 文件路径校验

# ===================== 全局常量定义 =====================
MAX_CAPACITY_DEFAULT = 100  # 默认背包最大容量
RESULT_COLUMNS = ['总容量', '最大价值', '求解时间(秒)', '选择方案']  # 结果导出列名


class DataLoader:
    """
    数据加载器类
    负责从文本文件中读取背包问题的输入数据，格式要求：
    - 第一行：背包总容量（整数）
    - 后续每行：6个整数，代表一组3个物品的(重量,价值)，格式为 w1 v1 w2 v2 w3 v3
    """

    @staticmethod
    def load_data(file_path):
        """
        从指定路径读取背包数据
        :param file_path: 数据文件路径（str）
        :return: (capacity, groups) 或 (None, None)
                 capacity: 背包总容量（int）
                 groups: 物品组列表，每个元素为[(w1,v1), (w2,v2), (w3,v3)]
        """
        try:
            # 读取文件并过滤空行、去除首尾空格
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            # 解析背包容量（第一行）
            capacity = int(lines[0])

            # 解析物品组数据（后续行）
            groups = []
            for line_num, line in enumerate(lines[1:], start=2):  # 行号从2开始（便于定位错误）
                parts = list(map(int, line.split()))
                # 校验每行数据格式（必须6个数字）
                if len(parts) != 6:
                    raise ValueError(f"第{line_num}行数据格式错误：{line}（需6个数字，实际{len(parts)}个）")
                # 组装为3个物品的元组列表
                group = [(parts[0], parts[1]), (parts[2], parts[3]), (parts[4], parts[5])]
                groups.append(group)

            return capacity, groups

        except ValueError as e:
            # 数据格式错误（非数字、数量不符）
            messagebox.showerror("读取失败", f"数据格式错误：{str(e)}")
            return None, None
        except FileNotFoundError:
            # 文件不存在
            messagebox.showerror("读取失败", f"文件不存在：{file_path}")
            return None, None
        except Exception as e:
            # 其他未知错误
            messagebox.showerror("读取失败", f"数据文件读取错误：{str(e)}")
            return None, None


class KnapsackSolver:
    """
    背包问题求解器类
    核心算法：动态规划(DP)求解0-1背包问题
    辅助功能：按第三项物品的价值/重量比排序物品组
    """

    @staticmethod
    def sort_by_third_ratio(groups):
        """
        按每组第三个物品的价值/重量比降序排序物品组
        :param groups: 原始物品组列表
        :return: 排序后的物品组列表
        """
        try:
            # 定义排序键：第三个物品的价值/重量比（避免除零错误）
            def get_ratio(group):
                w, v = group[2]  # 取第三个物品
                return v / w if w != 0 else float('inf')  # 重量为0时比值设为无穷大

            # 降序排序
            sorted_groups = sorted(groups, key=get_ratio, reverse=True)
            return sorted_groups

        except Exception as e:
            messagebox.showerror("排序失败", f"排序出错：{str(e)}")
            return groups  # 排序失败返回原数据

    @staticmethod
    def solve_dp(capacity, groups):
        """
        动态规划求解0-1背包最优解
        :param capacity: 背包总容量（int）
        :param groups: 物品组列表（已排序）
        :return: (max_value, selected_str, solve_time)
                 max_value: 最大价值（int）
                 selected_str: 选择方案字符串（如"第1组第2个；第3组第1个"）
                 solve_time: 求解耗时（秒，保留6位小数）
        """
        # 记录求解开始时间
        start_time = time.time()

        # 初始化DP表和路径记录表
        n = len(groups)  # 物品组数量
        # dp[i][w]：前i个物品组，背包容量为w时的最大价值
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]
        # path[i][w]：记录选择路径，格式为(物品组索引, 物品索引)
        path = [[None] * (capacity + 1) for _ in range(n + 1)]

        try:
            # 填充DP表
            for i in range(1, n + 1):
                # 获取当前物品组的3个物品
                item1, item2, item3 = groups[i - 1]
                w1, v1 = item1
                w2, v2 = item2
                w3, v3 = item3

                # 遍历所有可能的背包容量
                for w in range(1, capacity + 1):
                    # 初始值：不选当前物品组
                    dp[i][w] = dp[i - 1][w]

                    # 尝试选第一个物品
                    if w >= w1 and dp[i - 1][w - w1] + v1 > dp[i][w]:
                        dp[i][w] = dp[i - 1][w - w1] + v1
                        path[i][w] = (i - 1, 0)  # 0代表第一个物品

                    # 尝试选第二个物品
                    if w >= w2 and dp[i - 1][w - w2] + v2 > dp[i][w]:
                        dp[i][w] = dp[i - 1][w - w2] + v2
                        path[i][w] = (i - 1, 1)  # 1代表第二个物品

                    # 尝试选第三个物品
                    if w >= w3 and dp[i - 1][w - w3] + v3 > dp[i][w]:
                        dp[i][w] = dp[i - 1][w - w3] + v3
                        path[i][w] = (i - 1, 2)  # 2代表第三个物品

            # 回溯路径，获取选择方案
            selected = []
            current_w = capacity  # 从最大容量开始回溯
            for i in range(n, 0, -1):
                if path[i][current_w] is not None:
                    group_idx, item_idx = path[i][current_w]
                    # 转换为人类可读的序号（从1开始）
                    selected.append((group_idx + 1, item_idx + 1))
                    # 减去选中物品的重量
                    current_w -= groups[group_idx][item_idx][0]

            # 计算求解耗时
            solve_time = round(time.time() - start_time, 6)

            # 格式化选择方案
            selected = sorted(selected, key=lambda x: x[0])  # 按物品组序号排序
            selected_str = "; ".join([f"第{g}组第{i}个" for g, i in selected]) or "无"

            return dp[n][capacity], selected_str, solve_time

        except Exception as e:
            messagebox.showerror("求解失败", f"动态规划求解出错：{str(e)}")
            return 0, "", 0


class ResultExporter:
    """
    结果导出器类
    支持将求解结果导出为TXT或Excel格式
    """

    @staticmethod
    def export_result(result_data, file_type='txt'):
        """
        导出求解结果
        :param result_data: 结果字典，包含capacity/max_value/solve_time/selected
        :param file_type: 导出类型，'txt'或'excel'
        :return: 导出成功返回True，失败返回False
        """
        try:
            # 确定文件扩展名
            file_ext = '.txt' if file_type == 'txt' else '.xlsx'

            # 弹出保存文件对话框
            save_path = filedialog.asksaveasfilename(
                defaultextension=file_ext,
                filetypes=[(f"{file_type.upper()}文件", f"*{file_ext}"), ("所有文件", "*.*")]
            )

            # 用户取消保存
            if not save_path:
                return False

            # 导出为TXT格式
            if file_type == 'txt':
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write("D{0-1}背包问题求解结果\n")
                    f.write("=" * 30 + "\n")
                    f.write(f"背包总容量：{result_data['capacity']}\n")
                    f.write(f"最大价值：{result_data['max_value']}\n")
                    f.write(f"求解时间：{result_data['solve_time']} 秒\n")
                    f.write(f"选择方案：{result_data['selected']}\n")

            # 导出为Excel格式（需安装pandas和openpyxl）
            else:
                # 延迟导入（避免未安装时程序启动失败）
                import pandas as pd
                # 构造DataFrame
                df = pd.DataFrame([{
                    '背包总容量': result_data['capacity'],
                    '最大价值': result_data['max_value'],
                    '求解时间(秒)': result_data['solve_time'],
                    '选择方案': result_data['selected']
                }])
                # 写入Excel文件（不保留索引）
                df.to_excel(save_path, index=False)

            messagebox.showinfo("导出成功", f"结果已保存至：{save_path}")
            return True

        except ImportError:
            # 缺少Excel导出依赖
            messagebox.showerror("导出失败", "导出Excel需安装pandas和openpyxl：\npip install pandas openpyxl")
            return False
        except Exception as e:
            messagebox.showerror("导出失败", f"结果导出出错：{str(e)}")
            return False


class KnapsackGUI:
    """
    主界面类
    负责创建TKinter图形界面，处理用户交互逻辑
    """

    def __init__(self, root):
        """
        初始化界面
        :param root: TKinter根窗口对象
        """
        self.root = root
        self.root.title("D{0-1}背包问题求解器")
        self.root.geometry("800x500")  # 窗口大小

        # 定义界面变量
        self.file_path = tk.StringVar()  # 选中的数据文件路径
        self.capacity = tk.IntVar(value=MAX_CAPACITY_DEFAULT)  # 背包容量
        self.groups = None  # 加载的物品组数据
        self.result_data = None  # 求解结果

        # 创建界面组件
        self._create_widgets()

    def _create_widgets(self):
        """创建所有界面组件（私有方法）"""
        # ========== 1. 文件选择区域 ==========
        frame_file = tk.Frame(self.root, padx=10, pady=10)
        frame_file.pack(fill=tk.X)
        tk.Label(frame_file, text="数据文件：", font=("Arial", 12)).pack(side=tk.LEFT)
        # 文件路径输入框
        tk.Entry(frame_file, textvariable=self.file_path, width=60, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        # 选择文件按钮
        tk.Button(frame_file, text="选择文件", command=self._select_file, font=("Arial", 12)).pack(side=tk.LEFT)

        # ========== 2. 功能按钮区域 ==========
        frame_buttons = tk.Frame(self.root, padx=10, pady=10)
        frame_buttons.pack(fill=tk.X)
        # 读取数据按钮
        tk.Button(frame_buttons, text="读取数据", command=self._load_data, font=("Arial", 12), width=15).pack(
            side=tk.LEFT, padx=5)
        # 排序物品组按钮
        tk.Button(frame_buttons, text="排序物品组", command=self._sort_groups, font=("Arial", 12), width=15).pack(
            side=tk.LEFT, padx=5)
        # 求解最优解按钮
        tk.Button(frame_buttons, text="求解最优解", command=self._solve_knapsack, font=("Arial", 12), width=15).pack(
            side=tk.LEFT, padx=5)

        # ========== 3. 导出按钮区域 ==========
        frame_export = tk.Frame(self.root, padx=10, pady=10)
        frame_export.pack(fill=tk.X)
        # 导出TXT按钮
        tk.Button(frame_export, text="导出为TXT", command=lambda: self._export_result('txt'), font=("Arial", 12),
                  width=15).pack(side=tk.LEFT, padx=5)
        # 导出Excel按钮
        tk.Button(frame_export, text="导出为Excel", command=lambda: self._export_result('excel'), font=("Arial", 12),
                  width=15).pack(side=tk.LEFT, padx=5)

        # ========== 4. 结果显示区域 ==========
        frame_result = tk.Frame(self.root, padx=10, pady=10)
        frame_result.pack(fill=tk.BOTH, expand=True)
        tk.Label(frame_result, text="求解结果：", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        # 结果文本框
        self.result_text = tk.Text(frame_result, font=("Arial", 12), wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        # 滚动条
        scrollbar = tk.Scrollbar(self.result_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)

    def _select_file(self):
        """选择数据文件（私有方法）"""
        file_path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if file_path:
            self.file_path.set(file_path)

    def _load_data(self):
        """加载数据文件（私有方法）"""
        file_path = self.file_path.get()
        # 校验文件路径有效性
        if not file_path or not os.path.exists(file_path):
            messagebox.showwarning("警告", "请先选择有效的数据文件！")
            return

        # 调用数据加载器
        capacity, groups = DataLoader.load_data(file_path)
        if capacity and groups:
            self.capacity.set(capacity)
            self.groups = groups
            # 清空结果框并显示加载成功信息
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"✅ 数据加载成功！\n")
            self.result_text.insert(tk.END, f"📦 背包容量：{capacity}\n")
            self.result_text.insert(tk.END, f"📝 物品组数量：{len(groups)}\n")

    def _sort_groups(self):
        """排序物品组（私有方法）"""
        if not self.groups:
            messagebox.showwarning("警告", "请先加载数据！")
            return

        # 调用排序方法
        sorted_groups = KnapsackSolver.sort_by_third_ratio(self.groups)
        self.groups = sorted_groups
        # 显示排序成功信息
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"✅ 排序完成！（按第三项价值/重量比降序）\n")

    def _solve_knapsack(self):
        """求解背包最优解（私有方法）"""
        if not self.groups:
            messagebox.showwarning("警告", "请先加载数据！")
            return

        # 获取背包容量并调用求解方法
        capacity = self.capacity.get()
        max_value, selected, solve_time = KnapsackSolver.solve_dp(capacity, self.groups)

        # 保存结果数据（用于导出）
        self.result_data = {
            'capacity': capacity,
            'max_value': max_value,
            'solve_time': solve_time,
            'selected': selected
        }

        # 显示求解结果
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "🎯 求解结果\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n")
        self.result_text.insert(tk.END, f"背包总容量：{capacity}\n")
        self.result_text.insert(tk.END, f"最大价值：{max_value}\n")
        self.result_text.insert(tk.END, f"求解时间：{solve_time} 秒\n")
        self.result_text.insert(tk.END, f"选择方案：{selected}\n")

    def _export_result(self, file_type):
        """导出求解结果（私有方法）"""
        if not self.result_data:
            messagebox.showwarning("警告", "请先求解得到结果！")
            return

        # 调用结果导出器
        ResultExporter.export_result(self.result_data, file_type)


# ===================== 程序入口 ====================
if __name__ == "__main__":
    # 创建TKinter根窗口
    root = tk.Tk()
    # 初始化应用
    app = KnapsackGUI(root)
    # 启动主循环
    root.mainloop()