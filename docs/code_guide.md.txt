D{0-1}背包问题代码规范
一、格式与排版规范
  1、缩进：统一使用4个空格缩进，禁止使用Tab键，保证代码层级清晰。
  2、空格：
  （1）运算符（=、+、-、*、/ 等）前后各加 1 个空格，例如 max_value = dp[n][capacity]。
  （2）逗号后必须加1个空格，例如 groups.append((w1, v1, w2, v2))。
  3、空行：
  （1）函数与函数之间空2行，类与类之间空2行。
  （2）类内部方法之间空1行，逻辑块之间空1行（如变量定义与循环之间）。
  4、行长度：每行代码不超过120个字符，过长时用括号或反斜杠\换行拆分。
二、命名规范
  1、类名：采用大驼峰命名法（每个单词首字母大写），例如：DataLoader、KnapsackSolver、 ResultExporter。
  2、函数/变量名：采用下划线命名法（全小写，单词间用下划线分隔），例如 load_data、solve_dp、 selected_str。
  3、常量名：采用全大写+下划线命名，例如 MAX_CAPACITY_DEFAULT = 100。
  4、文件/文件夹名：采用小写+下划线命名，例如 src/knapsack.py、data/test_data.txt。
三、注释规范
  1、模块/类/函数注释：必须使用三引号 """ """ 编写文档字符串，说明功能、参数和返回值。
def solve_dp(capacity, groups):
    """
    动态规划求解D{0-1}背包问题
    :param capacity: 背包总容量（int）
    :param groups: 物品组列表，每组包含3个(重量, 价值)元组
    :return: 最大价值(int)、选中方案描述(str)、求解时间(float)
    """
  2、单行注释：关键逻辑处用#加单行注释，只解释「非显而易见」的代码，禁止无意义注释。
# 回溯选中的物品，从后往前推导最优方案
current_w = capacity
for i in range(n, 0, -1):
    if path[i][current_w] is not None:
        group_idx, item_idx = path[i][current_w]
        selected.append((group_idx + 1, item_idx + 1))
        current_w -= groups[group_idx][item_idx][0]  # 减去选中物品的重量
四、函数与类设计规范
  1、单一职责：一个函数/类只做一件事，例如load_data只负责读取数据，solve_dp只负责求解最优解。
  2、函数长度：单个函数行数不超过50行，过长时拆分为多个子函数。
  3、异常处理：所有涉及文件操作、数据解析的代码必须添加try-except捕获异常，避免程序崩溃，并给出友好提示。
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except FileNotFoundError:
    messagebox.showerror("错误", "数据文件不存在！")
except ValueError:
    messagebox.showerror("错误", "数据格式不符合要求！")
五、其他规则
  1、导入顺序：先导入标准库，再导入第三方库，最后导入项目内部模块。
  2、编码：文件统一使用UTF-8编码，避免中文乱码。
  3、可读性优先：代码逻辑清晰易读，优先保证可维护性。