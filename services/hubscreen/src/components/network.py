import subprocess

def is_connected():
    try:
        # Ping Google's DNS server to check for network connectivity
        output = subprocess.check_output(
            ['ping', '-c', '1', '8.8.8.8'],
            stderr=subprocess.STDOUT,  # Capture standard error
            universal_newlines=True    # Return output as a string
        )
        return True
    except subprocess.CalledProcessError:
        return False
