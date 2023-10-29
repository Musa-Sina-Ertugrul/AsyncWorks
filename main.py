"""sumary_line

Keyword arguments:
argument -- description
Return: return_description
"""
from typing import List, Dict
from copy import deepcopy
from flask import Flask, render_template, request, session

app = Flask(__name__)
app.config["SECRET_KEY"] = "my_key"
data_name = []
data_minutes = []
data_required_work = []


@app.route("/", methods=["GET", "POST"])
def index():
    """ 
    This function processes incoming requests and handles form data.
    Keyword arguments:
    - request: The HTTP request object.
    Return: Rendered template or an error message.
    """
    global data_required_work
    global data_minutes
    global data_name
    session["results"]: List = []
    if (
        request.method == "POST"
        and ("data_name" in request.form)
        and ("data_minutes" in request.form)
        and ("data_required_work" in request.form)
    ):
        data_name = request.form["data_name"].split(",")[:-1]
        data_minutes = request.form["data_minutes"].split(",")[:-1]
        data_required_work = request.form["data_required_work"].split(",")[:-1]

        data_minutes = turn_to_int(data_minutes)
        if is_minutes_none():
            error_message = "Invalid minute type, minutes contain invalid minute"
            session["error_message"] = error_message
            return render_template("error.html")
        if are_names_unique():
            error_message = "Invalid work names, work names are not unique."
            session["error_message"] = error_message
            return render_template("error.html")
        if are_required_works_in_names():
            error_message = "Invalid required work names, required work names contain not existing name."
            session["error_message"] = error_message
            return render_template("error.html")
        if are_they_same_len():
            error_message = "Invalid len, enter all values for all items."
            session["error_message"] = error_message
            return render_template("error.html")

        session["results"] = calculate_line_time()
        return render_template("listed.html")

    return render_template("index.html")


def calculate_line_time() -> int:
    """
    Calculate the total time based on the input data.
    Return: Total calculated time.
    """
    global data_required_work
    global data_minutes
    global data_name
    tmp_indexes: List = calculate_not_required()
    max_time: int = init_time(tmp_indexes)
    remove_not_requireds(tmp_indexes)
    graph: List[List[int]] = init_graph(len(data_minutes))
    graph = connect_nodes(graph)
    raw_result: List = dfs(graph)
    raw_time: int = make_results_clean(raw_result)
    return max(max_time, raw_time)


def make_results_clean(raw_result: List) -> int:
    """
    Clean the results obtained from depth-first search.
    Keyword arguments:
    - raw_result: Raw results from DFS.
    Return: Cleaned time value.
    """
    global data_required_work
    global data_minutes
    global data_name
    time: int = 0
    for i, inner_result in enumerate(raw_result):
        time = max(time, data_minutes[i] + pre_order(inner_result))
    return time


def pre_order(raw_result: List) -> int:
    """
    Perform pre-order traversal on the raw result.
    Keyword arguments:
    - raw_result: Raw result to traverse.
    Return: Time value.
    """
    global data_required_work
    global data_minutes
    global data_name
    time: int = 0

    if len(raw_result) > 2:
        for i in range(len(raw_result), 2):
            time = max(time, data_minutes[raw_result[i]] + pre_order(raw_result[i + 1]))
        return time
    else:
        if len(raw_result) == 2:
            if raw_result[1]:
                return time + data_minutes[raw_result[0]] + pre_order(raw_result[1])
            else:
                return time + data_minutes[raw_result[0]]
        else:
            return 0


def dfs(graph: List[List[int]]) -> List:
    """
    Perform depth-first search on the graph.
    Keyword arguments:
    - graph: The graph representing the data.
    Return: List of visited indexes.
    """
    global data_required_work
    global data_minutes
    global data_name
    visited: List[bool] = [False for _ in range(len(graph))]
    result: List = []
    for i in range(len(graph)):
        visited_indexes: List[int] = inner_dfs(graph, visited, i)
        result.append(visited_indexes)
        visited = [False for _ in range(len(graph))]

    return result


def inner_dfs(graph: List[List[int]], visited: List[bool], i) -> List[int]:
    """
    Recursively traverse the graph in a depth-first manner.
    Keyword arguments:
    - graph: The graph representing the data.
    - visited: List of visited nodes.
    - i: Current node index.
    Return: List of visited indexes.
    """
    global data_required_work
    global data_minutes
    global data_name
    visited_indexes = []
    if visited[i]:
        return visited_indexes
    else:
        visited[i] = True

    for j in range(i, len(graph), 1):
        if j != i and graph[i][j] == 1 and not visited[j]:
            visited_indexes.append(i)
            visited_indexes.append(inner_dfs(graph, visited, j))
            visited[j] = False

    return visited_indexes


def connect_nodes(graph: List[List[int]]) -> List[List[int]]:
    """
    Connect nodes in the graph based on required work.
    Keyword arguments:
    - graph: The graph representing the data.
    Return: Updated graph.
    """
    global data_required_work
    global data_minutes
    global data_name
    name_indexes: Dict[int] = {}
    name_connections: Dict[str] = {}
    for i, name in enumerate(data_name):
        name_indexes[name] = i
    for name, required in zip(data_name, data_required_work):
        name_connections[name] = required

    i = 0
    for name, required in zip(data_name, data_required_work):
        if not is_empty_required(name) and not is_empty_required(
            name_connections[name]
        ):
            graph[i][name_indexes[name_connections[name]]] = 1
        i += 1

    return graph


def calculate_not_required() -> List:
    """
    Identify and calculate the not required work.
    Return: List of indexes for not required work.
    """
    global data_required_work
    global data_minutes
    global data_name
    tmp_indexes = []
    requireds = set(data_required_work)
    for i, required_work in enumerate(data_required_work):
        if is_empty_required(required_work) and required_work not in requireds:
            tmp_indexes.append(i)
    return tmp_indexes


def remove_not_requireds(indexes: List[int]) -> None:
    """
    Remove not required items from the data.
    Keyword arguments:
    - indexes: List of indexes to be removed.
    """
    global data_required_work
    global data_minutes
    global data_name
    removed_count: int = 0
    indexes = sorted(indexes)
    for i in indexes:
        data_minutes.pop(i - removed_count)
        session["results"].append(data_name.pop(i - removed_count))
        data_required_work.pop(i - removed_count)
        removed_count += 1


def init_graph(node_count: int) -> List[List[int]]:
    """
    Initialize the graph with zeros.
    Keyword arguments:
    - node_count: Number of nodes in the graph.
    Return: Initialized graph.
    """
    result = []
    for i in range(node_count):
        tmp = []
        for j in range(node_count):
            tmp.append(0)
        result.append(tmp)
    return result


def init_time(not_requireds: List) -> int:
    """
    Initialize the time value for not required work.
    Keyword arguments:
    - not_requireds: List of not required work.
    Return: Initialized time value.
    """
    global data_required_work
    global data_minutes
    global data_name
    time: int = 0
    for i in not_requireds:
        time = max(time, data_minutes[i])
    return time


def is_empty_required(word: str) -> bool:
    """
    Check if a word represents an empty requirement.
    Keyword arguments:
    - word: The word to check.
    Return: True if it's an empty requirement, else False.
    """
    word = word.lower()
    match word:
        case "_":
            return True
        case " ":
            return True
        case "empty":
            return True
        case _:
            return False


def are_they_same_len():
    """
    Check if the input data lists have the same length.
    Return: True if they have the same length, else False.
    """
    global data_required_work
    global data_minutes
    global data_name

    return (
        len(data_minutes) != len(data_name)
        or len(data_name) != len(data_required_work)
        or len(data_minutes) != len(data_required_work)
    )


def are_required_works_in_names():
    """
    Check if required work names are in the list of names.
    Return: True if they are in the list, else False.
    """
    global data_required_work
    global data_minutes
    global data_name
    tmp_set = deepcopy(data_required_work)
    if "empty" in tmp_set:
        tmp_set.remove("empty")
    if "Empty" in tmp_set:
        tmp_set.remove("Empty")
    if " " in tmp_set:
        tmp_set.remove(" ")
    if "_" in tmp_set:
        tmp_set.remove("_")
    return len(set(tmp_set) - set(data_name)) != 0


def is_minutes_none() -> bool:
    """
    Check if the 'data_minutes' list is None.
    Return: True if it's None, else False.
    """
    global data_required_work
    global data_minutes
    global data_name
    return data_minutes is None


def are_names_unique() -> bool:
    """
    Check if work names are unique.
    Return: True if they are unique, else False.
    """
    global data_required_work
    global data_minutes
    global data_name
    return len(data_name) != len(set(data_name))


def turn_to_int(str_list: List[str]) -> List[int]:
    """
    Convert a list of strings to a list of integers.
    Keyword arguments:
    - str_list: List of strings to convert.
    Return: List of integers or None if conversion fails.
    """
    global data_required_work
    global data_minutes
    global data_name
    new_list = []
    for string in str_list:
        try:
            new_list.append(int(string))
        except ValueError:
            return None
    return new_list


if __name__ == "__main__":
    app.run(debug=True)
