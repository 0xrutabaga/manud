# Context Profiles (Stage A)

Each profile describes what readers of that kind of text expect. These are **norms, not templates**: never force a fixed opening, structure, or closing. When a text mixes categories (e.g. a founder post announcing a release), weigh the norms of both and keep the author's voice.

Quick reference:

| Category | Register | Format to keep | Typical problem in AI-drafted Thai | Common over-correction |
| :--- | :--- | :--- | :--- | :--- |
| General conversation | ภาษาพูดสุภาพ เป็นกันเอง | ข้อความสั้น | ภาษาเขียนในแชต, `ทำการ...` | ใส่สแลงหรืออีโมจิเกินจริง |
| Social / Facebook | อ่านง่ายบนมือถือ เป็นกันเองพอดี | ย่อหน้าสั้น | ปิดท้ายแบบหนังสือราชการ, hook คำถาม | ใส่ CTA, ความตื่นเต้น, `นะคะ` ทุกประโยค |
| Founder communication | ตรงไปตรงมา ถ่อมตัว | ตามต้นฉบับ | ภาษาประชาสัมพันธ์บริษัท | แต่งประวัติ/อารมณ์ของผู้ก่อตั้ง |
| Marketing / product | ชัดเจน จับต้องได้ | ตามต้นฉบับ | คำโปรยกลวง, `ตอบโจทย์` | เติมคุณสมบัติหรือคำสัญญาที่ไม่มี |
| Business email / announcement | สุภาพ กระชับ เป็นทางการพอดี | คำขึ้นต้น-ลงท้าย, รายการ | ราชการเยิ่นเย้อ, `จึงเรียนมาเพื่อ...` | ทำให้ห้วนหรือเป็นกันเองเกินไป |
| Research / academic | ทางการ ระมัดระวัง | ส่วนหัวข้อ, การอ้างอิง | ประโยคยาวซ้อน, คำนามซ้อน | ตัดคำสงวนท่าที (`อาจ`, `มีแนวโน้ม`) |
| Technical docs / release notes | แม่นยำ เป็นกลาง | หัวข้อ, รายการ, code, ตาราง | passive calque, `ได้มีการ...` | เขียนเป็นร้อยแก้วเล่าเรื่อง |
| Spoken presentation / pitch | ภาษาพูด ฟังครั้งเดียวเข้าใจ | เครื่องหมายเวลาสไลด์ | ภาษาเขียนอ่านออกเสียง | ขยายประโยคจนเกินเวลา |
| Already-natural | ตามต้นฉบับ | ตามต้นฉบับ | — | แก้ทั้งที่ไม่ต้องแก้ |

---

## General conversation (บทสนทนาทั่วไป, แชต, ข้อความสั้น)

- Readers expect how people actually talk in that relationship (colleague, friend, customer service).
- Fix written-language intrusions: `ทำการส่ง` → `ส่ง`, `ดำเนินการตรวจสอบ` → `เช็ก/ตรวจ`.
- Keep the politeness level the author chose. Do not upgrade `ครับ` to `ขอบพระคุณอย่างสูง` or downgrade a polite message to slang.

## Social media and Facebook posts

See [SOCIAL_MEDIA.md](SOCIAL_MEDIA.md). In short: short paragraphs, natural rhythm, information first, endings that fit an ordinary post. No bureaucratic sign-offs, no forced engagement hooks.

## Founder communications

- The voice is a person who built something, explaining it plainly: what it does, who it is for, what it does not do yet, what happens next.
- Candor beats polish. Stating limitations directly (`ตอนนี้ยังไม่รองรับ...`) is part of the voice.
- **Never** add a backstory, struggle, or motivation the source does not contain. Voice comes from attitude and word choice, not invented history.

## Marketing and product descriptions

- Concrete over abstract: say what the product does, using the source's features.
- Remove hollow praise (`ตอบโจทย์ทุกไลฟ์สไตล์`, `ถือเป็นอีกหนึ่งตัวเลือก`) unless the brand voice in the source uses it deliberately.
- Do not add benefits, comparisons, guarantees, or urgency that the source does not support.
- Keep feature/limitation pairs and price/plan pairs intact (see FIDELITY_CONTRACT).

## Business emails and announcements

- Preserve structure: greeting, purpose, details, action requested, deadline, contact, closing.
- Replace archaic bureaucratic filler with clear, polite Thai (`ขอแจ้งให้ทราบว่า...`, `รบกวน...ภายใน...`). Keep `ท่าน` / `ทางบริษัท` when the source's audience and organisation expect them.
- A formal closing is appropriate here; keep one, short.

## Research and academic writing

- Keep formal register, terminology, citations, and section structure.
- Keep hedges exactly: `อาจ`, `มีแนวโน้ม`, `ผลการศึกษาชี้ว่า` must not become certainties.
- Keep claims attached to the right study, sample, or condition (n, period, population).
- Improve readability by splitting overloaded sentences and de-nominalizing where the field allows. Do not make it conversational.

## Technical documentation and API release notes

See [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md). Precision first; structure stays; code never changes.

## Spoken presentations and pitching

See [SPOKEN_PRESENTATIONS.md](SPOKEN_PRESENTATIONS.md). Write for one-time listening, keep slide timing markers, preserve prototype/planned status.

## Already-natural Thai (minimal editing)

Signals that the text is already fine: varied sentence length, verbs rather than noun chains, a consistent voice, no translated syntax, information in a sensible order.

- Return it unchanged or fix only typos/spacing.
- Do not "improve" a sentence just to show you did something. If you change something, you should be able to say what was wrong with it.
- If the user explicitly asks for a different tone, that is a new brief, not a humanizing pass; follow the brief.
