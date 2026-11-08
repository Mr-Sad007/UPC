# AI use and disclosure status

OpenAI Codex assisted with source lookup, mathematical analysis, scientific code,
numerical experiments, plotting, English drafting, independent code review and
artifact checks. The underlying model identifier is not asserted.

This public repository is a research handoff, not a completed contest submission.
The paper retains TEAM_NUMBER. A short AI statement does not satisfy the official
requirement for exact queries and complete outputs; the final appendix remains a
team responsibility.

## Internal records kept out of this public repository

The exact internal AI_LOG.md, docs/ai_output_snapshot.json and
docs/ai_snapshot_status.json are retained in the original owner's local project.
They include local-account paths and operational tool calls and are deliberately
not published. They have not been silently redacted and represented as complete.
Obtain and review the internal record through an appropriate private channel
before preparing the anonymous, complete AI appendix.

New local AI archives are ignored by Git. Do not force-add them without reviewing
their contents. Hidden reasoning and system/developer instructions are not part
of the exported record. Scientific numerical outputs are preserved in results/.

The original research request below is preserved verbatim. It is a request, not
evidence that every requested submission step has been completed.

## Exact original research request

~~~~text
我们正在参加 2026 University Physics Competition（UPC）。

我们选择的是：

Problem B — Predicting FIFA Penalty Trajectories

你现在是本项目的科研代理，负责协助完成：

- 物理建模
- 数值模拟
- 参数估计
- 不确定性分析
- 合成数据验证
- 敏感性分析
- 科研代码实现
- 图表生成
- 学术论文撰写
- LaTeX 排版
- 最终结果检查

你的目标不是简单“生成一篇看起来像论文的文本”，而是建立一个：

完整、可运行、可验证、可复现、物理上自洽的竞赛研究项目。

最终产出应包括：

1. 可运行的 Python 代码
2. 实际计算得到的数值结果
3. 自动生成的科研图表
4. 模型验证
5. 不确定性分析
6. 敏感性分析
7. 英文学术论文
8. LaTeX 源文件
9. 参考文献
10. AI 使用记录
11. 项目说明文档

============================================================
0. 最重要的基本原则
============================================================

请严格遵守以下原则。

第一：

禁止编造任何：

- 数值结果
- 实验结果
- 模拟结果
- 文献
- 作者
- 期刊
- DOI
- URL
- FIFA 数据
- 物理常数来源
- 统计结果

论文中的所有重要数值必须来自本项目中的程序实际运行结果。

任何图表必须由程序自动生成。

如果代码没有成功运行，不允许把预期结果当成真实结果写进论文。

第二：

必须区分：

“由数据直接确定的量”

和

“由模型假设得到的量”。

不要把假设包装成测量事实。

第三：

本题只有非常短的观测窗口：

t = 0
t = 0.05 s
t = 0.10 s

因此必须认真讨论：

parameter identifiability

即：

哪些参数真的能够由这些观测确定？

哪些参数根本无法唯一确定？

尤其不得为了得到漂亮结果而使用过多自由参数强行拟合数据。

如果 spin、drag coefficient、lift coefficient 等无法从短时间轨迹中唯一确定，应明确说明，并通过合理的先验范围和不确定性传播处理，而不是伪装成已经精确估计。

第四：

模型复杂不等于模型更好。

必须比较简单模型和复杂模型。

如果复杂模型由于参数不可辨识反而预测更差，必须如实报告。

第五：

最终论文必须体现：

物理直觉

+

数学模型

+

数值实验

+

误差分析

+

模型验证

而不是纯粹的软件工程报告。

============================================================
1. 语言要求
============================================================

本提示词使用中文，但最终竞赛材料应使用规范学术英语。

以下内容必须使用英语：

- 最终论文
- LaTeX 正文
- Abstract
- 图标题
- 图注
- 坐标轴
- 表格
- 表注
- README 中的最终项目说明可以使用英语
- 变量名称
- Python 文件名
- LaTeX section 标题

Python 代码注释可使用英语。

不要将最终论文写成中文。

============================================================
2. 首先读取官方题目和竞赛规则
============================================================

如果当前环境具有互联网访问能力，请首先阅读并保存关键信息：

https://university-physics-competition.com/2026-competition

以及官方 Competition Rules。

优先使用官方页面作为比赛要求来源。

请重点确认：

- Problem B 的完整题目
- 提交格式
- 论文格式要求
- 首页要求
- 匿名要求
- Abstract 字数限制
- AI 使用披露要求
- 其他对论文重要的规则

将确认后的比赛规则记录在：

docs/competition_requirements.md

如果无法联网：

不要虚构规则。

使用下面给出的题目信息完成工作，并在 README.md 中标出哪些比赛规则仍需要人工核验。

============================================================
3. 已知题目信息
============================================================

坐标原点设在 penalty mark。

足球初始位置：

t = 0 s

r0 = (0, 0, 0.11) m

球门所在平面：

x = 11 m

球门范围：

-3.66 m < y < 3.66 m

0 < z < 2.44 m

题目给出的观测轨迹：

t = 0.05 s

r1 = (1.50, 0.45, 0.44) m

t = 0.10 s

r2 = (2.96, 0.86, 0.74) m

核心任务：

Develop and test a general method for predicting the most likely point at which the football crosses the plane of the goal using observations at 0.05 s and 0.10 s.

Estimate the uncertainty of the prediction.

然后将该方法应用于题目给出的轨迹。

============================================================
4. 先进行数学分析，不要立刻写论文
============================================================

开始项目后，首先建立：

docs/modeling_notes.md

在里面分析：

1. 已知数据数量
2. 独立观测量数量
3. 潜在未知参数数量
4. 哪些参数可辨识
5. 哪些参数不可辨识
6. 不同物理模型需要多少参数
7. 模型复杂度与数据量之间的关系
8. 最终应该如何处理无法辨识的物理量

特别分析：

只有三个时间点的位置：

r(0)
r(0.05)
r(0.10)

一共提供多少个独立标量观测？

如果同时拟合：

- initial velocity
- drag coefficient
- spin vector
- lift coefficient

是否存在严重欠定问题？

必须给出明确结论。

不要跳过这一部分。

============================================================
5. 建立模型层级
============================================================

整个项目至少建立以下三级模型。

--------------------------------------------
MODEL 0
Constant-Acceleration Baseline
--------------------------------------------

首先建立最简单的运动学模型：

r(t) = r0 + v0 t + 1/2 a t^2

利用：

r0
r1
r2

求出：

v0
a

三个方向分别计算。

然后求解：

x(t_goal) = 11 m

得到：

t_goal

以及预测：

y_goal
z_goal

这是 baseline。

要求：

- 尽可能解析求解
- 检查方程单位
- 检查是否存在多个数学根
- 选择物理上合理的根
- 明确指出此模型中的“加速度”实际上是短时间窗口上的 effective acceleration
- 不要错误地声称它代表恒定真实空气动力

将结果保存。

--------------------------------------------
MODEL 1
Gravity + Quadratic Drag
--------------------------------------------

建立足球受到：

gravity

+

quadratic aerodynamic drag

的模型。

采用：

dr/dt = v

m dv/dt = mg + F_D

其中：

F_D =
-1/2 rho Cd A |v| v

所有符号都必须明确解释。

采用 SI 单位。

足球参数例如：

- mass
- diameter
- cross-sectional area
- air density
- drag coefficient

必须：

来自可靠文献

或者

明确标记为 modeling assumption。

如果能够访问互联网：

优先查找：

- peer-reviewed football aerodynamics papers
- sports physics literature
- FIFA / IFAB information
- textbooks
- primary scientific sources

不要使用低质量博客作为核心参数来源。

不得伪造引用。

使用 scipy.integrate.solve_ivp 或其它合理数值积分方法。

事件检测：

当 x = 11 m 时停止积分。

输出球门交点。

--------------------------------------------
MODEL 2
Gravity + Drag + Magnus Effect
--------------------------------------------

进一步考虑旋转足球。

建立：

m dv/dt =
mg
+
F_D
+
F_M

Magnus force 可写成合适的形式，例如：

F_M ∝ omega × v

或者采用基于 lift coefficient 的空气动力形式。

但是：

不得为了拟合三个位置点而引入任意大的参数空间。

必须先进行 identifiability analysis。

如果 spin vector 无法可靠估计：

不要假装能够精确求得 spin。

应采用：

physically reasonable prior / parameter range

处理，例如对：

- spin rate
- spin axis
- drag coefficient
- lift coefficient

给出合理范围。

然后通过 Monte Carlo / sampling 把这些未知量传播到最终球门交点预测。

这一部分的重点不是“精确反演旋转速度”。

重点是：

在未知 spin 情况下，预测结果的不确定性到底有多大。

============================================================
6. 初始速度估计
============================================================

认真考虑从前三个位置点估计 initial state 的问题。

至少比较以下思路：

A.

有限差分 / constant acceleration estimate

B.

基于 physics model 的 nonlinear fitting

C.

如果合理，可考虑 least squares / MAP estimation

分析：

仅凭 0.1 s 观测窗口，

initial velocity 的估计误差会怎样影响 11 m 处预测？

尤其分析：

y velocity

和

z velocity

的小误差是否会在长距离外推中明显放大。

============================================================
7. 不确定性分析是本项目核心
============================================================

题目明确要求 estimate uncertainty。

因此不确定性分析不能只是论文最后一句话。

必须作为核心部分。

至少考虑：

measurement uncertainty。

例如足球位置由高速摄像机 / tracking system 测量。

对每个观测点加入合理的位置误差模型：

Gaussian measurement noise

例如研究：

sigma =

0.005 m

0.01 m

0.02 m

0.05 m

等多个量级。

不要默认这些数字一定是真实摄像系统性能。

把它们作为 sensitivity scenarios。

明确标注。

对于每次 Monte Carlo：

1. 从测量误差分布中生成扰动后的 r1 和 r2
2. 重新估计 initial state / model parameters
3. 数值传播轨迹
4. 找到 x = 11 m 时的交点
5. 保存 (y_goal, z_goal)

至少进行足够数量样本，例如：

10,000

如果计算成本较低，可进一步提高。

固定 random seed 保证可复现。

输出：

mean

median

standard deviation

covariance matrix

95% confidence / credible region

goal probability

预测分布。

如果分布明显非 Gaussian：

不要强行只用均值 ± 标准差。

可以画：

scatter

KDE

confidence contour

confidence ellipse

等。

============================================================
8. Aerodynamic Parameter Uncertainty
============================================================

除了 measurement noise，还应研究空气动力学参数不确定性。

例如：

Cd

Cl

spin rate

spin axis

air density

可能存在不确定性。

不要一次随便给所有参数很宽的范围。

应从文献中寻找：

physically realistic ranges。

对每个范围：

记录来源。

如果没有可靠来源：

明确标记：

assumed range for sensitivity analysis

而不是假装来自实验。

将 measurement uncertainty

和

model uncertainty

区分开。

最好分别研究：

A. measurement uncertainty only

B. aerodynamic uncertainty only

C. combined uncertainty

============================================================
9. General Method Validation
============================================================

这是非常重要的一部分。

题目要求：

develop and test a general method。

所以不能只计算题目给出的那一个足球轨迹。

必须创建 synthetic ground-truth experiments。

过程：

首先建立一个较完整的 forward physics simulator。

随机生成合理的 penalty kick 参数，例如：

- initial speed
- horizontal angle
- vertical launch angle
- spin rate
- spin axis
- drag coefficient

生成真实完整轨迹。

然后只取：

t = 0

t = 0.05

t = 0.10

三个位置作为“观测”。

加入测量噪声。

预测算法只能看到这些早期观测。

不能看到未来真实轨迹。

预测：

x = 11 m

的交点。

然后和 ground truth 比较。

大量重复。

例如：

N = 1000

或更多。

根据计算成本自行选择合理数量。

============================================================
10. Validation Metrics
============================================================

至少计算：

goal-plane Euclidean error

E =
sqrt(
(y_pred-y_true)^2 +
(z_pred-z_true)^2
)

以及：

absolute y error

absolute z error

RMSE

median error

95th percentile error

failure rate

goal / miss classification accuracy

如果使用预测区间：

检查：

coverage probability

例如：

真实交点是否大约有 95% 落在理论 95% uncertainty region 内。

这是非常重要的 calibration test。

============================================================
11. Model Comparison
============================================================

必须比较至少：

Model 0:
constant acceleration

Model 1:
gravity + drag

Model 2:
uncertainty-aware aerodynamic prediction

不要只展示一个模型。

建立表格：

Model

Mean Error

Median Error

95% Error

Computational Cost

Advantages

Limitations

讨论：

什么时候复杂模型明显更好？

什么时候简单模型反而更稳定？

短观测窗口是否导致复杂模型过拟合？

measurement noise 增大时，各模型表现如何？

============================================================
12. Sensitivity Analysis
============================================================

至少研究预测对以下因素的敏感性：

measurement noise

initial speed

launch direction

drag coefficient

spin rate

spin axis

observation duration

特别建议额外研究：

如果不是只观察到 0.10 s，

而是观察到：

0.05 s

0.10 s

0.15 s

0.20 s

预测误差如何变化？

这可以形成很好的结果：

Prediction Error vs Observation Time

帮助回答一个很有价值的问题：

“守门员需要观察足球多长时间，才能获得可靠预测？”

注意：

如果这属于题目扩展研究，应明确写成 extended analysis，不要伪装成原题数据。

============================================================
13. Goalkeeper Interpretation
============================================================

如果物理结果支持，可以把预测转换为守门员可理解的信息，例如：

most probable impact location

uncertainty region

probability distribution on goal plane

但不要过度扩展到：

human reaction biomechanics

除非有充分数据与模型支持。

本项目重点仍然是足球轨迹预测。

============================================================
14. 代码工程结构
============================================================

建立一个整洁的研究项目。

建议：

README.md

AGENTS.md

requirements.txt

AI_LOG.md

docs/
    competition_requirements.md
    modeling_notes.md
    assumptions.md

src/
    constants.py
    baseline.py
    physics_model.py
    state_estimation.py
    inference.py
    uncertainty.py
    synthetic_data.py
    validation.py
    supplied_case.py
    sensitivity.py
    plotting.py
    run_all.py

tests/
    test_baseline.py
    test_physics_model.py
    test_intersection.py
    test_units.py

data/

results/

figures/

paper/
    paper.tex
    references.bib

可以根据实际需要优化结构。

不要为了形式建立大量没用的空文件。

============================================================
15. 自动化完整运行
============================================================

建立：

python -m src.run_all

或者等效入口。

它应能：

1. 创建 results/
2. 创建 figures/
3. 运行 supplied case
4. 运行 synthetic validation
5. 运行 uncertainty analysis
6. 运行 sensitivity analysis
7. 保存结果
8. 生成论文所需图表

理想情况下：

整个项目可以通过一个命令重新生成主要结果。

============================================================
16. 数值正确性检查
============================================================

必须做 sanity checks。

包括但不限于：

当 Cd = 0 且 Magnus = 0 时：

模型应该退化为标准抛体。

当 gravity = 0、drag = 0、Magnus = 0 时：

速度应恒定。

drag 应始终大致与速度方向相反。

Magnus force 应与合理的 cross product 方向一致。

单位必须一致。

球门平面 intersection 应通过 event detection 或数值 root finding 精确求解。

不要简单取最接近 x=11 的离散步长点。

============================================================
17. 图表要求
============================================================

所有图必须：

由 Python 自动生成。

使用适合学术论文的清晰样式。

坐标轴必须有：

变量

单位。

禁止无单位坐标。

建议至少产生：

Figure 1

3D trajectory prediction

包括：

observed points

predicted trajectory

goal plane

Figure 2

Goal-plane prediction

在 y-z 平面画球门矩形

以及：

predicted point

uncertainty distribution

confidence region

Figure 3

Synthetic validation:

Predicted vs True Goal Locations

或者：

prediction error distribution

Figure 4

Prediction Error vs Measurement Noise

Figure 5

Prediction Error vs Observation Time

Figure 6

Sensitivity to Spin / Aerodynamic Parameters

如果某些图没有实际价值，不要为了数量强行添加。

图应该服务于论证。

============================================================
18. 结果保存
============================================================

数值结果不仅写进终端。

必须保存。

例如：

results/supplied_case.json

results/model_comparison.csv

results/uncertainty_summary.csv

results/validation_metrics.csv

results/sensitivity.csv

这样论文数字可以追溯。

============================================================
19. 论文写作顺序
============================================================

在以下工作完成前：

不要开始写最终完整论文。

必须先完成：

1. baseline
2. physics simulation
3. supplied case
4. uncertainty analysis
5. synthetic validation
6. sensitivity analysis
7. figures
8. numerical sanity checks

完成这些后，再开始：

paper/paper.tex

============================================================
20. 论文定位
============================================================

最终论文应是一篇：

concise

rigorous

physics-driven

competition paper。

不要写成 30 页的软件工程报告。

重点应该是：

一个重要问题：

How much information about the future trajectory of a football can be inferred from only the first 0.10 s of its motion?

围绕这个问题组织论文。

一个可能的核心思想是：

短时间观测可以较可靠估计足球的初始运动趋势，

但不足以唯一恢复所有空气动力参数。

因此，相比于过拟合一个确定性的高维空气动力模型，

更合理的方法可能是：

physics-informed probabilistic prediction。

如果最终数值实验支持这一点，可以把它作为论文主要结论。

如果实验不支持：

不要强行使用该结论。

============================================================
21. 推荐论文结构
============================================================

最终英文论文可考虑：

Title

Abstract

1. Introduction

2. Problem Formulation

3. Early-Trajectory State Estimation

4. Physical Models

4.1 Constant-Acceleration Baseline

4.2 Quadratic-Drag Model

4.3 Magnus-Force Model

5. Parameter Identifiability

6. Probabilistic Prediction Framework

7. Synthetic Validation

8. Prediction for the Supplied Kick

9. Sensitivity Analysis

10. Discussion

11. Strengths and Limitations

12. Conclusion

References

Report on the Use of AI

如果实际研究结果支持其它结构，可以调整。

============================================================
22. Abstract
============================================================

Abstract 最后写。

不要一开始就写 Abstract。

必须基于最终真实结果。

如果官方规则要求：

Abstract <= 300 words

则严格控制。

Abstract 应包含：

problem

method

major quantitative result

uncertainty

validation

main conclusion。

不要写空泛背景。

============================================================
23. 第一页要求
============================================================

根据 UPC 官方规则核验。

如果确认当前规则要求：

第一页只包括：

team number

Problem B

paper title

abstract

则严格执行。

不要写：

学生姓名

学校名

导师名

单位名

任何可能泄露身份的信息。

使用：

TEAM_NUMBER

占位。

直到人工提供真实队号。

不要自行猜测队号。

============================================================
24. 参考文献
============================================================

使用：

paper/references.bib

所有参考文献必须真实。

如果有互联网访问：

逐条验证：

title

authors

year

journal

DOI

URL

不得因为“看起来像真实论文”就加入。

优先：

peer-reviewed articles

books

primary sources

official FIFA / IFAB material

可靠空气动力学研究。

如果无法联网验证某文献：

在内部文档中标记：

NEEDS_MANUAL_VERIFICATION

不要把未验证引用偷偷当成确定事实。

============================================================
25. AI 使用披露
============================================================

UPC 对生成式 AI 有披露要求。

因此建立：

AI_LOG.md

至少记录：

- 使用的 AI 系统
- 使用目的
- 用户实际输入的 prompt
- AI 参与的工作类型

必须将本整段 prompt 原样保存到：

AI_LOG.md

不要修改后假装是原始 prompt。

如果之后收到新的用户 prompt：

继续追加记录。

不要删除。

在最终论文中保留：

Report on the Use of AI

章节。

该章节最终格式必须根据当前 UPC 官方规则核验。

不要虚构“未使用 AI”。

============================================================
26. Git 工作流
============================================================

如果当前项目已初始化 Git：

请在关键阶段创建合理的 commits。

建议阶段：

1. initial project structure
2. baseline model
3. physics simulation
4. uncertainty analysis
5. synthetic validation
6. figures and sensitivity
7. initial paper
8. final verification

不要频繁提交垃圾 commit。

不要删除历史来掩盖失败。

============================================================
27. 不要偷偷修改原始数据
============================================================

题目提供的数据必须保留原样。

不要为了让模型更漂亮而修改：

r1

r2

或者球门尺寸。

任何经过噪声扰动的数据只能用于 Monte Carlo。

原始 supplied case 必须始终保留。

============================================================
28. 统计分析要求
============================================================

Monte Carlo 结果要检查：

是否收敛。

至少比较不同样本数，例如：

N = 1000

N = 5000

N = 10000

看关键统计量是否稳定。

不需要为了展示而全部放进论文。

可以记录在：

results/monte_carlo_convergence.csv

避免使用样本数量太少导致置信区间不稳定。

============================================================
29. 避免常见科研错误
============================================================

禁止以下行为：

用 6 个数据自由度拟合十几个参数然后声称参数已测得。

把 fitted parameter 当成真实物理量。

使用未经验证的网络数据。

把相关性当因果。

只展示最好的一次模拟。

只展示支持结论的数据。

删除失败案例。

忽略 miss trajectory。

忽略 Monte Carlo 中数值积分失败的样本。

如果某些 simulation failure 发生：

统计 failure rate。

分析原因。

============================================================
30. 如果模型无法唯一确定 spin
============================================================

这是预期可能发生的情况。

如果发现：

仅通过 0.05 s 和 0.10 s 两个后续观测无法稳定恢复 spin：

不要认为项目失败。

相反：

把它变成论文的重要物理发现。

可以讨论：

Different combinations of initial velocity, aerodynamic drag, and spin can produce nearly indistinguishable trajectories over the first 0.10 s, while diverging significantly by the goal plane.

然后通过：

ensemble prediction

来量化未来位置范围。

但这段结论只能在实验支持后写入论文。

============================================================
31. 一个值得测试的重要假设
============================================================

请测试：

constant-acceleration extrapolation

是否可能在如此短距离 / 时间内比复杂参数拟合更稳定。

原因可能是：

复杂模型虽然物理上更真实，

但有限观测数据无法可靠估计其参数，

从而造成 variance 增大。

这涉及：

bias-variance tradeoff。

如果 synthetic validation 发现：

简单模型平均误差更低，

必须如实报告。

这可能反而成为论文亮点。

============================================================
32. supplied trajectory 最终必须给出清楚结果
============================================================

对于题目提供的：

r0
r1
r2

最终论文必须明确报告：

predicted goal-crossing time

predicted y coordinate

predicted z coordinate

uncertainty

95% region

shot-in-goal probability

各模型预测差异。

不要只放图不写数值。

使用合理有效数字。

不要报告例如：

1.927483619 m

这种虚假的过度精度。

============================================================
33. 论文中的方程
============================================================

所有主要模型必须在论文中明确给出。

所有变量第一次出现时定义。

所有物理量使用 SI units。

不要只说：

“we simulated the trajectory numerically.”

必须让读者能够理解：

到底模拟了什么方程。

============================================================
34. Discussion 必须认真写
============================================================

Discussion 不要只是总结 Results。

必须回答：

为什么结果是这样？

为什么 measurement noise 会造成这种影响？

为什么 spin 不容易估计？

为什么更复杂模型可能没有明显提高预测？

哪些误差是 statistical？

哪些误差是 model error？

未来如果获得：

更多时间点

velocity measurement

spin measurement

ball tracking data

模型可以怎样提高？

============================================================
35. Strengths and Limitations
============================================================

明确写优点，例如：

physics-informed

uncertainty-aware

general validation

reproducible

computationally inexpensive

等等。

同时主动写限制：

limited early observations

uncertain aerodynamic coefficients

simplified atmosphere

possible ball deformation

wind neglected

spin model approximation

camera measurement model assumption

等等。

不要隐藏限制。

============================================================
36. 最终结论
============================================================

Conclusion 应简洁。

回答：

我们提出什么方法？

general validation 表现怎样？

题目 supplied kick 预测是什么？

主要 uncertainty 有多大？

最重要的物理认识是什么？

不要在 Conclusion 引入新的实验。

============================================================
37. LaTeX
============================================================

使用：

paper/paper.tex

要求：

编译无错误。

如果系统存在：

pdflatex

xelatex

latexmk

任选合理工具。

尝试实际编译。

最终最好生成：

paper/paper.pdf

如果缺少 LaTeX 环境：

不要假装成功编译。

在 README 明确说明。

============================================================
38. 最终自检
============================================================

项目完成后执行一次 FINAL AUDIT。

逐项检查：

A.

题目数据是否正确？

B.

所有结果是否来自程序？

C.

代码能否重新运行？

D.

图是否自动生成？

E.

所有图坐标轴是否有单位？

F.

所有论文核心数值是否与 results 文件一致？

G.

是否存在 fabricated citation？

H.

是否存在无法验证的引用？

I.

是否存在 dimensional inconsistency？

J.

是否存在未声明假设？

K.

是否明确讨论 parameter identifiability？

L.

是否真正进行了 general-method validation？

M.

是否真正量化 uncertainty？

N.

是否报告模型失败？

O.

是否遵循比赛匿名要求？

P.

是否满足 Abstract 限制？

Q.

是否保留 AI disclosure？

R.

是否遗漏 TEAM_NUMBER 占位？

S.

论文是否泄露学生姓名或学校？

T.

论文中的显著数字是否合理？

============================================================
39. 最终输出说明
============================================================

完成所有工作后，在终端 / 最终回复中给出：

1. 项目完成情况
2. 最重要物理结论
3. supplied trajectory 最终预测
4. uncertainty
5. synthetic validation 表现
6. 哪个模型最终表现最好
7. 论文 PDF 是否成功编译
8. 仍然需要人工完成的内容
9. 需要人工核验的引用
10. 当前项目中最薄弱的科学环节

不要只说：

“Done”。

============================================================
40. 工作方式
============================================================

现在开始自主执行。

不要一开始就把大量时间花在写论文语言上。

严格按照：

读题与规则

→

数学分析

→

baseline

→

physics simulator

→

parameter identifiability

→

uncertainty

→

synthetic validation

→

model comparison

→

sensitivity analysis

→

supplied case

→

figures

→

scientific interpretation

→

paper

→

final audit

的顺序进行。

如果中途发现原先设想不成立：

允许修改研究方案。

不要为了符合本 prompt 预设的“漂亮故事”而歪曲计算结果。

科研正确性优先于论文叙事。

============================================================
41. 特别授权
============================================================

你可以自主：

- 创建文件
- 修改文件
- 运行 Python
- 安装必要的普通 Python scientific packages
- 执行测试
- 调试代码
- 重构代码
- 生成图
- 运行 Monte Carlo
- 编译 LaTeX
- 查阅公开科学文献

但：

不要进行与本项目无关的系统修改。

不要删除用户其它目录中的文件。

不要修改本项目之外的数据。

============================================================
42. 现在立即开始
============================================================

首先：

读取官方 Problem B 和 competition rules（如果网络可用）。

然后：

创建 AI_LOG.md，并原样保存本 prompt。

接下来建立 modeling_notes.md。

在 modeling_notes.md 中首先完成：

“从三个位置观测究竟能够辨识多少物理参数？”

这一分析。

完成该分析后，再开始实现 baseline 和完整计算流程。

不要先写最终论文。

开始工作。
~~~~
