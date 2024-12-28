from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_text_splitters import HTMLHeaderTextSplitter
from langchain_text_splitters import HTMLSectionSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
from langchain_community.document_loaders import PyPDFLoader




embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
os.environ['HF_TOKEN']="put you hugging face token"

def scrape_url_content(url: str) -> str:
    headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
    ("h4", "Header 4"),]

    html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

# for local file use html_splitter.split_text_from_file(<path_to_file>)
    html_header_splits = html_splitter.split_text_from_url(url)

    chunk_size = 1000
    chunk_overlap = 70
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splits = text_splitter.split_documents(html_header_splits)
    return splits


def extract_pdf_content(pdf_content):
    temp_pdf_path = "temp_uploaded_file.pdf"
    
    # Save the PDF content to a temporary file
    with open(temp_pdf_path, "wb") as temp_pdf:
        temp_pdf.write(pdf_content)
    
    try:
        # Load and split the PDF
        loader = PyPDFLoader(temp_pdf_path)
        docs = loader.load_and_split()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
        final_documents = text_splitter.split_documents(docs)
        return final_documents
    finally:
        # Cleanup the temporary file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

def get_embedding(text):
    from langchain_community.vectorstores import Chroma
    db=Chroma.from_documents(text,embeddings)
    return db