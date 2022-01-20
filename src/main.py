from numpy.core.arrayprint import dtype_is_implied
from comp62521 import app
from comp62521.database import database, mock_database
import sys
import os

if len(sys.argv) == 1:
    dataset = "Mock"
    db = mock_database.MockDatabase()
else:
    data_files = sys.argv[1:]
    dataset = ''
    for i in data_files:
        path, ds = os.path.split(i)
        print(f"Database: path={path} name={ds}")
        dataset = dataset + ds + ' '
    db = database.Database()
    if not db.read(data_files):
        sys.exit(1)

try:
    db.remove_duplicate_publications()
except:
    print("     WARNING!!   Duplicated publications remove is failed!!!")

app.config['DATASET'] = dataset.split()
app.config['DATABASE'] = db
app.config['SECRET_KEY'] = 'super secret key'

if "DEBUG" in os.environ:
    app.config['DEBUG'] = True

if "TESTING" in os.environ:
    app.config['TESTING'] = True

app.run(host='0.0.0.0', port=9292)
