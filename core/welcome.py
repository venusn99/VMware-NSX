from rich.console import Console
import random
import os
console = Console()
def get_file_path():
    file_path = os.getcwd()
    file = os.path.dirname(os.path.abspath(__file__)) + "/quotes.txt"
    return file
def random_line(file):
    lines = open(file).read().splitlines()
    return random.choice(lines)
joke = random_line(get_file_path())
if joke.endswith(','):
    console.rule("[bold cyan]💡 Joke of the Day 💡")
    console.print(f"[bold yellow]{joke.rsplit(',',1)[0]}", style="yellow")
    console.rule()
    # print(joke.rsplit(',',1)[0])
else:
    print("\n" + "=" * len(joke))
    # print(f"💡 Joke of the Day 💡\n{joke}")
    console.rule("[bold cyan]💡 Joke of the Day 💡")
    console.print(f"[bold yellow]{joke}", style="yellow")
    # print("=" * len(joke) + "\n")
    console.rule()