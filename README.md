<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/mascot-v1.0/svg/manud-mascot-dark.svg">
    <img src="assets/brand/mascot-v1.0/svg/manud-mascot-light.svg" width="160" height="160"
         alt="Little Manud, the MANUD mascot: a coral speech bubble whose outline makes a small Thai-letter loop">
  </picture>
</p>

<h1 align="center">MANUD · มะนุด</h1>
<p align="center"><b>Natural Thai. Same meaning.</b><br>เขียนไทยให้เป็นมะนุด</p>

<p align="center"><a href="#english">English</a> · <a href="#ภาษาไทย">ภาษาไทย</a></p>

---

## English

MANUD (pronounced "ma-nood", from Thai slang for *human*) is an open-source **Agent Skill** that edits existing Thai text so it reads naturally, **without changing what it says**. It was previously called **thai-humanizer** (V3.0.0).

It works like a careful editor, not a paraphraser:

- **Decides first** whether the text needs editing at all, and how much (keep / light / substantial). Text that already reads well is returned as is.
- **Keeps facts tied to the right thing**: which price belongs to which product, who did what, which condition applies to which offer.
- **Respects the format**: technical docs and release notes keep their headings, lists, code, versions and warnings.
- **Does not add** particles, slang, emoji, hype, calls to action or made-up details.

It is not a tool for hiding AI use or "beating detectors". The goal is clear, faithful Thai.

### Quick install

```bash
npx skills add 0xrutabaga/manud
```

This uses the open-source [Skills CLI](https://github.com/vercel-labs/skills) (needs Node.js 22.20 or newer). It normally lets you choose which agents to install for; add `-g` to install for your user instead of the current project. It installs the whole `manud` Skill folder (instructions, references, scripts), and you don't need to clone anything.

| Agent | Project install | Global install (`-g`) | Checked before release |
| :-- | :-- | :-- | :-- |
| Claude Code | `.claude/skills/manud` (link to `.agents/skills/manud`) | `~/.claude/skills/manud` | installed, found, used ✓ |
| Codex | `.agents/skills/manud` | `~/.agents/skills/manud` | installed, found, used when named (`$manud`) ✓ |
| Google Antigravity | `.agents/skills/manud` | `~/.agents/skills/manud` (see [docs/INSTALL.md](docs/INSTALL.md#antigravity)) | installed only; not tested in Antigravity |

Then just ask, for example: *"ช่วยเกลาข้อความนี้ให้อ่านเป็นธรรมชาติ แต่ห้ามเปลี่ยนข้อมูล: …"*

- **No Node.js?** Download this repository as a ZIP and copy its `skills/manud` folder into your agent's skills folder ([docs/INSTALL.md](docs/INSTALL.md#manual-install)).
- **Had `thai-humanizer` installed?** Check that MANUD works, then disable the old Skill or move it out of the skills folder, so the agent doesn't pick the wrong one ([docs/MIGRATION.md](docs/MIGRATION.md)).
- **Problems?** See [Troubleshooting](docs/INSTALL.md#troubleshooting).

### Example

Before:

> ทางฝ่ายบริหารทรัพยากรบุคคลมีความประสงค์ที่จะขอเรียนแจ้งให้พนักงานทุกท่านได้รับทราบว่า มีความจำเป็นอย่างยิ่งที่จะต้องดำเนินการส่งแบบประเมินผลการปฏิบัติงานประจำไตรมาสที่ 3 ภายในวันเสาร์ที่ 24 ตุลาคม 2569 เวลา 17:00 น. ...

After:

> ฝ่ายบุคคลขอแจ้งให้พนักงานทุกคนส่งแบบประเมินผลงานประจำไตรมาสที่ 3 ภายในวันเสาร์ที่ 24 ตุลาคม 2569 เวลา 17:00 น. ...

The date, time, quarter and deadline stay exactly the same. (Adapted from `skills/manud/examples/business_*.txt`, with the weekday corrected.)

### Use

Ask your agent in plain words, for example:

- "Make this Thai announcement sound natural: …"
- "ช่วยเกลาข้อความนี้ให้อ่านเป็นธรรมชาติ แต่ห้ามเปลี่ยนข้อมูล: …"

You get the edited text back. Ask for an audit if you want to see what changed and why. To call it by name: `/manud` (Claude Code) or `$manud` (Codex).

Optional fidelity check (Python 3, no dependencies):

```bash
python skills/manud/scripts/check_preservation.py original.txt edited.txt --json
```

It flags changed numbers, URLs, versions, code, negations and some meaning shifts. **A PASS means "no checked pattern found", not "meaning is proven identical".**

### How well does it work?

**BENCH1** (October 2026) compared V3.0.0 with no Skill on 30 held-out Thai tasks (3 runs each). The result is **exploratory evidence of improvement**, not proof:

- outputs with the Skill were preferred in all 30 tasks, and 1.1% of them had a material fidelity problem, against 87.6% without the Skill. The rubric counts added embellishment as material, and the no-Skill figure is 67.4% under a stricter rule. All of this was **rated by a single AI judge**;
- no native Thai speaker reviewed the results;
- the model ran through a third-party router (9Router), so the exact model settings could not be verified;
- the Skill text was injected into the prompt; loading it natively inside Antigravity was not tested.

Details and all limitations: [docs/evaluation/BENCH1_SUMMARY.md](docs/evaluation/BENCH1_SUMMARY.md). MANUD 3.1.0 has the same editing instructions as V3.0.0; only the name changed.

### Project

- [CONTRIBUTING.md](CONTRIBUTING.md): how to report problems and propose changes
- [SECURITY.md](SECURITY.md): how to report a security problem privately
- [CHANGELOG.md](CHANGELOG.md)
- License: code and Skill under [MIT](LICENSE). The MANUD names, wordmark and mascot are **not** covered by the MIT license. [LICENSING.md](LICENSING.md) shows what covers what; see also [TRADEMARKS.md](TRADEMARKS.md).
- Built with AI assistance: the Skill was developed with Claude Code, and the mascot with AI image and coding tools (details in [assets/brand/README.md](assets/brand/README.md)).

---

## ภาษาไทย

MANUD (มะนุด) คือ **Agent Skill** โอเพนซอร์สสำหรับเกลาข้อความภาษาไทยที่มีอยู่แล้วให้อ่านเป็นธรรมชาติ โดยมุ่งรักษาความหมาย ข้อเท็จจริง และรายละเอียดสำคัญของต้นฉบับ ชื่อเดิมคือ **thai-humanizer** (V3.0.0)

ทำหน้าที่เหมือนบรรณาธิการที่ช่วยเกลาข้อความเดิม ไม่ใช่เครื่องมือสร้างเนื้อหาใหม่จากศูนย์:

- **ตัดสินใจก่อน** ว่าควรแก้ไหม และแก้มากแค่ไหน ข้อความที่ดีอยู่แล้วจะคืนให้ตามเดิม
- **ข้อมูลต้องอยู่ถูกที่** ราคาไหนของสินค้าไหน ใครทำอะไร เงื่อนไขไหนของข้อเสนอไหน
- **เคารพรูปแบบเดิม** เอกสารเทคนิคและ release notes ยังมีหัวข้อ รายการ โค้ด เวอร์ชัน และคำเตือนครบ
- **ไม่เติม** คำลงท้าย สแลง อีโมจิ คำโฆษณา CTA หรือรายละเอียดที่ต้นฉบับไม่มี

MANUD ไม่ได้มีไว้ซ่อนการใช้ AI หรือหลบ AI detector เป้าหมายคือภาษาไทยที่อ่านง่ายและถูกต้องตามต้นฉบับ

### ติดตั้ง

```bash
npx skills add 0xrutabaga/manud
```

ต้องมี Node.js 22.20 ขึ้นไป โดยปกติตัวติดตั้งจะมีตัวเลือกให้เลือก Agent ที่ต้องการติดตั้ง ถ้าอยากให้ใช้ได้ทุกโปรเจกต์ ให้เติม `-g` ท้ายคำสั่ง ไม่ต้อง clone repo เอง (agent ที่รองรับและผลทดสอบอยู่ในตารางด้านบน)

ถ้าไม่มี Node.js ให้ดาวน์โหลด Repository นี้เป็นไฟล์ ZIP แล้วคัดลอกโฟลเดอร์ `skills/manud` ไปยังโฟลเดอร์ Skills ของ Agent ที่ใช้งาน (ดู [docs/INSTALL.md](docs/INSTALL.md)) หากเคยติดตั้ง `thai-humanizer` ไว้ ให้ทดสอบว่า MANUD ใช้งานได้ก่อน แล้วจึงปิดใช้งานหรือย้าย Skill เดิมไปเก็บไว้ เพื่อป้องกันการเรียกใช้ Skill ผิดตัว (ดู [docs/MIGRATION.md](docs/MIGRATION.md))

### ใช้งาน

บอก agent ตรง ๆ เช่น "ช่วยเกลาข้อความนี้ให้อ่านเป็นธรรมชาติ แต่ห้ามเปลี่ยนข้อมูล" แล้ววางข้อความ ถ้าอยากเห็นว่าแก้อะไรและเพราะอะไร ขอให้แสดงรายการที่แก้พร้อมเหตุผล

ตัวตรวจ `check_preservation.py` ช่วยตรวจหาปัญหาบางประเภท เช่น ตัวเลข URL เวอร์ชัน โค้ด คำปฏิเสธ และความหมายที่อาจเปลี่ยนไป แต่ **ผล PASS หมายถึงไม่พบข้อผิดพลาดตามกฎที่ตัวตรวจใช้เท่านั้น ไม่ได้รับประกันว่าความหมายและข้อเท็จจริงยังถูกต้องครบถ้วน**

### ผลการทดสอบ

BENCH1 (ตุลาคม 2569) เทียบ V3.0.0 กับการไม่ใช้ Skill บนโจทย์ที่กันไว้สำหรับทดสอบ 30 ข้อ ผลเป็น **หลักฐานเชิงสำรวจว่าดีขึ้น** ไม่ใช่ข้อพิสูจน์: ใช้ AI judge ตัวเดียว ไม่มีคนไทยตรวจ รันผ่าน router ภายนอก (9Router) และไม่ได้ทดสอบการโหลด Skill ใน Antigravity โดยตรง รายละเอียดอยู่ที่ [docs/evaluation/BENCH1_SUMMARY.md](docs/evaluation/BENCH1_SUMMARY.md)

### สัญญาอนุญาต

โค้ดและ Skill ใช้ [MIT](LICENSE) ส่วนชื่อ MANUD โลโก้ และมาสคอต **ไม่อยู่ภายใต้ MIT** ดู [LICENSING.md](LICENSING.md) และ [TRADEMARKS.md](TRADEMARKS.md) ตัว Skill พัฒนาโดยใช้ Claude Code ช่วย

ภาพอ้างอิงของเจ้ามะนุดสร้างด้วยโมเดลภาพ AI ผ่าน Meshy จากนั้นนำมาพัฒนาเป็นไฟล์เวกเตอร์ SVG ด้วยสคริปต์ที่เขียนโดยใช้ผู้ช่วย AI ภายใต้การกำกับของผู้ดูแลโปรเจกต์ (รายละเอียดใน [assets/brand/README.md](assets/brand/README.md))
