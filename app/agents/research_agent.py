class ResearchAgent:
    def __init__(slef):
        pass

    async def run(self, prompt:str) -> str:
        return {
            "answer": f"Research result for: {prompt}",
            "citations": [
                "https://example.com/source1",
                "https://example.com/source2"
            ],
            "confidence": 0.82
        }
