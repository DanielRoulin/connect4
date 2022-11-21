
def choose(options = [], named_options = {}):
    available_answers = []
    for i, option in enumerate(options):
        available_answers.append(i)
        print(f"{i+1}: {option}")

    for name, option in named_options.items():
        available_answers.append(name)
        print(f"{name}: {option}")

    while True:
        choice = input("Your choice: ")
        try:
            choice = int(choice) - 1
        except ValueError:
            pass
        if choice not in available_answers:
            print("This option does not exists!")
            continue
        return choice

if __name__ == "__main__":
    print(choose(["Hello", "World"], {"r": "Refresh", "e": "Export", "q": "Quit"}))