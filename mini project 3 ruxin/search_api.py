from create_mongodb import connect_to_mongodb
from create_mysql import connect_to_mysql
def search_api(dbkind):
    tag_name = input("Please input the tag you want to search: ")
    
    if dbkind == "mysql":
        mydb = connect_to_mysql()
        sqlcursor = mydb.cursor(buffered=True)
        ## show images_data

        sqlcursor.execute("SELECT img_id FROM tag_col WHERE description= '"+tag_name+"'")

        results = sqlcursor.fetchall()
        if len(results) == 0:
            print("0 image with this tag.")
        else:
            print("\n"+"Images with this tag: "+"\n")
            image_ids = []
            for result in results:
                image_ids.append(result[0])
            for image in image_ids:
                sqlcursor.execute("SELECT * FROM image_col WHERE img_id= '"+image+"'")
                print("img_id = "+ image+"\n")
                results = sqlcursor.fetchall()
                for result in results:
                    print(result)
                print("\n")
        mydb.commit()
        mydb.close()


    #Implement with MongoDB      
    elif dbkind == "mongodb":
        mydb = connect_to_mongodb()
        image_col = mydb["image_col"]
        tag_col = mydb["tag_col"]
        results = tag_col.find({ "description": tag_name })
        length = results.count()
        if length == 0:
            print("0 image with this tag.")
        else:
            print("\n"+"Images with this tag: "+"\n")
            image_ids = []
            for result in results:
                image_ids.append(result['img_id'])
            for image in image_ids:
                
                results = image_col.find({ "_id": image})
                
                for result in results:
                    print(result)

    else:
        print("Unknown databse.")
        return