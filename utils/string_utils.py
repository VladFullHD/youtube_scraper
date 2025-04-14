

def extract_channel_name(text):
    at_position = text.find('@')
    if at_position != -1:
        channel_name = text[at_position + 1:]
        channel_name = channel_name.strip()
        return channel_name
    else:
        return None