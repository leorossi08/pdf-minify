import os
import subprocess
from datetime import datetime
from pypdf import PdfReader, PdfWriter

def is_scanned_pdf(file_path):
    """
    Checks if a PDF has extractable text. 
    If it has very little or no text, it is likely a scanned image.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        # Check up to the first 3 pages
        for page in reader.pages[:3]:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        
        # If we found less than 50 characters of text, assume it's scanned
        return len(text.strip()) < 50
    except Exception:
        # If pypdf fails to read it, default to Ghostscript as a fallback
        return True

def compress_with_pypdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    writer.append(reader)
    
    for page in writer.pages:
        page.compress_content_streams() 
        
    with open(output_path, "wb") as f:
        writer.write(f)

def compress_with_gs(input_path, output_path):
    gs_cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook", 
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]
    subprocess.run(gs_cmd, check=True)

def compress_pdfs_smart(input_dir="./to-compress", output_dir="./compressed"):
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Created '{input_dir}'. Add PDFs and run again.")
        return
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    date_str = datetime.now().strftime("%Y-%m-%d")
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in '{input_dir}'.")
        return

    for filename in pdf_files:
        input_path = os.path.join(input_dir, filename)
        name_without_ext = os.path.splitext(filename)[0]
        output_filename = f"{name_without_ext}_{date_str}_compressed.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"Processing: {filename}...")
        
        try:
            if is_scanned_pdf(input_path):
                print("  Detected: Scanned/Image-heavy. Using Ghostscript...")
                compress_with_gs(input_path, output_path)
            else:
                print("  Detected: Text-based. Using pypdf...")
                compress_with_pypdf(input_path, output_path)
                
            orig_size = os.path.getsize(input_path) / 1024
            new_size = os.path.getsize(output_path) / 1024
            
            print(f"  Saved as: {output_filename}")
            print(f"  Size: {orig_size:.1f} KB -> {new_size:.1f} KB\n")
            
        except Exception as e:
            print(f"  Error compressing {filename}: {e}\n")

if __name__ == "__main__":
    compress_pdfs_smart()
