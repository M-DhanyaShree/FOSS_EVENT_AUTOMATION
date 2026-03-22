from fpdf import FPDF
import io
import os
from datetime import datetime
from PIL import Image

class EventReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        pass # We'll handle custom headers per page

    def footer(self):
        # Only add page number if it's not the cover? 
        # Actually sample shows "1" on cover.
        self.set_y(-15)
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'{self.page_no()}', 0, 0, 'R')

def generate_event_pdf(data, drive_handler=None):
    pdf = EventReport()
    
    # --- PAGE 1: COVER ---
    pdf.add_page()
    
    # Logos
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    col_logo = os.path.join(base_dir, 'templates', 'colege_logo.png')
    club_logo = os.path.join(base_dir, 'templates', 'club_logo.jpeg')
    
    if os.path.exists(col_logo):
        pdf.image(col_logo, x=85, y=20, w=40)
    else:
        # Placeholder circle for college
        pdf.set_draw_color(0, 0, 0)
        pdf.ellipse(85, 20, 40, 40)
        pdf.set_xy(85, 45)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(40, 10, "[College Logo]", 0, 0, 'C')

    pdf.set_font('Arial', 'B', 16)
    pdf.set_xy(10, 70)
    pdf.cell(0, 10, "COIMBATORE INSTITUTE OF TECHNOLOGY", 0, 1, 'C')
    pdf.set_font('Arial', 'I', 11)
    pdf.multi_cell(0, 6, "(Government Aided Autonomous Institution Approved by AICTE, New Delhi & Affiliated to Anna University, Chennai)", 0, 'C')
    
    if os.path.exists(club_logo):
        pdf.image(club_logo, x=80, y=100, w=50)
    else:
        # Placeholder for club
        pdf.rect(80, 100, 50, 40)
        pdf.set_xy(80, 120)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(50, 10, "[FOSS-CIT Logo]", 0, 1, 'C')

    pdf.set_font('Arial', 'B', 16)
    pdf.set_y(155)
    pdf.cell(0, 10, "FREE & OPEN SOURCE SOFTWARE CLUB", 0, 1, 'C')
    
    curr_year = datetime.now().year
    year_str = f"{curr_year} - {curr_year+1}"
    pdf.cell(0, 10, f"EVENT REPORT: {year_str}", 0, 1, 'C')
    
    # Secretaries - In a real app we might fetch this from settings, for now static or from data if available
    pdf.set_font('Arial', 'B', 12)
    pdf.set_xy(140, 230)
    pdf.cell(50, 8, "SECRETARIES:", 0, 1, 'R')
    pdf.set_font('Arial', '', 12)
    # Placeholder secretaries
    pdf.set_x(140)
    pdf.cell(50, 8, "Kavin Sanjai S", 0, 1, 'R')
    pdf.set_x(140)
    pdf.cell(50, 8, "Varshini N P", 0, 1, 'R')
    
    # --- PAGE 2: INFO & POSTER ---
    pdf.add_page()
    
    # Event Title
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 15, data['event']['name'].upper(), 0, 1, 'C')
    pdf.ln(5)
    
    # Boxed Info Table
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.5)
    pdf.set_xy(20, 40)
    
    info_x = 25
    info_y = 45
    details = data['details']
    
    # Pre-calculate content to draw the box correctly
    # We'll just use a fixed height or calculate based on lines
    pdf.rect(20, 35, 170, 60) # Main box
    
    pdf.set_font('Arial', 'B', 12)
    labels = ["DATE", "TIME", "MODE", "PARTICIPANTS", "ORGANIZERS"]
    
    # Get date from first flow item or details if exists
    evt_date = str(details.get('time') or 'N/A') # Borrowing time field if it contains date
    if data['flow'] and not evt_date:
        evt_date = data['flow'][0]['date_time'].split('T')[0]
        
    values = [
        evt_date,
        str(details.get('time') or 'N/A'),
        str(data['event'].get('mode') or 'OFFLINE').upper(),
        f"{str(details.get('expected_participants') or '0')}+",
        str(details.get('organizers') or 'FOSS-CIT Volunteer Team')
    ]
    
    for i, (lbl, val) in enumerate(zip(labels, values)):
        pdf.set_xy(info_x, 40 + (i * 10))
        pdf.cell(40, 8, f"{lbl}", 0)
        pdf.cell(5, 8, ":", 0)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(110, 8, f"{val}", 0)
        pdf.set_font('Arial', 'B', 12)
    
    # Poster
    pdf.ln(10)
    poster_item = next((r for r in data['resources'] if r['category'] == 'Poster'), None)
    if poster_item and drive_handler:
        try:
            import tempfile
            img_bytes = drive_handler.download_file(poster_item['drive_file_id'])
            
            # Use PIL to verify and potentially convert
            img_stream = io.BytesIO(img_bytes)
            with Image.open(img_stream) as img:
                # Save to a temporary PNG for FPDF compatibility if necessary
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    img.save(tmp_file.name, format='PNG')
                    tmp_path = tmp_file.name
                
                w, h = img.size
                aspect = h / w

            pdf.image(tmp_path, x=25, y=105, w=160)
            pdf.set_y(105 + (160 * aspect) + 10)
            os.remove(tmp_path)
        except Exception as e:
            pdf.set_y(110)
            pdf.cell(0, 10, f"[Poster Image Load Failed: {str(e)}]", 0, 1, 'C')
    else:
        pdf.set_y(110)
        pdf.rect(25, 110, 160, 80)
        pdf.set_xy(25, 140)
        pdf.cell(160, 10, "[Event Poster Placeholder]", 0, 1, 'C')
        pdf.set_y(200)

    # Event Description Header
    pdf.set_font('Arial', 'BU', 14)
    pdf.cell(0, 10, "EVENT DESCRIPTION:", 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, str(details.get('description') or 'No description provided.'))
    
    # --- PAGE 3: SNAPSHOT ---
    pdf.add_page()
    
    custom_link_name = data.get('custom_link_name')
    custom_link_url = data.get('custom_link_url')
    
    if custom_link_name and custom_link_url:
        pdf.set_font('Arial', '', 11)
        pdf.write(10, f"{str(custom_link_name)} : ")
        pdf.set_text_color(0, 0, 255)
        pdf.set_font('Arial', 'U', 11)
        pdf.write(10, str(custom_link_url), str(custom_link_url))
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 11)
        pdf.ln(15)
    
    # Snapshot Header
    pdf.set_font('Arial', 'BU', 14)
    pdf.cell(0, 10, "EVENT SNAPSHOT:", 0, 1, 'L')
    pdf.ln(5)
    
    # Search for first image resource (Snapshot)
    snapshot_item = next((r for r in data['resources'] if r['category'] == 'Picture'), None)
    if snapshot_item and drive_handler:
        try:
            import tempfile
            img_bytes = drive_handler.download_file(snapshot_item['drive_file_id'])
            # Use PIL to verify and potentially convert
            img_stream = io.BytesIO(img_bytes)
            with Image.open(img_stream) as img:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    img.save(tmp_file.name, format='PNG')
                    tmp_path = tmp_file.name
                
                pdf.image(tmp_path, x=20, y=pdf.get_y(), w=170)
                os.remove(tmp_path)
        except Exception as e:
            pdf.cell(0, 10, f"[Snapshot Image Load Failed: {str(e)}]", 0, 1, 'C')
    else:
        pdf.rect(20, pdf.get_y(), 170, 100)
        pdf.set_y(pdf.get_y() + 45)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(170, 10, "[Event Snapshot Placeholder]", 0, 1, 'C')
        
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
        tmp_pdf_path = tmp_pdf.name
    
    pdf.output(tmp_pdf_path)
    
    with open(tmp_pdf_path, 'rb') as f:
        content = f.read()
    
    os.remove(tmp_pdf_path)
    return content
