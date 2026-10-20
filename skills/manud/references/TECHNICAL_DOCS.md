# Technical Documentation & Release Notes Policy

Technical readers scan, copy, and act on what they read. Naturalness here means **clear, idiomatic Thai inside a precise, scannable structure**, not conversational prose.

## 1. Never change

- Code blocks (content, language tag, indentation)
- Inline code, commands, flags (`--dry-run`), file paths, environment variables
- API names, endpoints and methods (`GET /v3/invoices/{id}/pdf`), parameters, field names
- HTTP status codes and error codes (`HTTP 401`, `E_TIMEOUT`)
- Version numbers (`v3.2.0`), configuration keys and values, default values, units
- The order of steps in a procedure

If a sentence around code is wrong or unclear, fix the Thai sentence, not the code.

## 2. Keep the structure

- Headings and their hierarchy (`#`, `##`)
- Bulleted and numbered lists (one change or one step per item)
- Tables
- Warnings, notes, callouts (`> **คำเตือน**`, `[!WARNING]`), including their severity
- Release-note sections (e.g. เพิ่ม / เปลี่ยน / แก้ไข / เลิกใช้ / Breaking changes)

You may improve a heading's wording (`สิ่งที่เปลี่ยนแปลง` → `มีอะไรเปลี่ยน`) as long as its level and role stay the same. Converting a list into a paragraph is a regression, even if the paragraph reads smoothly.

## 3. What to improve

- Passive calques and noun padding: `ได้มีการเพิ่ม...` → `เพิ่ม...`; `ระบบจะทำการคืนค่า` → `ระบบจะคืนค่า`; `ได้รับการปรับเพิ่ม` → `ปรับเพิ่ม`.
- Clear conditions: `ในกรณีที่...` → `ถ้า...` is fine; dropping the condition is not.
- One idea per list item; lead with the verb or the changed thing.
- Consistent terminology: pick the term the source uses (Thai or English) and keep it throughout. Do not translate established English terms (`endpoint`, `token`, `schema`) into invented Thai, and do not replace clear Thai with English.

## 4. What to avoid

- Casual tone, jokes, exclamation marks, particles (`นะ`, `เลย`, `แค่นี้เอง`) in reference docs and release notes.
- Marketing language (`มาแล้ว!`, `อัปเกรดง่ายๆ`) unless the source is a marketing announcement of a release.
- Softening warnings (`ระวังนิดนึง`) — keep the original severity.
- Removing "obvious" flags or steps (e.g. dropping `--dry-run` from a command).

## 5. Example (synthetic)

Source (robotic):

```markdown
## สิ่งที่เปลี่ยนแปลง
- ในกรณีที่ token หมดอายุ ระบบจะทำการคืนค่ารหัสสถานะ HTTP 401 แทน 403
```

Good:

```markdown
## มีอะไรเปลี่ยน
- ถ้า token หมดอายุ ระบบจะคืนรหัสสถานะ HTTP 401 แทน 403
```

Regression (do not do this): `ถ้า token หมดอายุจะได้ 401 แทน 403 นะ` as a paragraph without the heading or list.

Use `--context technical` with the checker: in that mode, loss of headings, list items, tables, or warnings is a deterministic failure.
