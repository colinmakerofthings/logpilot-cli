# Shared utility functions for logpilot

def tab_indent(text: str) -> str:
	return '\n'.join('\t' + line if line.strip() else '' for line in text.splitlines())
