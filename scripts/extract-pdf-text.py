#!/usr/bin/env python3
"""
AFCA PDF Text Extraction Script
Extracts text from research PDFs for water data processing
"""

import os
import sys
import subprocess
from pathlib import Path

def get_working_directory():
    """Return the working directory for local storage"""
    return "."

def check_pdftotext():
    """Check if pdftotext is available"""
    try:
        result = subprocess.run(['pdftotext', '-h'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_pdftotext():
    """Install pdftotext using pip"""
    try:
        print("Installing pdftotext...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pdftotext'], check=True)
        return True
    except subprocess.CalledProcessError:
        print("Failed to install pdftotext via pip")
        return False

def extract_pdf_text_pdftotext(pdf_path, output_path):
    """Extract text using pdftotext command"""
    try:
        subprocess.run(['pdftotext', pdf_path, output_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting text with pdftotext: {e}")
        return False

def extract_pdf_text_python(pdf_path, output_path):
    """Extract text using Python libraries"""
    try:
        # Try PyPDF2 first
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(text)
                return True
        except ImportError:
            pass
        
        # Try pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(text)
                return True
        except ImportError:
            pass
        
        # Try pymupdf (fitz)
        try:
            import fitz
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(text)
            return True
        except ImportError:
            pass
        
        print("No PDF extraction libraries available")
        return False
        
    except Exception as e:
        print(f"Error extracting text with Python libraries: {e}")
        return False

def extract_all_pdfs():
    """Extract text from all PDFs in the pdf-source-materials directory"""
    base_dir = get_working_directory()
    pdf_dir = f"{base_dir}/pdf-source-materials"
    
    if not os.path.exists(pdf_dir):
        print(f"PDF directory not found: {pdf_dir}")
        return
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in pdf-source-materials directory")
        print("\nTo add PDFs:")
        print("1. Download research papers from academic sources")
        print("2. Save them to pdf-source-materials/ directory")
        print("3. Run this script again")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Check for pdftotext availability
    has_pdftotext = check_pdftotext()
    
    if not has_pdftotext:
        print("pdftotext not found. Installing Python PDF libraries...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyPDF2', 'pdfplumber', 'pymupdf'], check=True)
            print("PDF libraries installed successfully")
        except subprocess.CalledProcessError:
            print("Failed to install PDF libraries")
            return
    
    success_count = 0
    
    for pdf_file in pdf_files:
        pdf_path = f"{pdf_dir}/{pdf_file}"
        text_file = pdf_file.replace('.pdf', '.txt')
        output_path = f"{pdf_dir}/{text_file}"
        
        print(f"Processing: {pdf_file}")
        
        # Skip if text file already exists
        if os.path.exists(output_path):
            print(f"  Text file already exists: {text_file}")
            success_count += 1
            continue
        
        # Try pdftotext first, then Python libraries
        success = False
        
        if has_pdftotext:
            success = extract_pdf_text_pdftotext(pdf_path, output_path)
        
        if not success:
            success = extract_pdf_text_python(pdf_path, output_path)
        
        if success:
            print(f"  Successfully extracted text to: {text_file}")
            success_count += 1
        else:
            print(f"  Failed to extract text from: {pdf_file}")
    
    print(f"\nText extraction complete: {success_count}/{len(pdf_files)} files processed")
    
    if success_count > 0:
        print("\nNext steps:")
        print("1. Review extracted text files")
        print("2. Run process-water-data.py to extract water data")
        print("3. Validate extracted data quality")

def create_sample_pdf_text():
    """Create sample text file for testing"""
    base_dir = get_working_directory()
    pdf_dir = f"{base_dir}/pdf-source-materials"
    
    sample_text = """Alaska Salmon Stream Temperature and Flow Analysis

Abstract
This study examines water temperature and flow patterns in Alaska salmon streams during the 2023 spawning season. Data was collected from multiple monitoring stations including the Kenai River, Russian River, and Moose River systems.

Methods
Water temperature was measured using calibrated sensors at 15-minute intervals. Stream flow was monitored using USGS stream gauges. Data collection occurred from June 1 to September 30, 2023.

Results
Kenai River
The Kenai River showed average water temperatures of 12.5°C during the study period. Peak temperatures reached 18.2°C in mid-July. Stream flow averaged 850 ft³/s with peak flows of 1,200 ft³/s during spring runoff.

Russian River
The Russian River exhibited cooler temperatures with an average of 11.8°C. Maximum temperature was 16.5°C. Flow patterns showed average discharge of 180 ft³/s with seasonal variations.

Moose River
Moose River temperatures averaged 13.1°C with peak values of 17.8°C. Stream flow averaged 520 ft³/s with maximum flows of 800 ft³/s.

Discussion
Water temperature patterns correlated strongly with salmon spawning success. Optimal temperatures for salmon were observed between 10-15°C. Flow rates above 100 ft³/s provided adequate spawning habitat.

Conclusion
Monitoring of water temperature and flow is essential for salmon conservation in Alaska streams. The data presented here provides baseline information for future management decisions.

References
USGS Stream Gauge Network. 2023. Real-time water data for Alaska.
ADF&G. 2023. Salmon monitoring program annual report.
"""
    
    sample_file = f"{pdf_dir}/sample-research-paper.txt"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    print(f"Created sample text file: {sample_file}")
    print("This file can be used to test the water data extraction process")

def main():
    """Main extraction function"""
    print("AFCA PDF Text Extraction Script")
    print("================================")
    
    base_dir = get_working_directory()
    pdf_dir = f"{base_dir}/pdf-source-materials"
    
    # Create directory if it doesn't exist
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Check if any PDFs exist
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        if not pdf_files:
            print("No PDF files found. Creating sample text file for testing...")
            create_sample_pdf_text()
        else:
            extract_all_pdfs()
    else:
        print("PDF directory not found. Creating sample text file for testing...")
        create_sample_pdf_text()

if __name__ == "__main__":
    main()
