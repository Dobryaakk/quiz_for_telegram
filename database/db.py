import psycopg2


class Quiz:

    def __init__(self, host, user, password, db_name):
        self.connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name)
        self.cur = self.connection.cursor()
        self.create_table()

    def create_table(self):
        try:
            with self.connection:
                self.cur.execute(
                    """CREATE TABLE IF NOT EXISTS polls(
                    id serial PRIMARY KEY,
                    photo_id varchar(255),
                    poll_title varchar(255),
                    option_1 varchar(255),
                    option_2 varchar(255),
                    option_3 varchar(255),
                    option_4 varchar(255),
                    option_5 varchar(255),
                    correct_option serial,
                    option_6 varchar(255)
                    );"""
                )
                print('[INFO] polls table created')

                self.cur.execute(
                    """CREATE TABLE IF NOT EXISTS schedule(
                    id serial PRIMARY KEY,
                    hours serial,
                    minutes serial
                    );""")
                print('[INFO] schedule table created')

        except Exception as ex:
            print(ex)

    def insert_data(self, idd, poll_title, options, correct_option, option):
        with self.connection:
            self.cur.execute(
                """INSERT INTO polls (
                photo_id,
                poll_title,
                option_1,
                option_2,
                option_3,
                option_4,
                option_5,
                correct_option,
                option_6) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                (
                    idd,
                    poll_title,
                    options.split('\n')[0],
                    options.split('\n')[1],
                    options.split('\n')[2],
                    options.split('\n')[3],
                    options.split('\n')[4],
                    correct_option,
                    option
                )
            )
            print('[INFO] Data inserted into polls table')

    def insert_data_time(self, hours, minutes):
        with self.connection:
            self.cur.execute("""
            INSERT INTO schedule (id, hours, minutes)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET hours = EXCLUDED.hours, minutes = EXCLUDED.minutes;""",
                             (1, hours, minutes))

    def select_polls(self):
        with self.connection:
            self.cur.execute("""
            SELECT * FROM polls LIMIT 1;""")
            poll_data = self.cur.fetchone()
            return poll_data

    def select_time_send_polls(self):
        with self.connection:
            self.cur.execute("""
            SELECT hours, minutes FROM schedule;""")
            result = self.cur.fetchone()
            return result

    def delete_polls(self, id_deleted):
        with self.connection:
            self.cur.execute("""
            DELETE FROM polls WHERE id = %s;""", (id_deleted, ))

    def show_quiz(self):
        with self.connection:
            self.cur.execute("""
            SELECT COUNT(*) FROM polls;""")
            result = self.cur.fetchone()
        return result

