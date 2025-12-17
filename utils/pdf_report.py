from fpdf import FPDF

def generate_pdf(data, risk, action, filename="shipment_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "CargoGuard AI – Shipment Risk Report", ln=True)
    pdf.ln(5)

    for k, v in data.items():
        pdf.cell(0, 8, f"{k}: {v}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 8, f"Risk Score: {risk}%", ln=True)
    pdf.cell(0, 8, f"Recommended Action: {action}", ln=True)

    pdf.output(filename)
    return filename
