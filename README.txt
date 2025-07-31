
# Internet Brasil + Computadores para Inclusão – MCom

Este projeto permite extrair automaticamente os dados dos painéis públicos do Ministério das Comunicações via Power BI e Looker Studio.

## Como usar no Replit

1. Acesse https://replit.com e entre com sua conta (ou crie uma gratuita).
2. Clique em "Create Repl" > "Import from Zip" (ícone de upload).
3. Suba este arquivo `.zip`.
4. Espere carregar. Clique em "Run".
5. O script acessará os painéis, fará OCR e salvará os dados em `dados_mcom_unificado.xlsx`.
6. Clique no arquivo gerado para baixar.

## Requisitos (já inclusos via replit.nix)
- Python 3.10
- Selenium
- Pillow
- Pytesseract
- Pandas
- Chromium + Tesseract OCR

