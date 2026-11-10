# paper-figure

An agent skill for drawing research-paper figures (method overviews, pipelines, architectures) as editable
vector diagrams. It does not use image-generation models.

Ask an agent for a figure and you usually get text that leaves its box, labels that overlap and lines that
miss their targets. This skill measures every draft at the size it will be printed and fixes it until the
errors are zero, before you see it.

https://github.com/user-attachments/assets/b0a156f8-9704-4b76-9175-13607ee8ca95

Video file: [docs/demo.mp4](docs/demo.mp4) · GIF version: [docs/demo.gif](docs/demo.gif). The demo is a re-creation of the workflow; the figures
and the audit results in it are real output of the skill.

<details>
<summary><b>한국어</b></summary>

논문 그림(방법 개요, 파이프라인, 모델 구조)을 수정 가능한 벡터 다이어그램으로 그리는 에이전트 스킬입니다.
이미지 생성 모델은 쓰지 않습니다. 에이전트에게 그림을 맡기면 보통 글자가 상자 밖으로 나가고, 라벨이 겹치고,
선이 엉뚱한 곳에 닿습니다. 이 스킬은 모든 초안을 실제 인쇄 크기로 재고, 오류가 0이 될 때까지 고친 뒤에
보여줍니다.

- 수정 전후로 모듈·화살표·경계 목록을 대조해 구조를 지킵니다.
- ICML, NeurIPS, ICLR, ACL, AAAI, CVPR, IEEE, ACM, Nature 규격에 맞춰 글자를 인쇄 pt로 잽니다.
- 배치가 다른 후보 2–3개를 그려 나란히 보여주고 고르게 합니다.
- LaTeX용 벡터 PDF와 Word·슬라이드용 300 dpi PNG로 내보냅니다.

설치: Claude 앱은 [최신 릴리스](https://github.com/WonJeong0913/paper-figure/releases/latest)의
`paper-figure.zip`을 Customize › Skills › Upload a skill로 올리고, Claude Code는 아래 Install의
`git clone` 한 줄을 실행합니다. 사용 예: "paper-figure 스킬로 내 방법의 오버뷰 그림 그려줘."
</details>

<details>
<summary><b>日本語</b></summary>

論文の図（手法の概要、パイプライン、モデル構造）を編集可能なベクター図として描くエージェントスキルです。
画像生成モデルは使いません。エージェントに図を任せると、文字が枠からはみ出したり、ラベルが重なったり、
線がずれたりしがちです。このスキルはすべての下書きを実際の印刷サイズで測り、エラーがゼロになるまで直してから
見せます。

- 編集の前後でモジュール・矢印・境界の一覧を照合し、構造を守ります。
- ICML、NeurIPS、ICLR、ACL、AAAI、CVPR、IEEE、ACM、Nature の規格に合わせ、文字を印刷時の pt で測ります。
- レイアウトの異なる候補を 2〜3 案描いて並べ、選んでもらいます。
- LaTeX 用のベクター PDF と、Word・スライド用の 300 dpi PNG を書き出します。

インストール: Claude アプリでは[最新リリース](https://github.com/WonJeong0913/paper-figure/releases/latest)の
`paper-figure.zip` を Customize › Skills › Upload a skill からアップロードし、Claude Code では下の Install に
ある `git clone` を実行します。使い方の例:「paper-figure スキルで、私の手法の概要図を描いて。」
</details>

<details>
<summary><b>简体中文</b></summary>

一个把论文插图（方法概览、流程、模型结构）绘制成可编辑矢量图的智能体技能，不使用图像生成模型。
让智能体画图时，常见的问题是文字溢出方框、标签相互重叠、连线对不准。本技能会按实际印刷尺寸测量每一版草图，
修正到零错误后再交给你。

- 修改前后对照模块、箭头和边界清单，保证结构不变。
- 按 ICML、NeurIPS、ICLR、ACL、AAAI、CVPR、IEEE、ACM、Nature 的规范，以印刷磅值（pt）测量文字。
- 绘制 2–3 个布局不同的候选方案并排展示，由你选择。
- 导出用于 LaTeX 的矢量 PDF，以及用于 Word 和幻灯片的 300 dpi PNG。

安装：Claude 应用请从[最新发布](https://github.com/WonJeong0913/paper-figure/releases/latest)下载
`paper-figure.zip`，在 Customize › Skills › Upload a skill 中上传；Claude Code 请运行下方 Install 中的
`git clone` 命令。使用示例：“用 paper-figure 技能画出我的方法概览图。”
</details>

## What it does

- **Keeps your structure.** It lists every module, arrow, boundary and loop in a ledger before editing and
  checks that none of them disappeared afterwards.
- **Sizes text for the venue.** Presets for ICML, NeurIPS, ICLR, ACL, AAAI, CVPR, IEEE, ACM and Nature,
  or any width you give it. Text is measured in printed points, not screen pixels.
- **Compares before it commits.** It looks at reference figures from top papers, draws two or three
  layout candidates, and shows them side by side for you to choose.
- **Measures the result.** A script reports text that is too small, text outside its box, overlaps, thin
  lines, text on grey and near-miss alignment, and renders greyscale and colour-blind views.
- **Exports for the manuscript.** A vector PDF with embedded fonts for LaTeX and a 300 dpi PNG for Word
  or slides.

## Install

**Claude apps (claude.ai, desktop):** download `paper-figure.zip` from the
[latest release](https://github.com/WonJeong0913/paper-figure/releases/latest), then go to
**Customize › Skills › + › Create skill › Upload a skill** and choose the zip. Code execution must be on.
(Do not upload GitHub's "Download ZIP": its folder is named `paper-figure-main` and the upload is refused.)

**Claude Code:**

```bash
git clone https://github.com/WonJeong0913/paper-figure ~/.claude/skills/paper-figure
pip install playwright numpy pillow
python3 -m playwright install chromium
# optional, enables the PDF font check: poppler-utils
```

Then ask: "Use the paper-figure skill to draw the overview figure for my method."

## Try it

```bash
cd examples/react-agent
python3 gen_fig.py
python3 ../../scripts/figure_audit.py project/Main.dc.html --venue nature
python3 ../../scripts/dc_export.py . --out out --venue nature
```

| Example | Shows | Venue preset |
|---|---|---|
| `examples/react-agent` | system figure: icon cards, panels, chips, a state bar, a feedback loop | `nature`, 6.9 pt |
| `examples/transformer-block` | architecture figure: trapezoids, operation circles, a repeated block | `icml`, 9.2 pt |
| `examples/rag-pipeline` | the smallest possible board | `icml`, 9.2 pt |

All three pass the audit with zero errors, and their PDFs embed every font and contain no raster images.

Or ask your agent: "Draw the overview figure for my method. Target venue: ACL."

## Layout

```
SKILL.md            workflow and rules the agent follows
scripts/            dc_board.py (draw), figure_audit.py (measure), dc_export.py (export)
references/         venues, style, drawing boards, credits
examples/           three runnable figures
```

## Examples by model

Same skill, same request, three Claude models. Each figure was drawn on a Claude Design canvas and passed
the audit.

| | Mamba | Transformer |
|---|---|---|
| **Fable 5.2** | ![Mamba, Fable 5.2](docs/models/mamba_fable-5.2.png) | ![Transformer, Fable 5.2](docs/models/transformer_fable-5.2.png) |
| **Opus 5.5** | ![Mamba, Opus 5.5](docs/models/mamba_opus-5.5.png) | ![Transformer, Opus 5.5](docs/models/transformer_opus-5.5.png) |
| **Sonnet 5.5** | ![Mamba, Sonnet 5.5](docs/models/mamba_sonnet-5.5.png) | ![Transformer, Sonnet 5.5](docs/models/transformer_sonnet-5.5.png) |

Author's impression from these runs (one run per model, not a benchmark): Fable 5.2 was the fastest and
the most detailed; Opus 5.5 was slower with quality close to Fable; Sonnet 5.5 was simpler but usable.
The Fable figures were drawn in the session where the skill was being developed, the others in fresh
sessions.

### From a real repository

The overview of [Merlin](https://github.com/WonJeong0913/merlin), drawn from its README and code map:

![Merlin harness overview](docs/merlin_overview.png)

## Requirements and limits

- Python 3, Playwright with Chromium. A Claude Design canvas is optional.
- Built for diagrams. Data plots (line, bar, scatter) are out of scope.
- Venue presets were checked against each venue's author kit in November 2026. Templates change, so
  confirm against the current one before submission.

## Credits and licence

Borrowed procedures are listed in `references/credits.md`. Licence: see `LICENSE`.
