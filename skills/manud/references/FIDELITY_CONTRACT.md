# Fidelity Contract (Stage B) and Relationship Errors

Before rewriting, list for yourself the facts that must survive and **what each fact is attached to**. The most damaging rewrite errors keep every word but change how the words relate.

## 1. What to capture

| Item | Capture as | Example (synthetic) |
| :--- | :--- | :--- |
| Values | value + unit + owner | `Starter → 3 คน`, `Team → 15 คน` |
| Prices | product/plan → price | `Croissant → 75 บาท`, `Sourdough → 180 บาท` |
| Dates & times | event → date/time/range | `ปิดรับสมัคร → 30 พ.ย. 17:00 น.` |
| Actors | action → who does it | `รีเซ็ตรหัสผ่าน → ฝ่ายไอที` (not the user) |
| Features & limits | feature → supported? | `Android → ไม่รองรับ`, `iOS → รองรับ` |
| Conditions | benefit → condition | `ส่งฟรี → เฉพาะออเดอร์ 500 บาทขึ้นไป` |
| Exceptions | rule → exception | `เปิดทุกวัน → ยกเว้นวันจันทร์` |
| Certainty | claim → hedge | `เปิดให้ใช้ → น่าจะ ประมาณกลางเดือน` |
| Status | feature → proposed / planned / testing / released | `export PDF → วางแผน ไตรมาสหน้า` |
| Causality | effect → reason **given in source** | none given → none in rewrite |
| Technical contract | exact string | `POST /v2/sessions`, `--dry-run`, `HTTP 401`, `v2.8.1` |

## 2. Relationship errors to watch for

These keep the same tokens but change the meaning. Token-level checks will not catch most of them.

1. **Swapped attributes** — `Croissant 75 / Sourdough 180` → `Croissant 180 / Sourdough 75`. Happens most when sentences are reordered or merged.
2. **Condition detached** — `ส่งฟรีเฉพาะออเดอร์ครบ 500 บาท` → `ส่งฟรี! สั่งครบ 500 บาทรับส่วนลด` (condition now attached to a different benefit, or dropped).
3. **Negation moved or reversed** — `ไม่รองรับ Android แต่มีค่าบริการ` → `รองรับ Android และไม่มีค่าบริการ`. The number of `ไม่` is the same; the meaning is inverted twice.
4. **Actor changed** — `ฝ่ายไอทีจะรีเซ็ตให้` → `ผู้ใช้ต้องรีเซ็ตเอง`. Also watch passive→active conversions: choose the real agent, never a guessed one. If the source hides the agent, keep it hidden.
5. **Status upgraded** — `วางแผนจะเพิ่ม` → `เพิ่มแล้ว`; `ทดสอบในห้องแล็บ` → `ใช้งานจริง`. Also the reverse (`เปิดให้ใช้แล้ว` → `กำลังจะเปิด`).
6. **Certainty upgraded** — `น่าจะเปิดประมาณกลางเดือน` → `เปิดกลางเดือนแน่นอน`.
7. **Invented causality** — adding `เพื่อ...`, `เพราะ...`, `จึง...` that explains a limit, policy, or feature when the source gives no reason.
8. **Scope changed** — `ลูกค้าใหม่` → `ลูกค้าทุกคน`; `บางรุ่น` → `ทุกรุ่น`; `ไม่เกิน 3 ครั้ง` → `3 ครั้ง`.
9. **Merged entities** — two products, branches, or plans collapsed into one sentence so a fact now seems to apply to both.
10. **Dropped caveat** — limitations, eligibility, or exceptions cut "for brevity".

## 3. How to check (Stage E)

- Walk the contract list against the draft. For each row, find the fact **and** its owner in the draft.
- Pay extra attention to any sentence you reordered, merged, or split.
- If the source is ambiguous about an attachment (e.g. a price that could belong to either item), keep the source's word order for that part rather than choosing an interpretation.

## 4. About the automated checker

`scripts/check_preservation.py` compares exact inventories (numbers, code, URLs, versions, endpoints, identifiers, protected terms, negation counts, slide markers) and runs heuristics for some relationship errors (value/entity binding, negation reversal, condition/hedge counts, actor terms, status markers, causal connectors, new entities).

It **cannot** guarantee semantic fidelity. It does not parse Thai syntax, it binds values to entities only when they are close together, and it can miss errors (or raise false alarms) that a reader would judge correctly. Use its output as a list of places to re-read, not as a verdict.
