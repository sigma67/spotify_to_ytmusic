import webbrowser


def has_browser() -> bool:
    try:
        webbrowser.get()
        return True

    except webbrowser.Error:
        return False
