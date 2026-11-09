import os
from typing import Dict, Any

class PdfResumeGenerator:
    """Generates standard, ATS-friendly PDF resumes with standard single-column text layout."""

    def generate_pdf(self, resume_data: Dict[str, Any], output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        name = resume_data.get("name", "Candidate")
        headline = resume_data.get("headline", "Application Engineer (AI/ML)")
        contact = resume_data.get("contact", "+91-9876543210 | candidate@example.com")
        summary = resume_data.get("summary", "")

        # Format lines for PDF text stream
        lines = [
            f"BT /F1 16 Tf 50 780 Td ({name}) Tj ET",
            f"BT /F1 11 Tf 50 762 Td ({headline}) Tj ET",
            f"BT /F2 9 Tf 50 748 Td ({contact}) Tj ET",
            "BT /F1 12 Tf 50 725 Td (PROFESSIONAL SUMMARY) Tj ET",
            f"BT /F2 9 Tf 50 710 Td ({summary[:110]}) Tj ET",
            f"BT /F2 9 Tf 50 698 Td ({summary[110:220]}) Tj ET",
            "BT /F1 12 Tf 50 675 Td (EDUCATION) Tj ET",
            "BT /F2 9 Tf 50 660 Td (B.Tech in Artificial Intelligence and Machine Learning | SRKR Engineering College | CGPA 7.5/10 (2026)) Tj ET",
            "BT /F1 12 Tf 50 635 Td (RELEVANT PROJECTS) Tj ET"
        ]

        y = 620
        for proj in resume_data.get("projects", [])[:4]:
            p_title = proj.get("title", "")
            p_stack = ", ".join(proj.get("tech_stack", []))
            lines.append(f"BT /F1 10 Tf 50 {y} Td ({p_title} | {p_stack}) Tj ET")
            lines.append(f"BT /F2 8.5 Tf 60 {y-12} Td ({proj.get('about', '')[:100]}) Tj ET")
            y -= 28

        lines.append(f"BT /F1 12 Tf 50 {y-5} Td (TECHNICAL SKILLS) Tj ET")
        skills = resume_data.get("skills", {})
        if isinstance(skills, dict):
            y_s = y - 20
            for cat, s_list in list(skills.items())[:4]:
                s_txt = f"{cat.title()}: {', '.join(s_list[:6])}"
                lines.append(f"BT /F2 8.5 Tf 50 {y_s} Td ({s_txt[:100]}) Tj ET")
                y_s -= 14

        stream_content = "\n".join(lines).encode("latin-1", errors="replace")
        stream_len = len(stream_content)

        # PDF Structure
        pdf_body = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>
endobj
4 0 obj
<< /Length {stream_len} >>
stream
""".encode("latin-1") + stream_content + f"""
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>
endobj
6 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 7
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000236 00000 n 
0000000000 00000 n 
0000000000 00000 n 
trailer
<< /Size 7 /Root 1 0 R >>
startxref
500
%%EOF
""".encode("latin-1")

        with open(output_path, "wb") as f:
            f.write(pdf_body)

        return output_path

pdf_generator = PdfResumeGenerator()

