from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from time import sleep, time
import requests
from requests.exceptions import SSLError

def click_button(driver, button_text):
    buttons = driver.find_elements(by=By.TAG_NAME, value="button")
    for b in buttons:
        if button_text in b.text and b.is_displayed:
            b.click()
            return True
    return False

def send_telegram_notification(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(response.json)
    except SSLError as e:
        print(f"SSL error occured: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error occured: {e}")
    finally:
        if response.status_code == 200:
            print("Message envoyé avec succès.")
        else:
            print(f"Erreur lors de l'envoi du message : {response.status_code}")

def check_availability():
    login_email = "goulasquentin@gmail.com"
    login_mdp = "Ascfbrtoilkxc8!@!"

    options = Options()
    options.set_preference("permissions.default.image", 2)
    options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Firefox(options=options)
    driver.get("https://logement.cesal-residentiel.fr/espace-resident/cesal_login.php?so=14175&action=logout")


    driver.implicitly_wait(30)

    sidentifier_button = driver.find_element(by=By.ID, value="button_connexion")
    sidentifier_button.click()

    mail_box = driver.find_element(by=By.ID, value="login-email")
    mdp_box = driver.find_element(by=By.ID, value="login-password")


    mail_box.send_keys(login_email)
    mdp_box.send_keys(login_mdp)

    click_button(driver=driver, button_text="Se connecter")

    sleep(2)
    click_button(driver=driver, button_text="Réserver")
    date_entree_selector = driver.find_element(by=By.ID, value="date_arrivee")
    date_entree_selector.send_keys(date_entree_selector.text[-10:-1])

    date_sortie_selector = driver.find_element(by=By.ID, value="date_sortie")
    date_sortie_selector.send_keys("25/04/2025")

    sleep(2)
    click_button(driver, "Valider")
    sleep(2)

    rez_non_dispo = 0;

    for k in range(1,7):
        disp_text = driver.find_element(by=By.ID, value="residence_" + str(k) + "_logements_disponibles").text
        if disp_text == "Aucun logement disponible":
            rez_non_dispo = rez_non_dispo + 1
        else:
            rez_dispo = rez_dispo + str(k) + ","
    
    driver.quit()

    if rez_non_dispo < 6:
        print("IL Y A UN LOGEMENT DISPONIBLE !, ou une erreur est apparue")
        return(True, rez_dispo)
    elif rez_non_dispo == 6:
        print("Il n'y a pas de logement disponible")
        return (False, str(0))

    


if __name__ == '__main__':
    delay_availability = 20
    delay_programm_status = 20
    time_a = time()
    time_s = time()

    status_counter = 0

    bot_token = '7283120075:AAE8usg0ZiOfIdQRckbStT5gN8IaUyiYGVM'
    # chat_id = '7059050163'
    chat_id = '-4224874172'
    error_chat_id = '7059050163'
    send_telegram_notification(bot_token, error_chat_id, 'bot lancé')
    message_dispo = 'Un appart est dispo !!!! Ou une erreur est apparue dans le programme '
    message_erreur = 'Une erreur est apparue lors de la verif'

    while True:
        sleep(2)
        
        try:
            if time() - time_a > delay_availability:
                time_a = time()
                available, rez_available = check_availability()
                if available:
                    send_telegram_notification(bot_token, chat_id, message_dispo + 'dans la ou les rezs ' + rez_available)
                    send_telegram_notification(bot_token, error_chat_id, message_dispo + 'dans la ou les rezs ' + rez_available)
                    print(message_dispo + 'dans la ou les rezs ' + rez_available)
                else:
                    print('Pas d_appart')
                status_counter = status_counter + 1
        except:
            try:
                send_telegram_notification(bot_token, error_chat_id, message_erreur + " " + str(available) + " " + str(rez_available))
            except:
                send_telegram_notification(bot_token, error_chat_id, message_erreur)
            print(message_erreur)
        if time() - time_s > delay_programm_status:
            time_s = time()
            print(f"status ok, {status_counter} times checked")
            send_telegram_notification(bot_token, error_chat_id, f"status ok, {status_counter} times checked")
            status_counter = 0

