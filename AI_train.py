#Tutorial: https://www.youtube.com/watch?v=dvOnYLDg8_Y&list=PLQVvvaa0QuDdc2k5dwtDTyT9aCja0on8j
#Data sources: https://files.pushshift.io/reddit/comments/
import sqlite3
import os

rootPath = os.getcwd()
d_name = 'RC_2017-12_v1'
sql_con = sqlite3.connect(rootPath + '/{}.db'.format(d_name))
c = sql_con.cursor()
clean = True

def cleaning_db():
    print('Cleaning db...')
    c.execute("DELETE FROM parent_reply WHERE parent IS NULL")
    sql_con.commit()
    c.execute("VACUUM")
    sql_con.commit()
    print('Cleaning done.')


def write_to_file(name, parent_data, reply_data):
    with open(rootPath + '/training_model/parent_{}'.format(name),'a') as f:
        f.write(parent_data)
    with open(rootPath + '/training_model/reply_{}'.format(name),'a') as f:
        f.write(reply_data)

if __name__ == "__main__":
    if clean:
        cleaning_db()
    test = False
    chunk = 5000
    cur_len = chunk
    counter = 0
    while(cur_len == chunk):
        c.execute("SELECT parent,comment FROM parent_reply WHERE parent NOT NULL and score > 0 LIMIT {}, {}".format(counter*chunk,chunk))
        data = c.fetchall()
        parent = ''
        reply = ''
        for pair in data:
            parent += pair[0] + '\n'
            reply += pair[1] + '\n'
        if not test:
            write_to_file('test',parent,reply)
            test = True
        else:
            write_to_file('train',parent,reply)
        cur_len = len(data)
        counter +=1
