# main.py
from runtime.run import Runtime


def main():
    question = input("Question: ").strip()
    if not question:
        print("No question provided.")
        return

    runtime = Runtime()
    answer = runtime.run(question, k=4)

    print("\n--- ANSWER ---\n")
    print(answer)


if __name__ == "__main__":
    main()
