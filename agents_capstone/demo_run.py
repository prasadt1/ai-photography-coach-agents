from agents_capstone.agents.orchestrator import Orchestrator
from agents_capstone.agents.vision_agent import VisionAgent
from agents_capstone.agents.knowledge_agent import KnowledgeAgent

def main():
    orch = Orchestrator(VisionAgent(), KnowledgeAgent())

    result = orch.run(
        user_id="demo_user",
        image_path="agents_capstone/assets/image.jpg",  # adjust path
        query="How can I improve the composition of this landscape photo?"
    )

    print("=== Vision Analysis ===")
    print(result["vision"])

    print("\n=== Coaching Text ===")
    print(result["coach"]["text"])

    print("\n=== Suggested Exercise ===")
    print(result["coach"]["exercise"])

    print("\n=== Principles Used ===")
    for p in result["coach"]["principles"]:
        print("-", p["topic"], ":", p["text"])

if __name__ == "__main__":
    main()
