import os
import zipfile
import xml.sax.saxutils as saxutils
from typing import Dict, Any

class DocxResumeGenerator:
    """Generates standard Office Open XML (.docx) files natively using Python's standard library."""

    def generate_docx(self, resume_data: Dict[str, Any], output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        name = saxutils.escape(resume_data.get("name", "Candidate"))
        headline = saxutils.escape(resume_data.get("headline", "Application Engineer (AI/ML)"))
        contact = saxutils.escape(resume_data.get("contact", "+91-9876543210 | candidate@example.com | linkedin.com/in/candidate | github.com/candidate"))
        summary = saxutils.escape(resume_data.get("summary", ""))

        # Build document XML
        body_xml = f"""
        <w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t>{name}</w:t></w:r></w:p>
        <w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="22"/></w:rPr><w:t>{headline}</w:t></w:r></w:p>
        <w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:sz w:val="18"/></w:rPr><w:t>{contact}</w:t></w:r></w:p>
        <w:p><w:r><w:t></w:t></w:r></w:p>
        <w:p><w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr><w:t>PROFESSIONAL SUMMARY</w:t></w:r></w:p>
        <w:p><w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t>{summary}</w:t></w:r></w:p>
        <w:p><w:r><w:t></w:t></w:r></w:p>
        <w:p><w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr><w:t>EDUCATION</w:t></w:r></w:p>
        <w:p><w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t>B.Tech, Artificial Intelligence and Machine Learning | SRKR Engineering College | CGPA 7.5/10 (2026)</w:t></w:r></w:p>
        <w:p><w:r><w:t></w:t></w:r></w:p>
        <w:p><w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr><w:t>TECHNICAL SKILLS</w:t></w:r></w:p>
        """

        skills = resume_data.get("skills", {})
        if isinstance(skills, dict):
            for cat, items in skills.items():
                cat_clean = saxutils.escape(str(cat).replace("_", " ").title())
                items_clean = saxutils.escape(", ".join(items) if isinstance(items, list) else str(items))
                body_xml += f"""<w:p><w:r><w:rPr><w:b/><w:sz w:val="20"/></w:rPr><w:t>{cat_clean}: </w:t></w:r><w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t>{items_clean}</w:t></w:r></w:p>"""
        elif isinstance(skills, list):
            items_clean = saxutils.escape(", ".join(skills))
            body_xml += f"""<w:p><w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t>{items_clean}</w:t></w:r></w:p>"""

        body_xml += """<w:p><w:r><w:t></w:t></w:r></w:p><w:p><w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr><w:t>RELEVANT PROJECTS</w:t></w:r></w:p>"""

        for proj in resume_data.get("projects", []):
            p_title = saxutils.escape(proj.get("title", ""))
            p_stack = saxutils.escape(", ".join(proj.get("tech_stack", [])))
            p_about = saxutils.escape(proj.get("about", ""))
            body_xml += f"""
            <w:p><w:r><w:rPr><w:b/><w:sz w:val="21"/></w:rPr><w:t>{p_title}</w:t></w:r><w:r><w:rPr><w:sz w:val="18"/><w:color w:val="4A5568"/></w:rPr><w:t> | {p_stack}</w:t></w:r></w:p>
            <w:p><w:r><w:rPr><w:sz w:val="19"/></w:rPr><w:t>• {p_about}</w:t></w:r></w:p>
            """

        full_doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:body>
                {body_xml}
            </w:body>
        </w:document>"""

        content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
            <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
            <Default Extension="xml" ContentType="application/xml"/>
            <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
        </Types>"""

        rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
            <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
        </Relationships>"""

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as docx:
            docx.writestr("[Content_Types].xml", content_types_xml)
            docx.writestr("_rels/.rels", rels_xml)
            docx.writestr("word/document.xml", full_doc_xml)

        return output_path

docx_generator = DocxResumeGenerator()

