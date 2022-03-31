import secrets


def token(name: str):
    return name + "_" + secrets.token_hex(4)


"""Settings for app.run_server()"""
host = "127.0.0.1"  # os.getenv("HOST", "127.0.0.1"),
port = 9001  # os.getenv("PORT", "8050"),
proxy = None  # os.getenv("DASH_PROXY", None),
debug = True  # False,
dev_tools_ui = None  # None,
dev_tools_props_check = None  # None,
dev_tools_serve_dev_bundles = None  # None,
dev_tools_hot_reload = None  # None,
dev_tools_hot_reload_interval = None  # None,
dev_tools_hot_reload_watch_interval = None  # None,
dev_tools_hot_reload_max_retry = None  # None,
dev_tools_silence_routes_logging = None  # None,
dev_tools_prune_errors = None  # None,

"""Vanilla Callback ID's"""
ascii_to_morse_text_area_id_output = token("ascii_to_morse_text_area_id_output")
ascii_to_morse_text_area_id = token("ascii_to_morse_text_area_id")
morse_to_ascii_text_area_id_output = token("morse_to_ascii_text_area_id_output")
morse_to_ascii_text_area_id = token("morse_to_ascii_text_area_id")
