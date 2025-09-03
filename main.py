import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3

class VennOrganizer:
    def __init__(self):
        self.categories = {}

    def add_category(self, name, items):
        """Add a category with its items (as a list or set)."""
        self.categories[name] = set(items)

    def show_venn(self, cats):
        """
        Display a Venn diagram for 2 or 3 categories.
        Instead of counts, shows the actual item names.
        """
        if not (2 <= len(cats) <= 3):
            raise ValueError("You must provide 2 or 3 categories for a Venn diagram.")

        sets = [self.categories[c] for c in cats]

        plt.figure(figsize=(8,8))

        if len(cats) == 2:
            v = venn2(sets, set_labels=cats)
            # Replace region labels with actual items
            regions = {
                '10': sets[0] - sets[1],
                '01': sets[1] - sets[0],
                '11': sets[0] & sets[1]
            }
        else:  # 3 categories
            v = venn3(sets, set_labels=cats)
            regions = {
                '100': sets[0] - sets[1] - sets[2],
                '010': sets[1] - sets[0] - sets[2],
                '001': sets[2] - sets[0] - sets[1],
                '110': (sets[0] & sets[1]) - sets[2],
                '101': (sets[0] & sets[2]) - sets[1],
                '011': (sets[1] & sets[2]) - sets[0],
                '111': sets[0] & sets[1] & sets[2]
            }

        # Update labels
        for region_code, elements in regions.items():
            label = v.get_label_by_id(region_code)
            if label:
                if elements:
                    label.set_text("\n".join(elements))  # show items instead of count
                else:
                    label.set_text("")  # empty region

        plt.title("Venn Diagram for " + ", ".join(cats))
        # Save the plot as a PNG image file
        filename = f"venn_{'_'.join(cats)}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to free memory
        print(f"Venn diagram saved as: {filename}")


# Example usage
if __name__ == "__main__":
    organizer = VennOrganizer()

    organizer.add_category("Fruits", ["apple", "banana", "cherry", "mango"])
    organizer.add_category("Red Items", ["apple", "cherry", "tomato"])
    organizer.add_category("Tropical", ["mango", "banana", "pineapple", "papaya"])

    # Show Venn with actual items
    organizer.show_venn(["Fruits", "Red Items"])
    organizer.show_venn(["Fruits", "Red Items", "Tropical"])