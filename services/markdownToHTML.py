import markdown

def convert_markdown_to_html(markdown_string):
    """
    Converts a markdown string to an HTML string.

    Args:
        markdown_string (str): The markdown content to convert.

    Returns:
        str: The converted HTML content.
    """
    html_string = markdown.markdown(markdown_string)
    return html_string