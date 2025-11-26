#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from content_ai_agent.crew import ContentAiAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from dotenv import load_dotenv
load_dotenv()

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# def run():
#     """
#     Run the crew.
#     """
#     inputs = {
#         'topic': 'AI LLMs',
#         'current_year': str(datetime.now().year)
#     }

#     try:
#         ContentAiAgent().crew().kickoff(inputs=inputs)
#     except Exception as e:
#         raise Exception(f"An error occurred while running the crew: {e}")


# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         'current_year': str(datetime.now().year)
#     }
#     try:
#         ContentAiAgent().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         ContentAiAgent().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         "current_year": str(datetime.now().year)
#     }

#     try:
#         ContentAiAgent().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while testing the crew: {e}")

# def run_with_trigger():
#     """
#     Run the crew with trigger payload.
#     """
#     import json

#     if len(sys.argv) < 2:
#         raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

#     try:
#         trigger_payload = json.loads(sys.argv[1])
#     except json.JSONDecodeError:
#         raise Exception("Invalid JSON payload provided as argument")

#     inputs = {
#         "crewai_trigger_payload": trigger_payload,
#         "topic": "",
#         "current_year": ""
#     }

#     try:
#         result = ContentAiAgent().crew().kickoff(inputs=inputs)
#         return result
#     except Exception as e:
#         raise Exception(f"An error occurred while running the crew with trigger: {e}")



def run():
    """Auto mode - Agent finds trending topics."""
    inputs = {
        'niche': 'AI automation agency',
        'topic': '',
        'platform': 'YouTube Video'
    }
    result = ContentAiAgent().crew().kickoff(inputs=inputs)
    print(result)


def run_with_topic():
    """Topic mode - User provides specific topic."""
    topic = input("Enter your topic: ")
    platform = input("Enter platform (YouTube Video/YouTube Shorts/TikTok): ")
    
    inputs = {
        'niche': '',
        'topic': topic,
        'platform': platform
    }
    result = ContentAiAgent().crew().kickoff(inputs=inputs)
    print(result)


if __name__ == "__main__":
    print("\n=== Content AI Agent ===")
    print("1. Find with Agent (auto-discover trending topics)")
    print("2. Enter a Topic (search specific topic)")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "2":
        run_with_topic()
    else:
        run()