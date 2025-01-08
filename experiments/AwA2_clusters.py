import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv

from collections import Counter
from clustering import clusterConcepts

TRAIN_CONCEPT_PATH = "data/awa2/output/concepts_train.csv"
PLOTS_PATH = "experiments/plots/AwA2/"
CLUSTERS_PATH = "experiments/clusters/AwA2/"
VISUALIZATION = True

# load concepts
concepts = pd.read_csv(TRAIN_CONCEPT_PATH, index_col="animal")
concepts = np.array(concepts)

# read header, it contains the labels

with open(TRAIN_CONCEPT_PATH, mode="r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    labels = next(reader)  # Reads the first row as the header
    labels = [
        label.capitalize() for label in labels if label != "animal"
    ]  # remove id column


no_clusters = 4

table_data = clusterConcepts(concepts, no_clusters=no_clusters)
table_data.to_csv(CLUSTERS_PATH + "AwA2_clusters_idx.csv", index=False)

table_data = clusterConcepts(concepts, no_clusters=no_clusters, str_labels=labels)
table_data.to_csv(CLUSTERS_PATH + "AwA2_clusters_str.csv", index=False)

if VISUALIZATION:
    sns.set_theme(context="paper", style="white")

    # Increase font sizes globally
    plt.rcParams.update(
        {
            "font.size": 18,  # General font size
            "axes.titlesize": 24,  # Title font size
            "axes.labelsize": 20,  # Axis label font size
            "xtick.labelsize": 18,  # X-tick label font size
            "ytick.labelsize": 18,  # Y-tick label font size
            "legend.fontsize": 16,  # Legend font size
            "legend.title_fontsize": 18,  # Legend title font size
        }
    )

    # Extract Suffixes
    suffix_dict = {}
    cluster_shift = len("cluster_")
    for cluster in table_data.columns:
        capitalized = f"Cluster ${cluster[cluster_shift :]}$"
        suffix_dict[capitalized] = sorted(
            [entry for entry in table_data[cluster] if entry]
        )  # extract suffixes

    # Count the frequency of each suffix across all lists
    suffix_counts = Counter(
        item for sublist in suffix_dict.values() for item in sublist
    )

    """
    # Filter out single-occurrence suffixes, give them their own symbol
    suffix_dict = {
        key: sorted(
            [item for item in lst if suffix_counts[item] > 1]
            + ["UNIQUE" for item in lst if suffix_counts[item] == 1]
        )
        for key, lst in suffix_dict.items()
    }
    """

    # Flatten and get unique strings
    unique_items = sorted(
        set(item for sublist in suffix_dict.values() for item in sublist)
    )

    # Assign each unique string a combination of color and shape
    no_colors = 9
    colors = plt.cm.tab10(np.linspace(0, 1, no_colors))

    shapes = ["s", "D"]
    no_shapes = len(shapes)

    color_shape_map = {
        item: (colors[i % no_colors], shapes[i % no_shapes])
        for i, item in enumerate(unique_items)
    }

    # Track which labels have already been added to avoid duplicates in the legend
    already_labeled = set()

    # Create the plot
    plt.figure(figsize=(15, len(suffix_dict) * 2))
    y_offset = 0

    for key, lst in suffix_dict.items():
        x_vals = (
            np.linspace(0, len(lst) - 1, len(lst)) * 1
        )  # Increase spacing between symbols
        y_vals = [y_offset] * len(lst)

        # Plot each string with its assigned color and shape
        for i, item in enumerate(lst):
            color, shape = color_shape_map[item]
            label = item if item not in already_labeled else None  # Add label only once
            if label is not None:
                label = label.capitalize()

            plt.scatter(
                x_vals[i],
                y_vals[i],
                color=color,
                marker=shape,
                s=100,
                label=label,
            )
            already_labeled.add(item)  # Mark this item as labeled

        y_offset += 1  # Move to the next line

    # Beautify the plot
    plt.yticks(range(len(suffix_dict)), suffix_dict.keys())
    plt.xticks([])  # No x-axis labels
    plt.legend(bbox_to_anchor=(0, -0.4), loc="lower left", ncol=5)
    plt.savefig(PLOTS_PATH + "AwA2_clusters.pdf", bbox_inches="tight")

"""
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt
import radialtree as rt  # https://github.com/koonimaru/radialtree

metric = "jaccard"
distance_matrix = pdist(concepts.T, metric=metric)

# Apply agglomerative clustering using complete linkage
linkage_matrix = linkage(distance_matrix, method="complete")


no_concepts = concepts.shape[1]
trivial = list(range(1, no_concepts + 1))

smallest_t = 0
for t in np.linspace(0, 1, int(1e4)):
    if len(set(fcluster(Z=linkage_matrix, t=t, criterion="distance"))) < 5:
        break
    else:
        smallest_t = t

no_clusters = len(set(fcluster(Z=linkage_matrix, t=smallest_t, criterion="distance")))

# Visualize dendrogram
out = dendrogram(
    Z=linkage_matrix,
    p=no_clusters,
    labels=labels,
    orientation="left",
    color_threshold=smallest_t,
    no_plot=True,
)
rt.plot(out, figsize=(15, 15), pallete="Set1")
plt.savefig(PLOTS_PATH + "labeled.pdf", dpi=400)

out = dendrogram(
    Z=linkage_matrix,
    p=no_clusters,
    labels=labels,
    truncate_mode="lastp",
    orientation="left",
    show_leaf_counts=True,
    no_plot=True,
)
rt.plot(out)
plt.savefig(PLOTS_PATH + "collapsed.pdf", dpi=300)
"""
