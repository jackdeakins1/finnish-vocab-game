import random
import os
from collections import deque


def load_words(filename):
    word_list = []
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return []

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if ';' in line:
                parts = line.strip().split(';')
                if len(parts) >= 2:
                    # Storing as tuple to be hashable/comparable easily
                    word_list.append({'en': parts[0].strip(), 'fi': parts[1].strip()})
    return word_list


def print_stats(stats):
    print("\n--- Error Stats ---")
    if not stats:
        print("No errors yet!")
    else:
        # Sort by most errors
        sorted_stats = sorted(stats.items(), key=lambda item: item[1], reverse=True)
        for word, count in sorted_stats:
            print(f"'{word}': {count} wrong answers")
    print("-------------------\n")


def play_game():
    vocab = load_words("words")
    if not vocab:
        return

    print("Select Mode:")
    print("1: English -> Finnish")
    print("2: Finnish -> English")

    mode = input("Choice (1 or 2): ").strip()
    if mode not in ['1', '2']:
        print("Invalid selection.")
        return

    print("\n--- Game Started ---")
    print("Type 'stop' to quit, 'stats' to see error counts.")

    # Queue to track the last 5 words to avoid repetition
    # maxlen automatically discards old items when full
    recent_words = deque(maxlen=5)

    # Dictionary to track errors: {'EnglishWord': count}
    error_stats = {}

    while True:
        # Selection Logic: Pick a word that isn't in the recent buffer
        # Only apply filter if vocab is large enough (> 5) to prevent infinite loops
        available_pool = vocab
        if len(vocab) > 5:
            available_pool = [w for w in vocab if w['en'] not in recent_words]

        pair = random.choice(available_pool)

        # Add current word (unique ID is the English version) to buffer
        recent_words.append(pair['en'])

        if mode == '1':
            question = pair['en']
            correct_answer = pair['fi']
        else:
            question = pair['fi']
            correct_answer = pair['en']

        word_solved = False
        while not word_solved:
            user_input = input(f"Translate '{question}': ").strip().lower()

            if user_input == "stop":
                print("Game stopped.")
                return

            if user_input == "stats":
                print_stats(error_stats)
                continue  # Re-ask the current question

            if user_input == correct_answer.lower():
                print("Correct!\n")
                word_solved = True
            else:
                # Log the error
                error_stats[pair['en']] = error_stats.get(pair['en'], 0) + 1

                print("Wrong answer.")
                print("1: Try again | 2: Skip | 3: Reveal word")
                choice = input("Select option: ").strip()

                if choice == "stop":
                    print("Game stopped.")
                    return
                elif choice == "1":
                    continue
                elif choice == "2":
                    word_solved = True
                elif choice == "3":
                    print(f"The correct word was: {correct_answer}\n")
                    word_solved = True
                else:  # Default behavior for invalid input is skip
                    print("Invalid input, skipping word.\n")
                    word_solved = True


if __name__ == "__main__":
    play_game()