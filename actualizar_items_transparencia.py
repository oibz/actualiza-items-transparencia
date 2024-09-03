from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

# Inicializa el navegador
option = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=option)

try:
    # Abrir el sitio web
    driver.get("https://www.portaltransparencia.cl/PortalPdT/web/guest/home?p_p_id=58&p_p_lifecycle=0&p_p_state=maximized&p_p_mode=view&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin")

    # Iniciar sesión
    username = driver.find_element(By.ID, "_58_login")
    password = driver.find_element(By.ID, "_58_password")
    username.send_keys("Usuario")
    password.send_keys("Contraseña")
    driver.find_element(By.NAME, "_58_fm").submit()

    # Esperar a que cargue la página de los items
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "A2248:panel-vistas:infoTable_data")))

    while True:
        try:
            # Recolecta los items de la tabla nuevamente
            items = driver.find_elements(By.CSS_SELECTOR, "tbody#A2248\\:panel-vistas\\:infoTable_data tr")

            # Itera sobre cada item
            for item in items:
                try:
                    estado = item.find_element(By.CSS_SELECTOR, "td:nth-child(6) img").get_attribute("alt")

                    if "Desactualizada" in estado:
                        editar_button = item.find_element(By.CSS_SELECTOR, "td:nth-child(8) a")
                        editar_button.click()

                        # Selecciona la opción "Nada a informar"
                        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "A2248:panel-vistas:tabla-elementos:0:j_idt10441")))
                        driver.find_element(By.ID, "A2248:panel-vistas:tabla-elementos:0:j_idt10441").click()

                        # Valida la actualización
                        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "A2248:panel-vistas:tabla-elementos:1:j_idt10445")))
                        driver.find_element(By.ID, "A2248:panel-vistas:tabla-elementos:1:j_idt10445").click()

                        # Se vuelve al Escritorio
                        element = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, '//a[@title="Volver al escritorio"]'))
                        )

                        actions = ActionChains(driver)
                        actions.move_to_element(element).perform()

                        # Regresa al escritorio y refresca para actualizar la tabla
                        driver.execute_script("arguments[0].click();", element)
                        WebDriverWait(driver, 20).until(EC.staleness_of(element))
                        driver.refresh()

                        # Rompe el ciclo para re-evaluar la lista de elementos actualizada
                        break

                except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                    print(f"Error encontrado: {e}")
                    driver.save_screenshot("error_screenshot.png")  # Captura la página en caso de error
                    driver.refresh()
                    break  # Rompe el ciclo para re-evaluar la lista de elementos

            else:
                # Si se completa el ciclo sin encontrar más elementos "Desactualizada", sale del while
                break

        except StaleElementReferenceException:
            print("La página se ha actualizado, reintentando...")
            continue  # Reintenta si no pilla la referencia

finally:
    # Cierra el navegador
    driver.quit()