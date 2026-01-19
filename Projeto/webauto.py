from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time


def abrir_e_colar(codigo_vm):
    print("-" * 30)
    print("[AUTO] A iniciar o Chrome controlado...")

    # Configurações para manter o browser aberto no fim
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)

    # Iniciar o Browser
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    try:
        # 1. Abrir o site
        url = "https://ewvm.epl.di.uminho.pt/run"
        print(f"[AUTO] A carregar {url}...")
        driver.get(url)

        # 2. Esperar que o site carregue
        time.sleep(2)

        # 3. Encontrar a caixa de texto e escrever
        # O site tem uma <textarea>, vamos encontrá-la e escrever nela
        text_area = driver.find_element(By.TAG_NAME, "textarea")

        text_area.clear()  
        text_area.send_keys(codigo_vm)  

    except Exception as e:
        print(f"[ERRO] Falha na automação: {e}")
        print("Mas o ficheiro 'programa_final.vm' foi gerado na mesma.")

    print("-" * 30)
