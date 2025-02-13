from rich.console import Console
import random

console = Console()

def print_rich_joke():
    jokes = [
        "Why don’t routers gossip? They prefer secure communication.",
        "Keep calm and subnet on!",
        "Why did the network engineer carry a whiteboard? To draw topology maps on the go!"
    ]
    joke = random.choice(jokes)
    console.rule("[bold cyan]💡 Joke of the Day 💡")
    console.print(f"[bold yellow]{joke}", style="yellow")
    console.rule()

print_rich_joke()