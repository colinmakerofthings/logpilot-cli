import os
from github_copilot_sdk import CopilotClient

class LLMClient:
	def __init__(self):
		self.client = CopilotClient()

	def analyze(self, prompt: str) -> str:
		response = self.client.completions.create(prompt=prompt)
		return response.text
