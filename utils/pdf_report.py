from fpdf import FPDF
from io import BytesIO

def safe_text(text):
    if text is None:
        return ""
    return (
        str(text)
        .replace("–", "-")
        .replace("—", "-")
        .replace("₹", "Rs.")
        .encode("latin-1", "ignore")
        .decode("latin-1")
    )

def generate_pdf(data: dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    pdf.cell(0, 10, "CargoGuard AI - Shipment Risk Report", ln=True)
    pdf.ln(5)

    for k, v in data.items():
        line = f"{safe_text(k)}: {safe_text(v)}"
        pdf.multi_cell(0, 8, line)

    # 🔑 THIS IS THE IMPORTANT PART
    pdf_bytes = pdf.output(dest="S").encode("latin-1")

    buffer = BytesIO(pdf_bytes)
    return buffer
