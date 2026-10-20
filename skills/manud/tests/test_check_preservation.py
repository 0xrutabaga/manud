import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_preservation.py"


class PreservationTests(unittest.TestCase):
    def call(self, original: str, rewritten: str, terms: str | None = None, extra_flags: list[str] | None = None):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            before = root / "before.txt"
            after = root / "after.txt"
            before.write_text(original, encoding="utf-8")
            after.write_text(rewritten, encoding="utf-8")
            cmd = [sys.executable, str(SCRIPT), str(before), str(after)]
            if terms is not None:
                term_path = root / "terms.txt"
                term_path.write_text(terms, encoding="utf-8")
                cmd.extend(["--terms-file", str(term_path)])
            if extra_flags:
                cmd.extend(extra_flags)
            env = dict(os.environ)
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"
            return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)

    # --- Legacy Tests ---
    def test_example_passes(self):
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        result = subprocess.run([
            sys.executable, str(SCRIPT),
            str(ROOT / "examples" / "before.txt"),
            str(ROOT / "examples" / "after.txt"),
            "--terms-file", str(ROOT / "examples" / "protected_terms.txt")
        ], capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_changed_price_fails(self):
        self.assertEqual(self.call("ราคา 160 บาท", "ราคา 180 บาท").returncode, 1)

    def test_removed_url_fails(self):
        self.assertEqual(self.call("ดู https://example.com/a2", "ดูเว็บ").returncode, 1)

    def test_protected_name_fails(self):
        self.assertEqual(self.call("ร้านอารีย์", "ร้านแถวนี้", "อารีย์\n").returncode, 1)

    def test_thai_digits_fails(self):
        self.assertEqual(self.call("ราคา ๑๖๐ บาท", "ราคา 160 บาท").returncode, 1)

    def test_same_facts_pass(self):
        self.assertEqual(self.call("ราคา 1,600 บาท เปิด 18:00", "เปิด 18:00 ราคา 1,600 บาท").returncode, 0)

    # --- Negation, Anti-Hallucination, and Anti-Slop Tests ---
    def test_dropped_negation_fails(self):
        source = "ร้านไม่มีที่จอดรถส่วนตัว"
        rewritten = "ร้านมีที่จอดรถส่วนตัว"
        result = self.call(source, rewritten)
        self.assertEqual(result.returncode, 1)
        self.assertIn("dropped negation", result.stdout)

    def test_dropped_mai_rong_rab_negation_fails(self):
        source = "TaskNest ไม่รองรับการใช้งานออฟไลน์"
        rewritten = "TaskNest รองรับการใช้งานออฟไลน์"
        result = self.call(source, rewritten)
        self.assertEqual(result.returncode, 1)
        self.assertIn("dropped negation: 'ไม่รองรับ'", result.stdout)

    def test_unsupported_transit_fails(self):
        source = "คาเฟ่อารีย์เปิด 09:00–18:00 น. ไม่มีที่จอดรถส่วนตัว"
        rewritten = "คาเฟ่อารีย์เปิด 09:00–18:00 น. ไม่มีที่จอดรถ แนะนำให้นั่ง BTS มาสะดวกสุด"
        result = self.call(source, rewritten)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported transit claim", result.stdout)

    def test_transit_false_positive_prevention(self):
        # Words like 'early' or 'Charlie' should NOT trigger 'arl' transit detection
        source = "เปิดให้ลอง early beta โดยมี Charlie ร่วมทดสอบ"
        rewritten = "เปิดให้ลอง early beta โดยมี Charlie ร่วมทดสอบระบบ"
        result = self.call(source, rewritten)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("unsupported transit claim", result.stdout)

    def test_transit_in_source_passes(self):
        source = "คาเฟ่อยู่ใกล้ BTS อารีย์ เปิด 09:00–18:00 น."
        rewritten = "ร้านเปิด 09:00–18:00 น. อยู่ใกล้ BTS อารีย์"
        result = self.call(source, rewritten)
        self.assertEqual(result.returncode, 0)

    def test_ai_slop_warns_and_strict_fails(self):
        source = "คาเฟ่อารีย์เปิด 18:00 น. ราคา 160 บาท"
        rewritten = "คาเฟ่อารีย์เปิด 18:00 น. ราคา 160 บาท ถือเป็นอีกหนึ่งตัวเลือกที่น่าสนใจ"
        # In non-strict mode, returns 0 with warning
        res_warn = self.call(source, rewritten)
        self.assertEqual(res_warn.returncode, 0)
        self.assertIn("[STYLE WARNING]: detected robotic AI slop phrasing", res_warn.stdout)
        # In strict mode, returns 1
        res_strict = self.call(source, rewritten, extra_flags=["--strict"])
        self.assertEqual(res_strict.returncode, 1)
        self.assertIn("FAIL [STYLE WARNING]: detected robotic AI slop phrasing", res_strict.stdout)

    def test_slop_present_in_source_not_warned(self):
        # If source already contained the phrase, keeping it is not an introduced slop
        source = "ในส่วนของสัญญาข้อ 1 ระบุราคา 160 บาท"
        rewritten = "ในส่วนของสัญญาข้อ 1 ระบุราคา 160 บาท"
        result = self.call(source, rewritten, extra_flags=["--strict"])
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("robotic AI slop phrase introduced", result.stdout)

    def test_cafe_factual_regression_valid_passes(self):
        source = (
            "ร้าน Slow Morning Cafe ตั้งอยู่ในย่านอารีย์ กรุงเทพฯ เปิดให้บริการทุกวันตั้งแต่เวลา 09:00–18:00 น. "
            "มีเมนูแนะนำคือ Matcha latte ราคา 160 บาท และ Americano ราคา 95 บาท ภายในร้านมี Wi-Fi ฟรี "
            "มีโต๊ะให้บริการทั้งหมด 8 โต๊ะ และมีปลั๊กไฟ 6 จุด ทางร้านไม่มีที่จอดรถส่วนตัว บรรยากาศเงียบสงบเหมาะแก่การนั่งทำงาน"
        )
        valid_rewrite = (
            "Slow Morning Cafe ย่านอารีย์ กรุงเทพฯ เปิดทุกวัน 09:00–18:00 น. บรรยากาศเงียบ เหมาะสำหรับนั่งทำงาน "
            "มีโต๊ะ 8 โต๊ะ ปลั๊กไฟ 6 จุด และ Wi-Fi ฟรี เครื่องดื่มมี Matcha latte 160 บาท และ Americano 95 บาท "
            "ร้านไม่มีที่จอดรถส่วนตัว"
        )
        terms = "Slow Morning Cafe\nอารีย์\nกรุงเทพฯ\nMatcha latte\nAmericano\nWi-Fi\n"
        result = self.call(source, valid_rewrite, terms=terms, extra_flags=["--strict"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_cafe_factual_regression_hallucinated_fails(self):
        source = (
            "ร้าน Slow Morning Cafe ตั้งอยู่ในย่านอารีย์ กรุงเทพฯ เปิดให้บริการทุกวันตั้งแต่เวลา 09:00–18:00 น. "
            "มีเมนูแนะนำคือ Matcha latte ราคา 160 บาท และ Americano ราคา 95 บาท ภายในร้านมี Wi-Fi ฟรี "
            "มีโต๊ะให้บริการทั้งหมด 8 โต๊ะ และมีปลั๊กไฟ 6 จุด ทางร้านไม่มีที่จอดรถส่วนตัว บรรยากาศเงียบสงบเหมาะแก่การนั่งทำงาน"
        )
        bad_rewrite = (
            "หากคุณกำลังมองหาสถานที่นั่งทำงานชิลๆ ในย่านอารีย์ Slow Morning Cafe ถือเป็นอีกหนึ่งตัวเลือกที่น่าสนใจ "
            "ในส่วนของเมนูเครื่องดื่ม มีทั้ง Matcha latte 160 บาท และ Americano 95 บาท สามารถจัดสรรเวลามาได้ทุกวันตั้งแต่ 09:00–18:00 น. "
            "ภายในมี Wi-Fi ฟรี พร้อมโต๊ะ 8 โต๊ะ และปลั๊กไฟ 6 จุด แม้จะไม่มีที่จอดรถส่วนตัว แต่แนะนำให้นั่ง BTS อารีย์มาจะสะดวกที่สุด "
            "ถือว่าควรค่าแก่การแวะไปลอง"
        )
        terms = "Slow Morning Cafe\nอารีย์\nกรุงเทพฯ\nMatcha latte\nAmericano\nWi-Fi\n"
        result = self.call(source, bad_rewrite, terms=terms, extra_flags=["--strict"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported transit claim", result.stdout)
        self.assertIn("robotic AI slop phrase introduced", result.stdout)

    def test_already_natural_text_passes(self):
        text = "วันนี้อากาศดีมาก เราไปเดินเล่นที่สวนสาธารณะกันตอน 17:00 น."
        result = self.call(text, text, extra_flags=["--strict"])
        self.assertEqual(result.returncode, 0)

    def test_json_output_mode(self):
        source = "ราคา 160 บาท ไม่มีที่จอดรถ"
        rewritten = "ราคา 160 บาท ไม่มีที่จอดรถ นั่ง BTS สะดวกสุด"
        result = self.call(source, rewritten, extra_flags=["--json"])
        self.assertEqual(result.returncode, 1)
        data = json.loads(result.stdout)
        self.assertFalse(data["passed"])
        self.assertTrue(any("unsupported transit claim" in e for e in data["unsupported_claim_errors"]))

    # --- Canonical TaskNest Regression Tests ---
    def test_unsupported_immediacy_fails(self):
        source = "TaskNest มีระบบสรุปบันทึกการประชุมด้วย AI และแปลงบันทึกการประชุมเป็น action items"
        rewritten = "TaskNest มีระบบสรุปบันทึกการประชุมด้วย AI และแปลงเป็น action items ได้ทันที"
        result = self.call(source, rewritten)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported immediacy claim", result.stdout)

    def test_immediacy_in_source_passes(self):
        source = "ระบบจะส่งการแจ้งเตือนทันทีเมื่อมีงานใหม่"
        rewritten = "เมื่อมีงานใหม่ ระบบจะแจ้งเตือนทันที"
        result = self.call(source, rewritten)
        self.assertEqual(result.returncode, 0)

    def test_unsupported_causal_rationale_fails(self):
        source = "TaskNest เปิดลงทะเบียนเบต้าวันที่ 12 พฤศจิกายน 2569 จำกัด 30 ทีม"
        rewritten = "TaskNest เปิดลงทะเบียนเบต้า 12 พฤศจิกายน 2569 จำกัด 30 ทีม เพื่อให้ทีมงานสามารถดูแลได้อย่างทั่วถึง"
        result = self.call(source, rewritten)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported causal explanation", result.stdout)

    def test_canonical_tasknest_regression_valid_passes(self):
        # Canonical scenario with exact fictional facts
        source = (
            "TaskNest เป็นเว็บแอปพลิเคชันสำหรับจัดการงานในทีมขนาดเล็ก มีระบบสรุปบันทึกการประชุมด้วย AI "
            "และแปลงบันทึกการประชุมเป็น action items รองรับทั้งภาษาไทยและภาษาอังกฤษ ค่าบริการ 149 บาทต่อเดือน "
            "พร้อมทดลองใช้งานฟรี 7 วัน เปิดลงทะเบียนเบต้าวันที่ 12 พฤศจิกายน 2569 จำกัด 30 ทีม ไม่รองรับการใช้งานออฟไลน์"
        )
        valid_founder_rewrite = (
            "ช่วงนี้เรากำลังพัฒนา TaskNest เว็บแอปจัดการงานสำหรับทีมขนาดเล็ก จุดหลักคือช่วยสรุปบันทึกการประชุมด้วย AI "
            "และแปลงเป็น action items รองรับทั้งภาษาไทยและภาษาอังกฤษ ค่าบริการ 149 บาทต่อเดือน มีให้ทดลองใช้ฟรี 7 วัน "
            "ตอนนี้เตรียมเปิดรับรอบเบต้าวันที่ 12 พฤศจิกายน 2569 จำกัด 30 ทีม ตัวระบบไม่รองรับการใช้งานออฟไลน์ครับ"
        )
        terms = "TaskNest\nAI\naction items\n149\n7\n12\n2569\n30\n"
        result = self.call(source, valid_founder_rewrite, terms=terms, extra_flags=["--strict"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_canonical_tasknest_regression_hallucinated_fails(self):
        source = (
            "TaskNest เป็นเว็บแอปพลิเคชันสำหรับจัดการงานในทีมขนาดเล็ก มีระบบสรุปบันทึกการประชุมด้วย AI "
            "และแปลงบันทึกการประชุมเป็น action items รองรับทั้งภาษาไทยและภาษาอังกฤษ ค่าบริการ 149 บาทต่อเดือน "
            "พร้อมทดลองใช้งานฟรี 7 วัน เปิดลงทะเบียนเบต้าวันที่ 12 พฤศจิกายน 2569 จำกัด 30 ทีม ไม่รองรับการใช้งานออฟไลน์"
        )
        bad_rewrite = (
            "เคยไหมที่การประชุมในทีมยืดยาวแล้วตามงานต่อยาก? TaskNest พร้อมช่วยคุณแล้ว วันนี้เราเปิดตัวเว็บแอปพลิเคชันสำหรับจัดการงานในทีมขนาดเล็ก "
            "ที่สรุปบันทึกการประชุมด้วย AI และแปลงเป็น action items ได้ทันที รองรับทั้งภาษาไทยและภาษาอังกฤษ ค่าบริการเพียง 149 บาทต่อเดือน "
            "ทดลองใช้ฟรี 7 วัน เราจะเปิดลงทะเบียนเบต้าในวันที่ 12 พฤศจิกายน 2569 จำกัดเพียง 30 ทีมเท่านั้น "
            "เพื่อให้ทีมงานสามารถดูแลได้อย่างทั่วถึงและเก็บฟีดแบ็กมาพัฒนาต่อ ทั้งนี้ระบบไม่รองรับการใช้งานออฟไลน์"
        )
        terms = "TaskNest\nAI\naction items\n149\n7\n12\n2569\n30\n"
        result = self.call(source, bad_rewrite, terms=terms, extra_flags=["--strict"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported immediacy claim", result.stdout)
        self.assertIn("unsupported causal explanation", result.stdout)
        self.assertIn("robotic AI slop phrase introduced", result.stdout)

    def test_synthetic_teamflow_passes(self):
        # Independent synthetic test data check
        source = (
            "TeamFlow เป็นเครื่องมือบริหารจัดการงานสำหรับทีมขนาดเล็กถึงขนาดกลาง ช่วยติดตามความคืบหน้าของโปรเจกต์ "
            "มอบหมายงาน และแจ้งเตือนกำหนดส่งผ่านไลน์ ในช่วงเปิดตัวเวอร์ชันเบต้า เปิดรับผู้ทดลองใช้งานจำนวนจำกัด 30 ทีม "
            "ไม่มีค่าใช้จ่ายตลอดช่วงเบต้า สมัครได้ที่เว็บไซต์ teamflow.app"
        )
        rewrite = (
            "ช่วงนี้เรากำลังเปิดให้ลอง TeamFlow เครื่องมือจัดการงานสำหรับทีมขนาดเล็กถึงขนาดกลาง "
            "ตัวระบบเน้นช่วยตามโปรเจกต์ มอบหมายงาน และมีแจ้งเตือนกำหนดส่งเข้าไลน์ ช่วงเบต้านี้เปิดรับ 30 ทีม "
            "ไม่มีค่าใช้จ่ายตลอดช่วงทดสอบ ใครสนใจเข้าไปลงทะเบียนได้ที่ teamflow.app ครับ"
        )
        terms = "TeamFlow\nไลน์\n30\nteamflow.app\n"
        result = self.call(source, rewrite, terms=terms, extra_flags=["--strict"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    # --- Spoken Presentation & Pitching Tests ---
    def test_spoken_presentation_valid_passes(self):
        source = (
            "[Slide 1: 30s]\n"
            "สวัสดีครับกรรมการทุกท่าน ผลผลิตทางการเกษตรในไทยสูญเสียไปกว่า 30% ระหว่างการขนส่ง คิดเป็นมูลค่า 500 ล้านบาทต่อปี\n\n"
            "[Slide 2: 45s]\n"
            "AgriFlow จึงพัฒนาต้นแบบกล่องเก็บความเย็นพลังงานแสงอาทิตย์ ในขั้นทดสอบในห้องแล็บ สามารถคุมอุณหภูมิ 4–8 องศาเซลเซียสได้นาน 12 ชั่วโมง ต้นทุนกล่องละ 1,200 บาท"
        )
        valid_spoken = (
            "[Slide 1: 30s]\n"
            "สวัสดีครับกรรมการทุกท่าน ผลผลิตการเกษตรในไทยสูญเสียระหว่างขนส่งกว่า 30% คิดเป็นมูลค่าความเสียหายสูงถึง 500 ล้านบาทต่อปีครับ\n\n"
            "[Slide 2: 45s]\n"
            "เราจึงพัฒนา AgriFlow กล่องเก็บความเย็นพลังงานแสงอาทิตย์ ในขั้นทดสอบในห้องแล็บ สามารถคุมอุณหภูมิ 4–8 องศาเซลเซียสได้นาน 12 ชั่วโมง ต้นทุนกล่องละ 1,200 บาท"
        )
        terms = "AgriFlow\n"
        result = self.call(source, valid_spoken, terms=terms, extra_flags=["--strict"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_spoken_presentation_dropped_duration_fails(self):
        source = "[Slide 1: 30s]\nสวัสดีครับกรรมการทุกท่าน"
        bad_duration = "[Slide 1: 20s]\nสวัสดีครับกรรมการทุกท่าน"
        result = self.call(source, bad_duration)
        self.assertEqual(result.returncode, 1)
        self.assertIn("dropped or modified slide duration marker", result.stdout)

    def test_spoken_presentation_pacing_warns_and_strict_fails(self):
        source = "[Slide 1: 30s]\nข้อความสั้น"
        # 600 characters in 30 seconds (~20 chars/sec) is excessively dense for spoken Thai
        dense_content = "[Slide 1: 30s]\n" + ("ข้อความทดสอบความยาวการพูด " * 25)
        # Non-strict returns 0 with pacing warning
        res_warn = self.call(source, dense_content)
        self.assertEqual(res_warn.returncode, 0)
        self.assertIn("presentation pacing warning", res_warn.stdout)
        # Strict returns 1
        res_strict = self.call(source, dense_content, extra_flags=["--strict"])
        self.assertEqual(res_strict.returncode, 1)
        self.assertIn("presentation pacing warning", res_strict.stdout)

    def test_unsupported_freshness_guarantee_fails(self):
        source = "AgriFlow พัฒนากล่องเก็บความเย็นรักษาอุณหภูมิ 4–8 องศาเซลเซียส"
        bad = "AgriFlow พัฒนากล่องเก็บความเย็น การันตีความสด 100% ปลอดภัย 100% รักษาอุณหภูมิ 4–8 องศาเซลเซียส"
        result = self.call(source, bad)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported guarantee claim", result.stdout)

    def test_unsupported_status_modality_upgrade_fails(self):
        source = "AgriFlow อยู่ระหว่างการพัฒนาต้นแบบในห้องปฏิบัติการ"
        bad = "AgriFlow ใช้งานได้จริงทั่วประเทศสำเร็จแล้ว"
        result = self.call(source, bad)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported status upgrade", result.stdout)


if __name__ == "__main__":
    unittest.main()
