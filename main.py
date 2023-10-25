"""sumary_line

Keyword arguments:
argument -- description
Return: return_description
"""
from typing import List
import asyncio
from flask import Flask, render_template, request, session

app = Flask(__name__)
app.config["SECRET_KEY"] = "my_key"
data_name = []
data_minutes = []
data_required_work = []


@app.route("/", methods=["GET", "POST"])
def index():
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

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
        
        session["results"] = calculate_line()
        return render_template("listed.html")

    return render_template("index.html")

def calculate_line()->List[List]:
    """sumary_line"""
    # TODO: Continue from here
    
    return [[]]

def are_they_same_len():
    """sumary_line"""
    return (
        len(data_minutes) == len(data_name)
        and len(data_name) == len(data_required_work)
        and len(data_minutes) == len(data_required_work)
    )


def are_required_works_in_names():
    """sumary_line"""
    return len(set(data_required_work) - set(data_name)) != 0


def is_minutes_none() -> bool:
    """sumary_line"""
    return data_minutes is None


def are_names_unique() -> bool:
    """sumary_line"""
    return len(data_name) != len(set(data_name))


def turn_to_int(str_list: List[str]) -> List[int]:
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    new_list = []
    for string in str_list:
        try:
            new_list.append(int(string))
        except ValueError:
            return None
    return new_list


if __name__ == "__main__":
    app.run(debug=True)
