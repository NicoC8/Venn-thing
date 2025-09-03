import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3

class VennOrganizer:
    def __init__(self):
        # Store categories as dictionary: {name: set(items)}
        self.categories = {}

    def add_category(self, name, items):
        """Add a category with its items (as a list or set)."""
        self.categories[name] = set(items)

    def show_venn(self, cats):
        """
        Display a Venn diagram for up to 3 categories.
        cats: list of category names (must exist in self.categories)
        """
        if not (2 <= len(cats) <= 3):
            raise ValueError("You must provide 2 or 3 categories for a Venn diagram.")

        sets = [self.categories[c] for c in cats]

        plt.figure(figsize=(6,6))

        if len(cats) == 2:
            venn2(sets, set_labels=cats)
        elif len(cats) == 3:
            venn3(sets, set_labels=cats)

        plt.title("Venn Diagram for " + ", ".join(cats))
        plt.show()


# Example usage
if __name__ == "__main__":
    organizer = VennOrganizer()

    # Add categories
    organizer.add_category("Fruits", ["apple", "banana", "cherry", "mango"])
    organizer.add_category("Red Items", ["apple", "cherry", "tomato"])
    organizer.add_category("Tropical", ["mango", "banana", "pineapple", "papaya"])

    # Show Venn for 2 categories
    organizer.show_venn(["Fruits", "Red Items"])

    # Show Venn for 3 categories
    organizer.show_venn(["Fruits", "Red Items", "Tropical"])