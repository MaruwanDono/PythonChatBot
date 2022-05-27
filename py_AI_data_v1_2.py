#Inspired by sentdex tutorial on youtube
#link: https://www.youtube.com/watch?v=dvOnYLDg8_Y&list=PLQVvvaa0QuDdc2k5dwtDTyT9aCja0on8j
import sqlite3
import json
import os

rootPath = os.getcwd()
#The data file name, also the database name
d_name = 'RC_2017-12'
date = d_name.split('_')[1]
sql_commands = []
comments_num = 0
sql_con = sqlite3.connect(rootPath + '/{}.db'.format(d_name))
c = sql_con.cursor()

#error with id UNIQUE, cant update column in case its complete
def create_db_tab():
    c.execute("CREATE TABLE IF NOT EXISTS parent_reply(parent_id TEXT, comment_id TEXT , parent TEXT, comment TEXT, subreddit TEXT, score INT)")

#test len, deleted removed score>0
def comment_pass(body, score):
    if len(body) > 40000 or len(body) < 1:
        return False
    elif body == '[removed]' or body == '[deleted]':
        return False
    elif score < 1:
        return False
    else :
        return True


def text_format_db(text):
    text = text.encode('utf-8')
    text = text.replace('\n', ' _back_to_line_ ').replace('\r', ' _back_to_line_ ').replace('"','*')
    return text


def collect_sql_commands(sql):
    global sql_commands
    global comments_num
    sql_commands.append(sql)
    if len(sql_commands) >= 1000:
        comments_num += len(sql_commands)
        for com in sql_commands:
            c.execute(com)
        sql_con.commit()
        sql_commands = []
        print("{} comments harvested from reddit data of {}...\n".format(str(comments_num),date))
    return

# score of comment may be score of parent at first, comparing is useless
def comm_has_parent(score, p_id):
    #parent[1] : score of reply for the parent if it exists
    c.execute("""SELECT comment,score,parent,comment_id FROM parent_reply WHERE comment_id = '{}' OR parent_id = '{}' LIMIT 1""".format(p_id.split('_')[1],p_id))
    parent = c.fetchone()
    if parent != None:
        if parent[2] != None and score < parent[1] and parent[3] != p_id.split('_')[1]:
            return False
        else :
            return parent
    else:
        return False

#Many possible children, which one ?, we chose the 1st found, to deal with later
#t1_ problem, not really a problem
#Apparently not needed, parents come before children, and so is the single/paired att, but I'll leave it for now
def comm_has_child(com_id):
    c.execute("SELECT comment_id,comment FROM parent_reply WHERE parent_id = 't1_{}' LIMIT 1".format(com_id))
    child = c.fetchone()
    if child != None:
        return child
    else:
        return False


def cleaning_db():
    c.execute("DELETE FROM parent_reply WHERE parent IS NULL")
    sql_con.commit()
    c.execute("VACUUM")
    sql_con.commit()

if __name__ == "__main__":
    create_db_tab()
    counter = 0
    with open(rootPath + '/{}'.format(d_name),buffering = 1000) as f:
        for line in f:
            counter += 1
            #print line.encode('utf-8')+'\n'
            line_json = json.loads(line)
            subreddit = line_json['subreddit']
            comment_id = line_json['id']
            parent_id = line_json['parent_id']
            body = line_json['body']
            score = line_json['score']
            #if comment_id.find('dql0j4v') != -1:
                #print 'parent_id = {}\ncomment_id = {}\nbody = {}\nsubreddit = {}\n\n'.format(parent_id, comment_id,body.encode('utf-8'),subreddit)
            #print 'score = {}\nBody = {}\n\n'.format(score,body.encode('utf-8'))
            #print 'parent_id = {}\ncomment_id = {}\n\n'.format(parent_id, comment_id)
            if comment_pass(body, score):
                body = text_format_db(body)
                no_parent_no_child = True
                parent = comm_has_parent(score, parent_id)
                #child = comm_has_child(comment_id)
                if parent:
                    no_parent_no_child = False
                    if parent[2] == None: #single parent
                        collect_sql_commands("""UPDATE parent_reply SET parent_id = "{}", comment_id = "{}", parent = "{}", comment = "{}", subreddit = "{}", score = {} WHERE comment_id ="{}";""".format(parent_id, comment_id, parent[0].encode('utf-8'), body, subreddit, score, parent_id.split('_')[1]))
                    elif parent[3] == parent_id.split('_')[1]:#parent with his parent
                        collect_sql_commands("""INSERT INTO parent_reply (parent_id, comment_id, parent, comment, subreddit, score) VALUES ("t1_{}","{}","{}","{}","{}",{});""".format(parent[3], comment_id, parent[0].encode('utf-8'), body, subreddit, score))
                    elif score > parent[1]: #parent with child with lower score
                        collect_sql_commands("""UPDATE parent_reply SET parent_id = "{}", comment_id = "{}", parent = "{}", comment = "{}", subreddit = "{}", score = {} WHERE parent_id ="{}";""".format(parent_id, comment_id, parent[2].encode('utf-8'), body, subreddit, score, parent_id))
                #if child:
                    #collect_sql_commands("""UPDATE parent_reply SET parent_id = "{}", comment_id = "{}", parent = "{}", comment = "{}", subreddit = "{}", score = {} WHERE parent_id ="t1_{}";""".format(comment_id, child[0], body, child[1].encode('utf-8'), subreddit, score, parent_id))
                    #no_parent_no_child = False

                if no_parent_no_child:
                    collect_sql_commands("""INSERT INTO parent_reply (parent_id, comment_id, comment, subreddit, score) VALUES ("{}","{}","{}","{}",{});""".format(parent_id, comment_id, body, subreddit, score))

    cleaning_db()
    print("Database {}.db created.".format(d_name))
