from random import choice
from AUTOMATIKA.auto import hamster_client
from config import TOKENS
from strings import DELIMITER
import logging
import time
clients = [hamster_client.HamsterClient(**options) for options in TOKENS]

def main():
    while True:
        for client in clients:
            print(DELIMITER)
            client.sync()
            client.claim_daily_cipher()
            client.tap()
            client.buy_upgrades()
            client.check_task()
            client.claim_combo_reward()
            if client.is_taps_boost_available:
                client.boost(hamster_client.BOOST_ENERGY)
            logging.info(client.log_prefix + " ".join(f"{k}: {v} |" for k, v in client.stats.items()))
            print(DELIMITER)
            time.sleep(choice(range(1, 10)))
        time.sleep(60 * 10)

if __name__ == "__main__":
    main()