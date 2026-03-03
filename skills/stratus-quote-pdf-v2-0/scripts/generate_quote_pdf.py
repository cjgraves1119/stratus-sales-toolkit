#!/usr/bin/env python3
"""Stratus Quote PDF Generator v2.0 - Optimized with FPDF2 for 2x faster generation."""

import os
from fpdf import FPDF

# Pre-define colors as RGB tuples
STRATUS_BLUE = (0, 180, 216)
DARK_GRAY = (51, 51, 51)
LIGHT_GRAY = (204, 204, 204)
TABLE_BG = (245, 245, 245)
ROW_LINE = (238, 238, 238)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(SCRIPT_DIR, '..', 'assets', 'stratus_logo.png')

DEFAULT_TERMS = (
    "This quote consists of an initial pricing consultation for products and services "
    "provided by Stratus. The prices and discounts, if any, shown above shall be honored "
    "by Stratus and are good for purchase through a signed executed invoice. Stratus honors "
    "the original manufacturer's return policy from Cisco Meraki, and requires that Stratus "
    "be notified of any returns 15 days after delivery in order to administrate a timely "
    "return to the manufacturer within the allotted return window. The signer and signer's "
    "organization shall be responsible for any costs or untimely return resulting from their delay."
)


class StratusQuotePDF(FPDF):
    """Custom PDF class with Stratus branding."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header_section(self, quote_data):
        """Draw the header with logo and company address."""
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, x=10, y=10, w=55)
        
        self.set_xy(120, 10)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(80, 4, "548 Market St #69751\nSan Francisco CA, 94104", align='R')
        
        self.set_draw_color(*LIGHT_GRAY)
        self.line(10, 28, 200, 28)
        
    def quote_title_section(self, quote_number):
        """Draw Quote title and number."""
        self.set_xy(10, 32)
        self.set_font('Helvetica', '', 14)
        self.set_text_color(*STRATUS_BLUE)
        self.cell(95, 8, "Quote", ln=0)
        
        self.set_text_color(*DARK_GRAY)
        self.cell(95, 8, str(quote_number), ln=1, align='R')
        
        self.line(10, 42, 200, 42)
        
    def address_section(self, quote_data):
        """Draw Bill To, Ship To, and Info columns."""
        y_start = 48
        col_width = 63
        
        # Bill To
        self.set_xy(10, y_start)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*STRATUS_BLUE)
        self.cell(col_width, 6, "Bill To", ln=1)
        
        self.set_xy(10, y_start + 8)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*DARK_GRAY)
        bill = quote_data.get('bill_to', {})
        bill_text = f"{bill.get('name', '')}\n{bill.get('street', '')}\n{bill.get('city', '')}, {bill.get('state', '')} {bill.get('zip', '')}"
        self.multi_cell(col_width, 5, bill_text)
        
        # Ship To
        self.set_xy(75, y_start)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*STRATUS_BLUE)
        self.cell(col_width, 6, "Ship To", ln=1)
        
        self.set_xy(75, y_start + 8)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*DARK_GRAY)
        ship = quote_data.get('ship_to', {})
        ship_text = f"{ship.get('name', '')}\n{ship.get('street', '')}\n{ship.get('city', '')}, {ship.get('state', '')} {ship.get('zip', '')}"
        self.multi_cell(col_width, 5, ship_text)
        
        # Info table
        info_x = 140
        info_items = [
            ("Stage", quote_data.get('stage', '')),
            ("Valid Till", quote_data.get('valid_till', '')),
            ("Account Rep", quote_data.get('account_rep', '')),
            ("Amount", f"$ {quote_data.get('grand_total', 0):,.2f}")
        ]
        
        for i, (label, value) in enumerate(info_items):
            y_pos = y_start + (i * 7)
            self.set_xy(info_x, y_pos)
            self.set_font('Helvetica', '', 10)
            self.set_text_color(*STRATUS_BLUE)
            self.cell(25, 6, label, ln=0)
            self.set_text_color(*DARK_GRAY)
            self.cell(35, 6, str(value), ln=1)
            
    def subject_section(self, subject):
        """Draw the offer/subject title."""
        self.set_xy(10, 82)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*STRATUS_BLUE)
        self.cell(190, 8, str(subject or ''), ln=1)
        
    def line_items_table(self, line_items):
        """Draw the line items table."""
        cols = [8, 68, 15, 25, 25, 20, 25]
        headers = ['', 'Item & Description', 'Qty', 'List Price', 'Client Price', 'Tax', 'Net Total']
        
        y_start = 92
        self.set_xy(10, y_start)
        
        # Header row
        self.set_fill_color(*TABLE_BG)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*DARK_GRAY)
        
        for i, (header, width) in enumerate(zip(headers, cols)):
            align = 'R' if i >= 3 else ('C' if i == 2 else 'L')
            self.cell(width, 8, header, border=0, ln=0, align=align, fill=True)
        self.ln()
        
        self.set_draw_color(*LIGHT_GRAY)
        self.line(10, self.get_y(), 196, self.get_y())
        
        # Data rows
        self.set_font('Helvetica', '', 9)
        for idx, item in enumerate(line_items or [], 1):
            row_y = self.get_y() + 2
            
            # Row number
            self.set_xy(10, row_y)
            self.cell(cols[0], 6, str(idx), ln=0)
            
            # Item description
            desc_x = 18
            self.set_xy(desc_x, row_y)
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(*DARK_GRAY)
            name = str(item.get('name', ''))[:45]
            self.cell(cols[1], 4, name, ln=1)
            
            self.set_xy(desc_x, row_y + 4)
            self.set_font('Helvetica', '', 8)
            self.cell(cols[1], 4, str(item.get('sku', '')), ln=1)
            
            term = item.get('term')
            if term:
                self.set_xy(desc_x, row_y + 8)
                self.set_font('Helvetica', 'I', 8)
                self.set_text_color(*STRATUS_BLUE)
                self.cell(cols[1], 4, str(term), ln=1)
                row_height = 14
            else:
                row_height = 10
            
            # Numeric columns
            self.set_font('Helvetica', '', 9)
            self.set_text_color(*DARK_GRAY)
            
            num_data = [
                (str(item.get('qty', 0)), 'C'),
                (f"$ {item.get('list_price', 0):,.2f}", 'R'),
                (f"$ {item.get('client_price', 0):,.2f}", 'R'),
                (f"$ {item.get('tax', 0):,.2f}", 'R'),
                (f"$ {item.get('net_total', 0):,.2f}", 'R')
            ]
            
            x_pos = 86
            for (val, align), width in zip(num_data, cols[2:]):
                self.set_xy(x_pos, row_y + 2)
                self.cell(width, 6, val, ln=0, align=align)
                x_pos += width
            
            self.set_y(row_y + row_height)
            
            self.set_draw_color(*ROW_LINE)
            self.line(10, self.get_y(), 196, self.get_y())
            
    def totals_section(self, quote_data):
        """Draw the totals section."""
        y_start = self.get_y() + 8
        x_label = 130
        
        # Sub Total
        self.set_xy(x_label, y_start)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*DARK_GRAY)
        self.cell(40, 6, "Sub Total", ln=0, align='R')
        self.cell(26, 6, f"$ {quote_data.get('sub_total', 0):,.2f}", ln=1, align='R')
        
        # Shipping
        self.set_xy(x_label, y_start + 8)
        self.set_font('Helvetica', '', 10)
        self.cell(40, 6, "Shipping/Handling", ln=0, align='R')
        self.cell(26, 6, "$ 0.00", ln=1, align='R')
        
        # Grand Total
        self.set_xy(x_label, y_start + 18)
        self.set_draw_color(*LIGHT_GRAY)
        self.line(x_label, y_start + 17, 196, y_start + 17)
        
        self.set_fill_color(*TABLE_BG)
        self.set_font('Helvetica', 'B', 11)
        self.cell(40, 8, "Grand Total", ln=0, align='R', fill=True)
        self.cell(26, 8, f"$ {quote_data.get('grand_total', 0):,.2f}", ln=1, align='R', fill=True)
        
    def terms_page(self, terms=None):
        """Add terms and conditions page."""
        self.add_page()
        
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*DARK_GRAY)
        self.cell(190, 10, "Terms & Conditions", ln=1)
        
        self.set_font('Helvetica', '', 9)
        self.multi_cell(190, 5, terms or DEFAULT_TERMS)


def generate_quote_pdf(quote_data: dict, output_path: str) -> str:
    """
    Generate PDF from quote data using optimized FPDF2 approach.
    
    Args:
        quote_data: Dictionary containing quote information (see SKILL.md for structure)
        output_path: Full path where PDF should be saved
        
    Returns:
        The output_path on success
    """
    pdf = StratusQuotePDF()
    pdf.add_page()
    
    pdf.header_section(quote_data)
    pdf.quote_title_section(quote_data.get('quote_number', ''))
    pdf.address_section(quote_data)
    pdf.subject_section(quote_data.get('subject', ''))
    pdf.line_items_table(quote_data.get('line_items', []))
    pdf.totals_section(quote_data)
    pdf.terms_page(quote_data.get('terms'))
    
    pdf.output(output_path)
    return output_path


if __name__ == '__main__':
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Generate Stratus quote PDF (v2.0 - Optimized)')
    parser.add_argument('json_file', help='Path to JSON file with quote data')
    parser.add_argument('-o', '--output', default='quote.pdf', help='Output PDF path')
    args = parser.parse_args()
    
    with open(args.json_file) as f:
        data = json.load(f)
    
    generate_quote_pdf(data, args.output)
    print(f"Generated: {args.output}")
