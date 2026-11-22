# 搭档技能：不在本仓库里，缺了会怎样

这个 skill 是**编排器**，不是写作工具。它把写作、润色、红队、评审、绘图、统计交给别的 skill 做；
本仓库只含 `SKILL.md`、`references/`、`scripts/` 和测试。所以第一次在一台新机器上跑，`preflight.py`
大概率会报一串 `[missing]`。

这不是故障，是设计；但它必须**先说、再问、得到同意之后才装**（SKILL.md 规则 32）。

## 正确的顺序

```bash
python scripts/preflight.py            # 看谁缺
python scripts/preflight.py --explain  # 看每个缺失项：作用 / 安装方式 / 缺失代价
```

然后把 `--explain` 的清单原样交给用户，问一句「要装吗」，用户同意后才：

1. `skill-inspector` 扫描来源（引入第三方代码属于供应链决定，先看它要什么权限）；
2. `skills-manager-cli skills install <source>` 安装；
3. `skills-manager-cli skills deploy <name> --agent <agent>` 部署；
4. 重跑 `preflight.py`，把新状态报给用户。

不允许静默替代，也不允许静默安装：两者都会让这次运行的审计链条断掉。

## 三类来源

| 来源 | 例子 | 怎么装 |
|---|---|---|
| 公开仓库 | `anti-defensive-writing`、`scientific-visualization` | `skills-manager-cli skills install https://github.com/.../skills/<name>` |
| 本机技能库 | `paper-writer`、`paper-polish`、`grilling`、`figure-designer` | 从已有安装复制或 `skills install` 本地目录；没有公开地址 |
| 作者侧提供 | `academic-paper*`、`deep-research`、`sr-screener` | 向提供本 skill 的来源索取，仓库不代发 |

机器可读的清单在 `references/skill-dependencies.json`（`preflight.py --explain` 直接读它）。
那个文件里的 `install` 为空，就表示"没有公开地址，别让 agent 猜一个 URL 出来装"。

## 缺失时的降级

`references/skill-catalog.md` 有首选→替代→损失的降级表。原则是：

- 替代只能**降级**，不能等价；
- 必须说明损失（"没有 grilling：红队环节被跳过，主张链未受攻击"）；
- `anti-defensive-writing` 没有等价替代，缺了就只能人工按 `main-line.md` 的主张边界逐句自查。

## 不打包依赖的理由

- 那些 skill 各自有作者、许可证与更新节奏，打包进来会变成"三份不同步的副本"；
- 它们不是全部可公开再分发（本机库里若干是导入型，没有公开地址）；
- 装不装属于用户对自己机器的决定，编排器不该替他决定。

代价是第一次使用多一轮对话。这一轮对话是必要的：它把"缺什么、为什么缺、装不装"从后台静默变成了
用户可以否决的显式决定。
