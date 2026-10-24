from Core.Networking.Server import Server
import json  # meh

# from Utils.Updater import Updater (lazy)


class Main:
    def __init__(self):
        self.crashCount: int = 0
        self.configuration = json.loads(open("config.json", "r").read())
        self.useUpdater = self.configuration.get("UpgradesEnabled", False)
        self.main()
        self.updater: Updater = None

    def main(self):
        if self.useUpdater:
            from Utils.Updater import Updater
            self.updater = Updater()  # Execute deadly weapons

        if self.useUpdater and not self.updater.updateInstalled and self.crashCount >= 2:
            print("No fixes are available for the crashes. Shutting down server...")
            exit()

        try:
            print(r"""
   ________                _         ____                      __
  / ____/ /___ ___________(_)____   / __ )_________ __      __/ /
 / /   / / __ `/ ___/ ___/ / ___/  / __  / ___/ __ `/ | /| / / / 
/ /___/ / /_/ (__  |__  ) / /__   / /_/ / /  / /_/ /| |/ |/ / /  
\____/_/\__,_/____/____/_/\___/  /_____/_/   \__,_/ |__/|__/_/   

            """)

            Server("0.0.0.0", 9339).start()
        except ImportError:
            print("Some modules are missing, please run pip install -r requirements.txt on your terminal to install them.")

        except Exception as e:
            print(f"Encountered exception: {e}") 
            if self.useUpdater:
                self.crashCount += 1

                if self.crashCount >= 2:
                    # TODO: Close all connections so that the server gets a bit faster on fixing stuff
                    req = "yes" in input("The server has crashed 2+ times."
                                         " Would you like to check for updates in case there's a fix? ").lower()
                    if req: self.main()

                updaterRollbackRequest: bool = "yes" in input(
                    f"The Updater has detected that the server is in a crashed state (error: {e}).\n"
                    "Would you like to roll-back the update? ").lower()

                if updaterRollbackRequest:
                    self.updater.performRollback()
                    print("The roll-back has been completed successfully!")
                    self.crashCount = 0
                else:
                    print("Request declined. Restarting server...\n")

                self.main()


if __name__ == '__main__':
    Main()
