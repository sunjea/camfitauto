import sqlite3
import logging

logger = logging.getLogger(__name__)

def createTable() :
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS CampingListInfo_T(IDX INTEGER, CAMP_NAME TEXT, _ID TEXT);')
    cursor.execute('CREATE TABLE IF NOT EXISTS ZoneListInfo_T(IDX INTEGER, ZONE_NAME TEXT, _ID TEXT, CAMPE_ID TEXT);')
    cursor.execute('CREATE TABLE IF NOT EXISTS SiteListInfo_T(IDX INTEGER, SITE_NAME TEXT, _ID TEXT, ZONE_ID TEXT, CAMPE_ID TEXT);')
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

def insertZoneInfo(idx, name, _id, campId):
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT _ID FROM ZoneListInfo_T WHERE _ID=:_ID ;',{"_ID": _id})
    
    rows = cursor.fetchone()    
    if rows == None :
        logger.info(f' == insertZoneInfo : {idx}, {name}, {_id} ')
        cursor.execute('INSERT INTO ZoneListInfo_T VALUES(:IDX, :ZONE_NAME, :_ID, :CAMPE_ID);', {"IDX":idx, "ZONE_NAME":name, "_ID":_id, "CAMPE_ID":campId})  
        conn.commit()
    conn.close()

def insertSiteInfo(idx, name, _id, campId, zoneId):
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT _ID FROM SiteListInfo_T WHERE _ID=:_ID ;',{"_ID": _id})
    
    rows = cursor.fetchone()    
    if rows == None :
        logger.info(f' == insertSiteInfo : {idx}, {name}, {_id} ')
        cursor.execute('INSERT INTO SiteListInfo_T VALUES(:IDX, :SITE_NAME, :_ID, :ZONE_ID, :CAMPE_ID);', {"IDX":idx, "SITE_NAME":name, "_ID":_id, "ZONE_ID":zoneId , "CAMPE_ID":campId })  
        conn.commit()
    conn.close()


def getSelectCampId(idx, name):
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT _id FROM CampingListInfo_T WHERE IDX=:IDX AND CAMP_NAME = :CAMP_NAME;',{"IDX": idx, "CAMP_NAME":name})
    rows = cursor.fetchone()    
    if rows == None :
        rows = 0    
    else :
        rows = rows[0]
    logger.info(f' == getSelectCampId : {rows} ')
    conn.close()
    return rows

def getSelectZoneId(idx, camp_id):
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT _id FROM ZoneListInfo_T WHERE IDX=:IDX AND CAMPE_ID=:CAMPE_ID;',{"IDX": idx, "CAMPE_ID":camp_id})
    rows = cursor.fetchone()    
    if rows == None :
        rows = 0    
    else :
        rows = rows[0]
    logger.info(f' == getSelectZoneId : {rows} ')
    conn.close()
    return rows

def getSelectSiteId(idx, camp_id, zone_id):
    conn = sqlite3.connect('./keydata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT _id FROM SiteListInfo_T WHERE IDX=:IDX AND ZONE_ID=:ZONE_ID AND CAMPE_ID=:CAMPE_ID;',{"IDX": idx, "ZONE_ID":zone_id, "CAMPE_ID":camp_id})
    rows = cursor.fetchone()    
    if rows == None :
        rows = 0    
    else :
        rows = rows[0]
    logger.info(f' == getSelectSiteId : {rows} ')        
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