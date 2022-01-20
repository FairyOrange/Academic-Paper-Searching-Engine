
from werkzeug.exceptions import NotFound
from comp62521.statistics import average
import itertools
import numpy as np
import xml.sax

PublicationType = ["Conference Paper", "Journal", "Book", "Book Chapter"]


class Publication:
    CONFERENCE_PAPER = 0
    JOURNAL = 1
    BOOK = 2
    BOOK_CHAPTER = 3

    def __init__(self, pub_type, title, year, authors, key):
        self.pub_type = pub_type
        self.title = title
        if year:
            self.year = int(year)
        else:
            self.year = -1
        self.authors = authors
        self.key = key


class Author:
    def __init__(self, name):
        self.name = name


class Stat:
    STR = ["Mean", "Median", "Mode"]
    FUNC = [average.mean, average.median, average.mode]
    MEAN = 0
    MEDIAN = 1
    MODE = 2


class Database:
    def __init__(self):
        self.publications = []
        self.authors = []
        self.author_idx = {}
        self.min_year = None
        self.max_year = None

    def read(self, filenames):
        self.publications = []
        self.authors = []
        self.author_idx = {}
        self.min_year = None
        self.max_year = None

        handler = DocumentHandler(self)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        valid = True
        if isinstance(filenames, str):
            infile = open(filenames, "r")
            try:
                parser.parse(infile)
            except xml.sax.SAXException as e:
                valid = False
                print("Error reading file (" + e.getMessage() + ")")
            infile.close()
        else:
            if len(filenames) == 1:
                infile = open(filenames[0], "r")
                try:
                    parser.parse(infile)
                except xml.sax.SAXException as e:
                    valid = False
                    print("Error reading file (" + e.getMessage() + ")")
                infile.close()
            else:
                for file in filenames:
                    infile = open(file, "r")
                    try:
                        parser.parse(infile)
                    except xml.sax.SAXException as e:
                        valid = False
                        print("Error reading file (" + e.getMessage() + ")")
                    infile.close()



        # ** repeat check, delete for line coverage **
        # for p in self.publications:
        #     if self.min_year is None or p.year < self.min_year:
        #         self.min_year = p.year
        #     if self.max_year is None or p.year > self.max_year:
        #         self.max_year = p.year

        return valid

    def get_all_authors(self):
        return self.author_idx.keys()

    def get_coauthor_data(self, start_year, end_year, pub_type):
        coauthors = {}
        for p in self.publications:
            if ((start_year is None or p.year >= start_year) and
                    (end_year is None or p.year <= end_year) and
                    (pub_type == 4 or pub_type == p.pub_type)):
                for a in p.authors:
                    for a2 in p.authors:
                        if a != a2:
                            try:
                                coauthors[a].add(a2)
                            except KeyError:
                                coauthors[a] = set([a2])

        def display(db, coauthors, author_id):
            return f"{db.authors[author_id].name} {len(coauthors[author_id])}"

        header = ("Author", "Co-Authors")
        data = []
        for a in coauthors:
            data.append([display(self, coauthors, a),
                         ", ".join([
                             display(self, coauthors, ca) for ca in coauthors[a]])])

        return header, data

    def get_average_authors_per_publication(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [func(auth_per_pub[i]) for i in np.arange(4)] + [func(list(itertools.chain(*auth_per_pub)))]
        return header, data

    def get_average_publications_per_author(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))

        for p in self.publications:
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [func(pub_per_auth[:, i]) for i in np.arange(4)] + [func(pub_per_auth.sum(axis=1))]
        return header, data

    def get_average_publications_in_a_year(self, av):
        header = ("Conference Paper",
                  "Journal", "Book", "Book Chapter", "All Publications")

        ystats = np.zeros((int(self.max_year) - int(self.min_year) + 1, 4))

        for p in self.publications:
            ystats[p.year - self.min_year][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [func(ystats[:, i]) for i in np.arange(4)] + [func(ystats.sum(axis=1))]
        return header, data

    def get_average_authors_in_a_year(self, av):
        header = ("Conference Paper",
                  "Journal", "Book", "Book Chapter", "All Publications")

        yauth = [[set(), set(), set(), set(), set()] for _ in range(int(self.min_year), int(self.max_year) + 1)]

        for p in self.publications:
            for a in p.authors:
                yauth[p.year - self.min_year][p.pub_type].add(a)
                yauth[p.year - self.min_year][4].add(a)

        ystats = np.array([[len(S) for S in y] for y in yauth])

        func = Stat.FUNC[av]

        data = [func(ystats[:, i]) for i in np.arange(5)]
        return header, data

    def get_publication_summary_average(self, av):
        header = ("Details", "Conference Paper",
                  "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))
        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        name = Stat.STR[av]
        func = Stat.FUNC[av]

        data = [
            [name + " authors per publication"]
            + [func(auth_per_pub[i]) for i in np.arange(4)]
            + [func(list(itertools.chain(*auth_per_pub)))],
            [name + " publications per author"]
            + [func(pub_per_auth[:, i]) for i in np.arange(4)]
            + [func(pub_per_auth.sum(axis=1))]]
        return header, data

    def get_publication_summary(self):
        header = ("Details", "Conference Paper",
                  "Journal", "Book", "Book Chapter", "Total")

        plist = [0, 0, 0, 0]
        alist = [set(), set(), set(), set()]

        for p in self.publications:
            plist[p.pub_type] += 1
            for a in p.authors:
                alist[p.pub_type].add(a)
        # create union of all authors
        ua = alist[0] | alist[1] | alist[2] | alist[3]

        data = [
            ["Number of publications"] + plist + [sum(plist)],
            ["Number of authors"] + [len(a) for a in alist] + [len(ua)]]
        return header, data

    def get_average_authors_per_publication_by_author(self, av):
        header = ("Author", "Number of conference papers",
                  "Number of journals", "Number of books",
                  "Number of book chapers", "All publications")

        astats = [[[], [], [], []] for _ in range(len(self.authors))]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [[self.authors[i].name]
                + [func(L) for L in astats[i]]
                + [func(list(itertools.chain(*astats[i])))]
                for i in range(len(astats))]
        return header, data

    def get_publications_by_author(self):
        header = ("Author", "Number of conference papers",
                  "Number of journals", "Number of book",
                  "Number of book chapers", "Total")

        astats = [[0, 0, 0, 0] for _ in range(len(self.authors))]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type] += 1

        data = [[self.authors[i].name] + astats[i] + [sum(astats[i])]
                for i in range(len(astats))]
        return header, data

    def get_publications_by_author_year(self):
        header = ("Author Name", "Year", "Number of conference papers",
                  "Number of journals", "Number of books",
                  "Number of book chapters", "Total")

        aystats = {}
        for p in self.publications:
            for a in p.authors:
                key = self.authors[a].name + '#' + str(p.year)
                if aystats.get(key) is None:
                    aystats[key] = [0, 0, 0, 0]
                aystats[key][p.pub_type] += 1
        data = [[ay.split('#')[0]] + [ay.split('#')[1]] + aystats[ay] + [sum(aystats[ay])] for ay in aystats]
        return header, data

    def get_author_pub_by_year(self, author_name):
        header = ("Author Name", "Year", "Number of conference papers",
                  "Number of journals", "Number of books",
                  "Number of book chapters", "Total Number of Publications")

        author_list = [i.name for i in self.authors]

        author_list_sorted = Database.partial_search_by_author_name(author_list, author_name)

        if len(author_list_sorted) == 0:
            raise ValueError

        data = []
        _, pub_stat = self.get_publications_by_author_year()

        for i in author_list_sorted:
            single_author_data = []
            for j in range(len(pub_stat)):
                if pub_stat[j][0] == i:
                    single_author_data.append(pub_stat[j])
            single_author_data.sort(key=lambda t: t[1])
            data += single_author_data

        return header, data

    def get_appearance_by_author(self):
        header = ("Author Name", "First author", "Last author", "Sole author")

        astats = [[0, 0, 0] for _ in range(len(self.authors))]

        for i in range(len(self.authors)):
            for p in self.publications:
                if (self.author_idx[self.authors[i].name] == p.authors[0]) and (len(p.authors) == 1):
                    astats[i][2] += 1
                else:
                    if self.author_idx[self.authors[i].name] == p.authors[0]:
                        astats[i][0] += 1

                    if self.author_idx[self.authors[i].name] == p.authors[-1]:
                        astats[i][1] += 1

        data = [[self.authors[i].name] + astats[i] for i in range(len(astats))]

        return header, data
    
    def get_appearance_by_author_by_publications(self, author_name=None):
        header_publication = ("Conference Papers", "Journals", "Books", "Book Chapers", "All Types")
        header_author = ("Author Name", "First author", "Last author", "Sole author")
        
        author_list = [i.name for i in self.authors] 

        astats = [[[0, 0, 0] for _ in range(len(author_list))] for t in range(len(PublicationType)+1)]

        for i in range(len(author_list)):
            for p in self.publications:
                p_type = p.pub_type
                if (self.author_idx[author_list[i]] == p.authors[0]) and (len(p.authors) == 1):
                    astats[p_type][i][2] += 1
                    astats[-1][i][2] += 1
                else:
                    if self.author_idx[author_list[i]] == p.authors[0]:
                        astats[p_type][i][0] += 1
                        astats[-1][i][0] += 1

                    if self.author_idx[author_list[i]] == p.authors[-1]:
                        astats[p_type][i][1] += 1
                        astats[-1][i][1] += 1

        data = [([[author_list[i]] + astats[t][i] for i in range(len(astats[t]))]) for t in range(len(astats))]

        def search(author_name):
            author_found = False
            author_name_list = Database.partial_search_by_author_name(author_list, author_name)
            data_author = [[] for i in range(len(PublicationType)+1)]
            for k in author_name_list:
                for i in range(len(data)):
                    for j in range(len(data[i])):                   
                        if data[i][j][0] == k:
                            data_author[i].append(data[i][j])
                            author_found = True
            
            if author_found == False:
                raise ValueError
            
            return data_author
            
        if author_name is not None:
            data = search(author_name)
        
        return header_publication, header_author, data
    
    def partial_search_by_author_name(author_name_list, author_name):
        
        author_list = []
        
        if author_name is not None and len(author_name) > 0:       
            for i in range(len(author_name_list)):
                author_found = False
                full_name = author_name_list[i]
                full_name_l = full_name.lower()
                input_name_l = author_name.lower()
                partial_name = full_name_l.split()
                if author_name == full_name:
                    author_list.append((author_name, 0))
                    author_found = True
                else:
                    full_name_l = full_name.lower()
                    input_name_l = author_name.lower()
                    partial_name = full_name_l.split()
                    for j in range(len(partial_name)):                
                        if input_name_l == partial_name[j]:
                            if j == len(partial_name) - 1:
                                author_list.append((full_name, 1))
                            elif j == 0:
                                author_list.append((full_name, 3))
                            else:
                                author_list.append((full_name, 5))
                            author_found = True
                            break
                        
                    if author_found == False:
                        if input_name_l in partial_name[-1][0:len(input_name_l)]:
                            author_list.append((full_name, 2))
                            author_found = True
                        elif input_name_l in partial_name[0][0:len(input_name_l)]:
                            author_list.append((full_name, 4))
                            author_found = True
                        elif input_name_l in full_name_l:
                            author_list.append((full_name, 6))
                            author_found = True
                          
        author_list = sorted(author_list, key=lambda p: (p[1], p[0].split()[-1], p[0].split()[0]))   
        author_list_sorted = [i[0] for i in author_list]
        return author_list_sorted

    def get_author_info_by_search(self, author_name):
        header = ("Author", "Number of conference papers",
                  "Number of journals", "Number of books",
                  "Number of book chapters", "Number of Publications", "Number of co-authors",
                  "Number of first author", "Number of last author")
        
        author_list = [i.name for i in self.authors]

        author_list_sorted = Database.partial_search_by_author_name(author_list, author_name)

        if len(author_list_sorted) == 0:
            raise ValueError
        
        data = []
        
        for i in author_list_sorted:
            index = self.author_idx[i]
    
            _, pub_stat = self.get_publications_by_author()
            coauthors = {}
            for p in self.publications:
                for a in p.authors:
                    for a2 in p.authors: 
                        if a != a2:
                            try:
                                coauthors[a].add(a2)
                            except KeyError:
                                coauthors[a] = set([a2])
            co_author_stat = list(coauthors[index])
            #_, co_author_stat = self.get_coauthor_data()
            _, app_stat = self.get_appearance_by_author()
    
            data.append([self.authors[index].name] + list(pub_stat[index][1:]) + [len(co_author_stat)] + list(app_stat[index][1:3]))
            
        return header, data

    def get_single_author_info(self, author_name):
        header = ("Number of publications", "Number of times first author", 
                  "Number of times last author", "Number of times sole author", 
                  "Number of co-authors")

        try:
            index = self.author_idx[author_name]
        except:
            raise ValueError

        def display(stat):
            return f"overall: {stat[0]}, journal articles: {stat[1]}, conference papers: {stat[2]}, books: {stat[3]}, book chapters: {stat[4]}"

        # Publication stat
        _, pub_stat = self.get_author_info_by_search(author_name)
        
        pub_stat = pub_stat[0]
        
        num_of_pub = [pub_stat[5], pub_stat[2], pub_stat[1], pub_stat[3], pub_stat[4]]

        # First author
        _, fa_stat_oa = self.get_appearance_by_author()
        _, _, fa_stat = self.get_appearance_by_author_by_publications()
        num_of_fa = [fa_stat_oa[index][1], fa_stat[1][index][1], fa_stat[0][index][1], fa_stat[2][index][1], fa_stat[3][index][1]]

        # Last author
        num_of_la = [fa_stat_oa[index][2], fa_stat[1][index][2], fa_stat[0][index][2], fa_stat[2][index][2], fa_stat[3][index][2]]

        # Sole author
        num_of_sa = [fa_stat_oa[index][3], fa_stat[1][index][3], fa_stat[0][index][3], fa_stat[2][index][3], fa_stat[3][index][3]]

        # Co-authors
        num_of_co = pub_stat[6]

        data = []
        data.append(display(num_of_pub))
        data.append(display(num_of_fa))
        data.append(display(num_of_la))
        data.append(display(num_of_sa))
        data.append(str(num_of_co))

        return header, data

    def get_average_authors_per_publication_by_year(self, av):
        header = ("Year", "Conference papers",
                  "Journals", "Books",
                  "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type].append(len(p.authors))
            except KeyError:
                ystats[p.year] = [[], [], [], []]
                ystats[p.year][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [[y]
                + [func(L) for L in ystats[y]]
                + [func(list(itertools.chain(*ystats[y])))]
                for y in ystats]
        return header, data

    def get_publications_by_year(self):
        header = ("Year", "Number of conference papers",
                  "Number of journals", "Number of books",
                  "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type] += 1
            except KeyError:
                ystats[p.year] = [0, 0, 0, 0]
                ystats[p.year][p.pub_type] += 1

        data = [[y] + ystats[y] + [sum(ystats[y])] for y in ystats]
        return header, data

    def get_average_publications_per_author_by_year(self, av):
        header = ("Year", "Conference papers",
                  "Journals", "Books",
                  "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year]
            except KeyError:
                s = np.zeros((len(self.authors), 4))
                ystats[p.year] = s
            for a in p.authors:
                s[a][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [[y]
                + [func(ystats[y][:, i]) for i in np.arange(4)]
                + [func(ystats[y].sum(axis=1))]
                for y in ystats]
        return header, data

    def get_author_totals_by_year(self):
        header = ("Year", "Number of conference papers",
                  "Number of journals", "Number of books",
                  "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year][p.pub_type]
            except KeyError:
                ystats[p.year] = [set(), set(), set(), set()]
                s = ystats[p.year][p.pub_type]
            for a in p.authors:
                s.add(a)
        data = [[y] + [len(s) for s in ystats[y]] + [len(ystats[y][0] | ystats[y][1] | ystats[y][2] | ystats[y][3])]
                for y in ystats]
        return header, data

    def add_publication(self, pub_type, title, year, authors, key):
        if year is None or len(authors) == 0:
            print("Warning: excluding publication due to missing information")
            print("    Publication type:", PublicationType[pub_type])
            print("    Title:", title)
            print("    Year:", year)
            print("    Authors:", ",".join(authors))
            print("    Key: {}".format(key))
            return
        if title is None:
            print(f"Warning: adding publication with missing title "
                  f"[ {PublicationType[pub_type]} {year} ({','.join(authors)}) ]")
        idlist = []
        for a in authors:
            try:
                idlist.append(self.author_idx[a])
            except KeyError:
                a_id = len(self.authors)
                self.author_idx[a] = a_id
                idlist.append(a_id)
                self.authors.append(Author(a))
        self.publications.append(
            Publication(pub_type, title, year, idlist, key))
        if (len(self.publications) % 100000) == 0:
            print(
                f"Adding publication number {len(self.publications)} "
                f"(number of authors is {len(self.authors)})")

        if self.min_year is None or year < self.min_year:
            self.min_year = year
        if self.max_year is None or year > self.max_year:
            self.max_year = year

    def _get_collaborations(self, author_id, include_self):
        data = {}
        for p in self.publications:
            if author_id in p.authors:
                for a in p.authors:
                    try:
                        data[a] += 1
                    except KeyError:
                        data[a] = 1
        if not include_self:
            del data[author_id]
        return data

    def get_coauthor_details(self, name):
        author_id = self.author_idx[name]
        data = self._get_collaborations(author_id, True)
        return [(self.authors[key].name, data[key])
                for key in data]

    def get_network_data(self):
        na = len(self.authors)

        nodes = [[self.authors[i].name, -1] for i in range(na)]
        links = set()
        for a in range(na):
            collab = self._get_collaborations(a, False)
            nodes[a][1] = len(collab)
            for a2 in collab:
                if a < a2:
                    links.add((a, a2))
        return nodes, links
    
    def get_separation(self, author1, author2):
        header = ("Author 1", "Author 2", "Degrees of separation")
        try:
            index1 = self.author_idx[author1]
            index2 = self.author_idx[author2]
        except:
            raise KeyError
        
        queue = [index1]
        separation = ['X']*len(self.authors)
        separation[index1] = 0
        visited = [False]*len(self.authors)
        #initialize separation list
        
        while len(queue) != 0: #bfs
            l = len(queue)
            for i in range(l):
                head = queue.pop(0) #pop the first in the queue
                if visited[head]:
                    continue
                visited[head] = True
                collab = self._get_collaborations(head, False) #get collab
                for key in collab:
                    if separation[key] == 'X':
                        separation[key] = separation[head] + 1
                    else:
                        separation[key] = min(separation[head]+1, separation[key])
                    if not visited[key]:
                        queue.append(key)

        sep = separation[index2]
        if sep == 'X':
            result = sep
        else:
            result = sep - 1
        data = [author1, author2, result]
        return header, data

    def remove_duplicate_publications(self):
        key_store = []

        print("     There are {} publications got read".format(len(self.publications)))
        print("---------------")
        print("     The publication objects read have keys: ")
        for i in range(len(self.publications)):
            print("     Title: {}       Key: {}".format(self.publications[i].title, self.publications[i].key))
        print("---------------")
        for i in range(len(self.publications)-1, -1, -1):
            if self.publications[i].key not in key_store:
                key_store.append(self.publications[i].key)
            elif self.publications[i].key in key_store:
                self.publications.remove(self.publications[i])
                print("     Publication number {} is duplicated and deleted".format(i+1))

        print("---------------")
        print("     The publication objects read now have keys: ")
        for i in range(len(self.publications)):
            print("     Title: {}       Key: {}".format(self.publications[i].title, self.publications[i].key))

    def get_external_coauthor(self, author_name):
        header = ("Number of external co-authors", "List of external co-authors")
        try:
            index = self.author_idx[author_name]
        except:
            raise KeyError

        #staff = get_staff()
        with open('src/comp62521/static/CS-staff.txt') as f:
            staffstr=f.read()
        stafflist = staffstr.split('\n')

        collab = self._get_collaborations(index, False)
        excount = 0
        exlist = []
        for key in collab:
            name = self.authors[key].name
            if name not in stafflist:
                excount+=1
                exlist.append(name)

        exlist.sort(key=lambda x: x.split()[-1])
        data = [excount, exlist]
        
        return header, data


class DocumentHandler(xml.sax.handler.ContentHandler):
    TITLE_TAGS = ["sub", "sup", "i", "tt", "ref"]
    PUB_TYPE = {
        "inproceedings": Publication.CONFERENCE_PAPER,
        "article": Publication.JOURNAL,
        "book": Publication.BOOK,
        "incollection": Publication.BOOK_CHAPTER}

    def __init__(self, db):
        super().__init__()
        self.tag = None
        self.chrs = ""
        self.clearData()
        self.db = db
        self.pub_type = None
        self.authors = []
        self.year = None
        self.title = None
        self.key = None

    def clearData(self):
        self.pub_type = None
        self.authors = []
        self.year = None
        self.title = None

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        if name in self.TITLE_TAGS:
            return
        if name in DocumentHandler.PUB_TYPE.keys():
            self.pub_type = DocumentHandler.PUB_TYPE[name]
            try:
                attrs.getValue("key")
                attrNames = attrs.getNames()
                if "key" in attrNames:
                    self.key = attrs.getValue("key")
                    #print(attrs.getValue("key"))
            except:
                self.key = "/void"

        self.tag = name
        self.chrs = ""

    def endElement(self, name):
        if self.pub_type is None:
            return
        if name in self.TITLE_TAGS:
            return
        d = self.chrs.strip()
        if self.tag == "author":
            self.authors.append(d)
        elif self.tag == "title":
            self.title = d
        elif self.tag == "year":
            self.year = int(d)
        elif name in DocumentHandler.PUB_TYPE.keys():
            self.db.add_publication(
                self.pub_type,
                self.title,
                self.year,
                self.authors,
                self.key)
            self.clearData()
        self.tag = None
        self.chrs = ""

    def characters(self, chrs):
        if self.pub_type is not None:
            self.chrs += chrs
