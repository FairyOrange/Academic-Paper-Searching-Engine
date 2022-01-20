from flask.helpers import url_for
from comp62521 import app
from comp62521.database import database
from flask import render_template, request, flash, redirect
import string


def format_data(data):
    fmt = "%.2f"
    result = []
    for item in data:
        if type(item) is list:
            result.append(", ".join([(fmt % i).rstrip('0').rstrip('.') for i in item]))
        else:
            result.append((fmt % item).rstrip('0').rstrip('.'))
    return result


@app.route("/averages")
def showAverages():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset, "id": "averages", 'title': "Averaged Data"}
    tables = []
    headers = ["Average", "Conference Paper", "Journal", "Book", "Book Chapter", "All Publications"]
    averages = [database.Stat.MEAN, database.Stat.MEDIAN, database.Stat.MODE]
    tables.append({
        "id": 1,
        "title": "Average Authors per Publication",
        "header": headers,
        "rows": [
            [database.Stat.STR[i]]
            + format_data(db.get_average_authors_per_publication(i)[1])
            for i in averages]})
    tables.append({
        "id": 2,
        "title": "Average Publications per Author",
        "header": headers,
        "rows": [
            [database.Stat.STR[i]]
            + format_data(db.get_average_publications_per_author(i)[1])
            for i in averages]})
    tables.append({
        "id": 3,
        "title": "Average Publications in a Year",
        "header": headers,
        "rows": [
            [database.Stat.STR[i]]
            + format_data(db.get_average_publications_in_a_year(i)[1])
            for i in averages]})
    tables.append({
        "id": 4,
        "title": "Average Authors in a Year",
        "header": headers,
        "rows": [
            [database.Stat.STR[i]]
            + format_data(db.get_average_authors_in_a_year(i)[1])
            for i in averages]})

    args['tables'] = tables
    return render_template("averages.html", args=args)


@app.route("/coauthors")
def showCoAuthors():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters", "All Publications"]
    args = {"dataset": dataset, "id": "coauthors", "title": "Co-Authors"}

    start_year = db.min_year
    if "start_year" in request.args:
        start_year = int(request.args.get("start_year"))

    end_year = db.max_year
    if "end_year" in request.args:
        end_year = int(request.args.get("end_year"))

    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))

    args["data"] = db.get_coauthor_data(start_year, end_year, pub_type)
    args["data_len"] = len(args["data"][1])
    
    data_list = []
    for i in args["data"][1]:
        data_list.append(i) 
    table = str.maketrans('', '',string.digits)
    for i in range(len(data_list)):
        data_list[i] = data_list[i][0]
        data_list[i] = data_list[i].translate(table)
        data_list[i] = data_list[i].strip()
    
    args["author_names"] = data_list 
    
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_type"] = pub_type
    args["min_year"] = db.min_year
    args["max_year"] = db.max_year
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_str"] = PUB_TYPES[pub_type]
    return render_template("coauthors.html", args=args)


@app.route("/")
def showStatisticsMenu():
    dataset = app.config['DATASET']
    args = {"dataset": dataset}
    return render_template('statistics.html', args=args)


@app.route("/statisticsdetails/<status>")
def showPublicationSummary(status):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset, "id": status}

    if status == "publication_summary":
        args["title"] = "Publication Summary"
        args["data"] = db.get_publication_summary()

    if status == "publication_year":
        args["title"] = "Publication by Year"
        args["data"] = db.get_publications_by_year()

    if status == "author_year":
        args["title"] = "Author by Year"
        args["data"] = db.get_author_totals_by_year()

    return render_template('statistics_details.html', args=args)

@app.route("/statisticsdetailslink/<status>")
def showPublicationSummaryLink(status):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset, "id": status}

    if status == "publication_author":
        args["title"] = "Author Publication"
        args["data"] = db.get_publications_by_author()
    
    if status == "author_apperance":
        args["title"] = "First/Last Appearance on paper by Author"
        args["data"] = db.get_appearance_by_author()

    return render_template('statistics_details_link.html', args=args)

@app.route("/authorappearance", methods=['GET'])
def showAuthorAppearance():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset}

    args["title"] = "Author First/Last Appearance on paper by Publication Type"
    args["data"] = db.get_appearance_by_author_by_publications()
    args["num_pub_types"] = len(args["data"][0])
    
    name = request.args.get('author_name')

    try:
        if name:
            args["data"] = db.get_appearance_by_author_by_publications(name)
            return render_template('authorappearance.html', args=args)
    
    except:
        return "No author name found"
        
    return render_template('authorappearance.html', args=args)


@app.route("/searchauthorpub/", methods=['GET'])
def search_author_pub():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset}
    args["title"] = "Search Individual Author Publication"

    headers = ["Author Name", "Year", "Number of conference papers",
               "Number of journals", "Number of books",
               "Number of book chapters", "Total Number of Publications"]
    args['data'] = [headers, [" ", 0, 0, 0, 0, 0]]

    start_year = db.min_year
    if "start_year" in request.args:
        start_year = int(request.args.get("start_year"))

    end_year = db.max_year
    if "end_year" in request.args:
        end_year = int(request.args.get("end_year"))

    args["start_year"] = start_year
    args["end_year"] = end_year
    args["min_year"] = db.min_year
    args["max_year"] = db.max_year

    name = request.args.get('author_name')
    args["pub_str"] = "Stats"

    try:
        if name:
            args["data"] = db.get_author_pub_by_year(name)
            # args["author_name"] = args['data'][1][0][0]
            args["author_stats"] = []
            for i in range(len(args['data'][1])):
                if start_year <= int(args['data'][1][i][1]) <= end_year:
                    args["author_stats"] += [args['data'][1][i]]
            return render_template('searchauthorpub.html', args=args)

    except:
        return "No author name found"

    return render_template('searchauthorpub.html', args=args)


@app.route("/searchauthor/", methods=['GET'])
def search_author():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset}
    args["title"] = "Search Author by his name"

    headers = ["Author", "Number of conference paper",
                  "Number of journals", "Number of books",
                  "Number of book chapters", "Number of Publications", "Number of co-authors",
                  "Number of first author", "Number of last author"]
    
    args['data'] = [headers, [["", 0, 0, 0, 0, 0, 0, 0, 0]]]
    args["author_name"] = []
    args["author_stats"] = []
    args["num_authors"] = len(args["author_name"])

    name = request.args.get('author_name')
    
    try:
        if name:
            args["data"] = db.get_author_info_by_search(name)
            args["author_name"] = [i[0] for i in args['data'][1]]
            args["author_stats"] = [i[1:] for i in args['data'][1]]
            args["num_authors"] = len(args["author_name"])
            return render_template('searchauthor.html', args=args)
    
    except:
        return "No author name found"
    
    return render_template('searchauthor.html', args=args)
    
@app.route("/authorinfo/<authorname>")
def post_author(authorname):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset}
    args['authorname'] = str(authorname)

    args['title'] = "Author Information"
    try:
        args['data'] = db.get_single_author_info(authorname)
        args['ex_info'] = db.get_external_coauthor(authorname)
    except:
        return "No author name found"

    return render_template("author_info.html", args=args)



@app.route("/separation", methods=['GET'])
def get_separation_between_authors():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset}
    args["title"] = "Get Separation Between Two Authors"

    headers = ["Author 1", "Author 2", "Degrees of separation"]
    args['data'] = [headers, [" ", " ", 0]]

    name1 = request.args.get('author1')
    name2 = request.args.get('author2')

    try:
        if name1 and name2:
            args["data"] = db.get_separation(name1, name2)
            print(args["data"])
            return render_template('separation.html', args=args)
    
    except:
        return "No author name found!"
    
    return render_template('separation.html', args=args)    
