import os
import re
import time
import logging
import winsound
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# -------- CONFIG --------


URL = "https://faucetearner.org/login.php"

LOG_FILENAME = f"faucetearner_{time.strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILENAME, mode='a', encoding='utf-8')
    ]
)

Email = str(input('entrer votre email:'))
Password = str(input('entrer votre mot de passe:'))
class FaucetEarnerBot:
    def __init__(self, email, password):
        if not email or not password:
            raise ValueError("EMAIL ou PASSWORD non défini dans .env.")
        self.email = email
        self.password = password

        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.claim_count = 0

    def open_site(self):
        logging.info("🔗 Ouverture du site FaucetEarner...")
        self.driver.get(URL)

    def login(self):
        try:
            logging.info("🔐 Connexion...")
            email_input = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
            password_input = self.driver.find_element(By.NAME, "password")
            email_input.send_keys(self.email)
            password_input.send_keys(self.password)
            self.driver.find_element(By.CLASS_NAME, 'reqbtn').click()

            self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'dashboard')]")))
            logging.info("✅ Connexion réussie.")
        except Exception as e:
            logging.error(f"❌ Échec de la connexion: {e}")
            self.driver.quit()
            exit(1)

    def handle_popup(self):
        try:
            logging.info("🧾 Vérification du pop-up de confirmation...")
            ok_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='OK']"))
            )
            ok_button.click()
            logging.info("✅ Pop-up fermé.")
            time.sleep(2)
        except:
            logging.info("ℹ️ Aucun pop-up détecté.")

    def wait_for_timer(self):
        try:
            self.driver.refresh()
            self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "faucet"))).click()
            time.sleep(2)

            countdown = self.driver.find_element(By.ID, "countdown").text
            match = re.search(r'(\d{1,2}):(\d{2})', countdown)

            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                wait_time = (minutes * 60) + seconds
                logging.info(f"⏱️ Attente de {minutes} min {seconds} sec.")
                time.sleep(wait_time + 5)
            else:
                logging.info("✅ Aucun timer détecté.")
        except:
            logging.info("✅ Aucun timer détecté.")

    def claim_faucet(self):
        try:
            logging.info("🖱️ Tentative de claim...")
            claim_button = self.driver.find_element(By.CLASS_NAME, "reqbtn")
            claim_button.click()
            self.handle_popup()
            self.claim_count += 1
            logging.info(f"🎉 Claim #{self.claim_count} effectué.")
            time.sleep(10)
        except Exception as e:
            logging.warning(f"⚠️ Claim échoué : {e}")
            self.play_alert()

    def play_alert(self):
        try:
            winsound.Beep(1000, 800)
        except:
            logging.info("🔔 Beep non supporté sur ce système.")

    def close(self):
        logging.info("🚪 Fermeture du navigateur.")
        self.driver.quit()

    def get_claim_total(self):
        logging.info(f"📊 Claims effectués : {self.claim_count}")

# -------- MAIN --------
if __name__ == "__main__":
    bot = FaucetEarnerBot(Email, Password)
    try:
        bot.open_site()
        bot.login()
        while True:
            bot.wait_for_timer()
            bot.claim_faucet()
            bot.get_claim_total()
    except KeyboardInterrupt:
        logging.info("⛔ Bot arrêté manuellement.")
    finally:
        bot.close()
