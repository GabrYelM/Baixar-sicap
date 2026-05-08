from playwright.sync_api import sync_playwright
import os

def automateDownloadSicap(pStart, pFinal, user, password, stop):
    # Inicia o Playwright
    with sync_playwright() as p:
        # Abre o web Edge e faz o login no site
        # Dica: headless=True esconde o que o bot esta fazendo rodando ele em segundo plano.
        # Caso queira ver basta mudar para False.
        web = p.chromium.launch(headless=True, channel="msedge") 
        page = web.new_page()
        print("----- Acessando o site -----")
        page.goto("https://sicap.prefeitura.sp.gov.br/index.html")

        # O bot procura o campo para preencher com usuário e senha
        page.get_by_placeholder("Usuário").fill(user)
        page.get_by_placeholder("Senha").fill(password)
        
        # Faz os clicks de entrada até chegar na página dos relatórios
        print("----- Acessando a aba de relatorios -----")
        page.get_by_text("Entrar").click()
        page.wait_for_load_state('networkidle')
        page.get_by_text("Selecionar").click()
        page.wait_for_load_state('networkidle')
        page.get_by_title("Módulo de Relatórios").click()
        page.get_by_role("treeitem", name="Módulo de Relatórios Módulo").click()
        page.wait_for_load_state('networkidle')
        page.get_by_text("Relatório Produção Assistencial Prevista X Executada").click()
        page.wait_for_load_state('networkidle')

        # Inicia a seleção das unidades e conta quantas temos para poder fazer o loop
        page.locator('#idUnidadeConsolidadaSelectReport-arrow').click()
        nUnits = page.locator('li[id*="-idUnidadeConsolidadaSelectReport-"]').count()

        print("----- Acessando os relatorios -----")

        # Inicia o loop que seleciona as unidades
        for number in range(1, nUnits-1):
            
            #Função de parada caso o botão de cancelar tenha sido clicado
            if stop.is_set():
                print("\n[!] O robô detectou o cancelamento e está parando em segurança...")
                break

            # Clica na aba de seleção de unidade ignora a 1 pois ja foi clicado antes do for
            if number > 1:
                page.locator('#idUnidadeConsolidadaSelectReport-arrow').click()
            
            # Clica na unidade
            page.locator(f'[id$="-idUnidadeConsolidadaSelectReport-{number}"]').click() #TALVEZ DE ERRO NO FUTURO
            page.wait_for_timeout(500)
            
            # Armazena o nome da unidade para nomear o arquivo no futuro
            unitName = page.locator('#idUnidadeConsolidadaSelectReport-labelText').inner_text()
            Type = page.locator('#idBuscarPorSelectReport-hiddenSelect')
            
            # Verifica a unidade possui servicos
            if Type.get_attribute("aria-disabled") == "true":
                print(f"Unidade {unitName} sem serviço. Pulando para a próxima...\n")
                continue 
            print(f"----- Unidade {unitName} está ativa -----")

            # Inicia a seleção dos serviços e conta quantos tem para poder fazer o loop
            page.locator('#idBuscarPorSelectReport-arrow').click()
            nServices = page.locator('li[id*="-idBuscarPorSelectReport-"]').count()
            print(f"----- A unidade tem {nServices} serviços -----")
            page.wait_for_timeout(500)

            # Inicia o loop que seleciona o servico e faz os downloads
            for n in range(0, nServices):
                
                #Função de parada caso o botão de cancelar tenha sido clicado
                if stop.is_set():
                    print("\n[!] O robô detectou o cancelamento e está parando em segurança...")
                    break
                
                # Clica na aba de seleção de unidade ignora a 1 pois ja foi clicado antes do for
                if n > 0:
                    page.locator('#idBuscarPorSelectReport-arrow').click()

                # Seleciona o servico e armazena o nome dele para nomar o arquivo futuramente
                page.locator(f'[id$="-idBuscarPorSelectReport-{n}"]').click()
                page.wait_for_timeout(500)
                service = page.locator('#idBuscarPorSelectReport-labelText').inner_text()
                arcName = f"{unitName} - {service}"
                arcNameClean = arcName.replace('/', '-').replace(':', '')

                # Preenche as caixas do periodo e clica para mostrar o relatorio
                page.locator('#periodoInicialDatePicker-inner').fill(pStart)
                page.locator('#periodoFinalDatePicker-inner').fill(pFinal)
                page.get_by_text("Visualizar Relatório").click()
                page.wait_for_timeout(1000)

                # Verifica se o site alertou da ausencia de dados para o relatorio
                if (page.get_by_text("Não há dados para os filtros selecionados", exact=False)).is_visible():
                    print(f"Aviso: Serviço '{service}' não possui dados. Pulando...")
                    page.wait_for_timeout(5000)
                    continue
                
                # Inicia a sequencia do download
                with page.expect_download() as info_download:
                    page.locator("#buttonExcel").click()
                    page.wait_for_timeout(500)
                download = info_download.value
                save_path = fr"C:\DATASUS\SICAP\{arcNameClean}.xlsx"
                
                # Cria a pasta para o download caso ela não esteja presente na máquina e faz o download
                os.makedirs(fr"C:\DATASUS\SICAP", exist_ok=True)
                download.save_as(save_path)
                page.wait_for_timeout(500)
                page.get_by_title("Fechar").click()
                page.wait_for_timeout(500)
                
                print(f"Sucesso! Arquivo salvo em: {save_path}")
                   
            print()
            page.wait_for_timeout(1000)
            
        
        if __name__ == "__main__":
            print("Ações concluídas. Aguardando o usuário...")
            input("Pressione ENTER aqui na tela preta (terminal) para encerrar o robô...")

        web.close()