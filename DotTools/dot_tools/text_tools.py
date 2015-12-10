SEP_BAR_MAX_LENGTH=120
SEP_BAR_DEFAULT_LENGTH=16
SEP_BAR_DEFAULT_SUBSTRING='-'

def sep_bar(bar_length=SEP_BAR_DEFAULT_LENGTH, bar_substring=SEP_BAR_DEFAULT_SUBSTRING):
    try:
        bar_length = max(bar_length, 1)
        bar_string = bar_substring * bar_length
        bar_string = bar_string[:SEP_BAR_MAX_LENGTH]
        return bar_string
    except:
        raise ValueError("Can't compose separator bar with those arguments")

def underlined_header(text, is_footer=False, bar_substring=SEP_BAR_DEFAULT_SUBSTRING):
    try:
        bar_length = len(text)
        bar_string = sep_bar(bar_length=bar_length, bar_substring=bar_substring)
        header_text=''
        if (is_footer):
            header_text = bar_string + '\n' + text
        else:
            header_text = text + '\n' + bar_string
        return header_text
    except:
        raise ValueError("Couldn't compose an underlined header with those arguments")

