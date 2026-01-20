from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time


def abrir_e_colar(codigo_vm):
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)


    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    try:

        url = "https://ewvm.epl.di.uminho.pt/run"

        driver.get(url)


        time.sleep(2)

        text_area = driver.find_element(By.TAG_NAME, "textarea")

        text_area.clear()  
        text_area.send_keys(codigo_vm)  

    except Exception as e:
        print("Erro mas o ficheiro 'programa_final.vm' foi gerado na mesma.")


