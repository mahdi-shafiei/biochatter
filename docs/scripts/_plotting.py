import math
import re

import colorcet as cc
import matplotlib
import numpy as np
import seaborn as sns

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BENCHMARKED_MODELS = [
    "chatglm3",
    "claude-3-5-sonnet-20240620",
    "claude-3-opus-20240229",
    "code-llama-instruct",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-0125",
    "gpt-4-0613",
    "gpt-4-0125-preview",
    "gpt-4-1106-preview",
    "gpt-4-turbo-2024-04-09",
    "gpt-4o-2024-05-13",
    "gpt-4o-2024-08-06",
    "gpt-4o-2024-11-20",
    "gpt-4o-mini-2024-07-18",
    "llama-2-chat",
    "llama-3-instruct",
    "llama-3.1-instruct",
    "mixtral-instruct-v0.1",
    "mistral-instruct-v0.2",
    "openhermes-2.5",
]

MODEL_SIZE_ORDER = [
    "Unknown",
    "175",
    "70",
    "46,7",
    "34",
    "13",
    "8",
    "7",
    "6",
]


def plot_text2cypher() -> None:
    """Plot text2cypher tasks.

    Get entity_selection, relationship_selection, property_selection,
    property_exists, query_generation, and end_to_end_query_generation results
    files, combine and preprocess them and plot the accuracy for each model as a
    boxplot.
    """
    entity_selection = pd.read_csv("benchmark/results/entity_selection.csv")
    entity_selection["task"] = "entity_selection"
    relationship_selection = pd.read_csv(
        "benchmark/results/relationship_selection.csv",
    )
    relationship_selection["task"] = "relationship_selection"
    property_selection = pd.read_csv("benchmark/results/property_selection.csv")
    property_selection["task"] = "property_selection"
    property_exists = pd.read_csv("benchmark/results/property_exists.csv")
    property_exists["task"] = "property_exists"
    query_generation = pd.read_csv("benchmark/results/query_generation.csv")
    query_generation["task"] = "query_generation"
    end_to_end_query_generation = pd.read_csv(
        "benchmark/results/end_to_end_query_generation.csv",
    )
    end_to_end_query_generation["task"] = "end_to_end_query_generation"

    # combine all results
    results = pd.concat(
        [
            entity_selection,
            relationship_selection,
            property_selection,
            property_exists,
            query_generation,
            end_to_end_query_generation,
        ],
    )

    # calculate accuracy
    results["score_possible"] = results["score"].apply(
        lambda x: float(x.split("/")[1]),
    )
    results["scores"] = results["score"].apply(lambda x: x.split("/")[0])
    results["score_achieved"] = results["scores"].apply(
        lambda x: (np.mean([float(score) for score in x.split(";")]) if ";" in x else float(x)),
    )
    results["accuracy"] = results["score_achieved"] / results["score_possible"]
    results["score_sd"] = results["scores"].apply(
        lambda x: (np.std([float(score) for score in x.split(";")], ddof=1) if ";" in x else 0),
    )

    results["model"] = results["model_name"].apply(lambda x: x.split(":")[0])
    # create labels: openhermes, llama-3, gpt, based on model name, for all
    # other models, use "other open source"
    results["model_family"] = results["model"].apply(
        lambda x: (
            "openhermes"
            if "openhermes" in x
            else ("llama-3" if "llama-3" in x else "gpt" if "gpt" in x else "other open source")
        ),
    )

    # order task by median accuracy ascending
    task_order = results.groupby("task")["accuracy"].median().sort_values().index

    # order model_family by median accuracy ascending within each task
    results["model_family"] = results["model_family"].astype(
        pd.CategoricalDtype(
            categories=["other open source", "llama-3", "openhermes", "gpt"],
            ordered=True,
        ),
    )

    # plot results per task
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(6, 4))
    plt.xticks(rotation=45, ha="right")
    sns.boxplot(
        x="task",
        y="accuracy",
        hue="model_family",
        data=results,
        order=task_order,
    )
    plt.legend(bbox_to_anchor=(1, 1), loc="upper left")
    plt.savefig(
        "docs/images/boxplot-text2cypher.png",
        bbox_inches="tight",
        dpi=300,
    )


def plot_text2cypher_safety_only():
    """Get entity_selection, relationship_selection, property_selection,
    property_exists, query_generation, and end_to_end_query_generation results
    files, combine and preprocess them and plot the accuracy for each model as a
    boxplot. Only use data that has 'safety' in the task name.

    """
    entity_selection = pd.read_csv("benchmark/results/entity_selection.csv")
    entity_selection["task"] = "entity_selection"
    relationship_selection = pd.read_csv(
        "benchmark/results/relationship_selection.csv",
    )
    relationship_selection["task"] = "relationship_selection"
    property_selection = pd.read_csv("benchmark/results/property_selection.csv")
    property_selection["task"] = "property_selection"
    property_exists = pd.read_csv("benchmark/results/property_exists.csv")
    property_exists["task"] = "property_exists"
    query_generation = pd.read_csv("benchmark/results/query_generation.csv")
    query_generation["task"] = "query_generation"
    end_to_end_query_generation = pd.read_csv(
        "benchmark/results/end_to_end_query_generation.csv",
    )
    end_to_end_query_generation["task"] = "end_to_end_query_generation"

    # combine all results
    results = pd.concat(
        [
            entity_selection,
            relationship_selection,
            property_selection,
            property_exists,
            query_generation,
            end_to_end_query_generation,
        ],
    )

    # only include rows where 'safety' is in the subtask name
    results = results[results["subtask"].str.contains("safety")]

    # calculate accuracy
    results["score_possible"] = results["score"].apply(
        lambda x: float(x.split("/")[1]),
    )
    results["scores"] = results["score"].apply(lambda x: x.split("/")[0])
    results["score_achieved"] = results["scores"].apply(
        lambda x: (np.mean([float(score) for score in x.split(";")]) if ";" in x else float(x)),
    )
    results["accuracy"] = results["score_achieved"] / results["score_possible"]
    results["score_sd"] = results["scores"].apply(
        lambda x: (np.std([float(score) for score in x.split(";")], ddof=1) if ";" in x else 0),
    )

    results["model"] = results["model_name"].apply(lambda x: x.split(":")[0])

    # order task by median accuracy ascending
    task_order = results.groupby("task")["accuracy"].median().sort_values().index

    # order model by median accuracy ascending within each task
    results["model"] = results["model"].astype(
        pd.CategoricalDtype(
            categories=results.groupby("model")["accuracy"].median().sort_values().index,
            ordered=True,
        ),
    )

    # plot results per task
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(6, 4))

    plt.xticks(rotation=45, ha="right")
    sns.stripplot(
        x="model",
        y="accuracy",
        hue="subtask",
        data=results,
    )
    plt.legend(bbox_to_anchor=(1, 1), loc="upper left")
    plt.savefig(
        "docs/images/stripplot-text2cypher-safety.png",
        bbox_inches="tight",
        dpi=300,
    )


def plot_image_caption_confidence():
    """Get multimodal_answer_confidence.csv file, preprocess it and plot the
    confidence scores for correct and incorrect answers as histograms. Correct
    answer confidence values are in the correct_confidence column and incorrect
    answer confidence values are in the incorrect_confidence column; both
    columns contain individual confidence values (integers between 1 and 10)
    separated by semicolons.
    """
    results = pd.read_csv("benchmark/results/multimodal_answer_confidence.csv")
    correct_values = results["correct_confidence"].to_list()
    incorrect_values = results["incorrect_confidence"].to_list()
    # flatten lists of confidence values
    correct_values = [int(value) for sublist in correct_values for value in sublist.split(";")]
    for value in list(incorrect_values):
        if math.isnan(value):
            incorrect_values.remove(value)
        if isinstance(value, float):
            continue
        if ";" in value:
            incorrect_values.remove(value)
            incorrect_values.extend([int(val) for val in value.split(";")])

    incorrect_values = [int(value) for value in incorrect_values]

    # plot histograms of both correct and incorrect confidence values with
    # transparency, correct green, incorrect red
    plt.figure(figsize=(6, 4))
    plt.hist(
        [correct_values, incorrect_values],
        bins=range(1, 12),
        color=["green", "red"],
        label=["Correct", "Incorrect"],
    )
    plt.xlabel("Confidence")
    plt.ylabel("Count")
    plt.xticks(range(1, 11))
    plt.legend()
    plt.savefig(
        "docs/images/histogram-image-caption-confidence.png",
        bbox_inches="tight",
        dpi=300,
    )


def plot_accuracy_per_model(overview) -> None:
    overview_melted = melt_and_process(overview)

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.stripplot(
        x="Model name",
        y="Accuracy",
        hue="Size",
        data=overview_melted,
    )
    plt.title(
        "Strip plot across tasks, per Model, coloured by size (billions of parameters)",
    )
    plt.ylim(-0.1, 1.1)
    plt.xticks(rotation=45, ha="right")
    plt.legend(bbox_to_anchor=(0, 0), loc="lower left")
    plt.savefig(
        "docs/images/stripplot-per-model.png",
        bbox_inches="tight",
    )
    plt.close()


def plot_accuracy_per_quantisation(overview) -> None:
    overview_melted = melt_and_process(overview)

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(10, 6))
    sns.boxplot(
        x="Model name",
        y="Accuracy",
        hue="Quantisation",
        data=overview_melted,
    )
    plt.title("Boxplot across tasks, per Quantisation")
    plt.xticks(rotation=45)
    plt.savefig(
        "docs/images/boxplot-per-quantisation.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.close()


def plot_accuracy_per_task(overview):
    overview_melted = melt_and_process(overview)

    # concatenate model name and quantisation
    overview_melted["Coarse model name"] = overview_melted["Model name"].replace(
        {
            "gpt-3.5-turbo-0613": "gpt-3.5-turbo",
            "gpt-3.5-turbo-0125": "gpt-3.5-turbo",
            "gpt-4-0613": "gpt-4",
            "gpt-4-0125-preview": "gpt-4",
            "gpt-4o-2024-05-13": "gpt-4",
            "gpt-4o-2024-08-06": "gpt-4",
        },
        regex=True,
    )

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(20, 10))

    # Define the color palette
    palette = sns.color_palette(
        "Set1",
        len(overview_melted["Coarse model name"].unique()),
    )

    # Calculate mean accuracy for each task
    task_order = overview_melted.groupby("Task")["Accuracy"].mean().sort_values().index[::-1]

    # Sort the dataframe
    overview_melted["Task"] = pd.Categorical(
        overview_melted["Task"],
        categories=task_order,
        ordered=True,
    )
    overview_melted = overview_melted.sort_values("Task")

    sns.stripplot(
        x="Task",
        y="Accuracy",
        hue="Coarse model name",
        data=overview_melted,
        dodge=True,
        palette=palette,
        jitter=0.2,
        alpha=0.8,
    )

    sns.lineplot(
        x="Task",
        y="Accuracy",
        hue="Coarse model name",
        data=overview_melted,
        sort=False,
        legend=False,
        palette=palette,
        alpha=0.3,
    )

    # Get current axis
    ax = plt.gca()

    # Add vertical lines at each x tick
    for x in ax.get_xticks():
        ax.axvline(x=x, color="gray", linestyle="--", lw=0.5)

    plt.legend(bbox_to_anchor=(1, 1), loc="upper right")
    plt.title("Dot plot across models / quantisations, per Task")
    plt.xticks(rotation=45)
    plt.savefig(
        "docs/images/dotplot-per-task.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.savefig(
        "docs/images/dotplot-per-task.pdf",
        bbox_inches="tight",
    )
    plt.close()


def plot_scatter_per_quantisation(overview):
    overview_melted = melt_and_process(overview)

    # remove individual task accuracy columns
    overview_melted = overview_melted[
        [
            "Model name",
            "Size",
            "Quantisation",
            "Mean Accuracy",
            "Median Accuracy",
            "SD",
        ]
    ]

    # deduplicate remaining rows
    overview_melted = overview_melted.drop_duplicates()

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 8))
    # order x axis quantisation values numerically
    overview_melted["Quantisation"] = pd.Categorical(
        overview_melted["Quantisation"],
        categories=[
            "2-bit",
            "3-bit",
            "4-bit",
            "5-bit",
            "6-bit",
            "8-bit",
            ">= 16-bit*",
        ],
        ordered=True,
    )
    overview_melted["Size"] = pd.Categorical(
        overview_melted["Size"],
        categories=[
            "Unknown",
            "175",
            "70",
            "46,7",
            "34",
            "13",
            "8",
            "7",
            "6",
        ],
        ordered=True,
    )

    # Add jitter to x-coordinates
    x = pd.Categorical(overview_melted["Quantisation"]).codes.astype(float)

    # Create a mask for 'openhermes' and closed models
    mask_openhermes = overview_melted["Model name"] == "openhermes-2.5"
    mask_closed = overview_melted["Model name"].str.contains(
        "gpt|claude",
        case=False,
        regex=True,
    )

    # Do not add jitter for 'openhermes' model
    x[mask_openhermes] += 0

    # Manually enter jitter values for closed models
    jitter_values = {
        "gpt-3": -0.2,
        "gpt-4": 0.2,
        "claude-3-opus-20240229": -0.05,
        "claude-3-5-sonnet-20240620": 0.05,
    }

    for model, jitter in jitter_values.items():
        mask_model = overview_melted["Model name"].str.contains(model)
        x[mask_model] += jitter

    # For other models, add the original jitter
    x[~mask_openhermes & ~mask_closed] += np.random.normal(
        0,
        0.1,
        size=len(x[~mask_openhermes & ~mask_closed]),
    )

    # Define the order of model names
    model_names_order = BENCHMARKED_MODELS

    # Define the order of sizes
    size_order = MODEL_SIZE_ORDER

    # Create a ColorBrewer palette
    palette = sns.color_palette(cc.glasbey, n_colors=len(model_names_order))

    # Define a dictionary mapping model names to colors using the order list
    color_dict = {model: palette[i] for i, model in enumerate(model_names_order)}

    # Use the dictionary as the palette argument in sns.scatterplot
    ax = sns.scatterplot(
        x=x,
        y="Median Accuracy",
        hue="Model name",
        size="Size",
        sizes=(10, 300),
        data=overview_melted,
        palette=color_dict,  # Use the color dictionary here
        alpha=0.5,
    )

    # Reorder the legend using the same order list
    handles, labels = ax.get_legend_handles_labels()
    order = (
        ["Model name"]
        + [name for name in model_names_order if name in labels]
        + ["Size"]
        + [size for size in size_order if size in labels]
    )
    order_indices = [labels.index(name) for name in order if name in labels]
    plt.legend(
        [handles[idx] for idx in order_indices],
        [labels[idx] for idx in order_indices],
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )

    plt.ylim(0, 1)
    plt.xticks(
        ticks=range(len(overview_melted["Quantisation"].unique())),
        labels=overview_melted["Quantisation"].cat.categories,
    )
    plt.title(
        "Scatter plot across models, per quantisation, coloured by model name, size by model size (billions of parameters)",
    )
    plt.xticks(rotation=45)
    plt.savefig(
        "docs/images/scatter-per-quantisation-name.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.savefig(
        "docs/images/scatter-per-quantisation-name.pdf",
        bbox_inches="tight",
    )
    plt.close()


def plot_task_comparison(overview):
    overview_melted = melt_and_process(overview)

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.boxplot(
        x="Task",
        y="Accuracy",
        hue="Task",
        data=overview_melted,
    )
    plt.xticks(rotation=45, ha="right")
    plt.savefig(
        "docs/images/boxplot-tasks.png",
        bbox_inches="tight",
    )
    plt.close()


def plot_rag_tasks(overview):
    overview_melted = melt_and_process(overview)

    # select tasks naive_query_generation_using_schema and query_generation
    overview_melted = overview_melted[
        overview_melted["Task"].isin(
            [
                "explicit_relevance_of_single_fragments",
                "implicit_relevance_of_multiple_fragments",
            ],
        )
    ]

    # order models by median accuracy, inverse
    overview_melted["Model name"] = pd.Categorical(
        overview_melted["Model name"],
        categories=overview_melted.groupby("Model name")["Median Accuracy"].median().sort_values().index[::-1],
        ordered=True,
    )

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(6, 4))
    sns.stripplot(
        x="Model name",
        y="Accuracy",
        hue="Quantisation",
        data=overview_melted,
        jitter=0.2,
        alpha=0.8,
    )
    plt.xlabel(None)
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1, 0), loc="lower left")
    # Get current axis
    ax = plt.gca()

    # Add vertical lines at each x tick
    for x in ax.get_xticks():
        ax.axvline(x=x, color="gray", linestyle="--", lw=0.5)

    plt.savefig(
        "docs/images/stripplot-rag-tasks.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.savefig(
        "docs/images/stripplot-rag-tasks.pdf",
        bbox_inches="tight",
    )
    plt.close()


def plot_extraction_tasks():
    """Load raw result file for sourcedata_info_extraction; aggregate based on the
    subtask name and calculate mean accuracy for each model. Plot a stripplot
    of the mean accuracy across models, coloured by subtask.
    """
    sourcedata_info_extraction = pd.read_csv(
        "benchmark/results/sourcedata_info_extraction.csv",
    )
    # split subtask at colon and use second element
    sourcedata_info_extraction["subtask"] = sourcedata_info_extraction["subtask"].apply(lambda x: x.split(":")[1])
    sourcedata_info_extraction["score_possible"] = sourcedata_info_extraction["score"].apply(
        lambda x: float(x.split("/")[1]),
    )
    sourcedata_info_extraction["scores"] = sourcedata_info_extraction["score"].apply(lambda x: x.split("/")[0])
    sourcedata_info_extraction["score_achieved"] = sourcedata_info_extraction["scores"].apply(
        lambda x: np.mean(float(x.split(";")[0])) if ";" in x else float(x),
    )
    sourcedata_info_extraction["score_sd"] = sourcedata_info_extraction["scores"].apply(
        lambda x: np.std(float(x.split(";")[0])) if ";" in x else 0,
    )
    aggregated_scores = sourcedata_info_extraction.groupby(
        ["model_name", "subtask"],
    ).agg(
        {
            "score_possible": "sum",
            "score_achieved": "sum",
            "score_sd": "first",
            "iterations": "first",
        },
    )

    aggregated_scores["Accuracy"] = aggregated_scores.apply(
        lambda row: (row["score_achieved"] / row["score_possible"] if row["score_possible"] != 0 else 0),
        axis=1,
    )

    aggregated_scores["Full model name"] = aggregated_scores.index.get_level_values("model_name")
    aggregated_scores["Subtask"] = aggregated_scores.index.get_level_values(
        "subtask",
    )
    aggregated_scores["Score achieved"] = aggregated_scores["score_achieved"]
    aggregated_scores["Score possible"] = aggregated_scores["score_possible"]
    aggregated_scores["Score SD"] = aggregated_scores["score_sd"]
    aggregated_scores["Iterations"] = aggregated_scores["iterations"]
    new_order = [
        "Full model name",
        "Subtask",
        "Score achieved",
        "Score possible",
        "Score SD",
        "Accuracy",
        "Iterations",
    ]
    results = aggregated_scores[new_order]
    results = results.sort_values(by="Accuracy", ascending=False)

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(6, 4))
    sns.stripplot(
        x="Subtask",
        y="Accuracy",
        hue="Full model name",
        data=results,
    )

    plt.title("Strip plot across models, per subtask, coloured by model name")
    plt.ylim(-0.1, 1.1)
    plt.xticks(rotation=45, ha="right")
    plt.legend(bbox_to_anchor=(1, 1), loc="upper left")
    plt.savefig(
        "docs/images/stripplot-extraction-tasks.png",
        bbox_inches="tight",
        dpi=300,
    )


def plot_medical_exam():
    """Load raw result for medical_exam; aggregate based on the language and
    calculate mean accuracy for each model. Plot a stripplot of the mean
    accuracy across models, coloured by language.
    """
    medical_exam = pd.read_csv("benchmark/results/medical_exam.csv")

    medical_exam["score_possible"] = medical_exam["score"].apply(
        lambda x: float(x.split("/")[1]),
    )
    medical_exam["scores"] = medical_exam["score"].apply(
        lambda x: x.split("/")[0],
    )
    medical_exam["score_achieved"] = medical_exam["scores"].apply(
        lambda x: (np.mean([float(score) for score in x.split(";")]) if ";" in x else float(x)),
    )
    medical_exam["accuracy"] = medical_exam["score_achieved"] / medical_exam["score_possible"]
    medical_exam["score_sd"] = medical_exam["scores"].apply(
        lambda x: (np.std([float(score) for score in x.split(";")], ddof=1) if ";" in x else 0),
    )
    medical_exam["task"] = medical_exam["subtask"].apply(
        lambda x: x.split(":")[0],
    )
    medical_exam["domain"] = medical_exam["subtask"].apply(
        lambda x: x.split(":")[1],
    )
    medical_exam["language"] = medical_exam["subtask"].apply(
        lambda x: x.split(":")[2],
    )

    # processing: remove "short_words" task, not informative
    medical_exam = medical_exam[medical_exam["task"] != "short_words"]

    # plot language comparison
    aggregated_scores_language = medical_exam.groupby(
        ["model_name", "language"],
    ).agg(
        {
            "accuracy": "mean",
            "score_sd": "mean",
        },
    )
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(6, 4))
    sns.boxplot(
        x="language",
        y="accuracy",
        data=aggregated_scores_language,
    )

    plt.savefig(
        "docs/images/boxplot-medical-exam-language.png",
        bbox_inches="tight",
        dpi=300,
    )

    # plot language comparison per domain
    aggregated_scores_language_domain = medical_exam.groupby(
        ["model_name", "language", "domain"],
    ).agg(
        {
            "accuracy": "mean",
            "score_sd": "mean",
        },
    )
    # calculate mean accuracy per language and domain
    mean_accuracy = aggregated_scores_language_domain.groupby(
        ["language", "domain"],
    )["accuracy"].mean()
    # sort domains by mean accuracy
    sorted_domains = mean_accuracy.sort_values(
        ascending=False,
    ).index.get_level_values("domain")

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(6, 4))
    plt.xticks(rotation=45, ha="right")
    sns.boxplot(
        x="domain",
        y="accuracy",
        hue="language",
        data=aggregated_scores_language_domain,
        order=sorted_domains,
    )

    plt.savefig(
        "docs/images/boxplot-medical-exam-language-domain.png",
        bbox_inches="tight",
        dpi=300,
    )

    # plot task comparison
    aggregated_scores_task = medical_exam.groupby(["model_name", "task"]).agg(
        {
            "accuracy": "mean",
            "score_sd": "mean",
        },
    )
    # calculate mean accuracy per task
    mean_accuracy = aggregated_scores_task.groupby("task")["accuracy"].mean()
    # sort tasks by mean accuracy
    sorted_tasks = mean_accuracy.sort_values(ascending=False).index

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(6, 4))
    plt.xticks(rotation=45, ha="right")
    sns.boxplot(
        x="task",
        y="accuracy",
        data=aggregated_scores_task,
        order=sorted_tasks,
    )

    plt.savefig(
        "docs/images/boxplot-medical-exam-task.png",
        bbox_inches="tight",
        dpi=300,
    )

    # plot domain comparison
    aggregated_scores_domain = medical_exam.groupby(
        ["model_name", "domain"],
    ).agg(
        {
            "accuracy": "mean",
            "score_sd": "mean",
        },
    )
    # calculate mean accuracy per domain
    mean_accuracy = aggregated_scores_domain.groupby("domain")["accuracy"].mean()
    # sort domains by mean accuracy
    sorted_domains = mean_accuracy.sort_values(ascending=False).index

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(6, 4))
    plt.xticks(rotation=45, ha="right")
    sns.boxplot(
        x="domain",
        y="accuracy",
        data=aggregated_scores_domain,
        order=sorted_domains,
    )

    plt.savefig(
        "docs/images/boxplot-medical-exam-domain.png",
        bbox_inches="tight",
        dpi=300,
    )


def plot_comparison_naive_biochatter(overview):
    overview_melted = melt_and_process(overview)

    # select tasks naive_query_generation_using_schema and query_generation
    overview_melted = overview_melted[
        overview_melted["Task"].isin(
            ["naive_query_generation_using_schema", "query_generation"],
        )
    ]

    # print number of rows of each task
    print(overview_melted["Task"].value_counts())

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(6, 4))
    sns.boxplot(
        x="Task",
        y="Accuracy",
        hue="Task",
        data=overview_melted,
    )
    plt.ylim(0, 1)
    plt.xlabel(None)
    plt.xticks(
        ticks=range(len(overview_melted["Task"].unique())),
        labels=["BioChatter", "Naive LLM (using full YAML schema)"],
    )
    plt.savefig(
        "docs/images/boxplot-naive-vs-biochatter.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.savefig(
        "docs/images/boxplot-naive-vs-biochatter.pdf",
        bbox_inches="tight",
    )
    plt.close()

    # plot scatter plot
    plt.figure(figsize=(6, 4))
    sns.stripplot(
        x="Task",
        y="Accuracy",
        data=overview_melted,
        jitter=0.2,
        alpha=0.8,
    )
    plt.ylim(0, 1)
    plt.xlabel(None)
    plt.xticks(
        ticks=range(len(overview_melted["Task"].unique())),
        labels=["BioChatter", "Naive LLM (using full YAML schema)"],
    )
    plt.savefig(
        "docs/images/scatter-naive-vs-biochatter.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.savefig(
        "docs/images/scatter-naive-vs-biochatter.pdf",
        bbox_inches="tight",
    )
    plt.close()

    # plit violin plot
    plt.figure(figsize=(6, 4))
    sns.violinplot(
        x="Task",
        y="Accuracy",
        data=overview_melted,
    )
    plt.ylim(0, 1)
    plt.xlabel(None)
    plt.xticks(
        ticks=range(len(overview_melted["Task"].unique())),
        labels=["BioChatter", "Naive LLM (using full YAML schema)"],
    )
    plt.savefig(
        "docs/images/violin-naive-vs-biochatter.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.savefig(
        "docs/images/violin-naive-vs-biochatter.pdf",
        bbox_inches="tight",
    )
    plt.close()


def melt_and_process(overview: pd.DataFrame) -> pd.DataFrame:
    """Melt the overview table and process it for plotting."""
    overview_melted = overview.melt(
        id_vars=[
            "Full model name",
            "Model name",
            "Size",
            "Version",
            "Quantisation",
            "Mean Accuracy",
            "Median Accuracy",
            "SD",
        ],
        var_name="Task",
        value_name="Accuracy",
    )
    # unify quantisation names: 2-bit, 3-bit, etc
    digit_pattern = r"\d+"
    overview_melted["Quantisation"] = overview_melted["Quantisation"].apply(
        lambda x: f"{re.findall(digit_pattern, x)[0]}-bit" if x else "None",
    )
    # set quantisation of gpt models to None
    overview_melted["Quantisation"] = overview_melted.apply(
        lambda row: (
            ">= 16-bit*"
            if "gpt-3.5-turbo" in row["Model name"] or "gpt-4" in row["Model name"] or "claude" in row["Model name"]
            else row["Quantisation"]
        ),
        axis=1,
    )

    return overview_melted
