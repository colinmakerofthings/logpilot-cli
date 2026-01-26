def tab_indent(text: str) -> str:
    # TODO: Implement tab_indent function
    pass

# Shared utility functions for logpilot

def space_indent(text: str) -> str:
    return '\n'.join(
        '    ' + line if line.strip() else ''
        for line in text.splitlines()
    )
