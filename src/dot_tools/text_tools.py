from dot_tools.misc_tools import DotError


SEP_BAR_MAX_LENGTH = 120
SEP_BAR_DEFAULT_LENGTH = 16
SEP_BAR_DEFAULT_SUBSTRING = "-"


def sep_bar(
    bar_length=SEP_BAR_DEFAULT_LENGTH,
    bar_substring=SEP_BAR_DEFAULT_SUBSTRING,
):
    with DotError.handle_errors("Can't make separator bar with those args"):
        bar_length = max(bar_length, 1)
        bar_string = bar_substring * bar_length
        bar_string = bar_string[:SEP_BAR_MAX_LENGTH]
        return bar_string


def underlined_header(
    message,
    is_footer=False,
    bar_substring=SEP_BAR_DEFAULT_SUBSTRING,
):
    with DotError.handle_errors("Can't make undl. header with those args"):
        bar_length = len(message)
        bar_string = sep_bar(bar_length=bar_length, bar_substring=bar_substring)
        header_message = ""
        if is_footer:
            header_message = bar_string + "\n" + message
        else:
            header_message = message + "\n" + bar_string
        return header_message
