import streamlit as st
import re
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os

def format_cpf(cpf):
    # Remove todos os caracteres não numéricos
    cpf_numerico = re.sub(r'\D', '', cpf)
    return cpf_numerico

def obter_primeiro_nome(nome_completo):
    if not nome_completo:
        return "documento"
    
    # Remove espaços extras e divide
    partes = nome_completo.strip().split()
    
    # Retorna primeiro nome ou "documento" se não houver nomes
    return partes[0].lower() if partes else "documento"

def formatar_nome_arquivo(nome_original, primeiro_nome):
    # Encontra a extensão do arquivo
    nome, extensao = os.path.splitext(nome_original)
    
    # Retorna o novo nome do arquivo
    return f"{nome}_{primeiro_nome}{extensao}"

def add_watermark(input_pdf, name, cpf):
    # Formatar CPF para exibição
    cpf_formatado = format_cpf(cpf)
    cpf_exibicao = f"{cpf_formatado[:3]}.{cpf_formatado[3:6]}.{cpf_formatado[6:9]}-{cpf_formatado[9:]}"

    # Criar marca d'água
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 10)
    can.setFillColorRGB(1, 0, 0)  # Cor vermelha
    can.drawString(0, 10, f" {name} - {cpf_exibicao}")
    can.save()
    packet.seek(0)
    watermark = PdfReader(packet)

    # Adicionar marca d'água ao PDF
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in range(len(reader.pages)):
        page_obj = reader.pages[page]
        page_obj.merge_page(watermark.pages[0])
        writer.add_page(page_obj)

    # Salva em um BytesIO para retorno
    output_packet = BytesIO()
    writer.write(output_packet)
    output_packet.seek(0)
    return output_packet

def encrypt_pdf(input_pdf, password):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Adiciona todas as páginas ao writer
    for page in reader.pages:
        writer.add_page(page)

    # Criptografia com AES de 256 bits e permissões restritas
    writer.encrypt(
        password,
        owner_password=None,
        use_128bit=False
    )

    # Salva em um BytesIO para retorno
    output_packet = BytesIO()
    writer.write(output_packet)
    output_packet.seek(0)
    return output_packet

def main():
    st.set_page_config(
        page_title="Proteção de PDF",
        page_icon="🔒",
        layout="wide"
    )

    st.title("🔒 Proteção de Documentos PDF")
    st.write("Adicione marca d'água e criptografia ao seu PDF")

    # Sidebar de instruções
    st.sidebar.header("📝 Instruções")
    st.sidebar.markdown("""
    1. Faça upload do PDF original
    2. Adicione informações pessoais
    3. Gere PDF protegido
    """)

    # Upload do PDF
    uploaded_file = st.file_uploader(
        "Escolha um arquivo PDF", 
        type=['pdf'], 
        help="Selecione o documento PDF que deseja proteger"
    )

    if uploaded_file is not None:
        # Informações pessoais (obrigatórias)
        st.subheader("👤 Informações Pessoais")
        name = st.text_input("Nome Completo")
        cpf = st.text_input("CPF")

        # Primeiro nome para o arquivo
        primeiro_nome = obter_primeiro_nome(name)

        # Botão de processamento
        if st.button("Proteger PDF"):
            # Validações
            if not name:
                st.error("Nome completo é obrigatório!")
                return
            
            if not cpf:
                st.error("CPF é obrigatório!")
                return

            try:
                # Formata o CPF para a senha
                senha = format_cpf(cpf)

                # Gera nome do arquivo de saída
                nome_arquivo_saida = formatar_nome_arquivo(uploaded_file.name, primeiro_nome)

                # Adiciona marca d'água
                processed_pdf = add_watermark(uploaded_file, name, cpf)

                # Criptografa o PDF
                final_pdf = encrypt_pdf(processed_pdf, senha)

                # Download do PDF
                st.download_button(
                    label="📥 Baixar PDF Protegido",
                    data=final_pdf,
                    file_name=nome_arquivo_saida,
                    mime="application/pdf"
                )

                st.success("PDF protegido com sucesso! 🎉")
                st.warning(f"⚠️ Senha de acesso: {senha}")

            except Exception as e:
                st.error(f"Erro no processamento: {e}")

if __name__ == "__main__":
    main()