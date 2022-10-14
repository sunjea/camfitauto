import sqlite3
import logging

logger = logging.getLogger(__name__)

def createTable() :
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS CampingListInfo_T(IDX INTEGER, CAMP_NAME TEXT, _ID TEXT);')
    cursor.execute('CREATE TABLE IF NOT EXISTS ZoneListInfo_T(IDX INTEGER, ZONE_NAME TEXT, _ID TEXT);')
    cursor.execute('CREATE TABLE IF NOT EXISTS SiteListInfo_T(IDX INTEGER, SITE_NAME TEXT, _ID TEXT);')
    conn.close()


def insertCampingInfo(idx, name, _id):
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT _ID FROM CampingListInfo_T WHERE _ID=:_ID ;',{"_ID": _id})
    
    rows = cursor.fetchone()    
    if rows == None :
        logger.info(f' == insertCampingInfo : {idx}, {name}, {_id} ')
        cursor.execute('INSERT INTO CampingListInfo_T VALUES(:IDX, :CAMP_NAME, :_ID);', {"IDX":idx, "CAMP_NAME":name, "_ID":_id})  
        conn.commit()
    conn.close()

def insertZoneInfo(idx, name, _id):
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT _ID FROM ZoneListInfo_T WHERE _ID=:_ID ;',{"_ID": _id})
    
    rows = cursor.fetchone()    
    if rows == None :
        logger.info(f' == insertZoneInfo : {idx}, {name}, {_id} ')
        cursor.execute('INSERT INTO ZoneListInfo_T VALUES(:IDX, :ZONE_NAME, :_ID);', {"IDX":idx, "ZONE_NAME":name, "_ID":_id})  
        conn.commit()
    conn.close()

def insertSiteInfo(idx, name, _id):
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT _ID FROM SiteListInfo_T WHERE _ID=:_ID ;',{"_ID": _id})
    
    rows = cursor.fetchone()    
    if rows == None :
        logger.info(f' == insertSiteInfo : {idx}, {name}, {_id} ')
        cursor.execute('INSERT INTO SiteListInfo_T VALUES(:IDX, :SITE_NAME, :_ID);', {"IDX":idx, "SITE_NAME":name, "_ID":_id})  
        conn.commit()
    conn.close()


def getSelectCampId(idx, name):
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT _id FROM CampingListInfo_T WHERE IDX=:IDX AND CAMP_NAME=:CAMP_NAME;',{"IDX": idx, "CAMP_NAME": name})
    rows = cursor.fetchone()    
    if rows == None :
        rows = 0    
    else :
        rows = rows[0]
    conn.close()
    return rows

def getSelectZoneId(idx, name):
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT _id FROM ZoneListInfo_T WHERE IDX=:IDX AND ZONE_NAME=:ZONE_NAME;',{"IDX": idx, "ZONE_NAME": name})
    rows = cursor.fetchone()    
    if rows == None :
        rows = 0    
    else :
        rows = rows[0]
    conn.close()
    return rows

def getSelectSiteId(idx, name):
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT _id FROM SiteListInfo_T WHERE IDX=:IDX AND SITE_NAME=:SITE_NAME;',{"IDX": idx, "SITE_NAME": name})
    rows = cursor.fetchone()    
    if rows == None :
        rows = 0    
    else :
        rows = rows[0]
    conn.close()
    return rows


# def db_get_articleid():
#     conn = sqlite3.connect('./keydata.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT Article_Id FROM ArticleInfo ORDER BY Article_Id LIMIT 1;')
    
#     rows = cursor.fetchone()
#     if rows == None :
#         rows = 0
#     else :
#         rows = rows[0]
#     return rows

# def db_set_articleid(article_id):
#     conn = sqlite3.connect('./keydata.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT Article_Id FROM ArticleInfo ORDER BY Article_Id LIMIT 1;')
    
#     rows = cursor.fetchone()
#     if rows != None :
#         cursor.execute('DELETE FROM ArticleInfo;')
        
#     print('db_set_articleid : {0}'.format(article_id))
#     cursor.execute('INSERT INTO ArticleInfo VALUES(:Article_Id);', {"Article_Id":article_id})
    
#     conn.commit()
#     conn.close()