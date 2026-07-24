import markdown


def markdown_filter(content: str) -> str:
    return markdown.markdown(
        content,
        extensions=[
            "nl2br",
        ],
    )
