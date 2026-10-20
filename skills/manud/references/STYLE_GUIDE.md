# Thai Humanizer V3 Style Reference & Linguistic Guide

This guide details the structural, narrative, and stylistic principles for transforming robotic or translation-heavy Thai prose into authentic, fluent, and domain-appropriate language.

> **V3 note:** Phrase tables below are *examples of patterns* to recognise, not a banned-word filter. A phrase is a problem only when it is wrong for the context (e.g. `ทั้งนี้` is normal in a formal notice and odd in a Facebook post). Category norms live in [CONTEXT_PROFILES.md](CONTEXT_PROFILES.md); fact-preservation rules in [FIDELITY_CONTRACT.md](FIDELITY_CONTRACT.md).

---

## 1. Voice & Persona Differentiation

A single generic "friendly" or "professional" tone is insufficient. Match the persona and medium accurately:

### A. Founder Voice (น้ำเสียงคนทำ / ผู้ก่อตั้ง)
- **Tone:** ตรงไปตรงมา อ่อนน้อม จริงใจ มีความกระตือรือร้นในการแก้ปัญหา แต่ไม่โอ้อวด ไม่ใช้สำนวนโฆษณา
- **Style:** เล่าอย่างเป็นธรรมชาติเหมือนคุยกับเพื่อนร่วมวงการหรือผู้ใช้ตัวจริง เน้นว่าระบบทำอะไรได้จริง ช่วยแก้ปัญหาอะไร และเปิดรับฟัง
- **THE IRON LAW:** **ห้ามแต่งเรื่องราวส่วนตัวหรืออารมณ์ดราม่าขึ้นมาเอง (Never fabricate personal backstories or emotional anecdotes).** ความเป็นผู้ก่อตั้งไม่ได้อยู่ที่การปั้นเรื่องว่า "วันหนึ่งผมตื่นมาเจอปัญหา..." แต่อยู่ที่ความจริงใจในการอธิบายงานสร้าง ความโปร่งใส และความเคารพในตัวผู้อ่าน

### B. Corporate Announcements (ประกาศทางการขององค์กร)
- **Tone:** เป็นทางการ หนักแน่น สุภาพ รัดกุม ชัดเจนในข้อปฏิบัติและลำดับเวลา
- **Style:** ใช้สรรพนามองค์กร เช่น `ทางบริษัท`, `ฝ่าย...` ระบุเงื่อนไข ขอบเขต และขั้นตอนติดต่อชัดเจน
- **หลีกเลี่ยง:** คำราชการโบราณเยิ่นเย้อ (`จึงเรียนมาเพื่อโปรดทราบและพิจารณาดำเนินการ`)

### C. Social Media & Facebook Posts
- **Tone:** เข้าถึงง่าย สบายตา จังหวะการอ่านเหมาะกับหน้าจอมือถือ
- **Style:** ใช้ย่อหน้าสั้น เว้นวรรคเป็นจังหวะหายใจ เล่าเรื่องแบบมีลำดับ ไม่ยัดเยียดหัวข้อกระสุน (bullet points) มากเกินไปจนกลายเป็นเอกสารสเปก
- **หลีกเลี่ยง:** สแลงยัดเยียด (`ปังมากแม่`, `จึ้ง`) และคำโปรยสไตล์ขายคอร์ส

### D. Technical & System Documentation
- **Tone:** แม่นยำ เป็นกลาง เชิงขั้นตอน
- **Style:** รักษาคำเฉพาะทาง รหัสสถานะ พารามิเตอร์ และลำดับขั้นตอนอย่างเคร่งครัด 100% ไม่ใช้คำเปรียบเปรย

---

## 2. Audience-Aware Openings (การขึ้นต้นอย่างรู้กลุ่มเป้าหมาย)

อย่าใช้สูตรสำเร็จเดียวกับการขึ้นต้นทุกงานเขียน โดยเฉพาะการขึ้นต้นด้วยคำถามซ้ำซาก:

### 3 รูปแบบการขึ้นต้นที่ดี:
1. **Relatable Problem / Pain Point (ปัญหาหรือความท้าทายจริง):**
   - *ตัวอย่าง:* `การจัดการงานในทีมหลายคนมักเจอปัญหางานหลุดหรือตกหล่นตามแชตต่างๆ`
2. **Direct Observation (ข้อสังเกตตรงๆ หรือสิ่งที่กำลังทำอยู่):**
   - *ตัวอย่าง:* `ช่วงที่ผ่านมาเราเห็นหลายทีมต้องสลับแอปไปมาระหว่างโปรเจกต์กับแอปแชต`
3. **Concise Announcement / Launch (การประกาศเปิดตัวตรงไปตรงมา):**
   - *ตัวอย่าง:* `ช่วงนี้เรากำลังเปิดให้ลอง NoteLeaf แอปจดโน้ตสำหรับทีมขนาดเล็ก`

### ❌ Banned Opening Trope (คำโปรยต้องห้าม):
- **ห้ามบังคับเปิดด้วยคำถามทุกครั้ง:** หลีกเลี่ยง `เคยไหมที่...?`, `ใครกำลังมีปัญหา...?`, `หากคุณกำลังมองหา...?`
- การใช้คำถามเปิดหัวแบบนี้ทำให้งานเขียนดูเหมือนโฆษณาแฝงราคาถูกหรือข้อความที่ AI ร่างขึ้นมาแบบสูตรสำเร็จตายตัว

---

## 3. Structural Restructuring over Synonym Replacement

### A. De-nominalization (แกะคำนามซ้อนรูปกริยา)
Bureaucratic and AI-generated Thai frequently converts simple verbs into bloated noun phrases:
- **Robotic:** `ทำการตรวจสอบความถูกต้องของข้อมูล` -> **Natural:** `ตรวจความถูกต้องของข้อมูล`
- **Robotic:** `มีความประสงค์ที่จะขอเรียนแจ้งให้ทราบ` -> **Natural:** `ขอแจ้งให้ทราบ`
- **Robotic:** `จัดให้มีการประชุมเพื่อพิจารณาเรื่องดังกล่าว` -> **Natural:** `นัดประชุมเพื่อพิจารณาเรื่องนี้`
- **Robotic:** `มีความจำเป็นอย่างยิ่งที่จะต้องดำเนินการจัดส่ง` -> **Natural:** `จำเป็นต้องส่ง` หรือ `ต้องส่ง`

### B. Eliminating English Passive Calques (หลีกเลี่ยงไวยากรณ์กรรมแบบภาษาอังกฤษ)
Thai naturally uses passive voice ("ถูก...") primarily for negative or adverse events:
- **Robotic:** `ระบบนี้ได้รับการพัฒนาโดยทีมวิศวกร` -> **Natural:** `ทีมวิศวกรพัฒนาระบบนี้ขึ้นมา`
- **Robotic:** `เอกสารดังกล่าวจะถูกจัดส่งให้แก่ท่าน` -> **Natural:** `เราจะส่งเอกสารให้คุณ` หรือ `เอกสารจะส่งไปถึงคุณ`
- **Robotic:** `ฟังก์ชันนี้ถูกเรียกใช้เมื่อเกิดข้อผิดพลาด` -> **Natural:** `ระบบจะเรียกฟังก์ชันนี้เมื่อเกิดข้อผิดพลาด`

### C. Clause Unstacking & Flow (คลายประโยคซ้อนทับและคำเชื่อมเยิ่นเย้อ)
AI text frequently strings together stacked relative pronouns and repetitive transition words (`ซึ่ง...`, `โดยที่...`, `นอกจากนี้... อีกทั้งยัง... ตลอดจน...`):
- **Robotic:** `NoteLeaf ช่วยจัดการโน้ต ซึ่งมีระบบแจ้งเตือนผ่านไลน์ อีกทั้งยังเปิดรับ 30 ทีม ตลอดจนไม่มีค่าใช้จ่าย`
- **Natural:** `NoteLeaf ช่วยจัดการโน้ต มีแจ้งเตือนเข้าไลน์ ตอนนี้เปิดรับ 30 ทีม และไม่มีค่าใช้จ่าย` (no new facts such as "ตลอดช่วงทดสอบ" are added)

---

## 4. The "Anti-Slop" & Anti-Hallucination Catalog

Unless directly present in the source text, eliminate these robotic tropes, invented rationales, and immediacy embellishments:

| Phrase / Pattern | Category | Why it Fails | Strategy / Replacement |
| :--- | :--- | :--- | :--- |
| `เคยไหมที่... / เคยเจอปัญหานี้ไหม` | Cliché Opening Hook | คำโปรยขายของสำเร็จรูปของ AI ทำให้อ่านแล้วดูไม่จริงใจ | เปลี่ยนเป็นเล่าปัญหาตรงๆ หรือบอกสิ่งที่ทำอยู่ |
| `ได้ทันที / แบบเรียลไทม์` | Invented Immediacy | แต่งเติมความเร็วหรือ latency โดยที่ต้นฉบับไม่ได้ระบุ | ตัดคำว่า "ทันที" ออก เหลือเพียงกริยาที่แท้จริง |
| `เพื่อให้ทีมงานดูแลได้อย่างทั่วถึง` | Invented Causal Rationale | คิดเหตุผลแทนผู้สร้างโดยไม่มีข้อมูลรองรับ | ระบุแค่จำนวนจำกัดตามจริง เช่น `เปิดรับ 30 ทีม` |
| `เพื่อเก็บฟีดแบ็กมาพัฒนาต่อ` | Invented Motivation | แต่งเติมวัตถุประสงค์ที่ต้นฉบับไม่ได้ระบุ | ตัดทิ้ง เว้นแต่ต้นฉบับจะระบุไว้ชัดเจน |
| `ถือเป็นอีกหนึ่งตัวเลือกที่น่าสนใจ` | Brochure Slop | คำชมสำเร็จรูปไร้สาระเนื้อหา | ตัดทิ้ง หรือระบุจุดเด่นจริง |
| `ในส่วนของ... / ในด้านของ...` | Bureaucratic Padding | ติดมาจากไวยากรณ์ภาษาอังกฤษ (`as for / in terms of`) | ตัดออกแล้วขึ้นต้นด้วยคำนามนั้นตรงๆ |
| `สามารถจัดสรรเวลาได้...` | Robotic Filler | ภาษาแข็งทื่อ ไม่ใช่คำพูดของมนุษย์ | `แวะมาได้ตั้งแต่...` / `เปิด...` |
| `ควรค่าแก่การแวะไปลอง` | Brochure Slop | สำนวนปิดท้ายสำเร็จรูป ฟังดูประดิษฐ์ | ตัดทิ้ง หรือปิดด้วยข้อมูลที่เป็นประโยชน์ |
| `ตอบโจทย์ทุกไลฟ์สไตล์ / ความต้องการ` | Marketing Slop | คำโปรยกลวงๆ ไม่มีสาระเนื้อหา | ระบุให้ชัดว่าช่วยเรื่องอะไร หรือตัดทิ้ง |
| `ไม่ควรพลาดด้วยประการทั้งปวง` | Marketing Slop | การตลาดเว่อร์เกินจริง | ตัดทิ้ง |
| `บอกเลยว่า...` | Forced Casualness | พยายามทำตัวเป็นกันเองแบบยัดเยียด | เล่าเนื้อหาตรงๆ โดยไม่ต้องเกริ่น |

---

## 5. Minimal Editing Protocol for Already-Natural Text

When an input text is evaluated and found to be:
1. Already fluent and naturally rhythmic in Thai,
2. Appropriate in register for its context and intended audience, and
3. Factually sound, qualified, and clear:

**Do not rewrite for the sake of rewriting.** Keep edits strictly to fixing typos, punctuation glitches, or minor syntax hitches.
