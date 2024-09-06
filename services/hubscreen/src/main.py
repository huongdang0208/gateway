import sys
import threading
import asyncio
sys.path.append('../')  # This adds the parent directory to the path
from gui import InterfaceGraphic

def init_gui():
    InterfaceGraphic()


def main():
    loop = asyncio.get_event_loop()

    t1 = threading.Thread(target=init_gui, args=())

    t1.start()

    t1.join()
    # t2.join()

    print("Done!")

if __name__ == "__main__":
    main()
