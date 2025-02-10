import os
import re
import pdfplumber
import docx
import datetime
import spacy
from collections import Counter
from tkinter import Tk, filedialog

# Load NLP Model
nlp = spacy.load("en_core_web_sm")

# 1. Fungsi untuk membaca teks dari file PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# 2. Fungsi untuk membaca teks dari file Word (.docx)
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

# 3. Fungsi untuk membersihkan teks
def clean_text(text):
    text = re.sub(r"\n+", "\n", text)  # Menghapus spasi berlebih
    text = re.sub(r"\s+", " ", text)   # Menghapus spasi ganda
    return text.strip()

# 4. Fungsi untuk mengekstrak informasi dari teks
def extract_info(text):
    doc = nlp(text)
    title = None
    author = None
    date = None
    
    # Ekstraksi Judul (Menggunakan Kalimat Pertama)
    sentences = list(doc.sents)
    if sentences:
        title = sentences[0].text

    # Ekstraksi Entitas
    entities = {ent.label_: ent.text for ent in doc.ents}
    
    # Mencari Author dan Date
    author = entities.get("PERSON", "Unknown Author")
    date = entities.get("DATE", datetime.datetime.now().strftime("%Y-%m-%d"))

    # Kata kunci penting
    words = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]
    common_words = Counter(words).most_common(5)

    return {
        "Title": title,
        "Author": author,
        "Date": date,
        "Top Keywords": common_words
    }

# 5. Fungsi utama untuk memilih file dan mengekstrak informasi
def main():
    # Buka file dialog untuk memilih dokumen
    Tk().withdraw()
    file_path = filedialog.askopenfilename(title="Pilih Dokumen", filetypes=[("PDF Files", "*.pdf"), ("Word Files", "*.docx")])

    if not file_path:
        print("No file selected.")
        return

    # Tentukan jenis file dan ekstrak teks
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        print("Unsupported file format!")
        return

    # Bersihkan teks
    cleaned_text = clean_text(text)

    # Ekstraksi informasi
    info = extract_info(cleaned_text)

    # Tampilkan hasil
    print("\n=== Extracted Information ===")
    for key, value in info.items():
        print(f"{key}: {value}")

    # Simpan hasil ke file
    output_file = "extracted_info.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for key, value in info.items():
            f.write(f"{key}: {value}\n")
        f.write("\nExtracted Text:\n")
        f.write(cleaned_text)

    print(f"\nExtracted information saved to {output_file}")

# Jalankan program
if __name__ == "__main__":
    main()
