import pickledb




def set_db(dbname):
    assert(dbname is not None)
    return pickledb.load(dbname, True)

def set_dict_name(db, dname):
    try:
        if db.dgetall(dname):
            return True
        else:
            return db.dcreate(dname)
    except KeyError as e:
        return db.dcreate(dname)

def set_dict_items(db, name, keyvalue):
    return db.dadd(name, keyvalue)

def get_dict_item(db, name, key):
    try:
       return db.dget(name, key)
    except KeyError as e:
        return None
    
def get_dict(db, dname):
    try:
        return db.dgetall(dname)
    except KeyError as e:
        return None

    
def remove_dict(db, dname):
    try:
        return db.drem(dname)
    except KeyError as e:
        return None



def update_dict_item(db, name, key, value):
    try:
        db.dpop(name, key)
    except KeyError as e:
        pass
    keyvalue = (key, value)
    db.dadd(name, keyvalue)
