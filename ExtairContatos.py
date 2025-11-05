from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import time
import sys


def aguardar_usuario():
    while True:
        resposta = input("\nPressione 'y' para iniciar a extração: ").strip().lower()
        if resposta == "y":
            return True


def extrair_quantidade_contatos(page):
    try:
        selector = ".c-PJLV.c-PJLV-emhveM-theme-ONVIO.c-PJLV-iPJLV-css"
        elemento = page.locator(selector).first
        texto = elemento.inner_text()
        quantidade = int(texto.split("/")[0])
        print(f"Quantidade de contatos encontrados: {quantidade}")
        return quantidade
    except Exception as e:
        print(f"Erro ao extrair quantidade de contatos: {e}")
        return 0


def scrolar_para_elemento(page, index):
    try:
        xpath = f'//*[@id="page-content"]/div/div[4]/form/div[4]/div/div[{index}]'
        elemento = page.locator(f"xpath={xpath}")
        elemento.scroll_into_view_if_needed()
        time.sleep(0.3)
    except Exception as e:
        print(f"Aviso ao scrolar para índice {index}: {e}")


def extrair_contatos(page, quantidade_total):
    contatos = []
    batch_size = 5

    print(f"\nIniciando extração de {quantidade_total} contatos...")

    for i in range(1, quantidade_total + 1):
        try:
            xpathNum = f'//*[@id="page-content"]/div/div[4]/form/div[4]/div/div[{i}]/div[3]/div/div/span'
            xpathNome = f'//*[@id="page-content"]/div/div[4]/form/div[4]/div/div[{i}]/div[3]/div/div/div[1]/div/span'
            if i % batch_size == 0 or i == 1:
                scrolar_para_elemento(page, i)
                print(
                    f"Processando contatos {i - batch_size + 1 if i > 1 else 1} a {i}..."
                )

            elemento = page.locator(f"xpath={xpathNum}")
            elementoNome = page.locator(f"xpath={xpathNome}")

            elemento.wait_for(state="visible", timeout=5000)

            numero = elemento.inner_text()
            nome = elementoNome.inner_text()
            contatos.append({"indice": i, "telefone": numero, "nome": nome})

        except Exception as e:
            print(f"Erro ao extrair contato {i}: {e}")
            contatos.append({"indice": i, "telefone": "ERRO NA EXTRAÇÃO"})

    print(f"\nExtração concluída! Total de contatos capturados: {len(contatos)}")
    return contatos


def salvar_planilha(contatos):
    if not contatos:
        print("Nenhum contato para salvar.")
        return None

    df = pd.DataFrame(contatos)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"contatos_{timestamp}.xlsx"

    df.to_excel(nome_arquivo, index=False)
    print(f"\n✓ Planilha salva com sucesso: {nome_arquivo}")
    return nome_arquivo


def perguntar_continuar():
    while True:
        resposta = input("\nDeseja fazer o processo novamente? (s/n): ").strip().lower()
        if resposta in ["s", "n"]:
            return resposta == "s"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("about:blank")

        continuar = True

        while continuar:
            if not aguardar_usuario():
                break

            print("\nIniciando extração...")

            try:
                quantidade = extrair_quantidade_contatos(page)

                if quantidade == 0:
                    print(
                        "Nenhum contato encontrado. Verifique se está na página correta."
                    )
                    continuar = perguntar_continuar()
                    continue
                contatos = extrair_contatos(page, quantidade)
                salvar_planilha(contatos)
                continuar = perguntar_continuar()

            except Exception as e:
                print(f"\nErro durante a execução: {e}")
                continuar = perguntar_continuar()

        print("\nEncerrando aplicação...")
        browser.close()


if __name__ == "__main__":
    main()
