import streamlit as st
import re
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os
import zipfile

def format_cpf(cpf):
    cpf_numerico = re.sub(r'\D', '', cpf)
    return cpf_numerico

def obter_primeiro_nome(nome_completo):
    if not nome_completo:
        return "documento"
    partes = nome_completo.strip().split()
    return partes[0].lower() if partes else "documento"

def formatar_nome_arquivo(nome_original, primeiro_nome):
    nome, extensao = os.path.splitext(nome_original)
    return f"{nome}_{primeiro_nome}{extensao}"

def add_watermark(input_pdf, name, cpf):
    cpf_formatado = format_cpf(cpf)
    cpf_exibicao = f"{cpf_formatado[:3]}.{cpf_formatado[3:6]}.{cpf_formatado[6:9]}-{cpf_formatado[9:]}"

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 10)
    can.setFillColorRGB(1, 0, 0)  # Cor vermelha
    can.drawString(0, 10, f" {name} - {cpf_exibicao}")
    can.save()
    packet.seek(0)
    watermark = PdfReader(packet)

    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in range(len(reader.pages)):
        page_obj = reader.pages[page]
        page_obj.merge_page(watermark.pages[0])
        writer.add_page(page_obj)

    output_packet = BytesIO()
    writer.write(output_packet)
    output_packet.seek(0)
    return output_packet

def main():
    st.set_page_config(
        page_title="Adição de Marca D'água em PDFs",
        page_icon="🖋️",
        layout="wide"
    )

    st.title("🖋️ Adição de Marca D'água em PDFs")
    st.write("Adicione uma marca d'água com nome e CPF aos seus PDFs")

    st.sidebar.header("📝 Instruções")
    st.sidebar.markdown("""
    1. Faça upload dos PDFs originais
    2. Adicione informações pessoais
    3. Gere PDFs com marca d'água
    """)

    uploaded_files = st.file_uploader(
        "Escolha os arquivos PDF", 
        type=['pdf'], 
        accept_multiple_files=True,
        help="Selecione os documentos PDF aos quais deseja adicionar a marca d'água"
    )

    if uploaded_files:
        st.subheader("👤 Informações Pessoais")
        name = st.text_input("Nome Completo")
        cpf = st.text_input("CPF")

        primeiro_nome = obter_primeiro_nome(name)

        if st.button("Adicionar Marca D'água"):
            if not name:
                st.error("Nome completo é obrigatório!")
                return
            
            if not cpf:
                st.error("CPF é obrigatório!")
                return

            try:
                processed_pdfs = []
                progress_bar = st.progress(0)

                for i, uploaded_file in enumerate(uploaded_files):
                    nome_arquivo_saida = formatar_nome_arquivo(uploaded_file.name, primeiro_nome)
                    processed_pdf = add_watermark(uploaded_file, name, cpf)
                    processed_pdfs.append((nome_arquivo_saida, processed_pdf))
                    progress_bar.progress((i + 1) / len(uploaded_files))

                st.success("Marca d'água adicionada com sucesso a todos os PDFs! 🎉")

                # Opção para baixar todos os PDFs em um arquivo ZIP
                if len(processed_pdfs) > 1:
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for file_name, file_data in processed_pdfs:
                            zip_file.writestr(file_name, file_data.getvalue())
                    
                    st.download_button(
                        label="📥 Baixar todos os PDFs com marca d'água (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="pdfs_com_marca_dagua.zip",
                        mime="application/zip"
                    )

                # Opção para baixar PDFs individualmente
                st.write("Ou baixe os PDFs individualmente:")
                for file_name, file_data in processed_pdfs:
                    st.download_button(
                        label=f"📥 Baixar {file_name}",
                        data=file_data,
                        file_name=file_name,
                        mime="application/pdf",
                        key=file_name  # Necessário para criar botões únicos
                    )

            except Exception as e:
                st.error(f"Erro no processamento: {e}")

if __name__ == "__main__":
    main()
