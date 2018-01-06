# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web

import dbconn
dbconn.register_dsn("host=localhost dbname=examdb user=examdbo password=pass")


class BaseReqHandler(tornado.web.RequestHandler):

    def db_cursor(self, autocommit=True):
        return dbconn.SimpleDataCursor(autocommit=autocommit)
    

class MainHandler(BaseReqHandler):
    def get(self):
        with self.db_cursor() as cur:
            sql = '''
            SELECT t.tname, c.cname, s.sname, se.place, se.times, t.tn, c.cn, s.sn
            FROM schedule as se
            INNER JOIN teacher as t ON se.tea_tn=t.tn
            INNER JOIN course  as c ON se.cou_cn=c.cn
            INNER JOIN student as s ON se.stu_sn=s.sn
            ORDER BY tea_tn,cou_cn,stu_sn;
            '''
            cur.execute(sql)
            items = cur.fetchall()
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.render("list.html", title="课程表", items=items)

class StudentHandler(BaseReqHandler):
    def get(self):
        with self.db_cursor() as cur:
            sql = '''
            SELECT s.sn, s.sname,c.cname, c.week, t.tname, se.times, se.place
            FROM schedule as se
            INNER JOIN teacher as t ON se.tea_tn=t.tn
            INNER JOIN course  as c ON se.cou_cn=c.cn
            INNER JOIN student as s ON se.stu_sn=s.sn
            ORDER BY tea_tn,cou_cn,stu_sn;
            '''
            cur.execute(sql)
            items = cur.fetchall()
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.render("student.html", title="学生课程表", items=items)

class TeacherHandler(BaseReqHandler):
    def get(self):
        with self.db_cursor() as cur:
            sql = '''
            SELECT t.tn, s.sn, s.sname, c.cname, c.week, t.tname, se.times, se.place
            FROM schedule as se
            INNER JOIN teacher as t ON se.tea_tn=t.tn
            INNER JOIN course  as c ON se.cou_cn=c.cn
            INNER JOIN student as s ON se.stu_sn=s.sn
            ORDER BY tea_tn,cou_cn,stu_sn;
            '''
            cur.execute(sql)
            items = cur.fetchall()
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.render("teacher.html", title="教师排课表", items=items)



class GradeAddHandler(BaseReqHandler):
    def post(self):
        tea_tn = str(self.get_argument("tea_tn"))
        cou_cn = str(self.get_argument("cou_cn"))
        stu_sn = str(self.get_argument("stu_sn"))
        times = str(self.get_argument("times"))
        place = str(self.get_argument("place"))

        
        with self.db_cursor() as cur:
            sql = '''INSERT INTO schedule
            (tea_tn, cou_cn, stu_sn, times, place) VALUES (%s, %s, %s, %s, %s);'''
            cur.execute(sql, (tea_tn, cou_cn, stu_sn, times, place))
            cur.commit()
        
        self.set_header("Content-Type", "text/html; charset=UTF-8") 
        self.redirect("/")

class GradeDelHandler(BaseReqHandler):
    def get(self, tea_tn, cou_cn, stu_sn):
        tea_tn = str(tea_tn)
        cou_cn = str(cou_cn)
        stu_sn = str(stu_sn)
        
        with self.db_cursor() as cur:
            sql = '''DELETE FROM schedule
                         WHERE tea_tn= %s AND cou_cn =%s AND stu_sn=%s;'''
            cur.execute(sql, (tea_tn, cou_cn, stu_sn))
            cur.commit()

        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.redirect("/")

class GradeEditHandler(BaseReqHandler):
    def get(self, tea_tn, cou_cn, stu_sn):
        tea_tn = str(tea_tn)
        cou_cn = str(cou_cn)
        stu_sn = str(stu_sn)

        self.set_header("Content-Type", "text/html; charset=UTF-8")
        with self.db_cursor() as cur:
            sql = '''SELECT times, place FROM schedule
                        WHERE tea_tn= %s AND cou_cn =%s AND stu_sn=%s;
            '''
            cur.execute(sql, (tea_tn, cou_cn, stu_sn))
            row = cur.fetchone()
            if row:
                self.render("edit.html", tea_tn=tea_tn, 
                    cou_cn=cou_cn, stu_sn=stu_sn, times=row[0], place=row[1])
            else:
                self.write('Not FOUND!')
    
    def post(self, tea_tn, cou_cn, stu_sn):
        tea_tn = str(tea_tn)
        cou_cn = str(cou_cn)
        stu_sn = str(stu_sn)
        times  = str(self.get_argument("times"))
        place  = str(self.get_argument("place"))
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        with self.db_cursor() as cur:
            sql = '''UPDATE schedule SET times=%s, place=%s
                        WHERE tea_tn= %s AND cou_cn =%s AND stu_sn=%s;
            '''
            cur.execute(sql, (times, place, tea_tn, cou_cn, stu_sn))
            cur.commit()
        self.redirect("/")
        

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/grade.add", GradeAddHandler),
    (r"/grade.del/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)", GradeDelHandler),
    (r"/grade.edit/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)", GradeEditHandler),
    (r"/grade.student",StudentHandler),
    (r"/grade.teacher",TeacherHandler)
], debug=True)


if __name__ == "__main__":
    application.listen(8888)
    server = tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(lambda: None, 500, server).start()
    server.start()

