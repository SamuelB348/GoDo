"""
This section defines some utilities that may or may not be used inside the other sections.
"""


def print_percentage_bar(percentage1, percentage2, sample_size):
    """
    Display a percentage bar (percentage1*"="|percentage2*"="). %1 + %2 should equal 1.

    :param percentage1: a percentage (max 1)
    :param percentage2: a percentage (max 1)
    :param sample_size: a sample size these percentages are taken from
    :return:
    """

    total_length = 100

    green_length = int(total_length * percentage1)
    red_length = int(total_length * percentage2)

    green_part = "=" * green_length
    red_part = "=" * red_length

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


def sum_lists(list_of_lists):
    """
    Perform the sum of lists with variable lengths.

    :param list_of_lists: a list of lists of integers or floats
    :return: a list
    """

    max_length = max(
        len(lst) for lst in list_of_lists
    )  # Trouve la longueur maximale parmi toutes les listes
    new_lsts = [lst + [0] * max(0, max_length - len(lst)) for lst in list_of_lists]
    summed_list = []
    for i in range(max_length):
        count = 0
        nb = 1
        for lst in new_lsts:
            if lst[i] != 0:
                count += lst[i]
                nb += 1
        summed_list.append(count / nb)
    return summed_list
