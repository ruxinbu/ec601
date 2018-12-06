def connect_to_mysql():
    import mysql.connector
    
    username = "Enter your username"
    password = "Enter your password"
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user=username,
            passwd=password,
            database="twitterapi"
        )
    except:
        print("Wrong username or password.")
   
    return mydb

