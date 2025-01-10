from keylogger import Keylogger


def main() -> None:
    """
    Main function to start the keylogger GUI.

    :return: None
    """

    keylogger = Keylogger()
    keylogger.create_gui()


if __name__ == "__main__":
    main()
