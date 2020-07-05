# encoding: utf-8
# Author    : Alan Liu<pickerxxr@gmail.com >
# Datetime  : ${DATE} ${TIME}
# User      : ${USER}
# Product   : ${PRODUCT_NAME}
# Project   : ${PROJECT_NAME}
# File      : ${NAME}.py
# explain   : PyQt5 NBA数据管理系统 开发
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys
import pyodbc
import hashlib
# 实现 ui和Logic的分离

from connect_mssql import connect_mssql, close_conn, connect_directly

ui, _ = loadUiType('main.ui')
login, _ = loadUiType('choose_user.ui')
normal_ui, _ = loadUiType('normal_user.ui')

class LoginApp(QWidget, login):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.init_user_button.clicked.connect(self.handel_login)
        style = open("themes/darkorange.css", 'r')
        style = style.read()
        self.setStyleSheet(style)
        self.init_manage_button.clicked.connect(self.manage)
        self.init_quit_button.clicked.connect(self.close)

    def md5(self, arg):
        hs = hashlib.md5(bytes("交大NB", encoding="utf-8"))
        hs.update(bytes(arg, encoding='utf-8'))
        return hs.hexdigest()

    def handel_login(self):
        conn_cur = connect_mssql('sa', '123456')
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
            self.close()
            self.main_app.show()

        else:
            self.error_message.setText("用户名或密码错误，重新输入")


    def manage(self):
        self.main_app = MainApp()
        self.close()
        self.main_app.show()

class normal_user(QMainWindow, normal_ui):

    # 定义构造方法
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handle_buttons()
        self.show()
    def handle_buttons(self):
        pass

class MainApp(QMainWindow, ui):

    # 定义构造方法
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handle_ui_change()
        self.handle_buttons()
        self.show()

    # UI 的变化处理
    def handle_ui_change(self):
        self.player_button.clicked.connect(self.open_player_tab)
        self.team_button.clicked.connect(self.open_team_tab)
        self.games_button.clicked.connect(self.open_games_tab)
        self.player_compare_button.clicked.connect(self.open_compare_tab)
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

    # 数据库的连接处理
    def add_data_all(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)
            # 消息提示
            self.statusBar().showMessage("连接成功！")
            conn_cur.close()
        except Exception as e:
            self.statusBar().showMessage("连接错误:" + str(e))

    # 导入所有数据
    def load_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        try:
            conn_cur = connect_mssql(user_id, user_pwd)

            sql_create_table = r'''
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
            data_folder_dir = self.dir_input.text()
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
                                VALUES''' + '(' + player_id + ',\'' + player + '\',\'' + tm + '\',' + pts + ',' + trb + ',' + ast + ',' + stl + ',' + blk + ');'
            # 加球员
            try:
                conn_cur.execute(sql_add_player)
                conn_cur.commit()
                self.statusBar().showMessage("添加成功！")
            except Exception as e:
                self.statusBar().showMessage("添加失败" + str(e))

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
                conn_cur.execute(sql_delete)
                conn_cur.commit()
                # 消息提示
                self.statusBar().showMessage("删除数据成功！")
                conn_cur.close()
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
                self.statusBar().showMessage("添加成功！")
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
                conn_cur.execute(sql_delete)
                # 消息提示
                self.statusBar().showMessage("删除成功！")
                conn_cur.commit()
                conn_cur.close()
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
            if pwd ==pwd_confirm:
                hs = hashlib.md5(bytes("交大NB", encoding='UTF-8'))
                hs.update(bytes(pwd, encoding='UTF-8'))
                pwd_hs = hs.hexdigest()
                sql_add = """USE nba_db INSERT INTO users(user_name, user_pwd) VALUES (""" + "'" + str(name) + "'"+ ",'" + str(pwd_hs) + "');"
                try:
                    conn_cur.execute(sql_add)
                    conn_cur.commit()
                    conn_cur.close()
                    self.statusBar().showMessage("用户添加成功！")
                    self.lineEditname.setText('')
                    self.lineEdit_2.setText('')
                    self.lineEdit_3.setText('')
                except Exception as e:
                    self.statusBar().showMessage("错误: " + str(e))
            else:
                self.error_m.setText('两次密码不一致！请再次输入！')
                self.lineEdit_2.setText('')
                self.lineEdit_3.setText('')



        except Exception as e:
            QMessageBox.critical(self, "尚未连接", "请检查你的连接状态")

def main():
    app = QApplication([])
    window = LoginApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
