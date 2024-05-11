import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from hex_tools import (
    Cell,
    Point,
    neighbor,
    Layout,
    layout_flat,
    hex_to_pixel,
    polygon_corners,
)


def print_percentage_bar(percentage1, percentage2, sample_size):
    total_length = 100

    green_length = int(total_length * percentage1)
    red_length = int(total_length * percentage2)

    green_part = "=" * green_length
    red_part = "=" * red_length

    # Affichage de la barre de pourcentage avec les couleurs appropriées
    print(
        "\033[32m"
        + green_part
        + "\033[0m"
        + "|"
        + "\033[31m"
        + red_part
        + "\033[0m"
        + f" {percentage1*sample_size:.0f} vs {percentage2*sample_size:.0f}"
    )


def grid_heatmap_plot(heatmap: dict[Cell, float], hex_size: int):
    plt.figure(figsize=(10, 10))
    layout = Layout(layout_flat, Point(1, -1), Point(0, 0))

    min_count = min(heatmap.values())
    max_count = max(heatmap.values())

    norm = Normalize(vmin=min_count, vmax=max_count)
    cmap = plt.get_cmap('viridis')
    scalar_map = ScalarMappable(norm=norm, cmap=cmap)

    for box, count in heatmap.items():
        corners = polygon_corners(layout, box)
        center = hex_to_pixel(layout, box)

        # Contours de chaque hexagone
        list_edges_x = [corner.x for corner in corners]
        list_edges_y = [corner.y for corner in corners]
        list_edges_x.append(list_edges_x[0])
        list_edges_y.append(list_edges_y[0])

        color = scalar_map.to_rgba(count)

        polygon = Polygon(
            corners,
            closed=True,
            edgecolor="k",
            facecolor=color,
            alpha=0.8,
            linewidth=2,
        )

        plt.gca().add_patch(polygon)
        plt.text(
            center.x,
            center.y,
            f"{count:.2f}",
            horizontalalignment="right",
        )
    plt.xlim(-2 * hex_size-1, 2 * hex_size+1)
    plt.ylim(-2 * hex_size-1, 2 * hex_size+1)
    plt.show()
