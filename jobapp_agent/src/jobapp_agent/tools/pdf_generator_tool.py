from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO


class PDFGeneratorToolInput(BaseModel):
    cv_text: str = Field(..., description="The CV content text to convert to PDF")
    filename: str = Field(default="cv", description="Base filename for the PDF")


class PDFGeneratorTool(BaseTool):
    name: str = "pdf_generator_tool"
    description: str = (
        "Converts CV text content into a professional PDF document. "
        "Takes CV text content and generates a properly formatted PDF with appropriate styling, "
        "headers, and layout suitable for professional CVs."
    )
    args_schema: Type[BaseModel] = PDFGeneratorToolInput

    def _run(self, cv_text: str, filename: str = "cv") -> bytes:
        """Convert CV text to PDF and return PDF bytes"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=letter, 
                topMargin=0.75*inch, 
                bottomMargin=0.75*inch,
                leftMargin=0.75*inch,
                rightMargin=0.75*inch
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'CVTitle',
                parent=styles['Title'],
                fontSize=18,
                spaceAfter=12,
                alignment=1,  # Center alignment
                textColor='#333333'
            )
            
            heading_style = ParagraphStyle(
                'CVHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=8,
                spaceBefore=12,
                textColor='#444444',
                borderWidth=1,
                borderColor='#CCCCCC',
                borderPadding=4
            )
            
            normal_style = ParagraphStyle(
                'CVNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                leading=14,
                textColor='#222222'
            )
            
            bullet_style = ParagraphStyle(
                'CVBullet',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=4,
                leading=12,
                leftIndent=20,
                bulletIndent=10,
                textColor='#333333'
            )
            
            # Build PDF content
            story = []
            
            # Process the CV text
            lines = cv_text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Identify different sections
                if self._is_name_title(line, i):
                    story.append(Paragraph(line, title_style))
                    story.append(Spacer(1, 6))
                elif self._is_section_header(line):
                    story.append(Spacer(1, 8))
                    story.append(Paragraph(line.upper(), heading_style))
                    story.append(Spacer(1, 4))
                elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    # Bullet point
                    clean_line = line[1:].strip()
                    story.append(Paragraph(f"• {clean_line}", bullet_style))
                else:
                    # Regular paragraph
                    story.append(Paragraph(line, normal_style))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            raise Exception(f"Failed to generate PDF: {str(e)}")
    
    def _is_name_title(self, line: str, line_index: int) -> bool:
        """Check if this line is likely the person's name (usually first few lines)"""
        if line_index > 3:
            return False
        
        # Name is usually short, doesn't contain common CV keywords
        cv_keywords = ['email', 'phone', 'address', 'experience', 'education', 'skills', '@', 'www', 'http']
        line_lower = line.lower()
        
        # If it contains CV keywords, it's not a name
        if any(keyword in line_lower for keyword in cv_keywords):
            return False
            
        # If it's reasonably short and not all caps (unless it's very short)
        if len(line) < 50 and (not line.isupper() or len(line) < 20):
            return True
            
        return False
    
    def _is_section_header(self, line: str) -> bool:
        """Check if this line is a section header"""
        line_clean = line.strip()
        
        # Common CV section headers
        headers = [
            'experience', 'work experience', 'professional experience', 'employment',
            'education', 'academic background', 'qualifications',
            'skills', 'technical skills', 'core competencies', 'expertise',
            'projects', 'key projects', 'notable projects',
            'certifications', 'certificates', 'awards',
            'summary', 'profile', 'objective', 'about',
            'contact', 'contact information', 'personal details',
            'languages', 'publications', 'references'
        ]
        
        line_lower = line_clean.lower()
        
        # Check if it matches common headers
        if any(header in line_lower for header in headers):
            return True
            
        # Check if it's short, all caps, or ends with colon
        if (len(line_clean) < 30 and 
            (line_clean.isupper() or 
             line_clean.endswith(':') or 
             line_clean.replace(' ', '').isupper())):
            return True
            
        return False