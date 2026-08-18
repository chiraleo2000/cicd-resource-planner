# Compliance Standards Register (v4 — full dump)

> Compiled from `Compliance_Standards_Register_CICD_v4.xlsx`.
> Cite rule IDs (TH-/TX-/S-/IN-/IX-/CN-/SC-/G-/W-) in every recommendation.

## 00_ภาพรวม

**ทะเบียนมาตรฐาน กฎหมาย และกรอบปฏิบัติ (Compliance Register)**

| รวบรวมจากเอกสาร 5 ฉบับ: CICD Blueprint Service V0.2 / CICD Internal Service Proposal (V0.1 + ฉบับเดิม) / แนวปฏิบัติการพัฒนาซอฟต์แวร์ฯ V0.2 (2 ฉบับ) |  |
| --- | --- |
| ชีท | เนื้อหา |
| 01_กฎหมายไทย | พ.ร.บ. / ประกาศ กมช. / มาตรฐาน DGA หลัก — 11 รายการ |
| 01b_กฎหมายลำดับรอง_แนวปฏิบัติ | ประกาศ PDPC, แนวปฏิบัติ/คำแนะนำ สกมช. (Zero Trust/AI/PQC), ETDA, DGA — 24 รายการ |
| 01c_กฎเกณฑ์รายภาคส่วน | ธปท. / ก.ล.ต. / คปภ. / กสทช. / สาธารณสุข / OT-ICS / จัดซื้อฯ / ลิขสิทธิ์ — 15 รายการ |
| 02_มาตรฐานสากล | OWASP / NIST / ISO / PCI / CIS / CSA / W3C / MITRE — 26 รายการ |
| 02b_มาตรฐานสากล_ชุดขยาย | ISO ชุดเสริม, NIST SP ชุดเต็ม, CIS Controls v8.1, CSA CCM, OpenSSF, CISA KEV, GDPR/CRA/NIS2 — 50 รายการ |
| 03_CloudNative_SupplyChain | CNCF / SLSA / SBOM / K8s / DevSecOps / AI-ML — 29 รายการ |
| 04_OWASP_Top10_Mapping | ช่องโหว่ ↔ กฎหมาย/มาตรฐาน ↔ แนวทางป้องกัน — 11 รายการ |
| 05_CICD_Stage_Compliance | Stage 1-6 ↔ เครื่องมือ ↔ ข้อกำหนดที่ต้องปฏิบัติ — 6 รายการ |
| 06_WASS_ขอบเขตบริการ | ข้อกำหนดบริการ WASS 25 หมวด ↔ มาตรฐานรองรับ ↔ หลักฐาน ↔ SLA — 28 รายการ |
| 07_WASS_ประเภทการสแกน | SAST/SCA/Secret/DAST/IAST/API/Container/IaC/Config/TLS/Headers/Network/Malware/A11y/Privacy/Mobile/PenTest/EASM — 18 ประเภท |
| 08_WASS_SeverityGate_SLA | Critical/High/Medium/Low + KEV + EPSS + เกณฑ์ Block ↔ SLA แก้ไข ↔ ผู้อนุมัติ — 12 เกณฑ์ |
| 09_WASS_แผนรอบการสแกน | Commit/Build/Release/รายวัน/สัปดาห์/เดือน/90 วัน/6 เดือน/รายปี/Ad-hoc — 10 รอบ |
| รวมทั้งหมด | 155 มาตรฐาน/กฎหมาย/แนวปฏิบัติ + 28 ข้อกำหนด WASS + 18 ประเภทการสแกน + 11 ช่องโหว่ |
| หมายเหตุ WASS | WASS = Web Application Security Scanning — ชีท 06-09 คือชุดเอกสารบริการสแกนความปลอดภัยเว็บแอปพลิเคชันแบบครบวงจร ผูกกับกฎหมายไทยที่บังคับใช้จริง (มาตรฐานเว็บไซต์ สกมช. พ.ศ. 2568, มาตรฐานขั้นต่ำฯ 2566, มสพร.11-2566, PDPA + ประกาศ PDPC 2565) และมาตรฐานสากล (OWASP/NIST/ISO/CIS) ใช้เป็น TOR, Service Catalog, Pipeline Policy และ Audit Checklist ได้ทันที |

## 01_กฎหมายไทย

| รหัส | ประเภท | ชื่อกฎหมาย/มาตรฐาน | หน่วยงาน | สถานะ/วันบังคับใช้ | สาระสำคัญที่ต้องปฏิบัติ | อ้างอิงในเอกสาร | ลิงก์ทางการ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TH-01 | กฎหมายไทย | พ.ร.บ. การรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562 | สกมช. (NCSA) | บังคับใช้ | CII 7 ภาคส่วน (ความมั่นคง, รัฐบาล, การเงิน, IT/โทรคมนาคม, ขนส่ง, พลังงาน, สาธารณสุข) ตาม ม.3; ประเมินความเสี่ยง/ตรวจสอบ (audit); รายงานเหตุ ม.54-57; 3 ระดับภัยคุกคาม (ไม่ร้ายแรง/ร้ายแรง/วิกฤติ); ThaiCERT | แนวปฏิบัติฯ หัวข้อ 2.1 | https://www.ratchakitcha.soc.go.th/DATA/PDF/2562/A/069/T_0020.PDF |
| TH-02 | กฎหมายไทย | พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 (PDPA) | PDPC | บังคับใช้ | ฐานทางกฎหมาย ม.19, 24-26; มาตรการความมั่นคงปลอดภัย ม.37; RoPA ม.39; แจ้งเหตุละเมิดภายใน 72 ชม. ม.37(4); สิทธิเจ้าของข้อมูล; ข้อมูลอ่อนไหว; Privacy by Design/Default; DPO | แนวปฏิบัติฯ 2.2 / OWASP A01,A04 | https://ratchakitcha.soc.go.th/documents/17082307.pdf |
| TH-03 | กฎหมายไทย | พ.ร.บ. ว่าด้วยการกระทำความผิดเกี่ยวกับคอมพิวเตอร์ 2550/2560 | ETDA/DES | บังคับใช้ | เก็บ Log จราจรคอมพิวเตอร์อย่างน้อย 90 วัน (อ้างอิงในมาตรฐานขั้นต่ำฯ) | แนวปฏิบัติฯ 2.3 (Log Management) | https://www.etda.or.th/th/Useful-Resource/laws-regulation.aspx |
| TH-04 | กฎหมายไทย | พ.ร.บ. การบริหารงานและการให้บริการภาครัฐผ่านระบบดิจิทัล พ.ศ. 2562 | DGA | บังคับใช้ | Open Data / e-Service / ธรรมาภิบาลข้อมูลภาครัฐ | แนวปฏิบัติฯ 2.4 (มสพร.11-2566) | https://www.dga.or.th/policy-standard/law-and-regulation/ |
| TH-05 | ประกาศ กมช. | มาตรฐานขั้นต่ำของข้อมูลหรือระบบสารสนเทศ พ.ศ. 2566 | สกมช. (NCSA) | ราชกิจจาฯ 18 ม.ค. 2567 / บังคับ 18 ม.ค. 2568 | Security Categorization ต่ำ/กลาง/สูง (CIA); ระดับต่ำ=Risk Assessment+IR Plan; กลาง=Audit Plan, Remote Connection, Removable Media; สูง=VAPT, Third Party Mgmt, Info Sharing, Resilience & Recovery; Three Lines of Defense; Log 90 วัน; ทบทวนทุก 3 ปี + ซ้อมแผน BCP ทุกปี | แนวปฏิบัติฯ 2.3 | https://www.ncsa.or.th/standards |
| TH-06 | ประกาศ กมช. | มาตรฐานด้านการรักษาความมั่นคงปลอดภัยไซเบอร์ระบบคลาวด์ พ.ศ. 2567 | สกมช. (NCSA) | บังคับใช้ | นโยบาย Cloud First; Shared Responsibility (CSC/CSP); 2 ส่วน: Cloud Security Governance + Cloud Infrastructure Security & Operation; ข้อมูลส่วนบุคคลอย่างน้อย Medium Impact; Least Privilege, Encryption, Monitoring; CSP ควรได้ ISO 27001/27017/27018/27701, CSA STAR | แนวปฏิบัติฯ 2.5 | https://www.ncsa.or.th/standards |
| TH-07 | ประกาศ กมช. | มาตรฐานการรักษาความมั่นคงปลอดภัยสำหรับเว็บไซต์ พ.ศ. 2568 | สกมช. (NCSA) | ราชกิจจาฯ 16 ก.ย. 2568 | 2 มิติ: Website Security Governance (แต่งตั้งผู้รับผิดชอบ, นโยบาย, ประเมินความเสี่ยง, IR Plan, BCP, Awareness) + Website Security Operation (MFA, TLS 1.2+, WAF, Logging & Monitoring, Penetration Testing, Secure Coding); Self-Assessment ปีละครั้ง; ระบุใน TOR | แนวปฏิบัติฯ 2.6 | https://www.ncsa.or.th/standards |
| TH-08 | แนวปฏิบัติ สกมช. | แนวปฏิบัติการรักษาความมั่นคงปลอดภัยเว็บไซต์ (Website Security Guideline) | สกมช. (NCSA) | แนวปฏิบัติ | คู่มือปฏิบัติประกอบมาตรฐานเว็บไซต์ พ.ศ. 2568 | แนวปฏิบัติฯ 2.6 | https://www.ncsa.or.th/standards |
| TH-09 | มาตรฐาน DGA | มสพร. 11-2566 มาตรฐานเว็บไซต์ภาครัฐ เวอร์ชัน 3.0 | DGA | บังคับ/แนะนำภาครัฐ | 8 องค์ประกอบ (ชื่อ/โดเมน .go.th, ข้อมูลพื้นฐาน, Open Data, e-Service, การมีส่วนร่วม, คุณลักษณะที่ควรมี, ความมั่นคงปลอดภัย, ประกาศนโยบาย); WCAG 2.1/2.2 ระดับ AA; HTTPS TLS 1.2/1.3 ห้าม self-signed; Session Mgmt; Machine-readable (CSV/JSON/XML); Privacy & Cookies Policy + Consent Pop-up; Responsive; WAF; Layout Guidelines; ITA | แนวปฏิบัติฯ 2.4 | https://standard.dga.or.th/ |
| TH-10 | หน่วยงาน | ThaiCERT - ศูนย์ประสานการรักษาความมั่นคงปลอดภัยระบบคอมพิวเตอร์ | สกมช. | หน่วยงาน | ศูนย์ประสานเฝ้าระวังและแจ้งเตือนภัยคุกคามไซเบอร์ | แนวปฏิบัติฯ 2.1 | https://www.thaicert.or.th/ |
| TH-11 | การประเมิน | ITA - การประเมินคุณธรรมและความโปร่งใส (ป.ป.ช.) | ป.ป.ช. | ประเมินประจำปี | เชื่อมโยงกับการเปิดเผยข้อมูลภาครัฐบนเว็บไซต์ | แนวปฏิบัติฯ 2.4 | https://itas.nacc.go.th/ |

## 01b_กฎหมายลำดับรอง_แนวปฏิบัติ

| รหัส | ประเภท | ชื่อประกาศ/แนวปฏิบัติ | หน่วยงาน | สถานะ | สาระสำคัญที่ต้องปฏิบัติ | ลิงก์ทางการ |
| --- | --- | --- | --- | --- | --- | --- |
| TX-01 | ประกาศ PDPC | ประกาศ คกก.คุ้มครองข้อมูลส่วนบุคคล เรื่อง มาตรการรักษาความมั่นคงปลอดภัยของผู้ควบคุมข้อมูลส่วนบุคคล พ.ศ. 2565 | PDPC | บังคับใช้ (ราชกิจจาฯ 20 มิ.ย. 2565) | มาตรฐานขั้นต่ำตาม ม.37(1): มาตรการเชิงองค์กร+เทคนิค+กายภาพ; ครอบคลุม CIA; Defense in Depth หลายชั้น; Access Control + Identity Proofing/Authentication/Authorization; Least Privilege & Need-to-know; User Access Management (registration/de-registration/provisioning/review/removal); Audit Trails; Privacy & Security Awareness; ทบทวนเมื่อเทคโนโลยีเปลี่ยนหรือเกิดเหตุละเมิด; กำหนดให้ผู้ประมวลผลปฏิบัติตามผ่าน DPA | https://www.ratchakitcha.soc.go.th/DATA/PDF/2565/E/140/T_0028.PDF |
| TX-02 | ประกาศ PDPC | ประกาศ PDPC เรื่อง หลักเกณฑ์และวิธีการในการแจ้งเหตุการละเมิดข้อมูลส่วนบุคคล พ.ศ. 2565 | PDPC | บังคับใช้ | แจ้ง สคส. ภายใน 72 ชั่วโมงนับแต่ทราบเหตุ; ประเมินความเสี่ยงต่อสิทธิเสรีภาพ; แจ้งเจ้าของข้อมูลเมื่อความเสี่ยงสูง; บันทึกเหตุละเมิดทุกกรณี | https://www.dga.or.th/document/106115/ |
| TX-03 | ประกาศ PDPC | ประกาศ PDPC เรื่อง หลักเกณฑ์เกี่ยวกับบันทึกรายการกิจกรรมการประมวลผล (RoPA) ของผู้ประมวลผลข้อมูลส่วนบุคคล พ.ศ. 2565 | PDPC | บังคับใช้ | รายละเอียด RoPA ตาม ม.39/ม.40(3); ระบุวัตถุประสงค์ ประเภทข้อมูล ผู้รับข้อมูล ระยะเวลาเก็บ มาตรการความปลอดภัย | https://www.pdpc.or.th/ |
| TX-04 | ประกาศ PDPC | ประกาศ PDPC เรื่อง การยกเว้นการบันทึกรายการฯ สำหรับกิจการขนาดเล็ก พ.ศ. 2565 | PDPC | บังคับใช้ | เงื่อนไขยกเว้น RoPA สำหรับ SME (ยกเว้นไม่ครอบคลุมข้อมูลอ่อนไหว/ประมวลผลความเสี่ยงสูง) | https://www.pdpc.or.th/ |
| TX-05 | ประกาศ PDPC | ประกาศ PDPC เรื่อง มาตรการคุ้มครองสำหรับการส่งหรือโอนข้อมูลส่วนบุคคลไปยังต่างประเทศ พ.ศ. 2566/2567 | PDPC | บังคับใช้ | ม.28-29: Adequacy, BCRs, SCCs; สำคัญกรณีใช้ Cloud/SaaS ต่างประเทศ (เช่น Azure DevOps เก็บ data ที่ US ตามที่ระบุใน Proposal) | https://www.pdpc.or.th/ |
| TX-06 | ประกาศ PDPC | ประกาศ PDPC เรื่อง หลักเกณฑ์การพิจารณาออกคำสั่งลงโทษปรับทางปกครอง พ.ศ. 2565 | PDPC | บังคับใช้ | โทษปรับทางปกครองสูงสุด 5 ล้านบาท (ข้อมูลอ่อนไหว) | https://www.pdpc.or.th/ |
| TX-07 | แนวปฏิบัติ สกมช. | แนวปฏิบัติการใช้ซีโร่ทรัสต์ (Zero Trust Guidelines) | สกมช. (NCSA) | แนวปฏิบัติ (ใหม่) | แนวทางประยุกต์ Zero Trust ตาม NIST SP 800-207 สำหรับหน่วยงานรัฐ/CII ไทย | https://www.ncsa.or.th/standards |
| TX-08 | แนวปฏิบัติ สกมช. | แนวปฏิบัติการใช้ปัญญาประดิษฐ์อย่างมั่นคงปลอดภัย (AI Security Guidelines) | สกมช. (NCSA) | แนวปฏิบัติ (ใหม่) | ความมั่นคงปลอดภัยของการนำ AI มาใช้ — เกี่ยวข้องกับ Pipeline AI/ML ใน Blueprint | https://www.ncsa.or.th/standards |
| TX-09 | คำแนะนำ สกมช. | คำแนะนำ เรื่อง แนวทางการปฏิบัติการเตรียมความพร้อมสำหรับยุคควอนตัม (Guidelines for Post-Quantum Readiness) | สกมช. (NCSA) | คำแนะนำ | สอดคล้องหัวข้อ 3.11 Post-Quantum Threat & Crypto-Agility และ 6.2 PQC ในเอกสารแนวปฏิบัติฯ | https://www.ncsa.or.th/standards |
| TX-10 | ประกาศ สกมช. | ประกาศ สกมช. เรื่อง แนวทางการกำหนดคุณลักษณะความมั่นคงปลอดภัยไซเบอร์ให้แก่ข้อมูลหรือระบบสารสนเทศ พ.ศ. 2567 | สกมช. (NCSA) | บังคับใช้ | แนวทางประกอบมาตรฐานขั้นต่ำฯ 2566 — วิธี Security Categorization (Low/Medium/High) ตาม CIA | https://www.ncsa.or.th/standards |
| TX-11 | ประกาศ กมช. | ประมวลแนวทางปฏิบัติและกรอบมาตรฐานด้านการรักษาความมั่นคงปลอดภัยไซเบอร์ สำหรับหน่วยงานของรัฐและ CII พ.ศ. 2564 (Code of Practice) | กมช./สกมช. | บังคับใช้ | กรอบ Identify-Protect-Detect-Respond-Recover; นโยบาย, โครงสร้างบุคลากร, การประเมินความเสี่ยง, แผนรับมือ; เป็นฐานของมาตรฐานลูกทั้งหมด | https://www.ncsa.or.th/standards |
| TX-12 | แนวทาง สกมช. | แนวทางการแจ้งหรือรายงานเหตุการณ์ภัยคุกคามทางไซเบอร์ ตาม ม.57/58 พ.ร.บ.ไซเบอร์ฯ | สกมช. (NCSA) | แนวปฏิบัติ | ขั้นตอน/แบบฟอร์ม/ระยะเวลาการรายงานเหตุภัยคุกคามไปยัง สกมช./ThaiCERT | https://www.ncsa.or.th/standards |
| TX-13 | แนวทาง สกมช. | คำแนะนำ แนวทางปฏิบัติในการประเมินความเสี่ยงและการตรวจสอบด้านความมั่นคงปลอดภัยไซเบอร์ สำหรับ CII | สกมช. (NCSA) | แนวปฏิบัติ | Risk Assessment + Cybersecurity Audit ตาม ม.44-45; แผนการตรวจสอบประจำปี | https://www.ncsa.or.th/standards |
| TX-14 | แบบประเมิน สกมช. | แบบประเมินสถานภาพการดำเนินงานด้านการรักษาความมั่นคงปลอดภัยไซเบอร์ (หน่วยงานรัฐ/CII/หน่วยงานกำกับ) | สกมช. (NCSA) | แบบฟอร์ม | ใช้ประเมินตนเองประจำปี; คู่กับ แบบฟอร์ม ค. ของมาตรฐานเว็บไซต์ 2568 | https://www.ncsa.or.th/standards |
| TX-15 | แบบฟอร์ม สกมช. | แบบฟอร์ม ค สำหรับดำเนินการตามมาตรฐานความมั่นคงปลอดภัยสำหรับเว็บไซต์ | สกมช. (NCSA) | แบบฟอร์ม | แบบ Self-Assessment ที่ต้องส่งปีละครั้งตามมาตรฐานเว็บไซต์ พ.ศ. 2568 | https://www.ncsa.or.th/standards |
| TX-16 | แนวทางชาติ | แนวทางการยกระดับดัชนี Global Cybersecurity Index (GCI) ของ ITU สำหรับประเทศไทย ระยะ 3 ปี (2568-2570) | สกมช. / ITU | แผนระดับชาติ | ตัวชี้วัดระดับชาติ 5 เสา (Legal, Technical, Organizational, Capacity, Cooperation) | https://www.ncsa.or.th/standards |
| TX-17 | แผนชาติ | (ร่าง) แผนรับมือเหตุการณ์ทางไซเบอร์ / National Cyber Exercise | สกมช. | แผน/การฝึก | การซ้อมแผนรับมือประจำปี — สอดคล้องข้อกำหนดซ้อม BCP ปีละครั้งในมาตรฐานขั้นต่ำฯ | https://www.ncsa.or.th/standards |
| TX-18 | มาตรฐาน ETDA | ขมธอ. (ข้อเสนอแนะมาตรฐานฯ) ชุดความมั่นคงปลอดภัยสารสนเทศและธุรกรรมอิเล็กทรอนิกส์ | ETDA (สพธอ.) | ข้อเสนอแนะมาตรฐาน | ชุดมาตรฐานอ้างอิงสำหรับระบบธุรกรรมอิเล็กทรอนิกส์ (เช่น ขมธอ. 35-2567), Digital ID, e-Signature | https://www.etda.or.th/th/Our-Service/Recommendation.aspx |
| TX-19 | กฎหมาย | พ.ร.ฎ. ว่าด้วยการควบคุมดูแลธุรกิจบริการแพลตฟอร์มดิจิทัล พ.ศ. 2565 (DPS) | ETDA | บังคับใช้ | หน้าที่แจ้งข้อมูลและมาตรการดูแลผู้ใช้บริการแพลตฟอร์มดิจิทัล | https://www.etda.or.th/th/Useful-Resource/laws-regulation.aspx |
| TX-20 | กฎหมาย | พ.ร.ก. มาตรการป้องกันและปราบปรามอาชญากรรมทางเทคโนโลยี พ.ศ. 2566 | DES | บังคับใช้ | การระงับธุรกรรม/บัญชีม้า และการแลกเปลี่ยนข้อมูลระหว่างหน่วยงาน | https://www.mdes.go.th/law |
| TX-21 | มาตรฐาน DGA | มาตรฐานรัฐบาลดิจิทัล (มรด./มสพร.) ชุดธรรมาภิบาลข้อมูลภาครัฐ (Data Governance Framework) | DGA | มาตรฐานภาครัฐ | กรอบธรรมาภิบาลข้อมูล, Data Catalog, Metadata, การจำแนกชั้นความลับข้อมูล | https://standard.dga.or.th/ |
| TX-22 | มาตรฐาน DGA | มาตรฐาน DGA ชุดความมั่นคงปลอดภัยและการเชื่อมโยงข้อมูลภาครัฐ (GDX / API Standards) | DGA | มาตรฐานภาครัฐ | มาตรฐาน API ภาครัฐ, การเชื่อมโยงและแลกเปลี่ยนข้อมูล, Digital ID ภาครัฐ | https://standard.dga.or.th/ |
| TX-23 | นโยบายคลาวด์ | นโยบาย Cloud First Policy ภาครัฐ / GDCC (Government Data Center and Cloud Service) | DES/DGA/NT | นโยบายภาครัฐ | ข้อกำหนดใช้คลาวด์ภาครัฐ; อ้างถึงใน มาตรฐานคลาวด์ สกมช. 2567 | https://www.dga.or.th/policy-standard/ |
| TX-24 | คำแนะนำ สกมช. | คำแนะนำ แนวทางการดำเนินงานด้านความมั่นคงปลอดภัยไซเบอร์สำหรับโรงพยาบาลของรัฐ พ.ศ. 2567 | สกมช. | คำแนะนำเฉพาะภาคส่วน | ตัวอย่างมาตรฐานเฉพาะ CII ภาคสาธารณสุข (1 ใน 7 ภาคส่วน) | https://www.ncsa.or.th/standards |

## 01c_กฎเกณฑ์รายภาคส่วน

| รหัส | ภาคส่วน | ชื่อกฎหมาย/ประกาศ | หน่วยงานกำกับ | สาระสำคัญ | ลิงก์ทางการ |
| --- | --- | --- | --- | --- | --- |
| S-01 | การเงิน/ธนาคาร | ประกาศ ธปท. สนส. เรื่อง การกำกับดูแลความเสี่ยงด้านเทคโนโลยีสารสนเทศ (IT Risk Management) | ธนาคารแห่งประเทศไทย (ธปท./BOT) | IT Governance, IT Risk Management, IT Security, Cyber Resilience, Third Party Risk; บังคับสถาบันการเงินและ Non-bank; ครอบคลุม SDLC/Change Management และการทดสอบเจาะระบบ | https://www.bot.or.th/th/our-roles/payment-systems/information-technology-risk-supervision.html |
| S-02 | การเงิน/ธนาคาร | แนวปฏิบัติ ธปท. เรื่อง การบริหารความเสี่ยงด้านเทคโนโลยีสารสนเทศ (2566) | ธปท. (BOT) | หนังสือเวียน 9 พ.ย. 2566 ถึงสถาบันการเงินทุกแห่ง; ยกระดับ Cyber Resilience และการรายงานเหตุการณ์ | https://www.bot.or.th/content/dam/bot/fipcs/documents/FOG/2566/ThaiPDF/25660202.pdf |
| S-03 | ตลาดทุน | ประกาศ ก.ล.ต. เรื่อง ข้อกำหนดในรายละเอียดเกี่ยวกับการจัดให้มีระบบเทคโนโลยีสารสนเทศ (IT Governance / Cyber Resilience) | สำนักงาน ก.ล.ต. (SEC) | บังคับผู้ประกอบธุรกิจในตลาดทุน (บล./บลจ./ผู้ประกอบธุรกิจสินทรัพย์ดิจิทัล); ต้องมี IT Governance, Cybersecurity, การทดสอบ VAPT, IT Audit และรายงานเหตุการณ์ | https://www.sec.or.th/TH/Pages/CYBERRESILIENCE-REGULATIONS.aspx |
| S-04 | ประกันภัย | ประกาศ คปภ. เรื่อง หลักเกณฑ์ วิธีการออกกรมธรรม์ฯ และกรอบการบริหารความเสี่ยงด้านเทคโนโลยีสารสนเทศ | สำนักงาน คปภ. (OIC) | บังคับบริษัทประกันชีวิต/วินาศภัย; IT Risk Framework, Cybersecurity Governance, IT Audit, ERM/ORSA | https://www.oic.or.th/th/industry/law |
| S-05 | โทรคมนาคม | ประกาศ กสทช. ด้านความมั่นคงปลอดภัยไซเบอร์และการคุ้มครองข้อมูลผู้ใช้บริการโทรคมนาคม | กสทช. (NBTC) | ผู้ให้บริการโทรคมนาคมเป็น CII 1 ใน 7 ภาคส่วน; ต้องมี VAPT และมาตรการคุ้มครองข้อมูลผู้ใช้ | https://www.nbtc.go.th/ |
| S-06 | สาธารณสุข | คำแนะนำ สกมช. แนวทางการดำเนินงานด้านความมั่นคงปลอดภัยไซเบอร์สำหรับโรงพยาบาลของรัฐ พ.ศ. 2567 + มาตรฐาน HA IT | สกมช. / สธ. | CII ภาคสาธารณสุข; ป้องกันข้อมูลสุขภาพซึ่งเป็นข้อมูลอ่อนไหวตาม PDPA ม.26 | https://www.ncsa.or.th/standards |
| S-07 | พลังงาน/ขนส่ง | ข้อกำหนด CII ภาคพลังงานและขนส่ง (OT/ICS Security) | สกมช. + หน่วยงานกำกับรายสาขา | ระบบควบคุมอุตสาหกรรม (SCADA/ICS); อ้างอิง IEC 62443 และ NIST SP 800-82 | https://www.ncsa.or.th/standards |
| S-08 | OT/ICS | IEC 62443 (Industrial Automation and Control Systems Security) / NIST SP 800-82r3 | IEC / NIST | มาตรฐานสากลสำหรับ CII ภาคพลังงาน ขนส่ง และสาธารณูปโภค | https://csrc.nist.gov/pubs/sp/800/82/r3/final |
| S-09 | การชำระเงิน | พ.ร.บ. ระบบการชำระเงิน พ.ศ. 2560 + ประกาศ ธปท. e-Payment Security | ธปท. | ผู้ให้บริการชำระเงินต้องมีมาตรฐานความมั่นคงปลอดภัย และสอดคล้อง PCI DSS | https://www.bot.or.th/th/our-roles/payment-systems.html |
| S-10 | Digital ID | มาตรฐาน Digital ID / การพิสูจน์และยืนยันตัวตนทางดิจิทัล (ThaID, DGA Digital ID, ETDA Digital ID Framework) | DGA / ETDA / กรมการปกครอง | IAL/AAL Levels ตาม NIST SP 800-63; ใช้กับ e-Service ภาครัฐตาม มสพร.11-2566 | https://www.dga.or.th/our-services/digital-platform-services/digitalid/ |
| S-11 | จัดซื้อจัดจ้าง | พ.ร.บ. การจัดซื้อจัดจ้างและการบริหารพัสดุภาครัฐ พ.ศ. 2560 | กรมบัญชีกลาง | กรอบการเขียน TOR โครงการพัฒนาระบบ/เว็บ; ต้องระบุข้อกำหนดความมั่นคงปลอดภัยตามมาตรฐาน สกมช. | https://www.gprocurement.go.th/ |
| S-12 | ลิขสิทธิ์ | พ.ร.บ. ลิขสิทธิ์ พ.ศ. 2537 (แก้ไข 2565) | กรมทรัพย์สินทางปัญญา | การใช้ Open Source License ให้ถูกต้อง — เชื่อมกับ License Compliance ใน Blueprint Stage 2 (ห้าม GPL/AGPL ภาครัฐ) | https://www.ipthailand.go.th/ |
| S-13 | ธุรกรรมอิเล็กทรอนิกส์ | พ.ร.บ. ว่าด้วยธุรกรรมทางอิเล็กทรอนิกส์ พ.ศ. 2544 (แก้ไข 2562) | ETDA | ผลทางกฎหมายของเอกสาร/ลายมือชื่ออิเล็กทรอนิกส์; ฐานของ e-Signature และ Audit Trail | https://www.etda.or.th/th/Useful-Resource/laws-regulation.aspx |
| S-14 | ข้อมูลข่าวสาร | พ.ร.บ. ข้อมูลข่าวสารของราชการ พ.ศ. 2540 | สำนักงาน กพร./สขร. | การเปิดเผยข้อมูลบนเว็บไซต์ภาครัฐ; คู่กับ ITA และ Open Data | https://www.oic.go.th/ |
| S-15 | ความมั่นคง | พ.ร.บ. ความมั่นคงแห่งชาติ / ระเบียบว่าด้วยการรักษาความลับของทางราชการ พ.ศ. 2544 | สมช. / สำนักนายกฯ | การจำแนกชั้นความลับข้อมูลราชการ (ลับ/ลับมาก/ลับที่สุด) — ประกอบ Data Classification | https://www.nsc.go.th/ |

## 02_มาตรฐานสากล

| รหัส | กลุ่ม | ชื่อมาตรฐาน | ผู้ออก | สาระสำคัญ / ส่วนที่อ้างถึง | อ้างอิงในเอกสาร | ลิงก์ทางการ |
| --- | --- | --- | --- | --- | --- | --- |
| IN-01 | OWASP | OWASP Top 10 (2021 / 2025) | OWASP | A01-A10 + Post-Quantum ในเอกสาร | แนวปฏิบัติฯ บทที่ 3 | https://owasp.org/Top10/ |
| IN-02 | OWASP | OWASP ASVS (Application Security Verification Standard) | OWASP | V1 Design, V4 Access Control, V5 Injection, V7 Error Handling | แนวปฏิบัติฯ 3.1,3.5,3.6,3.10 | https://owasp.org/www-project-application-security-verification-standard/ |
| IN-03 | OWASP | OWASP ZAP (DAST) | OWASP | เครื่องมือ DAST/Pen Test ใน CI Pipeline | CICD Proposal Stage 4 / Blueprint Stage 4 | https://www.zaproxy.org/ |
| IN-04 | OWASP | OWASP Dependency-Check (SCA) | OWASP | สแกน CVE ใน 3rd-party libraries | CICD Proposal / Blueprint Stage 2 | https://owasp.org/www-project-dependency-check/ |
| IN-05 | OWASP | OWASP Top 10 CI/CD Security Risks | OWASP | ความเสี่ยงเฉพาะ CI/CD pipeline | Blueprint (Supply Chain) | https://owasp.org/www-project-top-10-ci-cd-security-risks/ |
| IN-06 | OWASP | OWASP SAMM / Cheat Sheet Series | OWASP | Secure Coding / Maturity Model | แนวปฏิบัติฯ DevSecOps | https://owaspsamm.org/ |
| IN-07 | NIST | NIST SP 800-218 SSDF v1.1 | NIST | Secure Software Development Framework - อ้างใน A08 Integrity Failures | แนวปฏิบัติฯ 3.8 | https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf |
| IN-08 | NIST | NIST SP 800-207 Zero Trust Architecture | NIST | Control Plane (PE/PA) + Data Plane (PEP); CDM, Threat Intel, PKI, ID Mgmt, SIEM | แนวปฏิบัติฯ 4.3 | https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf |
| IN-09 | NIST | NIST SP 800-161r1 C-SCRM | NIST | Supply Chain Risk - อ้างใน A03 Software Supply Chain Failures | แนวปฏิบัติฯ 3.3 | https://csrc.nist.gov/pubs/sp/800/161/r1/final |
| IN-10 | NIST | NIST SP 800-63B Digital Identity Guidelines | NIST | Authentication - อ้างใน A07 Authentication Failures (MFA, password hashing) | แนวปฏิบัติฯ 3.7 | https://pages.nist.gov/800-63-3/sp800-63b.html |
| IN-11 | NIST | NIST CSF 2.0 | NIST | Govern / Identify / Protect / Detect / Respond / Recover - โครง Roadmap บทที่ 5 | แนวปฏิบัติฯ 5.1-5.4 | https://www.nist.gov/cyberframework |
| IN-12 | NIST | NIST Post-Quantum Cryptography (PQC) + CSWP 39 Crypto-Agility | NIST | CRYSTALS-Kyber, hybrid encryption, migration plan | แนวปฏิบัติฯ 3.11, 6.2 | https://csrc.nist.gov/projects/post-quantum-cryptography |
| IN-13 | NIST | NIST SP 800-53 Rev.5 | NIST | Security & Privacy Controls (baseline อ้างอิงมาตรฐานขั้นต่ำฯ) | แนวปฏิบัติฯ 2.3 | https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final |
| IN-14 | ISO/IEC | ISO/IEC 27001:2022 (ISMS) | ISO | A.9 Access Control, A.10 Cryptography, A.12 Operations/Logging, A.14 Secure Development, A.15 Supplier Security | แนวปฏิบัติฯ บทที่ 3 ทุกข้อ | https://www.iso.org/standard/27001 |
| IN-15 | ISO/IEC | ISO/IEC 27002:2022 | ISO | แนวปฏิบัติควบคุมประกอบ 27001 | แนวปฏิบัติฯ บทที่ 3 | https://www.iso.org/standard/75652.html |
| IN-16 | ISO/IEC | ISO/IEC 27017 (Cloud Security) | ISO | CSP ภาครัฐควรได้รับการรับรอง | แนวปฏิบัติฯ 2.5 | https://www.iso.org/standard/43757.html |
| IN-17 | ISO/IEC | ISO/IEC 27018 (PII in Public Cloud) | ISO | CSP ภาครัฐควรได้รับการรับรอง | แนวปฏิบัติฯ 2.5 | https://www.iso.org/standard/76559.html |
| IN-18 | ISO/IEC | ISO/IEC 27701 (PIMS) | ISO | Privacy Information Management - เชื่อมกับ PDPA | แนวปฏิบัติฯ 2.5 | https://www.iso.org/standard/85819.html |
| IN-19 | PCI | PCI DSS v4.0 | PCI SSC | Req 2 (config), Req 3-4 (crypto), Req 6.5 (injection), Req 10 (logging) | แนวปฏิบัติฯ 3.2,3.4,3.5,3.9 | https://www.pcisecuritystandards.org/document_library/ |
| IN-20 | CIS | CIS Benchmarks | CIS | Hardening baseline - อ้างใน A02 Security Misconfiguration | แนวปฏิบัติฯ 3.2 | https://www.cisecurity.org/cis-benchmarks |
| IN-21 | CSA | CSA STAR Registry | Cloud Security Alliance | กรอบรับรอง CSP | แนวปฏิบัติฯ 2.5 | https://cloudsecurityalliance.org/star/ |
| IN-22 | W3C | WCAG 2.1 / 2.2 ระดับ AA | W3C | Web Accessibility ตาม มสพร.11-2566 | แนวปฏิบัติฯ 2.4 | https://www.w3.org/TR/WCAG22/ |
| IN-23 | IETF | TLS 1.2 / TLS 1.3 (RFC 5246 / RFC 8446) | IETF | บังคับใช้ตามมาตรฐานเว็บไซต์ 2568 และ มสพร.11-2566 | แนวปฏิบัติฯ 2.4, 2.6 | https://datatracker.ietf.org/doc/html/rfc8446 |
| IN-24 | MITRE | MITRE ATT&CK | MITRE | Threat modeling / Detection mapping | แนวปฏิบัติฯ Threat Modeling | https://attack.mitre.org/ |
| IN-25 | MITRE | CWE Top 25 / CVE / CVSS | MITRE / FIRST | ฐานข้อมูลช่องโหว่ที่ SCA และ Container Scan ใช้เทียบ | Blueprint Stage 2-3 | https://cwe.mitre.org/top25/ |
| IN-26 | Threat Model | STRIDE / PASTA | Microsoft / VerSprite | Threat Modeling - อ้างใน A06 Insecure Design | แนวปฏิบัติฯ 3.6 | https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats |

## 02b_มาตรฐานสากล_ชุดขยาย

| รหัส | กลุ่ม | ชื่อมาตรฐาน | ผู้ออก | สาระสำคัญ / การนำไปใช้ | ลิงก์ทางการ |
| --- | --- | --- | --- | --- | --- |
| IX-01 | ISO/IEC | ISO/IEC 27005 (Information Security Risk Management) | ISO | กระบวนการประเมินและจัดการความเสี่ยง — ใช้ตอบข้อกำหนด Risk Assessment ของ สกมช. | https://www.iso.org/standard/80585.html |
| IX-02 | ISO/IEC | ISO/IEC 27035 (Incident Management) | ISO | แผนรับมือเหตุการณ์ (IR Plan) ตามมาตรฐานขั้นต่ำฯ และ ม.57/58 | https://www.iso.org/standard/78973.html |
| IX-03 | ISO/IEC | ISO/IEC 27031 / ISO 22301 (BCMS) | ISO | Business Continuity & IT Readiness — ข้อกำหนด BCP + ซ้อมแผนปีละครั้ง | https://www.iso.org/standard/75106.html |
| IX-04 | ISO/IEC | ISO/IEC 27034 (Application Security) | ISO | ความมั่นคงปลอดภัยของแอปพลิเคชันตลอด SDLC | https://www.iso.org/standard/44378.html |
| IX-05 | ISO/IEC | ISO/IEC 27036 (Supplier Relationships / ICT Supply Chain) | ISO | Third Party Management ตามมาตรฐานขั้นต่ำฯ ระดับสูง | https://www.iso.org/standard/59648.html |
| IX-06 | ISO/IEC | ISO/IEC 29100 / 29134 (Privacy Framework / DPIA) | ISO | Privacy by Design และการประเมินผลกระทบด้านความเป็นส่วนตัว (DPIA) คู่กับ PDPA | https://www.iso.org/standard/85938.html |
| IX-07 | ISO/IEC | ISO/IEC 5962:2021 (SPDX) | ISO | มาตรฐานสากลรูปแบบ SBOM | https://www.iso.org/standard/81870.html |
| IX-08 | ISO/IEC | ISO/IEC 42001:2023 (AI Management System) | ISO | ระบบบริหารจัดการ AI — สำหรับ Pipeline AI/ML | https://www.iso.org/standard/42001 |
| IX-09 | ISO/IEC | ISO/IEC 20000-1 (ITSM) / ITIL 4 | ISO / AXELOS | Change Management, Release Management ประกอบ CD Pipeline | https://www.iso.org/standard/70636.html |
| IX-10 | ISO/IEC | ISO/IEC 25010 (SQuaRE - Software Quality Model) | ISO | แบบจำลองคุณภาพซอฟต์แวร์ — ประกอบ Code Quality Gate | https://www.iso.org/standard/78176.html |
| IX-11 | ISO/IEC | ISO/IEC 12207 (Software Life Cycle Processes) | ISO | กระบวนการวงจรชีวิตซอฟต์แวร์ (SDLC) | https://www.iso.org/standard/63712.html |
| IX-12 | NIST | NIST SP 800-190 Application Container Security Guide | NIST | ความมั่นคงปลอดภัยของ Container — Registry, Image, Orchestrator, Runtime | https://csrc.nist.gov/pubs/sp/800/190/final |
| IX-13 | NIST | NIST SP 800-204 / 204A / 204B / 204C (Microservices & Service Mesh Security) | NIST | ความปลอดภัย Microservices, Service Mesh, DevSecOps สำหรับ cloud-native | https://csrc.nist.gov/pubs/sp/800/204/final |
| IX-14 | NIST | NIST SP 800-171 / 800-172 | NIST | การป้องกันข้อมูลควบคุมที่ไม่เป็นความลับ (CUI) ในระบบภายนอก | https://csrc.nist.gov/pubs/sp/800/171/r3/final |
| IX-15 | NIST | NIST SP 800-61r2 Computer Security Incident Handling Guide | NIST | กระบวนการ IR 4 ระยะ — ประกอบแผนรับมือเหตุการณ์ | https://csrc.nist.gov/pubs/sp/800/61/r2/final |
| IX-16 | NIST | NIST SP 800-34 Contingency Planning Guide | NIST | BCP/DRP — Resilience & Recovery ตามมาตรฐานขั้นต่ำฯ ระดับสูง | https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final |
| IX-17 | NIST | NIST SP 800-92 Guide to Computer Security Log Management | NIST | การบริหารจัดการ Log — เก็บ 90 วันตาม พ.ร.บ.คอมพิวเตอร์ | https://csrc.nist.gov/pubs/sp/800/92/final |
| IX-18 | NIST | NIST SP 800-115 Technical Guide to Security Testing and Assessment | NIST | แนวทาง VAPT / Penetration Testing | https://csrc.nist.gov/pubs/sp/800/115/final |
| IX-19 | NIST | NIST SP 800-40 Guide to Enterprise Patch Management | NIST | Patch & Vulnerability Management | https://csrc.nist.gov/pubs/sp/800/40/r4/final |
| IX-20 | NIST | NIST SP 800-88 Guidelines for Media Sanitization | NIST | การลบ/ทำลายข้อมูล — Removable Media ตามมาตรฐานขั้นต่ำฯ ระดับกลาง | https://csrc.nist.gov/pubs/sp/800/88/r1/final |
| IX-21 | NIST | NIST SP 800-146 / 800-144 Cloud Computing Security | NIST | ความปลอดภัยคลาวด์ — ประกอบมาตรฐานคลาวด์ สกมช. 2567 | https://csrc.nist.gov/pubs/sp/800/144/final |
| IX-22 | NIST | NIST SP 800-137 Information Security Continuous Monitoring (ISCM) | NIST | Continuous Monitoring / CDM ใน Zero Trust | https://csrc.nist.gov/pubs/sp/800/137/final |
| IX-23 | NIST | NIST SP 1800-35 Implementing a Zero Trust Architecture | NIST NCCoE | คู่มือปฏิบัติจริงการ implement ZTA | https://www.nccoe.nist.gov/projects/implementing-zero-trust-architecture |
| IX-24 | NIST | NVD (National Vulnerability Database) | NIST | ฐานข้อมูลช่องโหว่ที่ SCA/Container Scan ใช้อ้างอิง | https://nvd.nist.gov/ |
| IX-25 | OWASP | OWASP MASVS / Mobile Top 10 | OWASP | ความปลอดภัยแอปพลิเคชันมือถือ | https://mas.owasp.org/MASVS/ |
| IX-26 | OWASP | OWASP API Security Top 10 (2023) | OWASP | ความเสี่ยงเฉพาะ API — ประกอบ API Security Testing Stage 4 | https://owasp.org/API-Security/editions/2023/en/0x11-t10/ |
| IX-27 | OWASP | OWASP Software Component Verification Standard (SCVS) | OWASP | การตรวจสอบ supply chain ของ component + SBOM | https://owasp.org/www-project-software-component-verification-standard/ |
| IX-28 | OWASP | OWASP DevSecOps Guideline / Proactive Controls | OWASP | แนวทางฝัง security ใน CI/CD และ Top 10 Proactive Controls | https://owasp.org/www-project-devsecops-guideline/ |
| IX-29 | OWASP | OWASP Threat Dragon / Threat Modeling Cheat Sheet | OWASP | เครื่องมือ Threat Modeling ตอบ A06 Insecure Design | https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html |
| IX-30 | CIS | CIS Critical Security Controls v8.1 (18 Controls) | CIS | ชุดควบคุมพื้นฐาน 18 ข้อ (IG1-IG3) — map กับมาตรฐานขั้นต่ำฯ ได้ดี | https://www.cisecurity.org/controls/cis-controls-list |
| IX-31 | CIS | CIS Docker Benchmark / CIS Cloud Benchmarks (AWS/Azure/GCP) | CIS | Hardening baseline สำหรับ container และ cloud | https://www.cisecurity.org/cis-benchmarks |
| IX-32 | CSA | CSA Cloud Controls Matrix (CCM) v4 + CAIQ | Cloud Security Alliance | เมทริกซ์ควบคุมคลาวด์ 197 ข้อ — ใช้ประเมิน CSP ตามมาตรฐานคลาวด์ 2567 | https://cloudsecurityalliance.org/research/cloud-controls-matrix |
| IX-33 | CSA | CSA DevSecOps Pillars / Serverless Security | Cloud Security Alliance | แนวทาง DevSecOps บนคลาวด์ | https://cloudsecurityalliance.org/research/topics/devsecops |
| IX-34 | MITRE | MITRE D3FEND / ATT&CK for Containers / ATLAS (AI) | MITRE | เมทริกซ์การป้องกัน, ATT&CK สำหรับ container, ATLAS สำหรับภัยคุกคาม AI/ML | https://d3fend.mitre.org/ |
| IX-35 | FIRST | CVSS v4.0 / EPSS | FIRST.org | การให้คะแนนความรุนแรงช่องโหว่ (Severity Gate ใน Pipeline) | https://www.first.org/cvss/ |
| IX-36 | CISA | CISA Known Exploited Vulnerabilities (KEV) Catalog | CISA | รายการช่องโหว่ที่ถูกใช้โจมตีจริง — ควรใช้เป็น Gate บังคับใน SCA | https://www.cisa.gov/known-exploited-vulnerabilities-catalog |
| IX-37 | CISA | CISA Secure by Design & Default / Secure Software Development Attestation | CISA | หลักการออกแบบปลอดภัยโดยกำเนิด + การรับรอง SSDF | https://www.cisa.gov/securebydesign |
| IX-38 | OpenSSF | OpenSSF S2C2F (Secure Supply Chain Consumption Framework) | OpenSSF | กรอบการบริโภค OSS อย่างปลอดภัย 8 ระดับ | https://github.com/ossf/s2c2f |
| IX-39 | OpenSSF | SLSA Provenance / OpenSSF Baseline / Sigstore Policy Controller | OpenSSF | หลักฐานต้นทาง artifact ที่ verify ได้ก่อน deploy | https://slsa.dev/spec/v1.0/provenance |
| IX-40 | Standard | IETF RFC 6749/6750 OAuth 2.0 + OpenID Connect + JWT (RFC 7519) | IETF / OpenID Foundation | มาตรฐาน Authentication/Authorization สำหรับ API และ SSO | https://openid.net/developers/specs/ |
| IX-41 | Standard | OWASP Secure Headers / HSTS (RFC 6797) / CSP Level 3 | OWASP / IETF / W3C | HTTP Security Headers บังคับตามมาตรฐานเว็บไซต์ 2568 | https://owasp.org/www-project-secure-headers/ |
| IX-42 | Standard | OpenAPI Specification 3.x | OpenAPI Initiative | สัญญา API สำหรับ API Security Testing (Schemathesis/42Crunch) | https://spec.openapis.org/oas/latest.html |
| IX-43 | Framework | DORA Metrics / DevOps Research & Assessment | Google Cloud / DORA | ตัววัดประสิทธิภาพ CI/CD (Deployment Frequency, Lead Time, MTTR, Change Failure Rate) | https://dora.dev/ |
| IX-44 | Framework | SAFECode / BSIMM | SAFECode / Synopsys | แนวปฏิบัติและ maturity model การพัฒนาซอฟต์แวร์ปลอดภัย | https://safecode.org/ |
| IX-45 | Framework | COBIT 2019 / ISO 38500 (IT Governance) | ISACA / ISO | ธรรมาภิบาล IT — ประกอบ GRC และ Three Lines of Defense | https://www.isaca.org/resources/cobit |
| IX-46 | Framework | Google BeyondCorp / BeyondProd | Google | โมเดล Zero Trust เชิงปฏิบัติสำหรับ enterprise และ cloud-native | https://cloud.google.com/beyondcorp |
| IX-47 | Framework | Microsoft SDL (Security Development Lifecycle) | Microsoft | กระบวนการพัฒนาปลอดภัย 12 practices | https://www.microsoft.com/en-us/securityengineering/sdl |
| IX-48 | Framework | Well-Architected Framework (AWS/Azure/GCP) - Security Pillar | Cloud Providers | แนวปฏิบัติสถาปัตยกรรมคลาวด์ปลอดภัย | https://aws.amazon.com/architecture/well-architected/ |
| IX-49 | Regulation | EU GDPR / EU Cyber Resilience Act (CRA) / NIS2 | EU | อ้างอิงเปรียบเทียบ PDPA; CRA บังคับ SBOM+vulnerability handling สำหรับผลิตภัณฑ์ดิจิทัล | https://eur-lex.europa.eu/eli/reg/2016/679/oj |
| IX-50 | Regulation | US EO 14028 / OMB M-22-18 (Software Supply Chain Security) | US Government | ต้นแบบข้อบังคับ SBOM + SSDF attestation ที่หลายประเทศนำมาใช้ | https://www.whitehouse.gov/briefing-room/presidential-actions/2021/05/12/executive-order-on-improving-the-nations-cybersecurity/ |

## 03_CloudNative_SupplyChain

| รหัส | กลุ่ม | ชื่อมาตรฐาน/เฟรมเวิร์ก | ผู้ออก/สถานะ | สาระสำคัญ | อ้างอิงในเอกสาร | ลิงก์ทางการ |
| --- | --- | --- | --- | --- | --- | --- |
| CN-01 | Supply Chain | SLSA (Supply-chain Levels for Software Artifacts) | OpenSSF | กรอบระดับความปลอดภัย supply chain, provenance | Blueprint Stage 3,5 (Signing/SBOM) | https://slsa.dev/ |
| CN-02 | Supply Chain | Sigstore (Cosign, Rekor, Fulcio) | OpenSSF/Linux Foundation | Artifact Signing / Image Signing (Mandatory ภาครัฐ) | Blueprint Stage 3,5 | https://www.sigstore.dev/ |
| CN-03 | Supply Chain | in-toto | CNCF | Supply chain attestation framework | Blueprint Stage 3,5 | https://in-toto.io/ |
| CN-04 | Supply Chain | Notary v2 / Notation | CNCF Graduated | Image signing และ verification | Blueprint Stage 5 | https://notaryproject.dev/ |
| CN-05 | SBOM | CycloneDX | OWASP/Ecma | รูปแบบ SBOM มาตรฐาน (Mandatory ภาครัฐ) | Blueprint Stage 5 | https://cyclonedx.org/ |
| CN-06 | SBOM | SPDX (ISO/IEC 5962:2021) | Linux Foundation / ISO | รูปแบบ SBOM มาตรฐานสากล | Blueprint Stage 5 | https://spdx.dev/ |
| CN-07 | SBOM | NTIA Minimum Elements for SBOM | NTIA (US) | องค์ประกอบขั้นต่ำของ SBOM | Blueprint Stage 5 | https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom |
| CN-08 | Policy | Open Policy Agent (OPA) / Conftest / Gatekeeper | CNCF Graduated | Policy-as-Code, Quality Gate, Branch Protection, Admission Control | Blueprint Stage 1,3,6 | https://www.openpolicyagent.org/ |
| CN-09 | Policy | Kyverno | CNCF Incubating | Kubernetes Policy Enforcement / Admission Controller | แนวปฏิบัติฯ 4.4 / Blueprint Stage 3 | https://kyverno.io/ |
| CN-10 | K8s | Kubernetes Pod Security Standards (PSS) | CNCF | บังคับใช้ผ่าน Admission Controller ก่อน Deploy | แนวปฏิบัติฯ 4.4 | https://kubernetes.io/docs/concepts/security/pod-security-standards/ |
| CN-11 | K8s | Kubernetes Security Documentation / RBAC / Network Policies | CNCF | RBAC Strict Mode, Service Accounts, Network Isolation, Secrets Management | แนวปฏิบัติฯ 4.4 | https://kubernetes.io/docs/concepts/security/ |
| CN-12 | K8s | CIS Kubernetes Benchmark | CIS | Hardening K8s Control Plane, etcd, API Server, Nodes | แนวปฏิบัติฯ 4.4 | https://www.cisecurity.org/benchmark/kubernetes |
| CN-13 | Cloud Native | CNCF Cloud Native Security Whitepaper | CNCF TAG-Security | กรอบความปลอดภัย Cloud Native 4 ระยะ (Develop/Distribute/Deploy/Runtime) | แนวปฏิบัติฯ 4.4 | https://github.com/cncf/tag-security |
| CN-14 | Runtime | Falco | CNCF Graduated | Runtime Security Monitoring (Mandatory Real-time ภาครัฐ) | แนวปฏิบัติฯ 4.4 / Blueprint Stage 6 | https://falco.org/ |
| CN-15 | Observability | OpenTelemetry | CNCF | Metrics / Logs / Traces มาตรฐานกลาง | Blueprint Stage 6 | https://opentelemetry.io/ |
| CN-16 | GitOps | OpenGitOps Principles / Argo CD / Flux | CNCF | GitOps deployment, Argo Rollouts (Blue-Green/Canary) | Blueprint Stage 6 | https://opengitops.dev/ |
| CN-17 | Secrets | HashiCorp Vault / K8s Secrets | HashiCorp / CNCF | Secrets Management ป้องกันข้อมูลลับรั่วไหล | แนวปฏิบัติฯ 4.4 / Blueprint Stage 2 | https://developer.hashicorp.com/vault/docs |
| CN-18 | Container | Distroless / Minimal Base Images | Google / OSS | ลด attack surface ของ container image | แนวปฏิบัติฯ 4.4 | https://github.com/GoogleContainerTools/distroless |
| CN-19 | Registry | Harbor (Secure Container Registry + Content Trust) | CNCF Graduated | Registry ปลอดภัย + Audit Logs + Vulnerability Scanning | Blueprint Stage 5 | https://goharbor.io/ |
| CN-19a | Package Repo | Sonatype Nexus Repository OSS (Maven/npm/PyPI/Docker/Helm) | Sonatype / EPL-1.0 | คลังแพ็กเกจภายใน + Upstream Proxy กัน typosquatting/dependency confusion | Blueprint Stage 5 | https://help.sonatype.com/en/sonatype-nexus-repository.html |
| CN-20 | Vuln DB | OSV / OSV-Scanner, Trivy, Grype | OpenSSF / Aqua / Anchore | สแกนช่องโหว่ container และ dependency | Blueprint Stage 2-3 | https://osv.dev/ |
| CN-21 | OpenSSF | OpenSSF Scorecard / Best Practices Badge | OpenSSF | ประเมินสุขภาพความปลอดภัยของ OSS project | Blueprint Stage 2 | https://scorecard.dev/ |
| CN-22 | Framework | DevSecOps (Shift-Left Security in SDLC) | อุตสาหกรรม | ฝัง Security ทุกขั้นของ SDLC; Roles ในแต่ละ Development Stage | แนวปฏิบัติฯ 4.1 | https://www.cisa.gov/sites/default/files/2024-08/DevSecOps.pdf |
| CN-23 | Framework | Defense in Depth (7 ชั้น) | อุตสาหกรรม | Perimeter, Network, Endpoint, Application, Data + Proactive (IAM/PAM/GRC) + Reactive (SIEM/SOAR/XDR) | แนวปฏิบัติฯ 4.2 | https://csrc.nist.gov/glossary/term/defense_in_depth |
| CN-24 | Framework | CIA Triad / Secure by Design | CISA | Secure by Design & Default principles | แนวปฏิบัติฯ 1.6 | https://www.cisa.gov/securebydesign |
| CN-25 | Licensing | SPDX License List / REUSE Specification | Linux Foundation / FSFE | License Compliance (ห้าม GPL/AGPL ในภาครัฐตาม Blueprint) | Blueprint Stage 2 | https://spdx.org/licenses/ |
| CN-26 | Versioning | Semantic Versioning (SemVer 2.0.0) | semver.org | Version Tagging มาตรฐาน | Blueprint Stage 5 | https://semver.org/ |
| CN-27 | AI/ML | NIST AI Risk Management Framework (AI RMF 1.0) | NIST | Model Bias / Privacy compliance สำหรับโครงการ AI/ML | Blueprint หมวด 5 AI/ML | https://www.nist.gov/itl/ai-risk-management-framework |
| CN-28 | AI/ML | OWASP Top 10 for LLM Applications | OWASP | ความเสี่ยงเฉพาะ LLM/AI application | Blueprint หมวด 5 AI/ML | https://owasp.org/www-project-top-10-for-large-language-model-applications/ |
| CN-29 | Audit | SOC 2 (Trust Services Criteria) | AICPA | Compliance แนะนำสำหรับภาคเอกชนใน Blueprint | Blueprint ตารางประเภทโครงการ | https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2 |

## 04_OWASP_Top10_Mapping

| รหัส | ช่องโหว่ (Vulnerability) | สาเหตุของการเกิดช่องโหว่ | กฎหมาย/มาตรฐานที่เกี่ยวข้อง | แนวทางป้องกันและข้อควรระวัง |
| --- | --- | --- | --- | --- |
| A01 | Broken Access Control (รวม SSRF) | ไม่ตรวจสอบสิทธิฝั่ง server, client-side authorization, ไม่มี role/permission model | ISO 27001 A.9; OWASP ASVS V4; PDPA ม.37 | RBAC/ABAC, ตรวจ authorization ทุก request, deny-by-default, API gateway, network allowlist |
| A02 | Security Misconfiguration | default config, debug mode ใน production, cloud storage public | CIS Benchmarks; ISO 27001 A.12; PCI-DSS Req 2 | Hardening baseline, ปิด service ที่ไม่ใช้, IaC + Policy-as-Code, configuration scanning |
| A03 | Software Supply Chain Failures | dependency ไม่ปลอดภัย, dependency confusion, typosquatting, CI/CD ถูกโจมตี | NIST SP 800-161; ISO 27001 A.15 | SBOM, SCA, private package registry, artifact signing |
| A04 | Cryptographic Failures | TLS เวอร์ชันเก่า, sensitive data plaintext, key management ไม่ดี | ISO 27001 A.10; PCI-DSS Req 3-4; PDPA ม.37 | TLS 1.2+/1.3, AES-256, secret manager, key rotation |
| A05 | Injection | input validation ไม่ดี, query concatenation, ไม่มี output encoding | OWASP ASVS V5; PCI-DSS Req 6.5 | parameterized query, allowlist validation, CSP header, sanitize input/output |
| A06 | Insecure Design | ไม่มี threat modeling, business logic flaw, ไม่มี defense-in-depth | ISO 27001 A.14; OWASP ASVS V1 | Threat Modeling (STRIDE/PASTA), Security Architecture Review, Abuse Case Analysis |
| A07 | Authentication Failures | รหัสผ่านอ่อน, ไม่มี MFA, session management ไม่ปลอดภัย | NIST SP 800-63B; ISO 27001 A.9.4 | บังคับ MFA, password hashing (Argon2/bcrypt), session rotation, rate limiting |
| A08 | Software/Data Integrity Failures | ไม่มี code signing, insecure deserialization, CI/CD ไม่มี integrity check | NIST SSDF (SP 800-218); ISO 27001 A.14.2.7 | code signing, artifact verification, pin dependency version |
| A09 | Logging & Alerting Failures | ไม่มี security logging, ไม่มี SIEM monitoring, incident detection ช้า | ISO 27001 A.12.4; PCI-DSS Req 10 | centralized logging, SIEM monitoring, alert rules สำหรับ security events |
| A10 | Mishandling of Exceptional Conditions | error handling ไม่ปลอดภัย, fail-open logic, stack trace leak | OWASP ASVS V7; ISO 27001 Operational Security | centralized exception handler, fail-safe defaults, sanitize error messages |
| PQ | Post-Quantum Threat & Crypto-Agility | RSA/ECC อาจถูกทำลายโดย Quantum Computing | NIST PQC Program; NIST CSWP 39 Crypto-Agility | ออกแบบ crypto-agility, migration ไป PQC เช่น CRYSTALS-Kyber, hybrid encryption |

## 05_CICD_Stage_Compliance

| Stage | ชื่อขั้นตอน | เครื่องมือหลัก | มาตรฐาน/กฎหมายที่เกี่ยวข้อง | เกณฑ์บังคับ (ภาครัฐ) |
| --- | --- | --- | --- | --- |
| Stage 1 | Source Code Management | Git Push, Webhook Trigger, Branch Protection (2+ approvers), Pipeline Orchestration | พ.ร.บ.ไซเบอร์ฯ (Audit); มาตรฐานขั้นต่ำฯ (Log Mgmt); ISO 27001 A.9 | Audit Log ทุกกิจกรรม, On-premise เท่านั้นสำหรับภาครัฐ |
| Stage 2 | Check & Scan (SAST/Secret/SCA/License/Quality) | SonarQube, Semgrep, GitLeaks, TruffleHog, OWASP Dependency-Check, Trivy, FOSSology | OWASP A01-A05; NIST SSDF; ISO 27001 A.14; PDPA ม.37 | Critical = 0, Block on secret detection, ห้าม GPL/AGPL, Coverage > 80% |
| Stage 3 | Build & Run (Compile, Image, Scan, IaC, Signing) | Kaniko/Buildah, Trivy, Checkov/tfsec, KubeLinter, Cosign, Notary v2 | OWASP A02,A03,A08; NIST SP 800-161; SLSA; CIS Benchmarks | Rootless Build, Scan ทุก Layer, IaC Validation Mandatory, Artifact Signing Mandatory |
| Stage 4 | Test Running (Unit/Integration/DAST/API/Perf) | JUnit/pytest, OWASP ZAP, Burp Suite, RESTler, K6/JMeter | มาตรฐานเว็บไซต์ 2568 (Penetration Testing); มาตรฐานขั้นต่ำฯ (VAPT ระดับสูง); OWASP ASVS | DAST Mandatory on Staging, Auth + RBAC Testing, SLA Testing required |
| Stage 5 | Store & Versioning (Registry/Package/Tag/SBOM/Sign/Audit) | Harbor, Nexus Repository OSS, Zot, Syft, CycloneDX, SPDX, Cosign, ELK/Loki | NTIA SBOM; SPDX ISO 5962; NIST SP 800-161; NIST SSDF PS.3/PW.4; OWASP A03; พ.ร.บ.คอมพิวเตอร์ (Log) | Air-gapped Network, Private Maven/npm proxy, SBOM Mandatory, Verify before Deploy, เก็บ Audit 7+ ปี |
| Stage 6 | Deploy & Operations (Gate/Strategy/Orchestration/Runtime/Monitor) | OPA Gates, Argo Rollouts, Kubernetes, Falco, Prometheus+Grafana | NIST SP 800-207 (Zero Trust); K8s PSS; มาตรฐานคลาวด์ 2567; NIST CSF 2.0 | CISO Approval, Blue-Green, RBAC Strict Mode, Runtime Monitoring Mandatory, 24/7 SOC |

## 06_WASS_WebAppSecurityService

| รหัส | หมวดบริการ | ข้อกำหนด / กิจกรรมที่ต้องทำ | มาตรฐาน/กฎหมายที่รองรับ | หลักฐาน (Evidence) | ความถี่ / SLA |
| --- | --- | --- | --- | --- | --- |
| W-01 | 1. Governance & Scope | จัดทำทะเบียนเว็บ/เว็บแอปพลิเคชันทั้งหมด (Web Asset Inventory) พร้อมเจ้าของระบบและระดับชั้นข้อมูล | มาตรฐานเว็บไซต์ สกมช. 2568 (Website Security Governance); CIS Control 1-2; มาตรฐานขั้นต่ำฯ 2566 (Security Categorization) | ทะเบียนระบบ + ผลจัดชั้น Low/Medium/High | ปีละ 1 ครั้ง / เมื่อมีระบบใหม่ |
| W-02 | 1. Governance & Scope | แต่งตั้งผู้รับผิดชอบเว็บไซต์ + นโยบายความมั่นคงปลอดภัยเว็บ + แผน IR/BCP เฉพาะเว็บ | มาตรฐานเว็บไซต์ 2568; ประมวลแนวทางปฏิบัติฯ 2564; ISO 27001 A.5 | คำสั่งแต่งตั้ง + นโยบาย + IR Plan | ทบทวนปีละครั้ง |
| W-03 | 1. Governance & Scope | Self-Assessment ตามแบบฟอร์ม ค. และส่ง สกมช. | มาตรฐานเว็บไซต์ สกมช. พ.ศ. 2568 (ราชกิจจาฯ 16 ก.ย. 2568) | แบบฟอร์ม ค. ที่กรอกครบ | ปีละ 1 ครั้ง (บังคับ) |
| W-04 | 2. Secure Design | Threat Modeling ระดับแอปพลิเคชัน (STRIDE/PASTA) + Security Architecture Review ก่อนพัฒนา | OWASP A06 Insecure Design; OWASP ASVS V1; ISO 27034; Microsoft SDL | เอกสาร Threat Model + Abuse Cases | ทุกโครงการใหม่ / major change |
| W-05 | 2. Secure Design | กำหนด Security Requirements ใน TOR/SRS อ้างอิงมาตรฐานเว็บไซต์ 2568 + มสพร.11-2566 | มาตรฐานเว็บไซต์ 2568 (ระบุใน TOR); มสพร. 11-2566 | TOR/SRS ที่มีข้อกำหนดความปลอดภัย | ทุกโครงการจัดซื้อ |
| W-06 | 3. Secure Coding | Secure Coding Standard + Peer Code Review + Pre-commit hooks | OWASP Cheat Sheet Series; OWASP Proactive Controls; NIST SSDF PW.4-PW.7 | Coding Standard + บันทึก Code Review | ทุก Pull Request |
| W-07 | 4. SAST | สแกนโค้ดแบบ Static ทุกครั้งที่ commit/PR (SonarQube, Semgrep, CodeQL, Bandit, gosec) | OWASP A01-A05; NIST SSDF PW.7-PW.8; ISO 27034; Blueprint Stage 2 | SAST Report; Gate: Critical = 0 | ทุก build (CI) |
| W-08 | 5. SCA / Dependency | สแกน 3rd-party libraries เทียบ CVE/NVD/OSV + ตรวจ License (OWASP Dependency-Check, Trivy, Grype) | OWASP A03 Supply Chain; NIST SP 800-161; CISA KEV; Blueprint Stage 2 | SCA Report + รายการ CVE/CVSS | ทุก build + รายสัปดาห์ |
| W-09 | 6. Secret Scanning | ตรวจจับ API Key / Password / Token / Private Key ที่หลุดในโค้ด (GitLeaks, TruffleHog, detect-secrets) | OWASP A04; PDPA ม.37 (ป้องกันเข้าถึงโดยมิชอบ); ประกาศ PDPC 2565 ข้อ 4(6) | Secret Scan Report; Gate: Block on detection | ทุก commit + pre-commit |
| W-10 | 7. SBOM | สร้าง SBOM (CycloneDX/SPDX) ทุก release ของเว็บแอปพลิเคชัน | NTIA Minimum Elements; ISO/IEC 5962; EU CRA; Blueprint Stage 5 (Mandatory ภาครัฐ) | ไฟล์ SBOM แนบกับ artifact | ทุก release |
| W-11 | 8. DAST | สแกน Running Application หาช่องโหว่ (OWASP ZAP, Burp Suite Pro, Nuclei, Acunetix) บน Staging | มาตรฐานเว็บไซต์ 2568 (Penetration Testing); OWASP Top 10; Blueprint Stage 4 (Mandatory on Staging) | DAST Report + Remediation Plan | ทุก release + อย่างน้อยไตรมาสละครั้ง |
| W-12 | 9. API Security Testing | ทดสอบ Authentication (JWT/OAuth2/OIDC), Authorization (RBAC/ABAC), Input Validation, Rate Limiting, API Fuzzing | OWASP API Security Top 10 (2023); OpenAPI 3.x; IETF RFC 6749/7519; Blueprint Stage 4 | API Security Test Report | ทุก release ที่มี API เปลี่ยน |
| W-13 | 10. VAPT / Pen Test | Vulnerability Assessment + Penetration Testing โดยผู้ทดสอบอิสระ (ภายนอก) | มาตรฐานขั้นต่ำฯ 2566 ระดับสูง (VAPT); NIST SP 800-115; แนวทางประเมินความเสี่ยง CII สกมช.; DGA แนะนำ VA ทุก 90 วัน | รายงาน VAPT + ใบรับรองแก้ไข | VA ทุก 90 วัน; Pen Test ปีละ 1 ครั้ง หรือก่อน Go-Live |
| W-14 | 11. Config & Hardening | Hardening web server / framework / cloud config; ปิด debug mode; ตรวจ IaC (Checkov, tfsec, KubeLinter) | OWASP A02 Security Misconfiguration; CIS Benchmarks; CIS Docker/Cloud Benchmarks; Blueprint Stage 3 | Hardening Checklist + IaC Scan Report | ทุก deploy + ทบทวนไตรมาส |
| W-15 | 12. TLS & Crypto | บังคับ HTTPS TLS 1.2/1.3, ห้าม self-signed, จัดการอายุใบรับรอง, เข้ารหัสข้อมูลพัก/ส่ง (AES-256) | มาตรฐานเว็บไซต์ 2568; มสพร.11-2566; IETF RFC 8446; PCI DSS Req 3-4; PDPA ม.37 | ผล SSL/TLS Scan (เกรด A) | ทุกไตรมาส + ก่อนใบรับรองหมดอายุ |
| W-16 | 13. Security Headers | ตั้งค่า HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy | OWASP Secure Headers Project; RFC 6797; CSP Level 3; มาตรฐานเว็บไซต์ 2568 | ผลสแกน Security Headers | ทุก deploy |
| W-17 | 14. Authentication & Access | บังคับ MFA สำหรับผู้ดูแลระบบ; password hashing (Argon2/bcrypt); session rotation; Least Privilege; ทบทวนสิทธิ | มาตรฐานเว็บไซต์ 2568 (MFA); NIST SP 800-63B; ประกาศ PDPC 2565 ข้อ 4(6)(ก)(ข); OWASP A07 | นโยบายรหัสผ่าน + บันทึกทบทวนสิทธิ | ทบทวนสิทธิทุก 6 เดือน |
| W-18 | 15. WAF | ติดตั้งและปรับจูน Web Application Firewall (block mode ไม่ใช่แค่ detect) + Anti-DDoS | มาตรฐานเว็บไซต์ 2568 (WAF); มสพร.11-2566; แนวปฏิบัติฯ 4.2 Defense in Depth ชั้น 1 และ 4 | WAF Policy + Blocked Attack Report | ทบทวน rule ทุกเดือน |
| W-19 | 16. Logging & Monitoring | เก็บ Log จราจรและ Security Event ส่งเข้า SIEM; ตั้ง Alert Rule; ป้องกัน Log ถูกแก้ไข | พ.ร.บ.คอมพิวเตอร์ (Log 90 วัน); มาตรฐานขั้นต่ำฯ 2566; OWASP A09; ISO 27001 A.12.4; NIST SP 800-92; ประกาศ PDPC ข้อ 4(6)(ง) Audit Trails | SIEM Dashboard + Alert Rules; ภาครัฐเก็บ Audit 7+ ปี | เฝ้าระวัง 24/7 (SOC) |
| W-20 | 17. Runtime Protection | RASP / Runtime Security Monitoring (Falco, Tetragon) + Container Runtime Security | แนวปฏิบัติฯ 4.4; NIST SP 800-190; Blueprint Stage 6 (Mandatory Real-time ภาครัฐ) | Runtime Alert Log | ต่อเนื่อง |
| W-21 | 18. Patch Management | แก้ไขช่องโหว่ตาม SLA แยกตามความรุนแรง (CVSS/EPSS/KEV) | NIST SP 800-40; CISA KEV; มาตรฐานขั้นต่ำฯ 2566 | ทะเบียนช่องโหว่ + วันปิด | Critical ≤ 7 วัน, High ≤ 30 วัน, Medium ≤ 90 วัน |
| W-22 | 19. Privacy Compliance | Privacy Policy + Cookie Policy + Consent Pop-up; RoPA; DPIA สำหรับระบบความเสี่ยงสูง; ปุ่มใช้สิทธิเจ้าของข้อมูล | PDPA ม.19,23,37,39; ประกาศ PDPC RoPA 2565; มสพร.11-2566; ISO 29134 | Privacy Notice + Consent Log + RoPA | ทบทวนปีละครั้ง |
| W-23 | 20. Data Breach Response | กระบวนการแจ้งเหตุละเมิดข้อมูลส่วนบุคคลภายใน 72 ชม. และรายงานเหตุภัยคุกคามต่อ สกมช. | ประกาศ PDPC หลักเกณฑ์แจ้งเหตุละเมิดฯ 2565; พ.ร.บ.ไซเบอร์ฯ ม.57/58; NIST SP 800-61r2; ISO 27035 | Playbook + แบบฟอร์มแจ้งเหตุ | ซ้อมแผนปีละ 1 ครั้ง |
| W-24 | 21. Accessibility | ตรวจสอบการเข้าถึงเว็บไซต์ระดับ AA (สำหรับเว็บภาครัฐ) | WCAG 2.1/2.2 ระดับ AA; มสพร. 11-2566 | ผลตรวจ Accessibility (axe/WAVE/Lighthouse) | ปีละ 1 ครั้ง |
| W-25 | 22. Third Party / Supply Chain | ประเมินความปลอดภัยผู้ให้บริการ/ผู้พัฒนาภายนอก + DPA กับผู้ประมวลผลข้อมูล + ตรวจ CSP | มาตรฐานขั้นต่ำฯ 2566 ระดับสูง (Third Party Mgmt); ISO 27036; PDPA ม.40; มาตรฐานคลาวด์ 2567; CSA CCM/CAIQ | แบบประเมินคู่ค้า + DPA | ก่อนทำสัญญา + ปีละครั้ง |
| W-26 | 23. Backup & Recovery | สำรองข้อมูลแบบ Immutable + ทดสอบกู้คืน + ป้องกัน Ransomware | มาตรฐานขั้นต่ำฯ 2566 ระดับสูง (Resilience & Recovery); ISO 22301; NIST SP 800-34 | ผลทดสอบ Restore | ทดสอบกู้คืนปีละ 1 ครั้ง |
| W-27 | 24. Awareness | อบรมนักพัฒนาเรื่อง Secure Coding + อบรมผู้ใช้เรื่อง Phishing/Privacy | มาตรฐานเว็บไซต์ 2568 (Awareness); ประกาศ PDPC 2565 ข้อ 4(7); ISO 27001 A.7.2.2 | ทะเบียนอบรม + ผลทดสอบ | ปีละ 1 ครั้งขึ้นไป |
| W-28 | 25. Reporting | ออกรายงานอัตโนมัติ (HTML/PDF/JSON) + Dashboard สถานะช่องโหว่ ส่งผู้บริหาร/ผู้ตรวจสอบ | CICD Proposal (Auto-Reports); มาตรฐานขั้นต่ำฯ (Audit Plan); Blueprint Stage 2-6 | รายงานประจำเดือน/ไตรมาส | รายเดือน + ตามเหตุการณ์ |

## 07_WASS_ประเภทการสแกน

| รหัส | ประเภท | ชื่อเต็ม | สิ่งที่ตรวจพบ / วิธีการ | เป้าหมายที่สแกน | ความถี่ | เครื่องมือ | มาตรฐาน/กฎหมายรองรับ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SC-01 | SAST | Static Application Security Testing | สแกนซอร์สโค้ด/ไบต์โค้ดโดยไม่ต้องรันโปรแกรม หา SQL Injection, XSS, Hardcoded Credentials, Buffer Overflow, Path Traversal | Source Code / Bytecode | ทุก commit + Pull Request (CI) | SonarQube, Semgrep, Checkmarx, Fortify SCA, Veracode, CodeQL, Bandit, gosec, Brakeman, SpotBugs | OWASP A01-A05; NIST SSDF PW.7-8; ISO 27034; Blueprint Stage 2 |
| SC-02 | SCA | Software Composition Analysis | สแกน 3rd-party libraries และ dependencies เทียบฐาน CVE/NVD/OSV/GHSA พร้อมตรวจ transitive dependencies | Manifest files (package.json, pom.xml, requirements.txt, go.mod) | ทุก build + สแกนซ้ำรายวัน/สัปดาห์ | OWASP Dependency-Check, Trivy, Grype, Snyk, Dependency-Track, OSV-Scanner, JFrog Xray, BlackDuck | OWASP A03 Supply Chain; NIST SP 800-161; CISA KEV; EU CRA |
| SC-03 | Secret Scanning | Credential / Secret Detection | ตรวจจับ API Key, Password, Private Key, Token, Connection String ที่หลุดในโค้ดและ Git History | Source Code + Git History + Config files | Pre-commit hook + ทุก push + สแกนย้อนหลังทั้ง repo | GitLeaks, TruffleHog, detect-secrets, git-secrets, ggshield, GitHub Secret Scanning | PDPA ม.37; ประกาศ PDPC 2565 ข้อ 4(6); OWASP A04; CWE-798 |
| SC-04 | DAST | Dynamic Application Security Testing | สแกนแอปที่กำลังรัน ส่ง HTTP Request จริงและวิเคราะห์ Response หา Injection, XSS, Auth Bypass, SSRF, IDOR | Running Application (Staging/UAT) | ทุก release + อย่างน้อยไตรมาสละครั้ง | OWASP ZAP, Burp Suite Pro, Nuclei, Acunetix, Nikto, Rapid7 InsightAppSec, StackHawk, Qualys WAS | มาตรฐานเว็บไซต์ สกมช. 2568; OWASP Top 10; NIST SP 800-115; Blueprint Stage 4 (Mandatory on Staging) |
| SC-05 | IAST | Interactive Application Security Testing | ฝัง Agent ในแอประหว่างทดสอบ วิเคราะห์ code path จริงขณะรัน ให้ False Positive ต่ำกว่า SAST/DAST | Running App + Instrumented Agent | ระหว่างรัน Integration/Functional Test | Contrast Assess, Synopsys Seeker, Checkmarx IAST, HCL AppScan | OWASP ASVS; Blueprint Stage 4 (Optional) |
| SC-06 | API Scanning | API Security Scanning | สแกน REST/GraphQL/gRPC API ตาม OpenAPI Spec ทดสอบ BOLA, Broken Auth, Excessive Data Exposure, Rate Limiting, Mass Assignment | API Endpoints + OpenAPI/Swagger Spec | ทุก release ที่ API เปลี่ยน | OWASP ZAP API Scan, 42Crunch, Schemathesis, RESTler, Postman/Newman, Dredd, Burp API Scanner | OWASP API Security Top 10 (2023); OpenAPI 3.x; RFC 6749/7519; Blueprint Stage 4 |
| SC-07 | Container Scanning | Container Image Vulnerability Scanning | สแกน Docker/OCI Image หาช่องโหว่ใน OS packages และ application layers ทุก layer | Container Image (ทุก layer) | ทุก build + สแกนซ้ำใน Registry รายวัน | Trivy, Grype, Clair, Docker Scout, Aqua, Prisma Cloud, Snyk Container, Harbor built-in | NIST SP 800-190; แนวปฏิบัติฯ 4.4; Blueprint Stage 3 (Scan ทุก Layer) |
| SC-08 | IaC Scanning | Infrastructure as Code Scanning | ตรวจ Terraform, CloudFormation, Kubernetes YAML, Helm หา Security Misconfiguration เช่น Security Group เปิดกว้าง, ไม่มี encryption, privileged container | IaC Files (.tf, .yaml, .json) | ทุก commit ที่แตะ IaC | Checkov, tfsec, KubeLinter, Datree, Conftest/OPA, Kyverno, Snyk IaC, Prisma Cloud IaC | OWASP A02; CIS Benchmarks; K8s Pod Security Standards; Blueprint Stage 3 (Mandatory) |
| SC-09 | Config Scanning | Configuration & Hardening Scan | ตรวจการตั้งค่า Web Server, Framework, Database, Cloud Account เทียบ CIS Benchmark | Server/Cloud/Framework Config | ทุก deploy + ทบทวนรายไตรมาส | CIS-CAT, Lynis, OpenSCAP, ScoutSuite, Prowler, CloudSploit, Wiz, Orca | OWASP A02 Security Misconfiguration; CIS Benchmarks; มาตรฐานคลาวด์ สกมช. 2567 |
| SC-10 | TLS/SSL Scanning | TLS & Certificate Scanning | ตรวจเวอร์ชัน TLS, cipher suite, ความถูกต้อง/อายุใบรับรอง, HSTS, ห้าม self-signed | HTTPS Endpoint | ทุกไตรมาส + แจ้งเตือนก่อนใบรับรองหมดอายุ 30 วัน | SSL Labs (Qualys), testssl.sh, sslyze, nmap ssl-enum-ciphers | มาตรฐานเว็บไซต์ 2568; มสพร.11-2566; RFC 8446; PCI DSS Req 4 |
| SC-11 | Security Headers Scan | HTTP Security Headers Scanning | ตรวจ HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, CORS | HTTP Response Headers | ทุก deploy | securityheaders.com, OWASP ZAP passive scan, Mozilla Observatory, Nuclei templates | OWASP Secure Headers Project; RFC 6797; CSP Level 3; มาตรฐานเว็บไซต์ 2568 |
| SC-12 | Network/Port Scan | Network & Port Vulnerability Scan | สแกนพอร์ตเปิด, บริการที่ไม่จำเป็น, ช่องโหว่ระดับ OS/Network ของ host ที่โฮสต์เว็บ | Host / IP Range | รายเดือน + ทุก 90 วัน (ภาครัฐ) | Nmap, Nessus, OpenVAS/Greenbone, Qualys VMDR, Rapid7 InsightVM | มาตรฐานขั้นต่ำฯ 2566; NIST SP 800-115; DGA แนะนำ VA ทุก 90 วัน |
| SC-13 | Malware/Defacement | Web Malware & Defacement Monitoring | เฝ้าระวังการฝัง malware, webshell, การเปลี่ยนหน้าเว็บโดยไม่ได้รับอนุญาต, SEO spam | Web Content + File System | ต่อเนื่อง (real-time) / รายวัน | ClamAV, YARA rules, Wazuh FIM, Tripwire, Sucuri, Google Safe Browsing API | พ.ร.บ.ไซเบอร์ฯ ม.57/58; มาตรฐานเว็บไซต์ 2568; OWASP A08 Integrity |
| SC-14 | Accessibility Scan | Web Accessibility Scanning | ตรวจการเข้าถึงเว็บระดับ AA สำหรับผู้พิการ (alt text, contrast, keyboard navigation, ARIA) | Rendered Web Pages | ปีละ 1 ครั้ง + ทุก major redesign | axe DevTools, WAVE, Lighthouse CI, Pa11y, IBM Equal Access | WCAG 2.1/2.2 ระดับ AA; มสพร. 11-2566 |
| SC-15 | Privacy/Cookie Scan | Privacy & Cookie Compliance Scanning | ตรวจ cookie ที่ตั้งก่อนได้รับ consent, third-party tracker, การส่งข้อมูลออกนอกประเทศ | Browser Session + Network Traffic | ทุกไตรมาส + เมื่อเพิ่ม 3rd-party script | Cookiebot Scanner, OneTrust, Blacklight (The Markup), Browser DevTools | PDPA ม.19, 24, 28-29; ประกาศ PDPC โอนข้อมูลต่างประเทศ; มสพร.11-2566 (Consent Pop-up) |
| SC-16 | Mobile App Scan | Mobile Application Scanning | สแกนแอป Android/iOS ที่เชื่อมกับเว็บแอป หา hardcoded secret, insecure storage, weak crypto, cert pinning | APK / IPA Binary | ทุก release | MobSF, QARK, Frida, Objection, NowSecure, Appknox | OWASP MASVS / Mobile Top 10 |
| SC-17 | Pen Test | Manual Penetration Testing | ทดสอบเจาะระบบโดยผู้เชี่ยวชาญอิสระ ครอบคลุม Business Logic Flaw ที่เครื่องมืออัตโนมัติหาไม่เจอ | ทั้งระบบ (Black/Grey/White Box) | ปีละ 1 ครั้ง + ก่อน Go-Live + หลัง major change | ทีมผู้ทดสอบที่มีใบรับรอง (OSCP, CREST, GPEN); Burp Suite Pro, Metasploit, Cobalt Strike | มาตรฐานขั้นต่ำฯ 2566 ระดับสูง (VAPT); มาตรฐานเว็บไซต์ 2568; NIST SP 800-115; PTES |
| SC-18 | Attack Surface | External Attack Surface Management (EASM) | ค้นหา asset ที่ลืม/ไม่ได้ลงทะเบียน เช่น subdomain เก่า, staging ที่เปิดสาธารณะ, S3 bucket เปิด | Public Internet Footprint | ต่อเนื่อง / รายเดือน | Amass, Subfinder, Shodan, Censys, SecurityTrails, Detectify, Wiz EASM | มาตรฐานเว็บไซต์ 2568 (Asset Inventory); CIS Control 1 |

## 08_WASS_SeverityGate_SLA

| รหัส | ระดับ | เกณฑ์ | การดำเนินการใน Pipeline | SLA การแก้ไข | ผู้อนุมัติ/รับผิดชอบ | ตัวอย่าง / หมายเหตุ |
| --- | --- | --- | --- | --- | --- | --- |
| G-01 | Critical | CVSS 9.0-10.0 | Block ทันที — ห้าม merge / ห้าม deploy | แก้ไขภายใน 7 วัน | CISO + เจ้าของระบบ | RCE, SQLi ที่ดึงข้อมูลได้, Auth Bypass, Secret หลุด, CVE ใน CISA KEV |
| G-02 | High | CVSS 7.0-8.9 | Block บน Production; อนุญาต Staging พร้อมแผนแก้ | แก้ไขภายใน 30 วัน | หัวหน้าทีม Security | XSS แบบ Stored, IDOR, SSRF, Privilege Escalation, TLS ต่ำกว่า 1.2 |
| G-03 | Medium | CVSS 4.0-6.9 | Warning — บันทึกใน Risk Register | แก้ไขภายใน 90 วัน | เจ้าของระบบ | Missing Security Headers, Verbose Error, Weak Password Policy |
| G-04 | Low | CVSS 0.1-3.9 | Informational — พิจารณาตามความเหมาะสม | แก้ไขภายใน 180 วัน หรือ Accept Risk | เจ้าของระบบ | Version Disclosure, Cookie ไม่มี flag ที่ไม่กระทบ |
| G-05 | KEV | อยู่ใน CISA Known Exploited Vulnerabilities | Block ทันทีทุกกรณี ไม่ว่า CVSS เท่าใด | แก้ไขภายใน 7 วัน (หรือเร็วกว่า) | CISO | ช่องโหว่ที่มีหลักฐานว่าถูกใช้โจมตีจริงแล้ว |
| G-06 | EPSS สูง | EPSS Score > 0.5 (โอกาสถูก exploit สูง) | ยกระดับความสำคัญขึ้น 1 ระดับ | ตามระดับที่ยกแล้ว | หัวหน้าทีม Security | ใช้ประกอบ CVSS เพื่อจัดลำดับความสำคัญตามความเสี่ยงจริง |
| G-07 | Secret หลุด | พบ credential ใน source/history | Block + Revoke key ทันที | ทันที (ภายใน 24 ชม.) | CISO + เจ้าของ key | ต้อง revoke ไม่ใช่แค่ลบ commit; ตรวจสอบว่าถูกใช้ไปแล้วหรือไม่ |
| G-08 | License ต้องห้าม | GPL / AGPL ในโครงการภาครัฐ | Block ตามนโยบาย Blueprint | เปลี่ยน library ก่อนส่งมอบ | Compliance Officer | ตาม Blueprint Stage 2 ภาครัฐ ห้าม GPL/AGPL |
| G-09 | Code Coverage | Test Coverage < 80% | Warning / Block ตามนโยบายโครงการ | ปรับปรุงก่อน release ถัดไป | หัวหน้าทีมพัฒนา | Blueprint ภาครัฐกำหนด Coverage > 80% |
| G-10 | SBOM ขาด | ไม่มี SBOM แนบกับ artifact | Block (ภาครัฐ Mandatory) | สร้าง SBOM ก่อน release | DevOps Engineer | Blueprint Stage 5 ภาครัฐบังคับ SBOM ทุก artifact |
| G-11 | ไม่มีลายเซ็น | Artifact ไม่ได้ Sign / verify ไม่ผ่าน | Block ก่อน Deploy (ภาครัฐ Mandatory) | Sign ใหม่และ verify | DevOps Engineer | Cosign/Notary v2 — Verify before Deploy |
| G-12 | Exception | ขอยกเว้นชั่วคราว (Risk Acceptance) | อนุญาตเฉพาะมีเอกสารอนุมัติ + วันหมดอายุ | ไม่เกิน 90 วัน ต้องทบทวน | CISO อนุมัติเป็นลายลักษณ์อักษร | ต้องบันทึกใน Risk Register พร้อม compensating control |

## 09_WASS_แผนรอบการสแกน

| รอบเวลา | กิจกรรมการสแกน | วิธีดำเนินการ | ผู้รับผิดชอบ | เวลาที่ใช้ | ผลลัพธ์ / หลักฐาน |
| --- | --- | --- | --- | --- | --- |
| ทุก Commit / PR | SAST, Secret Scanning, Lint | อัตโนมัติใน CI | ทีมพัฒนา | < 10 นาที | Pipeline Report |
| ทุก Build | SCA, Container Scan, IaC Scan, SBOM Generation | อัตโนมัติใน CI | DevSecOps | < 20 นาที | Build Report + SBOM |
| ทุก Release / ก่อน Deploy | DAST, API Scan, Security Headers, Quality Gate, Signature Verify | อัตโนมัติ + Manual Approval | DevSecOps + CISO | < 2 ชั่วโมง | Release Security Report |
| รายวัน | Registry Re-scan (image ที่เก็บอยู่), Malware/Defacement Monitor, Threat Intel Feed | อัตโนมัติ (Scheduled) | SOC | ต่อเนื่อง | Daily Alert Digest |
| รายสัปดาห์ | SCA Re-scan (CVE ใหม่), Dependency Update Review, Attack Surface Discovery | กึ่งอัตโนมัติ | DevSecOps | - | Weekly Vulnerability Report |
| รายเดือน | Network/Port Scan, WAF Rule Review, Access Review (privileged), Patch Status | Manual + Tool | Security Engineer | - | Monthly Security Dashboard |
| ทุก 90 วัน (ไตรมาส) | Vulnerability Assessment เต็มรูปแบบ, TLS/Cert Scan, Config/CIS Benchmark Scan, Privacy/Cookie Scan | Manual + Tool | Security Engineer | - | Quarterly VA Report (ตามแนวทาง DGA) |
| ทุก 6 เดือน | User Access Review ทั้งระบบ, Third Party Assessment, Threat Model Review | Manual | Security + เจ้าของระบบ | - | Access Review Report |
| รายปี (บังคับ) | Penetration Testing โดยผู้ทดสอบอิสระ, Self-Assessment แบบฟอร์ม ค. ส่ง สกมช., Accessibility Audit (WCAG AA), ซ้อมแผน IR/BCP, IT Audit | Manual (External) | CISO + External Auditor | - | Pen Test Report, แบบฟอร์ม ค., Audit Report |
| ตามเหตุการณ์ (Ad-hoc) | Emergency Scan เมื่อมี 0-day / CVE ร้ายแรง, Post-Incident Scan, สแกนก่อน Go-Live โครงการใหม่, สแกนหลัง major architecture change | Manual (Trigger) | CISO + SOC | ภายใน 24-72 ชม. | Incident/Emergency Scan Report |
