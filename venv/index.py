# encoding: utf-8
# Author    : Alan Liu <pickerxxr@gmail.com >
# Datetime  : 2020-7-7
# Product   : ${NBA Management system by Fudan 5012}
# Project   : ${PROJECT_NAME}
# explain   : PyQt5 NBA数据管理系统
import sys

import matplotlib
import numpy as np
from PyQt5.QtGui import QIcon
import icons_rc
from mplwidget_2 import *
matplotlib.use("Qt5Agg")
from mplwidget import *
from PyQt5.uic import loadUiType

import pyodbc
import hashlib
# 实现 ui和Logic的分离

from connect_mssql import connect_mssql, close_conn, connect_directly

ui, _ = loadUiType('main.ui')
login, _ = loadUiType('choose_user.ui')
normal_ui, _ = loadUiType('normal_user.ui')
hello_ui, _ = loadUiType('hello.ui')

class helloApp(QWidget, hello_ui):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Choose next")
        style = open("themes/darkorange.css", 'r')
        style = style.read()
        self.setStyleSheet(style)
        self.setWindowIcon(QIcon("./exe_icon.png"))

        self.pushButton_2.clicked.connect(self.manage)
        self.pushButton.clicked.connect(self.user_mode)
        self.pushButton_3.clicked.connect(self.close)

    def user_mode(self):
        self.main_app = LoginApp()
        self.main_app.show()

    def manage(self):
        self.main_app = MainApp()
        self.main_app.show()

class LoginApp(QWidget, login):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("login")

        self.init_user_button.clicked.connect(self.handle_login)
        style = open("themes/darkorange.css", 'r')
        style = style.read()
        self.setStyleSheet(style)
        self.setWindowIcon(QIcon("./exe_icon.jpg"))


    def md5(self, arg):
        hs = hashlib.md5(bytes("交大NB", encoding="utf-8"))
        hs.update(bytes(arg, encoding='utf-8'))
        return hs.hexdigest()

    def handle_login(self):
        conn_cur = connect_mssql('sa', 'Admin123456')
        name = self.name_init.text()
        pwd = self.pwd_init.text()
        pwd_hs = self.md5(pwd)
        sql = """USE nba_db
                 SELECT * FROM users WHERE user_name = '""" + name + "' and user_pwd = '" + pwd_hs + "';"

        conn_cur.execute(sql)
        while conn_cur.nextset():  # NB: This always skips the first result set
            try:
                results = conn_cur.fetchall()
                break
            except pyodbc.ProgrammingError:
                continue
        if results:
            self.main_app = normal_user()
            self.main_app.show()
            self.close()
        else:
            self.error_message.setText("用户名或密码错误，重新输入")


class normal_user(QMainWindow, normal_ui):

    # 定义构造方法
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handle_buttons()
        self.setWindowTitle("Normal user")
        self.setWindowIcon(QIcon("./exe_icon.png"))

        self.show()
        self.user_name_show.setText("已连接")



    def md5(self, arg):
        hs = hashlib.md5(bytes("交大NB", encoding="utf-8"))
        hs.update(bytes(arg, encoding='utf-8'))
        return hs.hexdigest()

    def handle_buttons(self):
        self.show_all_pushButton.clicked.connect(self.show_all_players)
        self.score_order_button.clicked.connect(self.pts_order)
        self.trb_order_button.clicked.connect(self.trb_order)
        self.ast_order_button.clicked.connect(self.ast_order)
        self.player_search_ID_button.clicked.connect(self.search_player_id)
        self.player_search_name_exact_button.clicked.connect(self.search_player_name)
        self.player_search_name_fuzzy_button.clicked.connect(self.search_player_name_fuzzy)
        self.team_show_all_button.clicked.connect(self.show_all_teams)
        self.game_show_all_button.clicked.connect(self.show_all_game_data)
        self.cmpare_confirm_pushbutton.clicked.connect(self.compare_players)
        self.hist_button.clicked.connect(self.hist)
        self.pushButton.clicked.connect(self.sort_team)
        self.pushButton_2.clicked.connect(self.pts_and_lost_pts_order)
        self.pushButton_7.clicked.connect(self.customize)
        self.pushButton_3.clicked.connect(self.button_set_text_1)
        self.pushButton_5.clicked.connect(self.button_set_text_2)
        self.pushButton_4.clicked.connect(self.button_set_text_3)
        self.pushButton_6.clicked.connect(self.button_set_text_4)


    ###########################################################球队排名############################################
    def button_set_text_1(self):
        self.textEdit.setText("""USE nba_db
                                 SELECT TOP 10 teamname, fga FROM teams
                                 JOIN team_stats ON teams.teamid = team_stats.teamid
                                 ORDER BY FGA DESC
                                 -- FGA最高的10支球队
                                 """)
    def button_set_text_2(self):
        self.textEdit.setText("""Use nba_db \nSELECT teamname, pf/g as foulsPerGm\nFROM teams\nJOIN team_stats ON teams.teamid = team_stats.teamid;\n-- Fouls per game\n
                                """)

    def button_set_text_3(self):
        self.textEdit.setText("""Use nba_db\nSELECT TOP 1 teamname, CAST(tov as FLOAT)/CAST(g as FLOAT) as tovPerGm\nFROM teams\nJOIN team_stats ON teams.teamid = team_stats.teamid\nORDER BY tovPerGm DESC
            -- 最喜欢换人的球队
                                """)

    def button_set_text_4(self):
        self.textEdit.setText("""
                                -- most time efficient scorer in the league
                                    USE nba_db
                                    SELECT TOP 1 player, pts, mp, ptsPer48
                                    FROM (
                                        SELECT player, pts, mp, CAST(pts as FLOAT)*48/CAST(mp as FLOAT) as ptsPer48
                                        FROM player_stats
                                        WHERE pts > 0 AND mp > 0) as ps
                                    ORDER BY ptsPer48 DESC
                                """)

    def customize(self):
        conn_cur = connect_directly()
        sql = self.textEdit.toPlainText()
        conn_cur.execute(sql)
        while conn_cur.nextset():  # NB: This always skips the first result set
            try:
                results = conn_cur.fetchall()
                break
            except pyodbc.ProgrammingError:
                continue
        row = len(results)  # 取得记录个数，用于设置表格的行数
        vol = len(results[0])  # 取得字段数，用于设置表格的列数

        self.tableWidget_3.setRowCount(row)
        self.tableWidget_3.setColumnCount(vol)

        for i in range(row):
            for j in range(vol):
                temp_data = results[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.tableWidget_3.setItem(i, j, data)
        conn_cur.close()


    def sort_team(self):
        conn_cur = connect_directly()
        sql_use = """use nba_db"""
        conn_cur_2 = connect_directly()
        sql_q = """ USE nba_db
                    SELECT TeamID, TeamName, win_rate, play_sum, win_sum, lose_sum FROM sort_team ORDER BY win_rate DESC ;"""
        conn_cur_2.execute(sql_q)
        while conn_cur_2.nextset():  # NB: This always skips the first result set
            try:
                results_2 = conn_cur_2.fetchall()
                break
            except pyodbc.ProgrammingError:
                continue
        row = len(results_2)  # 取得记录个数，用于设置表格的行数
        vol = len(results_2[0])  # 取得字段数，用于设置表格的列数

        self.tableWidget_2.setRowCount(row)
        self.tableWidget_2.setColumnCount(vol)

        for i in range(row):
            for j in range(vol):
                temp_data = results_2[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.tableWidget_2.setItem(i, j, data)
        conn_cur.close()

    def pts_and_lost_pts_order(self):
        conn_cur_1 = connect_directly()
        sql_use = """USE nba_db"""
        sql_sum = """(SELECT COUNT(*) FROM sort_team)"""
        conn_cur_1.execute(sql_use)
        conn_cur_1.execute(sql_sum)
        sumnum = conn_cur_1.fetchall()[0][0]
        conn_cur_2 = connect_directly()
        sql_self = """
                    SELECT TOP 3 * FROM sort_team ORDER BY avg_pts DESC;
                   """
        conn_cur_2.execute(sql_use)
        conn_cur_2.execute(sql_self)
        re = conn_cur_2.fetchall()
        most_pts = []
        most_pts_label = []

        for i in range(3):
            most_pts.append(re[i][6])
            most_pts_label.append(re[i][1])

        sql_self_2 = """SELECT TOP 3 * FROM sort_team ORDER BY avg_op_pts;"""
        conn_cur_2.execute(sql_use)
        conn_cur_2.execute(sql_self_2)
        re_2 = conn_cur_2.fetchall()
        least_pts = []
        least_pts_label = []

        for i in range(3):
            least_pts.append(re_2[i][8])
            least_pts_label.append(re_2[i][1])
        conn_cur_1.close()
        conn_cur_2.close()

        # PLot the graph
        self.widget.canvas_2.axes_2.tick_params(labelsize=7)
        self.widget_2.canvas_2.axes_2.tick_params(labelsize=7)
        self.widget.canvas_2.axes_2.bar(most_pts_label, most_pts)
        self.widget_2.canvas_2.axes_2.bar(least_pts_label, least_pts)
        for x, y in zip(most_pts_label, most_pts):
            self.widget.canvas_2.axes_2.text(x, y + 0.01, '%.2f' % y, ha='center', va='bottom', fontsize=7)
        for x, y in zip(least_pts_label, least_pts):
            self.widget_2.canvas_2.axes_2.text(x, y + 0.01, '%.2f' % y, ha='center', va='bottom', fontsize=7)
        self.widget.canvas_2.draw()
        self.widget_2.canvas_2.draw()

    def compare_players(self):
        conn_cur = connect_directly()
        try:
            sql_c = """ USE nba_db"""
            conn_cur.execute(sql_c)
            sql_trb_max = """SELECT MAX(TRB) FROM Player_Stats;"""
            conn_cur.execute(sql_trb_max)
            max_trb = conn_cur.fetchall()[0][0]
            sql_trb = """SELECT DRB FROM Player_Stats WHERE PlayerID = """ + self.compare_player_1_input.text()
            conn_cur.execute(sql_trb)
            trb_1 = (conn_cur.fetchall()[0][0]) / max_trb

            conn_cur = connect_directly()
            sql_c = """ USE nba_db"""
            conn_cur.execute(sql_c)
            sql_pts_max = """SELECT MAX(PTS) FROM Player_Stats;"""
            conn_cur.execute(sql_pts_max)
            max_pts = conn_cur.fetchall()[0][0]
            sql_pts = """SELECT PTS FROM Player_Stats WHERE PlayerID = """ + self.compare_player_1_input.text()
            conn_cur.execute(sql_pts)
            pts_1 = (conn_cur.fetchall()[0][0]) / max_pts

            conn_cur = connect_directly()
            sql_c = """ USE nba_db"""
            conn_cur.execute(sql_c)
            sql_ast_max = """SELECT MAX(AST) FROM Player_Stats;"""
            conn_cur.execute(sql_ast_max)
            max_ast = conn_cur.fetchall()[0][0]
            sql_ast = """SELECT AST FROM Player_Stats WHERE PlayerID = """ + self.compare_player_1_input.text()
            conn_cur.execute(sql_ast)
            ast_1 = (conn_cur.fetchall()[0][0]) / max_ast

            conn_cur = connect_directly()
            sql_c = """ USE nba_db"""
            conn_cur.execute(sql_c)
            sql_blk_max = """SELECT MAX(BLK) FROM Player_Stats;"""
            conn_cur.execute(sql_blk_max)
            max_blk = conn_cur.fetchall()[0][0]
            sql_blk = """SELECT BLK FROM Player_Stats WHERE PlayerID = """ + self.compare_player_1_input.text()
            conn_cur.execute(sql_blk)
            blk_1 = (conn_cur.fetchall()[0][0]) / max_blk

            conn_cur = connect_directly()
            sql_c = """ USE nba_db"""
            conn_cur.execute(sql_c)
            sql_stl_max = """SELECT MAX(STL) FROM Player_Stats;"""
            conn_cur.execute(sql_stl_max)
            max_stl = conn_cur.fetchall()[0][0]
            sql_stl = """SELECT STL FROM Player_Stats WHERE PlayerID = """ + self.compare_player_1_input.text()
            conn_cur.execute(sql_stl)
            stl_1 = (conn_cur.fetchall()[0][0]) / max_stl

            sql_name_1 = """SELECT Player FROM Player_Stats WHERE PlayerID = """ + self.compare_player_1_input.text()
            conn_cur.execute(sql_name_1)
            name_1 = conn_cur.fetchall()[0][0]

            input_character = ['PTS', 'TRB', 'AST', 'BLK', 'STL']
            input_num = [pts_1, trb_1, ast_1, blk_1, stl_1]
            input_name = name_1
            labels = np.array(input_character)
            # 数据个数
            dataLenth = len(input_num)
            # 数据
            data = np.array(input_num)
            # 分割圆周长
            angles = np.linspace(0, 2 * np.pi, dataLenth, endpoint=False)
            # 闭合
            data = np.concatenate((data, [data[0]]))
            # 闭合
            angles = np.concatenate((angles, [angles[0]]))
            # 设置画布大小
            # 这里一定要设置为极坐标格式
            loc = np.array([-0.1, 0.9])
            # 画若干个五边形
            floor = np.floor(loc.min())  # 大于最小值的最大整数
            ceil = np.ceil(loc.max())  # 小于最大值的最小整数
            for i in np.arange(floor, ceil + 2, 2):
                self.MplWidget2_2.canvas.axes.plot(angles, [i] * (int(len(labels)) + 1), '-', lw=0.3, color='black')

            self.MplWidget2_2.canvas.axes.clear()
            # self.MplWidget2_2.canvas.axes.spines['polar'].set_visible(False)  # 不显示极坐标最外圈的圆
            self.MplWidget2_2.canvas.axes.grid(False)  # 不显示默认的分割线
            self.MplWidget2_2.canvas.axes.set_yticks([])  # 不显示坐标间隔
            self.MplWidget2_2.canvas.axes.plot(angles, data, 'ro-', linewidth=2)
            self.MplWidget2_2.canvas.axes.set_thetagrids(angles * 180/np.pi, labels)
            self.MplWidget2_2.canvas.axes.set_title('capability radar map of ' + input_name, va='bottom', fontproperties="SimHei")
            self.MplWidget2_2.canvas.axes.grid(True)
            self.MplWidget2_2.canvas.axes.set_title(str(input_name))
            self.MplWidget2_2.canvas.draw()

            n = len(input_num)
            for i in range(n - 1, -1, -1):
                for j in range(i, n - 1):
                    if input_num[j] < input_num[j + 1]:
                        input_num[j], input_num[j + 1] = input_num[j + 1], input_num[j]
                        input_character[j], input_character[j + 1] = input_character[j + 1], input_character[j]
            s = ''

            s = input_name + '的'
            s = s + input_character[0] + '和' + input_character[1] + '比较出众。'
            self.label_2.setText(s)

            conn_cur.close()
            #########################################player_2#############################################
            conn_cur = connect_directly()
            sql_c = """ USE nba_db"""
            conn_cur.execute(sql_c)
            sql_trb_max = """SELECT MAX(DRB) FROM Player_Stats;"""
            conn_cur.execute(sql_trb_max)
            max_trb = conn_cur.fetchall()[0][0]
            sql_trb = """SELECT DRB FROM Player_Stats WHERE PlayerID = """ + self.compare_player_2_input.text()
            conn_cur.execute(sql_trb)
            trb_2 = (conn_cur.fetchall()[0][0]) / max_trb

            conn_cur = connect_directly()
            sql_c = """ USE nba_db"""
            conn_cur.execute(sql_c)
            sql_pts_max = """SELECT MAX(PTS) FROM Player_Stats;"""
            conn_cur.execute(sql_pts_max)
            max_pts = conn_cur.fetchall()[0][0]
            sql_pts = """SELECT PTS FROM Player_Stats WHERE PlayerID = """ + self.compare_player_2_input.text()
            conn_cur.execute(sql_pts)
            pts_2 = (conn_cur.fetchall()[0][0]) / max_pts

            conn_cur = connect_directly()
            sql_c = """ USE nba_db"""
            conn_cur.execute(sql_c)
            sql_ast_max = """SELECT MAX(AST) FROM Player_Stats;"""
            conn_cur.execute(sql_ast_max)
            max_ast = conn_cur.fetchall()[0][0]
            sql_ast = """SELECT AST FROM Player_Stats WHERE PlayerID = """ + self.compare_player_2_input.text()
            conn_cur.execute(sql_ast)
            ast_2 = (conn_cur.fetchall()[0][0]) / max_ast

            conn_cur = connect_directly()
            sql_c = """ USE nba_db"""
            conn_cur.execute(sql_c)
            sql_blk_max = """SELECT MAX(BLK) FROM Player_Stats;"""
            conn_cur.execute(sql_blk_max)
            max_blk = conn_cur.fetchall()[0][0]
            sql_blk = """SELECT BLK FROM Player_Stats WHERE PlayerID = """ + self.compare_player_2_input.text()
            conn_cur.execute(sql_blk)
            blk_2 = (conn_cur.fetchall()[0][0]) / max_blk

            conn_cur = connect_directly()
            sql_c = """ USE nba_db"""
            conn_cur.execute(sql_c)
            sql_stl_max = """SELECT MAX(STL) FROM Player_Stats;"""
            conn_cur.execute(sql_stl_max)
            max_stl = conn_cur.fetchall()[0][0]
            sql_stl = """SELECT STL FROM Player_Stats WHERE PlayerID = """ + self.compare_player_2_input.text()
            conn_cur.execute(sql_stl)
            stl_2 = (conn_cur.fetchall()[0][0]) / max_stl

            sql_name_2 = """SELECT Player FROM Player_Stats WHERE PlayerID = """ + self.compare_player_2_input.text()
            conn_cur.execute(sql_name_2)
            name_2 = conn_cur.fetchall()[0][0]

            input_character = ['PTS', 'TRB', 'AST', 'BLK', 'STL']
            input_num = [pts_2, trb_2, ast_2, blk_2, stl_2]
            input_name = name_2
            labels = np.array(input_character)
            # 数据个数
            dataLenth = len(input_num)
            # 数据
            data = np.array(input_num)
            # 分割圆周长
            angles = np.linspace(0, 2 * np.pi, dataLenth, endpoint=False)
            # 闭合
            data = np.concatenate((data, [data[0]]))
            # 闭合
            angles = np.concatenate((angles, [angles[0]]))
            loc = np.array([-0.1, 0.9])
            # 画若干个五边形
            floor = np.floor(loc.min())  # 大于最小值的最大整数
            ceil = np.ceil(loc.max())  # 小于最大值的最小整数
            for i in np.arange(floor, ceil + 2, 2):
                self.MplWidget2.canvas.axes.plot(angles, [i] * (int(len(labels)) + 1), '-', lw=0.3, color='black')

            self.MplWidget2.canvas.axes.clear()
            # self.MplWidget2_2.canvas.axes.spines['polar'].set_visible(False)  # 不显示极坐标最外圈的圆
            self.MplWidget2.canvas.axes.grid(False)  # 不显示默认的分割线
            self.MplWidget2.canvas.axes.set_yticks([])  # 不显示坐标间隔
            self.MplWidget2.canvas.axes.plot(angles, data, 'ro-', linewidth=2)
            self.MplWidget2.canvas.axes.set_thetagrids(angles * 180 / np.pi, labels)

            self.MplWidget2.canvas.axes.grid(True)
            self.MplWidget2.canvas.axes.set_title(str(input_name))
            self.MplWidget2.canvas.draw()

            n = len(input_num)
            for i in range(n - 1, -1, -1):
                for j in range(i, n - 1):
                    if input_num[j] < input_num[j + 1]:
                        input_num[j], input_num[j + 1] = input_num[j + 1], input_num[j]
                        input_character[j], input_character[j + 1] = input_character[j + 1], input_character[j]
            s = ''

            s = input_name + '的'
            s = s + input_character[0] + '和' + input_character[1] + '比较出众。'
            self.label_3.setText(s)

            conn_cur.close()
        except Exception as e:
            self.statusBar().showMessage("出现错误: " + str(e))
        ###########################输出数据结果######################################

        try:
            conn_cur = connect_directly()

            player_id_1 = self.compare_player_1_input.text()
            sql_id_search = '''use nba_db
                               SELECT Player, PTS, AST, TRB, BLK, STL FROM Player_Stats WHERE PlayerID = ''' + player_id_1 + ';'
            try:
                conn_cur.execute(sql_id_search)
                while conn_cur.nextset():  # NB: This always skips the first result set
                    try:
                        results = conn_cur.fetchall()
                        break
                    except pyodbc.ProgrammingError:
                        continue
                row = len(results)  # 取得记录个数，用于设置表格的行数
                vol = len(results[0])  # 取得字段数，用于设置表格的列数

                self.compare_player_1_tablewidget.setRowCount(row)
                self.compare_player_1_tablewidget.setColumnCount(vol)

                for i in range(row):
                    for j in range(vol):
                        temp_data = results[i][j]  # 临时记录，不能直接插入表格
                        data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                        self.compare_player_1_tablewidget.setItem(i, j, data)
                conn_cur.close()
                # 消息提示
            except Exception as e:
                self.statusBar().showMessage("搜索失败:数据不存在或输入格式有误！")
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

        try:
            conn_cur = connect_directly()
            player_id_2 = self.compare_player_2_input.text()
            sql_id_search_2 = '''use nba_db
                               SELECT Player, PTS, AST, TRB, BLK, STL FROM Player_Stats WHERE PlayerID = ''' + player_id_2 + ';'
            try:
                conn_cur.execute(sql_id_search_2)
                while conn_cur.nextset():  # NB: This always skips the first result set
                    try:
                        results = conn_cur.fetchall()
                        break
                    except pyodbc.ProgrammingError:
                        continue
                row = len(results)  # 取得记录个数，用于设置表格的行数
                vol = len(results[0])  # 取得字段数，用于设置表格的列数

                self.compare_player_1_tablewidget_2.setRowCount(row)
                self.compare_player_1_tablewidget_2.setColumnCount(vol)

                for i in range(row):
                    for j in range(vol):
                        temp_data = results[i][j]  # 临时记录，不能直接插入表格
                        data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                        self.compare_player_1_tablewidget_2.setItem(i, j, data)
                conn_cur.close()
                # 消息提示
            except Exception as e:
                self.statusBar().showMessage("搜索失败:数据不存在或输入格式有误！")
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")


    def hist(self):
        try:
            conn_cur = connect_directly()

            all_players_data = '''
                                 use nba_db
                                 SELECT Name, Points, PlayYear, TeamName, TeamScore FROM Top_Scorers;
                                 '''
            try:
                conn_cur.execute(all_players_data)
                while conn_cur.nextset():  # NB: This always skips the first result set
                    try:
                        results = conn_cur.fetchall()
                        break
                    except pyodbc.ProgrammingError:
                        continue
                row = len(results)  # 取得记录个数，用于设置表格的行数
                vol = len(results[0])  # 取得字段数，用于设置表格的列数

                self.tableWidget.setRowCount(row)
                self.tableWidget.setColumnCount(vol)

                for i in range(row):
                    for j in range(vol):
                        temp_data = results[i][j]  # 临时记录，不能直接插入表格
                        data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                        self.tableWidget.setItem(i, j, data)
                conn_cur.close()
            except Exception as e:
                self.statusBar().showMessage("错误: " + str(e))
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def show_all_players(self):
        try:
            conn_cur = connect_directly()

            all_players_data = '''
                                 use nba_db
                                 SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats;
                                 '''
            try:
                conn_cur.execute(all_players_data)
                while conn_cur.nextset():  # NB: This always skips the first result set
                    try:
                        results = conn_cur.fetchall()
                        break
                    except pyodbc.ProgrammingError:
                        continue
                row = len(results)  # 取得记录个数，用于设置表格的行数
                vol = len(results[0])  # 取得字段数，用于设置表格的列数

                self.player_tableWidget.setRowCount(row)
                self.player_tableWidget.setColumnCount(vol)

                for i in range(row):
                    for j in range(vol):
                        temp_data = results[i][j]  # 临时记录，不能直接插入表格
                        data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                        self.player_tableWidget.setItem(i, j, data)
                conn_cur.close()
            except Exception as e:
                self.statusBar().showMessage("错误: " + str(e))
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def pts_order(self):
        try:
            conn_cur = connect_directly()

            all_players_data = '''
                                         use nba_db
                                         SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats ORDER BY PTS DESC;
                                         '''

            try:
                conn_cur.execute(all_players_data)
            except Exception as e:
                self.statusBar().showMessage("错误：" + str(e))
            while conn_cur.nextset():  # NB: This always skips the first result set
                try:
                    results = conn_cur.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
            row = len(results)  # 取得记录个数，用于设置表格的行数
            vol = len(results[0])  # 取得字段数，用于设置表格的列数

            self.player_tableWidget.setRowCount(row)
            self.player_tableWidget.setColumnCount(vol)

            for i in range(row):
                for j in range(vol):
                    temp_data = results[i][j]  # 临时记录，不能直接插入表格
                    data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                    self.player_tableWidget.setItem(i, j, data)
            conn_cur.close()
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def trb_order(self):
        try:
            conn_cur = connect_directly()

            all_players_data = '''
                                         use nba_db
                                         SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats ORDER BY TRB DESC;
                                         '''

            conn_cur.execute(all_players_data)
            while conn_cur.nextset():  # NB: This always skips the first result set
                try:
                    results = conn_cur.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
            row = len(results)  # 取得记录个数，用于设置表格的行数
            vol = len(results[0])  # 取得字段数，用于设置表格的列数

            self.player_tableWidget.setRowCount(row)
            self.player_tableWidget.setColumnCount(vol)

            for i in range(row):
                for j in range(vol):
                    temp_data = results[i][j]  # 临时记录，不能直接插入表格
                    data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                    self.player_tableWidget.setItem(i, j, data)
            conn_cur.close()
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def ast_order(self):
        try:
            conn_cur = connect_directly()

            all_players_data = '''
                             use nba_db
                             SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats ORDER BY AST DESC;
                             '''

            conn_cur.execute(all_players_data)
            while conn_cur.nextset():  # NB: This always skips the first result set
                try:
                    results = conn_cur.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
            row = len(results)  # 取得记录个数，用于设置表格的行数
            vol = len(results[0])  # 取得字段数，用于设置表格的列数

            self.player_tableWidget.setRowCount(row)
            self.player_tableWidget.setColumnCount(vol)

            for i in range(row):
                for j in range(vol):
                    temp_data = results[i][j]  # 临时记录，不能直接插入表格
                    data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                    self.player_tableWidget.setItem(i, j, data)
            conn_cur.close()

        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def show_all_game_data(self):
        try:
            conn_cur = connect_directly()

            all_games_data = '''
                             use nba_db
                             select * from Game_stats;
                             '''
            conn_cur.execute(all_games_data)
            while conn_cur.nextset():  # NB: This always skips the first result set
                try:
                    results = conn_cur.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
            row = len(results)  # 取得记录个数，用于设置表格的行数
            vol = len(results[0])  # 取得字段数，用于设置表格的列数

            self.games_show_all_tableWidget.setRowCount(row)
            self.games_show_all_tableWidget.setColumnCount(vol)

            for i in range(row):
                for j in range(vol):
                    temp_data = results[i][j]  # 临时记录，不能直接插入表格
                    data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                    self.games_show_all_tableWidget.setItem(i, j, data)
            conn_cur.close()
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def search_player_id(self):

        try:
            conn_cur = connect_directly()

            player_id = self.player_search_ID_input.text()
            sql_id_search = '''use nba_db
                               SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats WHERE PlayerID = ''' + player_id + ';'
            try:
                conn_cur.execute(sql_id_search)
                while conn_cur.nextset():  # NB: This always skips the first result set
                    try:
                        results = conn_cur.fetchall()
                        break
                    except pyodbc.ProgrammingError:
                        continue
                row = len(results)  # 取得记录个数，用于设置表格的行数
                vol = len(results[0])  # 取得字段数，用于设置表格的列数

                self.player_search_tableWidget.setRowCount(row)
                self.player_search_tableWidget.setColumnCount(vol)

                for i in range(row):
                    for j in range(vol):
                        temp_data = results[i][j]  # 临时记录，不能直接插入表格
                        data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                        self.player_search_tableWidget.setItem(i, j, data)
                conn_cur.close()
                # 消息提示
                self.statusBar().showMessage("搜索完成！")
            except Exception as e:
                self.statusBar().showMessage("搜索失败:数据不存在或输入格式有误！")
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def search_player_name(self):
        try:
            conn_cur = connect_directly()

            try:

                player_name = self.player_search_name_exact_input.text()
                sql_name_search = "use nba_db SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats WHERE " \
                                  "Player = '" + str(player_name) + "';"

                try:
                    conn_cur.execute(sql_name_search)
                    # 消息提示
                    self.statusBar().showMessage("搜索完成！")

                except Exception as e:
                    self.statusBar().showMessage("搜索失败:" + str(e))

                try:
                    while conn_cur.nextset():  # NB: This always skips the first result set
                        try:
                            results = conn_cur.fetchall()
                            break
                        except pyodbc.ProgrammingError:
                            continue
                    conn_cur.close()

                    row = len(results)  # 取得记录个数，用于设置表格的行数
                    vol = len(results[0])  # 取得字段数，用于设置表格的列数

                    self.player_search_tableWidget.setRowCount(row)
                    self.player_search_tableWidget.setColumnCount(vol)

                    for i in range(row):
                        for j in range(vol):
                            temp_data = results[i][j]  # 临时记录，不能直接插入表格
                            data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                            self.player_search_tableWidget.setItem(i, j, data)
                except Exception as e:
                    self.statusBar().showMessage("出现错误: 数据不存在")
            except pyodbc.Error:
                self.statusBar().showMessage("未登录！")
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def search_player_name_fuzzy(self):
        try:
            conn_cur = connect_directly()

            player_name = self.player_search_name_fuzzy_input.text()
            sql_name_search = """DECLARE @NAME Varchar(100), @str1 Varchar(100), @str2 Varchar(100), @num Int, @n Int
                                SELECT @NAME = '""" + player_name + """'
                                SELECT @str1 = '%' + @NAME + '%'
                                SELECT @str2 = ''
                                SELECT @n = LEN(@NAME)
                                SELECT @num = 1
                                WHILE @num < @n
                                    BEGIN 
                                        SET @str2 = @str2 + substring(@NAME, @num, 1)+ '% '
                                        SET @num = @num + 1
                                    END
                                SET @str2 = @str2 + substring(@NAME, @n, 1) + '%'
                                USE nba_db
                                SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats WHERE Player LIKE @str2
                                UNION 
                                SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats WHERE Player LIKE @str1"""
            try:
                conn_cur.execute(sql_name_search)
                # 消息提示
                self.statusBar().showMessage("搜索完成！")
            except Exception as e:
                self.statusBar().showMessage("搜索失败:" + str(e))

            try:
                while conn_cur.nextset():  # NB: This always skips the first result set
                    try:
                        results = conn_cur.fetchall()
                        break
                    except pyodbc.ProgrammingError:
                        continue
                row = len(results)  # 取得记录个数，用于设置表格的行数
                vol = len(results[0])  # 取得字段数，用于设置表格的列数

                self.player_search_tableWidget.setRowCount(row)
                self.player_search_tableWidget.setColumnCount(vol)

                for i in range(row):
                    for j in range(vol):
                        temp_data = results[i][j]  # 临时记录，不能直接插入表格
                        data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                        self.player_search_tableWidget.setItem(i, j, data)
            except Exception as e:
                self.statusBar().showMessage("出现错误: 数据不存在")
            conn_cur.close()
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def show_all_teams(self):
        try:
            conn_cur = connect_directly()

            all_teams_data = '''
                                         use nba_db
                                         SELECT * FROM Teams;
                                         '''

            conn_cur.execute(all_teams_data)
            while conn_cur.nextset():  # NB: This always skips the first result set
                try:
                    results = conn_cur.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
            row = len(results)  # 取得记录个数，用于设置表格的行数
            vol = len(results[0])  # 取得字段数，用于设置表格的列数

            self.team_show_all_tableWidget.setRowCount(row)
            self.team_show_all_tableWidget.setColumnCount(vol)

            for i in range(row):
                for j in range(vol):
                    temp_data = results[i][j]  # 临时记录，不能直接插入表格
                    data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                    self.team_show_all_tableWidget.setItem(i, j, data)
            conn_cur.close()
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")


class MainApp(QMainWindow, ui):

    # 定义构造方法
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handle_ui_change()
        self.setWindowTitle("Manager controller")
        self.handle_buttons()
        self.setWindowIcon(QIcon("./exe_icon.png"))

        self.show()

    # UI 的变化处理
    def handle_ui_change(self):
        self.player_button.clicked.connect(self.open_player_tab)
        self.team_button.clicked.connect(self.open_team_tab)
        self.games_button.clicked.connect(self.open_games_tab)
        self.add_login.clicked.connect(self.open_add_user_tab)

    # 处理所有button的消息和槽的通信
    def handle_buttons(self):
        self.connect_button.clicked.connect(self.add_data_all)
        self.load_button.clicked.connect(self.load_data)
        self.game_show_all_button.clicked.connect(self.show_all_game_data)
        self.games_add_confirm_button.clicked.connect(self.add_game_data)
        self.games_delete_confirm_button.clicked.connect(self.delete_game)
        self.game_show_all_delete_button.clicked.connect(self.after_delete_show_all)
        self.show_all_pushButton.clicked.connect(self.show_all_players)
        self.score_order_button.clicked.connect(self.pts_order)
        self.trb_order_button.clicked.connect(self.trb_order)
        self.ast_order_button.clicked.connect(self.ast_order)
        self.player_save_button.clicked.connect(self.add_player_data)
        self.player_show_all_button_2.clicked.connect(self.show_all_players_from_delete)
        self.player_delete_confirm_pushButton.clicked.connect(self.delete_player_data)
        self.player_search_ID_button.clicked.connect(self.search_player_id)
        self.player_search_name_exact_button.clicked.connect(self.search_player_name)
        self.player_search_name_fuzzy_button.clicked.connect(self.search_player_name_fuzzy)
        self.team_show_all_button.clicked.connect(self.show_all_teams)
        self.team_change_button.clicked.connect(self.change_team_data)
        self.theme_button.clicked.connect(self.dark_gray_theme)
        self.theme_button_2.clicked.connect(self.dark)
        self.add_user_button.clicked.connect(self.add_user)

    # 选项卡的联动
    def open_player_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(0)

    def open_team_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(1)

    def open_games_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(2)

    def open_compare_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(3)

    def open_add_user_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(4)

    def dark_blue_theme(self):
        style = open("themes/darkblue.css", 'r')
        style = style.read()
        self.setStyleSheet(style)

    def dark_gray_theme(self):
        style = open("themes/darkgray.css", 'r')
        style = style.read()
        self.setStyleSheet(style)

    def dark(self):
        style = open("themes/qdark.css", 'r')
        style = style.read()
        self.setStyleSheet(style)

    # 数据库的连接处理
    def add_data_all(self):
        global super_user_id, super_user_pwd

        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        super_user_id = user_id
        super_user_pwd = user_pwd
        try:
            conn_cur = connect_mssql(user_id, user_pwd)
            hs = hashlib.md5(bytes("交大NB", encoding='UTF-8'))
            hs.update(bytes(user_pwd, encoding='UTF-8'))
            pwd_hs = hs.hexdigest()
            sql_create = """USE nba_db
                            CREATE TABLE superuser(
                            super_user_name VARCHAR(50) NOT NULL,
                            super_user_pwd VARCHAR(MAX) NOT NULL);"""
            conn_cur.execute(sql_create)
            sql_add = """   
                            USE nba_db INSERT INTO superuser(super_user_name, super_user_pwd) VALUES (""" + "'" + str(
                user_id) + "'" + ",'" + str(pwd_hs) + "');"
            conn_cur.execute(sql_add)
            conn_cur.commit()
            conn_cur.close()

            # 消息提示
            self.statusBar().showMessage("连接成功！")

        except Exception as e:
            self.statusBar().showMessage("连接错误: 用户或密码有误")

    # 导入所有数据
    def load_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            sql_create_table = r'''
                            IF NOT EXISTS(select * From master.dbo.sysdatabases where name='nba_db')
                    		CREATE DATABASE nba_db                            
                            use nba_db
                            CREATE TABLE Teams(
                            TeamID INT NOT NULL,
                            TeamName VARCHAR(100) NOT NULL,
                            TeamAbbr VARCHAR(10),
                            Location VARCHAR(100),
                            CoachName VARCHAR(100),
                            PRIMARY KEY(TeamID));
                            
                            CREATE TABLE Top_Scorers (
                            TopID INT NOT NULL,
                            Points INT NOT NULL,
                            Name VARCHAR(100) NOT NULL,
                            PlayYear INT,
                            TeamName VARCHAR(100),
                            OppTeamName VARCHAR(100),
                            TeamScore INT,
                            OppTeamScore INT,
                            PRIMARY KEY(TopID));
                            
                            CREATE TABLE Player_Stats (
                            PlayerID INT NOT NULL,
                            Player VARCHAR(100) NOT NULL,
                            Tm VARCHAR(10) NOT NULL,
                            Gms INT,
                            Gstart INT,
                            MP FLOAT,
                            FG FLOAT,
                            FGA INT,
                            FGP FLOAT,
                            ThreeP INT,
                            ThreePA INT,
                            ThreePP FLOAT,
                            TwoP INT,
                            TwoPA FLOAT,
                            TwoPP FLOAT,
                            eFGP FLOAT,
                            FT INT,
                            FTA FLOAT,
                            FTP FLOAT,
                            ORB FLOAT,
                            DRB FLOAT,
                            TRB FLOAT,
                            AST FLOAT,
                            STL FLOAT,
                            BLK FLOAT,
                            TOV FLOAT,
                            PF FLOAT,
                            PTS FLOAT,
                            PRIMARY KEY(PlayerID));
                            
                            CREATE TABLE Team_Stats (
                            TeamID INT NOT NULL REFERENCES Teams(TeamID),
                            G INT,
                            MP INT,
                            FG INT,
                            FGA INT,
                            FGP FLOAT,
                            ThreeP INT,
                            ThreePA INT,
                            ThreePP FLOAT,
                            TwoP INT,
                            TwoPA INT,
                            TwoPP FLOAT,
                            FT INT,
                            FTA INT,
                            FTP FLOAT,
                            ORB INT,
                            DRB INT,
                            TRB INT,
                            AST INT,
                            STL INT,
                            BLK INT,
                            TOV INT,
                            PF INT,
                            PTS INT,
                            PRIMARY KEY(TeamID));
                            
                            CREATE TABLE Game_Stats(
                            game_id CHAR(4) NOT NULL,
                            home_id INT NOT NULL REFERENCES Teams(TeamID),
                            home_name varchar(50) NOT NULL,
                            away_id INT NOT NULL REFERENCES Teams(TeamID),
                            away_name varchar(50) NOT NULL,
                            game_date date NOT NULL,
                            winner_name VARCHAR(50) NOT NULL,
                            home_pts INT NOT NULL,
                            away_pts INT NOT NULL,
                            PRIMARY KEY(game_id));
                            
                            CREATE TABLE users(
                            user_name VARCHAR(50) NOT NULL,
                            user_pwd VARCHAR(MAX) NOT NULL,
                            PRIMARY KEY(user_name));
                        
                                                       
                            
                              '''
            data_folder_dir = ".\\"
            sql_import = '''
                        use nba_db
                            
                        BULK INSERT Player_Stats
                            FROM ''' + '\'' + data_folder_dir + r'''\Player_Stats.csv'
                            WITH(
                                FIRSTROW = 2,
                                FIELDTERMINATOR = ',',
                                ROWTERMINATOR = '\n'
                            )
                            
                            BULK INSERT Team_Stats
                            FROM ''' + '\'' + data_folder_dir + r'''\Team_Stats.csv'
                            WITH(
                                FIRSTROW = 2,
                                FIELDTERMINATOR = ',',
                                ROWTERMINATOR = '\n'
                            )
                            
                            BULK INSERT Teams
                            FROM ''' + '\'' + data_folder_dir + r'''\Teams.csv'
                            WITH(
                                FIRSTROW = 2,
                                FIELDTERMINATOR = ',',
                                ROWTERMINATOR = '\n'
                            )
                            
                            BULK INSERT Top_Scorers
                            FROM ''' + '\'' + data_folder_dir + r'''\Top_Scorers.csv'
                            WITH(
                                FIRSTROW = 2,
                                FIELDTERMINATOR = ',',
                                ROWTERMINATOR = '\n'
                            )
                            
                            BULK INSERT Game_Stats
                            FROM ''' + '\'' + data_folder_dir + r'''\final.csv'
                            WITH(
                                FIRSTROW = 2,
                                FIELDTERMINATOR = ',',
                                ROWTERMINATOR = '\n'
                            );
                         '''
            try:
                conn_cur.execute(sql_create_table)
                conn_cur.commit()
            except Exception:
                self.statusBar().showMessage("出现错误")
            try:
                conn_cur.execute(sql_import)
                conn_cur.commit()
                # 消息提示
                self.statusBar().showMessage("所有数据导入成功！")
                conn_cur.close()
            except Exception as e:
                self.statusBar().showMessage("出现异常：" + str(e))
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def show_all_players(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            all_players_data = '''
                                 use nba_db
                                 SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats;
                                 '''
            try:
                conn_cur.execute(all_players_data)
                while conn_cur.nextset():  # NB: This always skips the first result set
                    try:
                        results = conn_cur.fetchall()
                        break
                    except pyodbc.ProgrammingError:
                        continue
                row = len(results)  # 取得记录个数，用于设置表格的行数
                vol = len(results[0])  # 取得字段数，用于设置表格的列数

                self.player_tableWidget.setRowCount(row)
                self.player_tableWidget.setColumnCount(vol)

                for i in range(row):
                    for j in range(vol):
                        temp_data = results[i][j]  # 临时记录，不能直接插入表格
                        data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                        self.player_tableWidget.setItem(i, j, data)
                conn_cur.close()
            except Exception as e:
                self.statusBar().showMessage("错误: " + str(e))
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def show_all_players_from_delete(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            all_players_data = '''
                                 use nba_db
                                 SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats;
                                 '''
            try:
                conn_cur.execute(all_players_data)
                while conn_cur.nextset():  # NB: This always skips the first result set
                    try:
                        results = conn_cur.fetchall()
                        break
                    except pyodbc.ProgrammingError:
                        continue
                row = len(results)  # 取得记录个数，用于设置表格的行数
                vol = len(results[0])  # 取得字段数，用于设置表格的列数

                self.player_delete_tableWidget.setRowCount(row)
                self.player_delete_tableWidget.setColumnCount(vol)

                for i in range(row):
                    for j in range(vol):
                        temp_data = results[i][j]  # 临时记录，不能直接插入表格
                        data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                        self.player_delete_tableWidget.setItem(i, j, data)
                conn_cur.close()
            except Exception as e:
                self.statusBar().showMessage("错误：" + str(e))
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def add_player_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            player_id = self.player_id_input.text()
            player = self.player_name_input.text()
            tm = self.player_teamAbbreviation_box.currentText()
            pts = self.player_pts_input.text()
            trb = self.player_rbd_input.text()
            ast = self.player_ast_input.text()
            stl = self.player_stl_input.text()
            blk = self.player_blk_input.text()

            sql_add_player = ''' USE nba_db
                                INSERT INTO Player_Stats(PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK) 
                                VALUES''' + '(' + player_id + ',\'' + player + '\',\'' + tm + '\',' + pts + ',' + trb + ',' + ast + ',' + stl + ',' + blk + ')'
            # 加球员
            try:
                conn_cur.execute(sql_add_player)
                conn_cur.commit()
                sql_use = """use nba_db"""
                sql_find = """SELECT * FROM Player_Stats WHERE PlayerID = '""" + player_id + "';"
                conn_cur_2 = connect_directly()
                conn_cur_2.execute(sql_use)
                conn_cur_2.execute(sql_find)
                ctr = conn_cur_2.fetchall()
                if ctr != []:
                    self.statusBar().showMessage("已存在此球员！")
                else:
                    self.statusBar().showMessage("添加成功！")
            except pyodbc.Error:
                self.statusBar().showMessage("添加失败")

            conn_cur.close()
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def delete_player_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            ipt_id = self.player_delete_id_input.text()
            sql_delete = '''
                            USE nba_db
                            DELETE FROM Player_Stats WHERE PlayerID = ''' + str(ipt_id) + ';'
            try:

                ans = QMessageBox.question(self, "警告", "操作不可逆，确定继续？", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if ans == QMessageBox.Yes:
                    conn_cur.execute(sql_delete)
                    conn_cur.commit()
                    # 消息提示
                    self.statusBar().showMessage("删除数据成功！")
                    conn_cur.close()
                    self.player_delete_id_input.setText('')

            except Exception as e:
                self.statusBar().showMessage("删除失败：" + str(e))
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def search_player_id(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            player_id = self.player_search_ID_input.text()
            sql_id_search = '''use nba_db
                               SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats WHERE PlayerID = ''' + player_id + ';'
            try:
                conn_cur.execute(sql_id_search)
                while conn_cur.nextset():  # NB: This always skips the first result set
                    try:
                        results = conn_cur.fetchall()
                        break
                    except pyodbc.ProgrammingError:
                        continue
                row = len(results)  # 取得记录个数，用于设置表格的行数
                vol = len(results[0])  # 取得字段数，用于设置表格的列数

                self.player_search_tableWidget.setRowCount(row)
                self.player_search_tableWidget.setColumnCount(vol)

                for i in range(row):
                    for j in range(vol):
                        temp_data = results[i][j]  # 临时记录，不能直接插入表格
                        data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                        self.player_search_tableWidget.setItem(i, j, data)
                conn_cur.close()
                # 消息提示
                self.statusBar().showMessage("搜索完成！")
                self.player_search_ID_input.setText('')

            except Exception as e:
                self.statusBar().showMessage("搜索失败:数据不存在或输入格式有误！")
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def search_player_name(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            try:

                player_name = self.player_search_name_exact_input.text()
                sql_name_search = "use nba_db SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats WHERE " \
                                  "Player = '" + str(player_name) + "';"

                try:
                    conn_cur.execute(sql_name_search)
                    # 消息提示
                    self.statusBar().showMessage("搜索完成！")

                except Exception as e:
                    self.statusBar().showMessage("搜索失败:" + str(e))

                try:
                    while conn_cur.nextset():  # NB: This always skips the first result set
                        try:
                            results = conn_cur.fetchall()
                            break
                        except pyodbc.ProgrammingError:
                            continue
                    conn_cur.close()

                    row = len(results)  # 取得记录个数，用于设置表格的行数
                    vol = len(results[0])  # 取得字段数，用于设置表格的列数

                    self.player_search_tableWidget.setRowCount(row)
                    self.player_search_tableWidget.setColumnCount(vol)

                    for i in range(row):
                        for j in range(vol):
                            temp_data = results[i][j]  # 临时记录，不能直接插入表格
                            data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                            self.player_search_tableWidget.setItem(i, j, data)
                    self.player_search_name_exact_input.setText('')

                except Exception as e:
                    self.statusBar().showMessage("出现错误: 数据不存在")
            except pyodbc.Error:
                self.statusBar().showMessage("未登录！")
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def search_player_name_fuzzy(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            player_name = self.player_search_name_fuzzy_input.text()
            sql_name_search = """DECLARE @NAME Varchar(100), @str1 Varchar(100), @str2 Varchar(100), @num Int, @n Int
                                SELECT @NAME = '""" + player_name + """'
                                SELECT @str1 = '%' + @NAME + '%'
                                SELECT @str2 = ''
                                SELECT @n = LEN(@NAME)
                                SELECT @num = 1
                                WHILE @num < @n
                                    BEGIN 
                                        SET @str2 = @str2 + substring(@NAME, @num, 1)+ '% '
                                        SET @num = @num + 1
                                    END
                                SET @str2 = @str2 + substring(@NAME, @n, 1) + '%'
                                USE nba_db
                                SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats WHERE Player LIKE @str2
                                UNION 
                                SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats WHERE Player LIKE @str1"""
            try:
                conn_cur.execute(sql_name_search)
                # 消息提示
                self.statusBar().showMessage("搜索完成！")
            except Exception as e:
                self.statusBar().showMessage("搜索失败:" + str(e))

            try:
                while conn_cur.nextset():  # NB: This always skips the first result set
                    try:
                        results = conn_cur.fetchall()
                        break
                    except pyodbc.ProgrammingError:
                        continue
                row = len(results)  # 取得记录个数，用于设置表格的行数
                vol = len(results[0])  # 取得字段数，用于设置表格的列数

                self.player_search_tableWidget.setRowCount(row)
                self.player_search_tableWidget.setColumnCount(vol)

                for i in range(row):
                    for j in range(vol):
                        temp_data = results[i][j]  # 临时记录，不能直接插入表格
                        data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                        self.player_search_tableWidget.setItem(i, j, data)

            except Exception as e:
                self.statusBar().showMessage("出现错误: 数据不存在")
            conn_cur.close()
            self.player_search_name_fuzzy_input.setText('')

        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def show_all_teams(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            all_teams_data = '''
                                         use nba_db
                                         SELECT * FROM Teams;
                                         '''

            conn_cur.execute(all_teams_data)
            while conn_cur.nextset():  # NB: This always skips the first result set
                try:
                    results = conn_cur.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
            row = len(results)  # 取得记录个数，用于设置表格的行数
            vol = len(results[0])  # 取得字段数，用于设置表格的列数

            self.team_show_all_tableWidget.setRowCount(row)
            self.team_show_all_tableWidget.setColumnCount(vol)

            for i in range(row):
                for j in range(vol):
                    temp_data = results[i][j]  # 临时记录，不能直接插入表格
                    data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                    self.team_show_all_tableWidget.setItem(i, j, data)
            conn_cur.close()
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def change_team_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)
            ans = QMessageBox.question(self, "警告", "操作不可逆，确定继续？", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if ans == QMessageBox.Yes:
                choice = self.comboBox_team_alter.currentText()
                id = self.team_alter_id.text()
                content = self.team_alter_content.text()
                if choice == "教练":
                    sql_change = r"""USE nba_db UPDATE Teams SET Teams.CoachName = """ + "'" + content + "'" + """ FROM Teams WHERE TeamID = """ + id
                else:
                    sql_change = r"""USE nba_db UPDATE Teams SET Teams.Location = """ + "'" + content + "'" + """ FROM Teams WHERE TeamID = """ + id
                try:
                    conn_cur.execute(sql_change)
                    self.statusBar().showMessage("修改完毕！")
                except Exception as e:
                    self.statusBar().showMessage("错误: " + str(e))
                conn_cur.execute('use nba_db SELECT * FROM Teams')
                while conn_cur.nextset():  # NB: This always skips the first result set
                    try:
                        results = conn_cur.fetchall()
                        break
                    except pyodbc.ProgrammingError:
                        continue
                row = len(results)  # 取得记录个数，用于设置表格的行数
                vol = len(results[0])  # 取得字段数，用于设置表格的列数

                self.team_change_tableWidget.setRowCount(row)
                self.team_change_tableWidget.setColumnCount(vol)

                for i in range(row):
                    for j in range(vol):
                        temp_data = results[i][j]  # 临时记录，不能直接插入表格
                        data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                        self.team_change_tableWidget.setItem(i, j, data)
                conn_cur.close()
                self.team_alter_content.setText('')
                self.team_alter_id.setText('')

        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def show_all_game_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            all_games_data = '''
                             use nba_db
                             select * from Game_stats;
                             '''
            conn_cur.execute(all_games_data)
            while conn_cur.nextset():  # NB: This always skips the first result set
                try:
                    results = conn_cur.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
            row = len(results)  # 取得记录个数，用于设置表格的行数
            vol = len(results[0])  # 取得字段数，用于设置表格的列数

            self.games_show_all_tableWidget.setRowCount(row)
            self.games_show_all_tableWidget.setColumnCount(vol)

            for i in range(row):
                for j in range(vol):
                    temp_data = results[i][j]  # 临时记录，不能直接插入表格
                    data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                    self.games_show_all_tableWidget.setItem(i, j, data)
            conn_cur.close()
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def add_game_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur_1 = connect_mssql(user_id, user_pwd)

            try:
                conn_cur_2 = connect_mssql(user_id, user_pwd)
            except Exception as e:
                QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")
            try:
                conn_cur_3 = connect_mssql(user_id, user_pwd)
            except Exception as e:
                QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

            game_id = self.games_add_game_id_input.text()
            games_add_home_id_input = self.games_add_home_id_input.text()
            games_add_away_id_input = self.games_add_away_id_input.text()
            games_add_home_pts_input = self.games_add_home_pts_input.text()
            games_add_away_pts_input = self.games_add_away_pts_input.text()
            games_add_home_date_input = self.games_add_home_date_input.text()

            try:
                conn_cur_1.execute(
                    "Use nba_db SELECT TeamName FROM Teams WHERE TeamID = " + str(self.games_add_home_id_input.text()))
            except Exception as e:
                self.statusBar().showMessage("添加失败! ")
            while conn_cur_1.nextset():  # NB: This always skips the first result set
                try:
                    games_add_name_home = conn_cur_1.fetchall()[0][0]
                    break
                except pyodbc.ProgrammingError:
                    continue
            try:
                conn_cur_2.execute(
                    "use nba_db SELECT TeamName FROM Teams WHERE TeamID = " + str(self.games_add_away_id_input.text()))
            except Exception as e:
                self.statusBar().showMessage("添加失败！")
            while conn_cur_2.nextset():  # NB: This always skips the first result set
                try:
                    games_add_away_name = conn_cur_2.fetchall()[0][0]
                    break
                except pyodbc.ProgrammingError:
                    continue
            if games_add_home_pts_input > games_add_away_pts_input:
                win_res = games_add_name_home
            else:
                win_res = games_add_away_name
            games_add_home_winner_input = str(win_res)

            sql_add_game = '''
                            use nba_db
                            INSERT INTO Game_Stats (game_id, home_id, home_name,
                            away_id, away_name
                            ,game_date,winner_name,
                             home_pts,away_pts) VALUES 
                            ''' + '(' + game_id + ',' + games_add_home_id_input + ',\'' + games_add_name_home + '\',' + games_add_away_id_input + ',\'' + games_add_away_name + '\',\'' + games_add_home_date_input + '\',\'' + games_add_home_winner_input + '\',' + games_add_home_pts_input + ',' + games_add_away_pts_input + ');'

            try:
                conn_cur_3.execute(sql_add_game)
                conn_cur_3.commit()

                # 消息提示
                sql_use = """use nba_db"""
                sql_find = """SELECT * FROM Game_Stats WHERE game_id = '""" + game_id + "';"
                conn_cur_4 = connect_directly()
                conn_cur_4.execute(sql_use)
                conn_cur_4.execute(sql_find)
                ctr = conn_cur_4.fetchall()
                if ctr != []:
                    self.statusBar().showMessage("已存在此ID, 请更换ID！")
                else:
                    self.statusBar().showMessage("添加成功！")
                sql_refresh = """
                            DECLARE @input_game_id INT
                            SET @input_game_id = """+ game_id + """
                            
                            DECLARE @sum_data INT,  @home_id INT, @home_name varchar(100), @away_id INT, @away_name varchar(100), @home_pts INT, @away_pts INT 
                            SELECT @home_id = home_id, @away_id = away_id, @home_name = home_name, @away_name = away_name, @home_pts = home_pts, @away_pts = away_pts FROM Game_Stats WHERE game_id = @input_game_id
                            IF NOT EXISTS(SELECT * FROM sort_team WHERE TeamID = @home_id)
                            BEGIN
                            INSERT INTO sort_team VALUES(@home_id, @home_name, 0, 0, 0, 0, 0, 0, 0, 0)
                            END
                            IF NOT EXISTS(SELECT * FROM sort_team WHERE TeamID = @away_id)
                            BEGIN
                            INSERT INTO sort_team VALUES(@away_id, @away_name, 0, 0, 0, 0, 0, 0, 0, 0)
                            END
                            
                            
                            IF @home_pts > @away_pts
                            BEGIN 
                            UPDATE sort_team SET win_sum = win_sum + 1, play_sum = play_sum + 1  WHERE TeamID = @home_id
                            UPDATE sort_team SET win_rate = win_sum / play_sum WHERE TeamID = @home_id
                            UPDATE sort_team SET lose_sum = lose_sum + 1, play_sum = play_sum + 1 WHERE TeamID = @away_id
                            UPDATE sort_team SET win_rate = win_sum / play_sum WHERE TeamID = @away_id
                            END
                            ELSE
                            BEGIN
                            UPDATE sort_team SET win_sum = win_sum + 1, play_sum = play_sum + 1 WHERE TeamID = @away_id
                            UPDATE sort_team SET win_rate = win_sum / play_sum WHERE TeamID = @away_id
                            UPDATE sort_team SET lose_sum = lose_sum + 1, play_sum = play_sum + 1 WHERE TeamID = @home_id
                            UPDATE sort_team SET win_rate = win_sum / play_sum WHERE TeamID = @home_id
                            END
                            
                            
                            UPDATE sort_team SET all_pts = all_pts + @home_pts WHERE TeamID = @home_id
                            UPDATE sort_team SET all_op_pts = all_op_pts + @away_pts WHERE TeamID = @home_id
                            UPDATE sort_team SET all_op_pts = all_op_pts + @home_pts WHERE TeamID = @away_id
                            UPDATE sort_team SET all_pts = all_pts + @away_pts WHERE TeamID = @away_id
                            
                            UPDATE sort_team SET avg_pts = all_pts / play_sum WHERE TeamID = @home_id
                            UPDATE sort_team SET avg_op_pts = all_op_pts / play_sum WHERE TeamID = @home_id
                            UPDATE sort_team SET avg_op_pts = all_op_pts / play_sum WHERE TeamID = @away_id
                            UPDATE sort_team SET avg_pts = all_pts / play_sum WHERE TeamID = @away_id
                        """
                conn_cur_3.execute(sql_refresh)
                self.games_add_home_date_input.setText('')
                self.games_add_away_pts_input.setText('')
                self.games_add_home_pts_input.setText('')
                self.games_add_home_id_input.setText('')
                self.games_add_away_id_input.setText('')
                self.games_add_game_id_input.setText('')

            except Exception as e:
                self.statusBar().showMessage("添加数据失败:" + str(e))

            conn_cur_1.close()
            conn_cur_2.close()
            conn_cur_3.close()

        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")



    def delete_game(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            ipt_id = self.games_delete_id_input.text()
            sql_delete = '''
                            USE nba_db
                            DELETE FROM Game_Stats WHERE game_id = ''' + str(ipt_id) + ';'

            try:
                ans = QMessageBox.question(self, "警告", "操作不可逆，确定继续？", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if ans == QMessageBox.Yes:
                    conn_cur.execute(sql_delete)
                    # 消息提示
                    self.statusBar().showMessage("删除成功！")
                    conn_cur.commit()
                    conn_cur.close()
                    self.games_delete_id_input.setText('')

            except Exception as e:
                self.statusBar().showMessage("删除失败！")

        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def after_delete_show_all(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            all_games_data = '''
                                     use nba_db
                                     select * from Game_stats;
                                     '''
            try:
                conn_cur.execute(all_games_data)
            except Exception as e:
                self.statusBar().showMessage("失败！" + str(e))

            while conn_cur.nextset():  # NB: This always skips the first result set
                try:
                    results = conn_cur.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
            row = len(results)  # 取得记录个数，用于设置表格的行数
            vol = len(results[0])  # 取得字段数，用于设置表格的列数

            self.games_elete_tableWidget.setRowCount(row)
            self.games_elete_tableWidget.setColumnCount(vol)

            for i in range(row):
                for j in range(vol):
                    temp_data = results[i][j]  # 临时记录，不能直接插入表格
                    data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                    self.games_elete_tableWidget.setItem(i, j, data)
            conn_cur.close()

        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def pts_order(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            all_players_data = '''
                                         use nba_db
                                         SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats ORDER BY PTS DESC;
                                         '''

            try:
                conn_cur.execute(all_players_data)
            except Exception as e:
                self.statusBar().showMessage("错误：" + str(e))
            while conn_cur.nextset():  # NB: This always skips the first result set
                try:
                    results = conn_cur.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
            row = len(results)  # 取得记录个数，用于设置表格的行数
            vol = len(results[0])  # 取得字段数，用于设置表格的列数

            self.player_tableWidget.setRowCount(row)
            self.player_tableWidget.setColumnCount(vol)

            for i in range(row):
                for j in range(vol):
                    temp_data = results[i][j]  # 临时记录，不能直接插入表格
                    data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                    self.player_tableWidget.setItem(i, j, data)
            conn_cur.close()
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def trb_order(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            all_players_data = '''
                                         use nba_db
                                         SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats ORDER BY TRB DESC;
                                         '''

            conn_cur.execute(all_players_data)
            while conn_cur.nextset():  # NB: This always skips the first result set
                try:
                    results = conn_cur.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
            row = len(results)  # 取得记录个数，用于设置表格的行数
            vol = len(results[0])  # 取得字段数，用于设置表格的列数

            self.player_tableWidget.setRowCount(row)
            self.player_tableWidget.setColumnCount(vol)

            for i in range(row):
                for j in range(vol):
                    temp_data = results[i][j]  # 临时记录，不能直接插入表格
                    data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                    self.player_tableWidget.setItem(i, j, data)
            conn_cur.close()
        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    def ast_order(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            all_players_data = '''
                             use nba_db
                             SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats ORDER BY AST DESC;
                             '''

            conn_cur.execute(all_players_data)
            while conn_cur.nextset():  # NB: This always skips the first result set
                try:
                    results = conn_cur.fetchall()
                    break
                except pyodbc.ProgrammingError:
                    continue
            row = len(results)  # 取得记录个数，用于设置表格的行数
            vol = len(results[0])  # 取得字段数，用于设置表格的列数

            self.player_tableWidget.setRowCount(row)
            self.player_tableWidget.setColumnCount(vol)

            for i in range(row):
                for j in range(vol):
                    temp_data = results[i][j]  # 临时记录，不能直接插入表格
                    data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                    self.player_tableWidget.setItem(i, j, data)
            conn_cur.close()

        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

    ###############################################user management system##########################################
    ###############################################################################################################
    def add_user(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)
            name = self.lineEditname.text()
            pwd = self.lineEdit_2.text()
            pwd_confirm = self.lineEdit_3.text()
            if pwd == pwd_confirm:
                try:
                    hs = hashlib.md5(bytes("交大NB", encoding='UTF-8'))
                    hs.update(bytes(pwd, encoding='UTF-8'))
                    pwd_hs = hs.hexdigest()
                    sql_add = """USE nba_db INSERT INTO users(user_name, user_pwd) VALUES (""" + "'" + str(
                        name) + "'" + ",'" + str(pwd_hs) + "');"
                    conn_cur.execute(sql_add)
                    conn_cur.commit()
                    sql_use = """use nba_db"""
                    sql_find = """SELECT * FROM users WHERE user_name = '""" + name + "';"
                    conn_cur_2 = connect_directly()
                    conn_cur_2.execute(sql_use)
                    conn_cur_2.execute(sql_find)
                    ctr = conn_cur_2.fetchall()
                    if ctr != []:
                        self.statusBar().showMessage("已存在此用户！！")

                    else:
                        self.statusBar().showMessage("用户添加成功！")
                    self.lineEditname.setText('')
                    self.lineEdit_2.setText('')
                    self.lineEdit_3.setText('')
                    conn_cur.close()
                    conn_cur_2.close()
                except pyodbc.ProgrammingError as e:
                    self.statusBar().showMessage("出现错误：" + str(e))
            else:
                self.error_m.setText('两次密码不一致！请再次输入！')
                self.lineEdit_2.setText('')
                self.lineEdit_3.setText('')

        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")


def main():
    app = QApplication([])
    window = helloApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
