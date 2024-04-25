import psycopg2

class DatabaseConnection:
    def __init__(self):
        self.connection = None

    
    def connect(self, host, user, password, database):
        self.connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        print('Connected to database!!')

        return self.connection


    def close(self):
        self.connection.close()
        print('Connection closed!!')
