from os import path
import unittest

from comp62521.database import database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        directory, _ = path.split(__file__)
        self.data_dir = path.join(directory, "..", "data")

    def test_read(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        self.assertEqual(len(db.publications), 1)
        self.assertEqual(db.max_year, 9999)
        self.assertEqual(db.min_year, 9999)

    def test_db_read(self):
        db = database.Database()
        db.read(path.join(self.data_dir, "dblp_curated_sample.xml"))
        self.assertFalse(db.read(path.join(self.data_dir, "error.xml")))
        self.assertTrue(db.read([path.join(self.data_dir, "dblp_curated_sample.xml"),
                                 path.join(self.data_dir, "dblp_curated_sample_half.xml"),
                                 path.join(self.data_dir, "dblp_curated_sample_half.xml")]))

    def test_read_invalid_xml(self):
        db = database.Database()
        self.assertFalse(db.read([path.join(self.data_dir, "invalid_xml_file.xml")]))

    def test_read_missing_year(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "missing_year.xml")]))
        self.assertEqual(len(db.publications), 0)

    def test_read_missing_title(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "missing_title.xml")]))
        # publications with missing titles should be added
        self.assertEqual(len(db.publications), 1)

    def test_init_publication_without_year(self):
        pb = database.Publication(2, 'testpublication', None, ['author1'], '/testpublication')
        self.assertEqual(pb.year, -1)

    def test_get_average_authors_per_publication(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "sprint-2-acceptance-1.xml")]))
        _, data = db.get_average_authors_per_publication(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.3, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 2, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MODE)
        self.assertEqual(data[0], [2])

    def test_get_average_publications_per_author(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "sprint-2-acceptance-2.xml")]))
        _, data = db.get_average_publications_per_author(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MODE)
        self.assertEqual(data[0], [0, 1, 2, 3])

    def test_get_average_publications_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "sprint-2-acceptance-3.xml")]))
        _, data = db.get_average_publications_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.5, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [3])

    def test_get_average_authors_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "sprint-2-acceptance-4.xml")]))
        _, data = db.get_average_authors_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.8, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [0, 2, 4, 5])
        # additional test for union of authors
        self.assertEqual(data[-1], [0, 2, 4, 5])

    def test_get_publication_summary(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        header, data = db.get_publication_summary()
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data[0]), 6, "incorrect number of columns in data")
        self.assertEqual(len(data), 2, "incorrect number of rows in data")
        self.assertEqual(data[0][1], 1, "incorrect number of publications for conference papers")
        self.assertEqual(data[1][1], 2, "incorrect number of authors for conference papers")

    def test_get_average_authors_per_publication_by_author(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "three-authors-and-three-publications.xml")]))
        header, data = db.get_average_authors_per_publication_by_author(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 3, "incorrect average of number of conference papers")
        self.assertEqual(data[0][1], 1.5, "incorrect mean journals for author1")
        self.assertEqual(data[1][1], 2, "incorrect mean journals for author2")
        self.assertEqual(data[2][1], 1, "incorrect mean journals for author3")

    def test_get_publications_by_author(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        header, data = db.get_publications_by_author()
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 2, "incorrect number of authors")
        self.assertEqual(data[0][-1], 1, "incorrect total")

    def test_get_average_publications_per_author_by_year(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        header, data = db.get_average_publications_per_author_by_year(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0][0], 9999, "incorrect year in result")

    def test_get_publications_by_year(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        header, data = db.get_publications_by_year()
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0][0], 9999, "incorrect year in result")

    def test_get_author_totals_by_year(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        header, data = db.get_author_totals_by_year()
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0][0], 9999, "incorrect year in result")
        self.assertEqual(data[0][1], 2, "incorrect number of authors in result")

    def test_get_all_authors(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        authors = list(db.get_all_authors())
        self.assertEqual(authors, ['AUTHOR1', 'AUTHOR2'], "incorrect authors in result")

    def test_get_coauthor_details(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        coauthors = db.get_coauthor_details('AUTHOR1')
        self.assertEqual(coauthors, [('AUTHOR1', 1), ('AUTHOR2', 1)], "incorrect coauthors in result")

    def test_get_coauthor_data(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        coauthors = db.get_coauthor_data(9999, 9999, database.Publication.CONFERENCE_PAPER)
        self.assertEqual(coauthors,
                         (('Author', 'Co-Authors'), [['AUTHOR1 1', 'AUTHOR2 1'], ['AUTHOR2 1', 'AUTHOR1 1']]),
                         "incorrect coauthors in result")

    def test_get_average_authors_per_publication_by_year(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        header, data = db.get_average_authors_per_publication_by_year(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0][0], 9999, "incorrect year in result")
        self.assertEqual(data[0][1], 2.0, "incorrect number of conference papers in result")
        self.assertEqual(data[0][2], 0, "incorrect number of journals in result")
        self.assertEqual(data[0][3], 0, "incorrect number of books in result")
        self.assertEqual(data[0][4], 0, "incorrect number of book chapers in result")
        self.assertEqual(data[0][5], 2.0, "incorrect number of all publications in result")

    def test_get_publication_summary_average(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        header, data = db.get_publication_summary_average(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 2, "incorrect number of rows")
        self.assertEqual(data[0][0], "Mean authors per publication",
                         "incorrect title(Mean authors per publication) in result")
        self.assertEqual(data[0][1], 2.0, "incorrect number of conference papers in result")
        self.assertEqual(data[0][2], 0, "incorrect number of journals in result")
        self.assertEqual(data[0][3], 0, "incorrect number of books in result")
        self.assertEqual(data[0][4], 0, "incorrect number of book chapers in result")
        self.assertEqual(data[0][5], 2.0, "incorrect number of all publications in result")

        self.assertEqual(data[1][0], "Mean publications per author",
                         "incorrect title(Mean publications per author) in result")
        self.assertEqual(data[1][1], 1.0, "incorrect number of conference papers in result")
        self.assertEqual(data[1][2], 0, "incorrect number of journals in result")
        self.assertEqual(data[1][3], 0, "incorrect number of books in result")
        self.assertEqual(data[1][4], 0, "incorrect number of book chapers in result")
        self.assertEqual(data[1][5], 1.0, "incorrect number of all publications in result")

    def test_add_100000_publications(self):
        db = database.Database()
        for i in range(0, 100000):
            db.add_publication(1, '%d' % i, 2001, ['author1'], "test")
        self.assertEqual(len(db.publications), 100000, "Adding publication number 100000 (number of authors is 1)")

    def test_get_network_data(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "simple.xml")]))
        nodes, links = db.get_network_data()
        self.assertEqual(nodes, [['AUTHOR1', 1], ['AUTHOR2', 1]])
        self.assertEqual(links, {(0, 1)})

    def test_startElement_with_name_in_titletags(self):
        db = database.Database()
        handler = database.DocumentHandler(db)
        handler.startElement("sub", None)
        self.assertEqual(handler.tag, None)
        self.assertEqual(handler.pub_type, None)

    def test_endElement_with_name_in_titletags(self):
        db = database.Database()
        handler = database.DocumentHandler(db)
        handler.pub_type = 3
        handler.endElement("sub")
        self.assertEqual(handler.authors, [])
        self.assertEqual(handler.title, None)
        self.assertEqual(handler.year, None)

    def test_get_appearance_by_author(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "three-authors-and-three-publications.xml")]))
        header, data = db.get_appearance_by_author()
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 3, "incorrect number of rows")
        self.assertEqual(data[0], ['author1', 1, 0, 1], "incorrect author appearance times in result")
        self.assertEqual(data[1], ['author2', 0, 1, 0], "incorrect author appearance times in result")
        self.assertEqual(data[2], ['author3', 0, 0, 1], "incorrect author appearance times in result")
        self.assertTrue(db.read([path.join(self.data_dir, "sprint-2-acceptance-4.xml")]))
        header, data = db.get_appearance_by_author()
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 7, "incorrect number of rows")
        self.assertEqual(data[0], ['AUTHOR1', 1, 0, 2], "incorrect author appearance times in result")
        self.assertEqual(data[1], ['AUTHOR2', 0, 1, 0], "incorrect author appearance times in result")
        self.assertEqual(data[2], ['AUTHOR3', 2, 1, 0], "incorrect author appearance times in result")
        self.assertEqual(data[3], ['AUTHOR4', 0, 2, 0], "incorrect author appearance times in result")
        self.assertEqual(data[4], ['AUTHOR6', 1, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[5], ['AUTHOR7', 0, 0, 1], "incorrect author appearance times in result")
        self.assertEqual(data[6], ['AUTHOR8', 0, 0, 2], "incorrect author appearance times in result")

    def test_get_author_info_by_search(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "dblp_curated_sample.xml")]))
        header, data = db.get_author_info_by_search("Stefano Ceri")
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(data[0], ['Stefano Ceri', 100, 94, 6, 18, 218, 230, 78, 25],
                         "incorrect author information in search result")
        header, data = db.get_author_info_by_search("Norman W. Paton")
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(data[0], ['Norman W. Paton', 102, 71, 1, 6, 180, 242, 21, 57],
                         "incorrect author information in search result")
        self.assertRaises(ValueError, db.get_author_info_by_search, "Non-exist")
        self.assertRaises(ValueError, db.get_author_info_by_search, "")

        # Test partial match
        self.assertTrue(db.read([path.join(self.data_dir, "sprint2review/dblp_2006_2010_205_papers.xml")]))
        header, data = db.get_author_info_by_search("wang")
        self.assertEqual(2, len(data), "the number of authors doesn't match")
        self.assertEqual(data[0], ['Hai Wang', 2, 0, 0, 0, 2, 7, 0, 1], 'incorrect author info')
        self.assertEqual(data[1], ['Yimin Wang', 1, 0, 0, 0, 1, 3, 1, 0], 'incorrect author info')

        # More tests for partial match
        header, data = db.get_author_info_by_search("robert")
        self.assertEqual(2, len(data), "the number of authors doesn't match")
        self.assertEqual(data[0], ['Robert Stevens', 34, 24, 0, 2, 60, 173, 6, 23], 'incorrect author info')
        self.assertEqual(data[1], ['Robert D. Stevens', 0, 1, 0, 0, 1, 6, 0, 0], 'incorrect author info')

        header, data = db.get_author_info_by_search("stevens")
        self.assertEqual(3, len(data), "the number of authors doesn't match")
        self.assertEqual(data[0], ['Margaret Stevens', 1, 0, 0, 0, 1, 1, 0, 1], 'incorrect author info')
        self.assertEqual(data[1], ['Robert Stevens', 34, 24, 0, 2, 60, 173, 6, 23], 'incorrect author info')
        self.assertEqual(data[2], ['Robert D. Stevens', 0, 1, 0, 0, 1, 6, 0, 0], 'incorrect author info')

        header, data = db.get_author_info_by_search("ua")
        self.assertEqual(6, len(data), "the number of authors doesn't match")
        self.assertEqual(data[0], ['Juan I. Castrillo', 0, 1, 0, 0, 1, 11, 0, 0], 'incorrect author info')
        self.assertEqual(data[1], ['Jesualdo Toms Fernndez-Breis', 1, 0, 0, 0, 1, 4, 1, 0], 'incorrect author info')
        self.assertEqual(data[2], ['Chenjuan Guo', 1, 0, 0, 0, 1, 6, 0, 0], 'incorrect author info')
        self.assertEqual(data[3], ['Stuart Owen', 3, 2, 0, 0, 5, 35, 0, 0], 'incorrect author info')
        self.assertEqual(data[4], ['Carlos Eduardo Scheidegger', 0, 1, 0, 0, 1, 49, 0, 0], 'incorrect author info')
        self.assertEqual(data[5], ['Fang Siyuan', 0, 1, 0, 0, 1, 2, 1, 0], 'incorrect author info')

        # Test sorting
        self.assertTrue(db.read([path.join(self.data_dir, "sprint3-4-sort.xml")]))
        header, data = db.get_author_info_by_search("sam")
        self.assertEqual(14, len(data), "the number of authors doesn't match")
        self.assertEqual(data[0], ['Alice Sam', 1, 0, 0, 0, 1, 13, 1, 0], 'incorrect author info')
        self.assertEqual(data[1], ['Brian Sam', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[2], ['Alice Sammer', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[3], ['Brian Sammer', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[4], ['Alice Samming', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[5], ['Brian Samming', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[6], ['Sam Alice', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[7], ['Sam Brian', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[8], ['Samuel Alice', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[9], ['Samuel Brian', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[10], ['Brian Sam Alice', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[11], ['Alice Sam Brian', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[12], ['Alice Esam', 1, 0, 0, 0, 1, 13, 0, 0], 'incorrect author info')
        self.assertEqual(data[13], ['Brian Esam', 1, 0, 0, 0, 1, 13, 0, 1], 'incorrect author info')

    def test_get_appearance_by_author_by_publications(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "sprint-3-2-test-1.xml")]))

        header_publication, header_author, data = db.get_appearance_by_author_by_publications("AUTHOR1")
        self.assertEqual(len(header_publication), 5, "header size doesn't match")
        self.assertEqual(len(header_author), 4, "header size doesn't match")
        self.assertEqual(len(data), 5, "incorrect number of columns")
        self.assertEqual(data[0][0], ['AUTHOR1', 1, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[1][0], ['AUTHOR1', 2, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[2][0], ['AUTHOR1', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[3][0], ['AUTHOR1', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[4][0], ['AUTHOR1', 3, 0, 0], "incorrect author appearance times in result")

        self.assertRaises(ValueError, db.get_appearance_by_author_by_publications, "AUTHOR5")
        self.assertRaises(ValueError, db.get_appearance_by_author_by_publications, "")

        header_publication, header_author, data = db.get_appearance_by_author_by_publications()
        self.assertEqual(len(header_publication), 5, "header size doesn't match")
        self.assertEqual(len(header_author), 4, "header size doesn't match")
        self.assertEqual(len(data), 5, "incorrect number of columns")
        # Conference
        self.assertEqual(len(data[0]), 4, "incorrect number of rows")
        self.assertEqual(data[0][0], ['AUTHOR1', 1, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[0][1], ['AUTHOR2', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[0][2], ['AUTHOR3', 1, 1, 0], "incorrect author appearance times in result")
        self.assertEqual(data[0][3], ['AUTHOR4', 0, 1, 0], "incorrect author appearance times in result")
        # Journal
        self.assertEqual(len(data[1]), 4, "incorrect number of rows")
        self.assertEqual(data[1][0], ['AUTHOR1', 2, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[1][1], ['AUTHOR2', 0, 1, 0], "incorrect author appearance times in result")
        self.assertEqual(data[1][2], ['AUTHOR3', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[1][3], ['AUTHOR4', 0, 1, 0], "incorrect author appearance times in result")
        # Book
        self.assertEqual(len(data[2]), 4, "incorrect number of rows")
        self.assertEqual(data[2][0], ['AUTHOR1', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[2][1], ['AUTHOR2', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[2][2], ['AUTHOR3', 0, 0, 1], "incorrect author appearance times in result")
        self.assertEqual(data[2][3], ['AUTHOR4', 0, 0, 0], "incorrect author appearance times in result")
        # Book chapter
        self.assertEqual(len(data[3]), 4, "incorrect number of rows")
        self.assertEqual(data[3][0], ['AUTHOR1', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[3][1], ['AUTHOR2', 1, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[3][2], ['AUTHOR3', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[3][3], ['AUTHOR4', 0, 1, 0], "incorrect author appearance times in result")
        # All Types
        self.assertEqual(len(data[4]), 4, "incorrect number of rows")
        self.assertEqual(data[4][0], ['AUTHOR1', 3, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[4][1], ['AUTHOR2', 1, 1, 0], "incorrect author appearance times in result")
        self.assertEqual(data[4][2], ['AUTHOR3', 1, 1, 1], "incorrect author appearance times in result")
        self.assertEqual(data[4][3], ['AUTHOR4', 0, 3, 0], "incorrect author appearance times in result")

        self.assertTrue(db.read([path.join(self.data_dir, "sprint-3-2-test-2.xml")]))
        header_publication, header_author, data = db.get_appearance_by_author_by_publications()
        self.assertEqual(len(header_publication), 5, "header size doesn't match")
        self.assertEqual(len(header_author), 4, "header size doesn't match")
        self.assertEqual(len(data), 5, "incorrect number of columns")
        # Conference
        self.assertEqual(len(data[0]), 4, "incorrect number of rows")
        self.assertEqual(data[0][0], ['AUTHOR2', 1, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[0][1], ['AUTHOR4', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[0][2], ['AUTHOR1', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[0][3], ['AUTHOR3', 0, 1, 1], "incorrect author appearance times in result")

        # Journal
        self.assertEqual(len(data[1]), 4, "incorrect number of rows")
        self.assertEqual(data[1][0], ['AUTHOR2', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[1][1], ['AUTHOR4', 1, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[1][2], ['AUTHOR1', 0, 1, 1], "incorrect author appearance times in result")
        self.assertEqual(data[1][3], ['AUTHOR3', 0, 0, 0], "incorrect author appearance times in result")

        # Book
        self.assertEqual(len(data[2]), 4, "incorrect number of rows")
        self.assertEqual(data[2][0], ['AUTHOR2', 0, 1, 0], "incorrect author appearance times in result")
        self.assertEqual(data[2][1], ['AUTHOR4', 0, 0, 1], "incorrect author appearance times in result")
        self.assertEqual(data[2][2], ['AUTHOR1', 1, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[2][3], ['AUTHOR3', 0, 0, 0], "incorrect author appearance times in result")

        # Book chapter
        self.assertEqual(len(data[3]), 4, "incorrect number of rows")
        self.assertEqual(data[3][0], ['AUTHOR2', 0, 0, 1], "incorrect author appearance times in result")
        self.assertEqual(data[3][1], ['AUTHOR4', 1, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[3][2], ['AUTHOR1', 0, 0, 0], "incorrect author appearance times in result")
        self.assertEqual(data[3][3], ['AUTHOR3', 0, 1, 0], "incorrect author appearance times in result")
        # All Types
        self.assertEqual(len(data[4]), 4, "incorrect number of rows")
        self.assertEqual(data[4][0], ['AUTHOR2', 1, 1, 1], "incorrect author appearance times in result")
        self.assertEqual(data[4][1], ['AUTHOR4', 2, 0, 1], "incorrect author appearance times in result")
        self.assertEqual(data[4][2], ['AUTHOR1', 1, 1, 1], "incorrect author appearance times in result")
        self.assertEqual(data[4][3], ['AUTHOR3', 0, 2, 1], "incorrect author appearance times in result")

    def test_get_single_author_info(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "dblp_curated_sample.xml")]))
        # Stefano Ceri
        header, data = db.get_single_author_info("Stefano Ceri")
        self.assertEqual(data[0],
                         'overall: 218, journal articles: 94, conference papers: 100, books: 6, book chapters: 18',
                         'incorrect number of publication')
        self.assertEqual(data[1],
                         'overall: 78, journal articles: 43, conference papers: 28, books: 3, book chapters: 4',
                         'incorrect number of first author')
        self.assertEqual(data[2],
                         'overall: 25, journal articles: 10, conference papers: 10, books: 0, book chapters: 5',
                         'incorrect number of last author')
        self.assertEqual(data[3], 'overall: 8, journal articles: 0, conference papers: 7, books: 0, book chapters: 1',
                         'incorrect number of sole author')
        self.assertEqual(data[4], '230', 'incorrect number of co-authors')

        # Test1
        self.assertTrue(db.read([path.join(self.data_dir, "sprint-3-2-test-1.xml")]))
        header, data = db.get_single_author_info("AUTHOR1")
        self.assertEqual(data[0], 'overall: 3, journal articles: 2, conference papers: 1, books: 0, book chapters: 0',
                         'incorrect number of publication')
        self.assertEqual(data[1], 'overall: 3, journal articles: 2, conference papers: 1, books: 0, book chapters: 0',
                         'incorrect number of first author')
        self.assertEqual(data[2], 'overall: 0, journal articles: 0, conference papers: 0, books: 0, book chapters: 0',
                         'incorrect number of last author')
        self.assertEqual(data[3], 'overall: 0, journal articles: 0, conference papers: 0, books: 0, book chapters: 0',
                         'incorrect number of sole author')
        self.assertEqual(data[4], '3', 'incorrect number of co-authors')

        # Test2
        self.assertTrue(db.read([path.join(self.data_dir, "sprint2review/dblp_2006_2010_205_papers.xml")]))
        header, data = db.get_single_author_info("Robert Stevens")
        self.assertEqual(data[0],
                         'overall: 60, journal articles: 24, conference papers: 34, books: 0, book chapters: 2',
                         'incorrect number of publication')
        self.assertEqual(data[1], 'overall: 6, journal articles: 2, conference papers: 3, books: 0, book chapters: 1',
                         'incorrect number of first author')
        self.assertEqual(data[2], 'overall: 23, journal articles: 6, conference papers: 17, books: 0, book chapters: 0',
                         'incorrect number of last author')
        self.assertEqual(data[3], 'overall: 0, journal articles: 0, conference papers: 0, books: 0, book chapters: 0',
                         'incorrect number of last author')
        self.assertEqual(data[4], '173', 'incorrect number of co-author')

        # Error handle
        self.assertRaises(ValueError, db.get_single_author_info, "Non-exist")
        self.assertRaises(ValueError, db.get_single_author_info, "")

    def test_get_author_pub_by_year(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "sprint3.5-example1.xml")]))
        header, data = db.get_author_pub_by_year('author1')
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 3, "incorrect number of rows")
        self.assertEqual(data[0], ["author1", "2000", 2, 2, 3, 0, 7], "incorrect author information in search result")
        self.assertEqual(data[1], ["author1", "2001", 0, 2, 1, 1, 4], "incorrect author information in search result")
        self.assertEqual(data[2], ["author1", "2002", 0, 0, 0, 1, 1], "incorrect author information in search result")
        header, data = db.get_author_pub_by_year('author2')
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0], ["author2", "2001", 0, 0, 1, 3, 4], "incorrect author information in search result")
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        header, data = db.get_author_pub_by_year('Carole A. Goble')
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 3, "incorrect number of rows")
        self.assertEqual(data[0], ["Carole A. Goble", "2004", 1, 0, 0, 0, 1],
                         "incorrect author information in search result")
        self.assertEqual(data[1], ["Carole A. Goble", "2006", 1, 0, 0, 0, 1],
                         "incorrect author information in search result")
        self.assertEqual(data[2], ["Carole A. Goble", "2008", 0, 1, 0, 0, 1],
                         "incorrect author information in search result")
        header, data = db.get_author_pub_by_year('Robert Stevens')
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 2, "incorrect number of rows")
        self.assertEqual(data[0], ["Robert Stevens", "2004", 1, 0, 0, 0, 1],
                         "incorrect author information in search result")
        self.assertEqual(data[1], ["Robert Stevens", "2008", 0, 1, 0, 0, 1],
                         "incorrect author information in search result")
        header, data = db.get_author_pub_by_year('Stefano Ceri')
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0], ["Stefano Ceri", "1997", 0, 0, 1, 1, 2],
                         "incorrect author information in search result")

        # Error handle
        self.assertRaises(ValueError, db.get_author_pub_by_year, "Non-exist")
        self.assertRaises(ValueError, db.get_author_pub_by_year, "")

    def test_get_degree_separation_authors(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "sprint3.7-example.xml")]))

        header, data = db.get_separation('Author C', 'Author D')
        self.assertEqual(len(header), len(data), "header and data column size doesn't match")
        self.assertEqual(data, ['Author C', 'Author D', 1], "incorrect author appearance times in result")

        header, data = db.get_separation('Author A', 'Author B')
        self.assertEqual(len(header), len(data), "header and data column size doesn't match")
        self.assertEqual(data, ['Author A', 'Author B', 0], "incorrect author appearance times in result")

        header, data = db.get_separation('Author E', 'Author C')
        self.assertEqual(len(header), len(data), "header and data column size doesn't match")
        self.assertEqual(data, ['Author E', 'Author C', 2], "incorrect author appearance times in result")

        header, data = db.get_separation('Author A', 'Author F')
        self.assertEqual(len(header), len(data), "header and data column size doesn't match")
        self.assertEqual(data, ['Author A', 'Author F', 'X'], "incorrect author appearance times in result")

        header, data = db.get_separation('Author A', 'Author A')
        self.assertEqual(len(header), len(data), "header and data column size doesn't match")
        self.assertEqual(data, ['Author A', 'Author A', -1], "incorrect author appearance times in result")

        self.assertRaises(KeyError, db.get_separation, "Author A", "Author Unknown")
        self.assertRaises(KeyError, db.get_separation, "", "Author C")
        self.assertRaises(KeyError, db.get_separation, "Author Unknown1", "Author Unknown2")

    def test_get_external_coauthor(self):
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "dblp_curated_sample.xml")]))

        header, data = db.get_external_coauthor("Markel Vigo")
        self.assertEqual(len(header), len(data), "header and data column size doesn't match")
        self.assertEqual(data[0], 2, "incorrect external coauthers in result")

        header, data = db.get_external_coauthor("Bijan Parsia")
        self.assertEqual(len(header), len(data), "header and data column size doesn't match")
        self.assertEqual(data[0], 5, "incorrect external coauthers in result")

        header, data = db.get_external_coauthor("Markel Vigo")
        self.assertEqual(len(header), len(data), "header and data column size doesn't match")
        self.assertEqual(data[1], ["Giorgio Brajnik", "Yeliz Yesilada"], "incorrect external coauthers in result")

        header, data = db.get_external_coauthor("Bijan Parsia")
        self.assertEqual(len(header), len(data), "header and data column size doesn't match")
        self.assertEqual(data[1],
                         ["Klitos Christodoulou", "Alvaro A. A. Fernandes", "Cornelia Hedeler", "Alan L. Rector",
                          "Patrice Seyed"],
                         "incorrect external coauthers in result")

        self.assertRaises(KeyError, db.get_external_coauthor, "Author Unknown")

    def test_multifiles_input(self):  # Test for sprint4.2
        db = database.Database()
        self.assertTrue(db.read([path.join(self.data_dir, "sprint-2-acceptance-1.xml"),
                                 path.join(self.data_dir, "sprint-2-acceptance-2.xml")]))
        header, data = db.get_publications_by_author_year()
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 4, "incorrect number of rows")
        self.assertEqual(data[0], ["AUTHOR1", "9999", 5, 0, 0, 0, 5], "incorrect author information in search result")
        self.assertEqual(data[1], ["AUTHOR2", "9999", 2, 0, 1, 0, 3], "incorrect author information in search result")
        self.assertEqual(data[2], ["AUTHOR3", "9999", 2, 0, 0, 0, 2], "incorrect author information in search result")
        self.assertEqual(data[3], ["AUTHOR4", "9999", 4, 0, 0, 0, 4], "incorrect author information in search result")

    def test_multifiles_invalid_input(self):
        db = database.Database()
        self.assertFalse(
            db.read([path.join(self.data_dir, "invalid_xml_file.xml"), path.join(self.data_dir, "simple.xml")]))

    def test_remove_duplicate_publications(self):
        db = database.Database()
        # two duplicate files input
        self.assertTrue(db.read([path.join(self.data_dir, "file_1.xml"), path.join(self.data_dir, "file_1.xml")]))
        db.remove_duplicate_publications()
        self.assertEqual(len(db.publications), 1, "remove duplicate pulications not working")

        # three duplicate files input
        self.assertTrue(db.read([path.join(self.data_dir, "file_1.xml"), path.join(self.data_dir, "file_1.xml"),
                                 path.join(self.data_dir, "file_1.xml")]))
        db.remove_duplicate_publications()
        self.assertEqual(len(db.publications), 1, "remove duplicate pulications not working")

        # complex test 1
        self.assertTrue(db.read(
            [path.join(self.data_dir, "dblp_curated_sample.xml"), path.join(self.data_dir, "dblp_curated_sample.xml"),
             path.join(self.data_dir, "dblp_curated_sample.xml")]))
        self.assertEqual(len(db.publications), 2796,
                         "incorrect number of publications before remove duplicate operation")
        db.remove_duplicate_publications()
        self.assertEqual(len(db.publications), 932, "incorrect number of publications after remove duplicate operation")

        # complex test 2
        self.assertTrue(db.read([path.join(self.data_dir, "dblp_curated_sample.xml"),
                                 path.join(self.data_dir, "dblp_curated_sample_half.xml"),
                                 path.join(self.data_dir, "dblp_curated_sample_half.xml")]))
        self.assertEqual(len(db.publications), 996,
                         "incorrect number of publications before remove duplicate operation")
        db.remove_duplicate_publications()
        self.assertEqual(len(db.publications), 932, "incorrect number of publications after remove duplicate operation")


if __name__ == '__main__':
    unittest.main()
