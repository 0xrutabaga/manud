"""V3 regression tests built from NEW, independent synthetic examples.

None of these cases come from the historical benchmark (TaskNest, Slow Morning Cafe,
or the T01-T10 blind evaluation). They exist to exercise checker behaviour, not to
score writing quality. Do not reuse them as held-out evaluation prompts.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_preservation.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(ROOT / "scripts"))
import check_preservation as cp  # noqa: E402


def run_cli(original: str, rewritten: str, terms: str | None = None, flags: list[str] | None = None):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.txt").write_text(original, encoding="utf-8")
        (root / "b.txt").write_text(rewritten, encoding="utf-8")
        cmd = [sys.executable, str(SCRIPT), str(root / "a.txt"), str(root / "b.txt"), "--json"]
        if terms is not None:
            (root / "terms.txt").write_text(terms, encoding="utf-8")
            cmd += ["--terms-file", str(root / "terms.txt")]
        cmd += flags or []
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
        return proc.returncode, json.loads(proc.stdout)


def joined(result: dict, key: str) -> str:
    return "\n".join(result[key])


class RelationshipTests(unittest.TestCase):
    def test_swapped_latin_product_prices_flagged(self):
        src = "เมนูขายดีของร้านคือ Croissant 75 บาท และ Sourdough 180 บาท"
        bad = "เมนูขายดีของร้านคือ Croissant 180 บาท และ Sourdough 75 บาท"
        r = cp.check(src, bad)
        self.assertEqual(r["deterministic_failures"], [], "same numbers: token inventory alone cannot catch a swap")
        self.assertIn("relationship change", joined(r, "suspected_semantic_violations"))

    def test_reordered_prices_with_correct_pairs_pass(self):
        src = "เมนูขายดีของร้านคือ Croissant 75 บาท และ Sourdough 180 บาท"
        good = "ตัวที่ขายดีคือ Sourdough 180 บาท ส่วน Croissant 75 บาท"
        r = cp.check(src, good)
        self.assertNotIn("relationship change", joined(r, "suspected_semantic_violations"))

    def test_swapped_thai_product_prices_flagged_with_terms(self):
        src = "ขนมปังโฮลวีท 65 บาท ส่วนขนมปังลูกเกด 85 บาท"
        bad = "ขนมปังโฮลวีท 85 บาท ส่วนขนมปังลูกเกด 65 บาท"
        code, out = run_cli(src, bad, terms="ขนมปังโฮลวีท\nขนมปังลูกเกด\n")
        self.assertEqual(code, 1)
        self.assertTrue(any("relationship change" in x for x in out["suspected_semantic_violations"]))

    def test_swapped_plan_quotas_flagged(self):
        src = "แพ็กเกจ Starter ใช้ได้ 3 คน ส่วน Team ใช้ได้ 15 คน"
        bad = "แพ็กเกจ Starter ใช้ได้ 15 คน ส่วน Team ใช้ได้ 3 คน"
        r = cp.check(src, bad)
        self.assertIn("relationship change", joined(r, "suspected_semantic_violations"))


class ConditionAndNegationTests(unittest.TestCase):
    def test_missing_exclusivity_condition_flagged(self):
        src = "ส่งฟรีเฉพาะออเดอร์ที่สั่งครบ 500 บาทขึ้นไป"
        bad = "ส่งฟรี สั่งครบ 500 บาทขึ้นไป"
        r = cp.check(src, bad)
        self.assertIn("possible missing condition", joined(r, "suspected_semantic_violations"))

    def test_redundant_exclusivity_pair_is_one_condition(self):
        src = "ตอนนี้แอปรองรับเฉพาะ iOS เท่านั้น"
        good = "ตอนนี้แอปใช้ได้เฉพาะบน iOS"
        r = cp.check(src, good)
        self.assertNotIn("possible missing condition", joined(r, "suspected_semantic_violations"))

    def test_exclusivity_fully_dropped_still_flagged(self):
        src = "ตอนนี้แอปรองรับเฉพาะ iOS เท่านั้น"
        bad = "ตอนนี้แอปรองรับ iOS"
        r = cp.check(src, bad)
        self.assertIn("possible missing condition", joined(r, "suspected_semantic_violations"))

    def test_missing_conditional_flagged(self):
        src = "หากชำระเงินภายใน 7 วัน จะได้รับส่วนลด 10%"
        bad = "ได้รับส่วนลด 10% ชำระเงิน 7 วัน"
        r = cp.check(src, bad)
        text = joined(r, "suspected_semantic_violations")
        self.assertIn("conditional", text)
        self.assertIn("deadline", text)

    def test_reversed_negation_with_compensating_negation_flagged(self):
        # Total negation count is unchanged, so the V2 count check stays silent.
        src = "แอปเวอร์ชันนี้ไม่รองรับ Android และมีค่าบริการรายเดือน"
        bad = "แอปเวอร์ชันนี้รองรับ Android และไม่มีค่าบริการรายเดือน"
        r = cp.check(src, bad)
        self.assertNotIn("dropped negation", joined(r, "deterministic_failures"))
        self.assertIn("negation reversed", joined(r, "suspected_semantic_violations"))

    def test_preserved_negation_in_new_order_passes(self):
        src = "แอปเวอร์ชันนี้ไม่รองรับ Android และมีค่าบริการรายเดือน"
        good = "เวอร์ชันนี้มีค่าบริการรายเดือน และยังไม่รองรับ Android"
        r = cp.check(src, good)
        self.assertEqual(r["deterministic_failures"], [])
        self.assertEqual(r["suspected_semantic_violations"], [])

    def test_introduced_negation_flagged(self):
        src = "คอร์สนี้มีใบประกาศนียบัตรให้ผู้เรียน"
        bad = "คอร์สนี้ไม่มีใบประกาศนียบัตรให้ผู้เรียน"
        r = cp.check(src, bad)
        self.assertIn("negation introduced", joined(r, "suspected_semantic_violations"))

    def test_dropped_hedge_and_added_certainty_flagged(self):
        src = "ระบบน่าจะเปิดให้ใช้ประมาณกลางเดือนธันวาคม"
        bad = "ระบบเปิดให้ใช้กลางเดือนธันวาคมแน่นอน"
        r = cp.check(src, bad)
        self.assertIn("possible certainty upgrade", joined(r, "suspected_semantic_violations"))


class ActorStatusReasonTests(unittest.TestCase):
    def test_altered_actor_flagged(self):
        src = "ฝ่ายไอทีจะรีเซ็ตรหัสผ่านให้พนักงานภายใน 24 ชั่วโมง"
        bad = "ผู้ใช้ต้องรีเซ็ตรหัสผ่านด้วยตัวเองภายใน 24 ชั่วโมง"
        r = cp.check(src, bad)
        self.assertIn("possible actor change", joined(r, "suspected_semantic_violations"))

    def test_proposed_feature_described_as_completed_flagged(self):
        src = "ทีมวางแผนจะเพิ่มฟีเจอร์ส่งออกไฟล์ PDF ในไตรมาสหน้า"
        bad = "ทีมเพิ่มฟีเจอร์ส่งออกไฟล์ PDF เรียบร้อยแล้ว"
        r = cp.check(src, bad)
        self.assertIn("unsupported status upgrade", joined(r, "suspected_semantic_violations"))

    def test_planned_feature_kept_as_planned_passes(self):
        src = "ทีมวางแผนจะเพิ่มฟีเจอร์ส่งออกไฟล์ PDF ในไตรมาสหน้า"
        good = "ไตรมาสหน้าทีมมีแผนจะเพิ่มฟีเจอร์ส่งออกไฟล์ PDF"
        r = cp.check(src, good)
        self.assertEqual(r["suspected_semantic_violations"], [])

    def test_invented_reason_flagged(self):
        src = "ร้านปิดทุกวันจันทร์"
        bad = "ร้านปิดทุกวันจันทร์ เพื่อให้พนักงานได้พักผ่อนเต็มที่"
        r = cp.check(src, bad)
        self.assertIn("possible invented reason", joined(r, "suspected_semantic_violations"))

    def test_friend_word_is_not_a_causal_connector(self):
        src = "ร้านปิดทุกวันจันทร์"
        good = "ร้านปิดทุกวันจันทร์ ชวนเพื่อนมาวันอื่นได้"
        r = cp.check(src, good)
        self.assertNotIn("possible invented reason", joined(r, "suspected_semantic_violations"))

    def test_unsupported_capability_flagged(self):
        src = "PlantPal แจ้งเตือนเวลารดน้ำต้นไม้ตามตารางที่ผู้ใช้ตั้งไว้"
        bad = "PlantPal แจ้งเตือนเวลารดน้ำต้นไม้ตามตารางที่ผู้ใช้ตั้งไว้ และเชื่อมต่อกับ Google Home ได้"
        r = cp.check(src, bad)
        text = joined(r, "suspected_semantic_violations")
        self.assertIn("new entity or term not in source", text)
        self.assertIn("possible unsupported capability", text)

    def test_fabricated_testimonial_and_experience_flagged(self):
        src = "ผมทำแอปนี้ขึ้นมาสำหรับจดรายจ่ายประจำวัน"
        bad = "ผมเองก็เคยเจอปัญหาเงินหมดก่อนสิ้นเดือน เลยทำแอปนี้ขึ้นมาจดรายจ่ายประจำวัน ผู้ใช้หลายคนบอกว่าชอบมาก"
        r = cp.check(src, bad)
        text = joined(r, "suspected_semantic_violations")
        self.assertIn("possible invented personal experience", text)
        self.assertIn("possible fabricated testimonial", text)


class TechnicalDocumentTests(unittest.TestCase):
    def read(self, name: str) -> str:
        return (FIXTURES / name).read_text(encoding="utf-8")

    def test_structured_release_notes_rewrite_passes(self):
        code, out = run_cli(self.read("release_notes_before.md"), self.read("release_notes_good.md"),
                            flags=["--context", "technical"])
        self.assertEqual(code, 0, out)

    def test_flattened_release_notes_fail_in_technical_context(self):
        code, out = run_cli(self.read("release_notes_before.md"), self.read("release_notes_flattened.md"),
                            flags=["--context", "technical"])
        self.assertEqual(code, 1)
        det = "\n".join(out["deterministic_failures"])
        self.assertIn("structure loss: headings", det)
        self.assertIn("structure loss: list items", det)
        self.assertIn("code blocks", det)
        self.assertIn("inline code", det)

    def test_structure_loss_is_suspected_outside_technical_context(self):
        r = cp.check(self.read("release_notes_before.md"), self.read("release_notes_flattened.md"))
        self.assertIn("structure loss", joined(r, "suspected_semantic_violations"))

    def test_changed_cli_flag_fails(self):
        src = "รันคำสั่ง `ledgerlite sync --dry-run` ก่อนทุกครั้ง"
        bad = "รันคำสั่ง `ledgerlite sync --dryrun` ก่อนทุกครั้ง"
        r = cp.check(src, bad)
        self.assertIn("inline code", joined(r, "deterministic_failures"))

    def test_changed_version_and_endpoint_fail(self):
        src = "ตั้งแต่ v2.8.1 ให้เรียก POST /v2/sessions แทน"
        bad = "ตั้งแต่ v2.8 ให้เรียก POST /v2/session แทน"
        det = joined(cp.check(src, bad), "deterministic_failures")
        self.assertIn("versions", det)
        self.assertIn("HTTP endpoints", det)

    def test_changed_config_identifier_fails(self):
        src = "ตั้งค่า retry_limit เป็น 5 และ maxBackoff เป็น 30 วินาที"
        bad = "ตั้งค่า retryLimit เป็น 5 และ maxBackoff เป็น 30 วินาที"
        self.assertIn("identifiers", joined(cp.check(src, bad), "deterministic_failures"))


class SocialAndMinimalEditTests(unittest.TestCase):
    SOCIAL_SRC = (
        "สัปดาห์นี้ร้านต้นไม้ใบบางย้ายไปเปิดที่ตลาดนัดสวนจตุจักรโซน C ทุกวันเสาร์ 08:00–14:00 น. "
        "จึงขอให้ทุกท่านนำข้อมูลนี้ไปประกอบการพิจารณา"
    )

    def test_retained_bureaucratic_closing_warned_in_social_context(self):
        retained = (
            "สัปดาห์นี้ร้านต้นไม้ใบบางย้ายไปเปิดที่ตลาดนัดสวนจตุจักรโซน C ทุกวันเสาร์ 08:00–14:00 น. "
            "ขอให้ทุกท่านนำข้อมูลนี้ไปประกอบการพิจารณา"
        )
        code, out = run_cli(self.SOCIAL_SRC, retained, flags=["--context", "social", "--strict"])
        self.assertEqual(code, 1)
        self.assertTrue(any("retained from source" in w for w in out["stylistic_warnings"]))

    def test_natural_social_closing_passes_strict(self):
        natural = (
            "สัปดาห์นี้ร้านต้นไม้ใบบางย้ายไปเปิดที่ตลาดนัดสวนจตุจักรโซน C นะครับ "
            "เปิดทุกวันเสาร์ 08:00–14:00 น. แวะมาเจอกันได้"
        )
        code, out = run_cli(self.SOCIAL_SRC, natural, flags=["--context", "social", "--strict"])
        self.assertEqual(code, 0, out)

    def test_formal_register_not_warned_for_business_context(self):
        code, out = run_cli(self.SOCIAL_SRC, self.SOCIAL_SRC, flags=["--context", "business", "--strict"])
        self.assertEqual(code, 0, out)

    def test_engagement_bait_introduced_warned(self):
        src = "ร้านเปิดสาขาใหม่ที่ลาดพร้าว 71"
        bad = "ร้านเปิดสาขาใหม่ที่ลาดพร้าว 71 อย่าลืมกดไลก์กดแชร์ด้วยนะ"
        r = cp.check(src, bad, context="social")
        self.assertIn("engagement bait", joined(r, "stylistic_warnings"))

    def test_unnecessary_rewriting_warned_for_minimal_context(self):
        src = "พรุ่งนี้ประชุมทีมตอน 10 โมงที่ห้อง B2 ใครติดธุระแจ้งในกลุ่มได้เลย"
        churned = "สำหรับวันพรุ่งนี้ จะมีการจัดประชุมทีมขึ้นในเวลา 10 โมง ณ ห้อง B2 หากท่านใดติดภารกิจกรุณาแจ้งในกลุ่ม"
        code, out = run_cli(src, churned, flags=["--context", "minimal", "--strict"])
        self.assertEqual(code, 1)
        self.assertTrue(any("unnecessary rewriting" in w for w in out["stylistic_warnings"]))

    def test_unchanged_natural_text_passes_minimal_strict(self):
        src = "พรุ่งนี้ประชุมทีมตอน 10 โมงที่ห้อง B2 ใครติดธุระแจ้งในกลุ่มได้เลย"
        code, out = run_cli(src, src, flags=["--context", "minimal", "--strict"])
        self.assertEqual(code, 0, out)
        self.assertEqual(out["metrics"]["similarity"], 1.0)


class FalsePositiveGuards(unittest.TestCase):
    def test_teacher_and_yesterday_are_not_hedges_or_conditions(self):
        src = "เมื่อวานอาจารย์สั่งงานกลุ่ม ส่งวันศุกร์"
        good = "อาจารย์สั่งงานกลุ่มไว้เมื่อวาน ให้ส่งวันศุกร์"
        r = cp.check(src, good)
        self.assertEqual(r["suspected_semantic_violations"], [])

    def test_semantic_advisory_reports_without_failing(self):
        src = "ร้านปิดทุกวันจันทร์"
        bad = "ร้านปิดทุกวันจันทร์ เพื่อให้พนักงานได้พักผ่อนเต็มที่"
        code, out = run_cli(src, bad, flags=["--semantic-advisory"])
        self.assertEqual(code, 0)
        self.assertTrue(out["suspected_semantic_violations"])

    def test_json_reports_three_tiers_and_disclaimer(self):
        code, out = run_cli("ราคา 160 บาท", "ราคา 160 บาท")
        self.assertEqual(code, 0)
        for key in ("deterministic_failures", "suspected_semantic_violations", "stylistic_warnings", "disclaimer"):
            self.assertIn(key, out)
        self.assertIn("cannot prove", out["disclaimer"])

    def test_shipped_example_pairs_pass_default_mode(self):
        pairs = [
            ("before.txt", "after.txt"),
            ("cafe_before.txt", "cafe_after.txt"),
            ("business_before.txt", "business_after.txt"),
            ("technical_before.txt", "technical_after.txt"),
            ("social_before.txt", "social_after.txt"),
            ("tasknest_before.txt", "tasknest_after.txt"),
        ]
        for a, b in pairs:
            with self.subTest(pair=a):
                src = (ROOT / "examples" / a).read_text(encoding="utf-8")
                out = (ROOT / "examples" / b).read_text(encoding="utf-8")
                r = cp.check(src, out)
                self.assertEqual(r["deterministic_failures"] + r["suspected_semantic_violations"], [])


class SkillStructureTests(unittest.TestCase):
    def test_skill_folder_validates(self):
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_skill.py"), str(ROOT)],
                              capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_checker_version_matches_skill(self):
        self.assertIn(f'version: "{cp.VERSION}"', (ROOT / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
