# PyQt5 NBAs数据管理系统 开发
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys
import pyodbc

# 实现 ui和Logic的分离
from appdirs import unicode

from connect_mssql import connect_mssql, close_conn, connect_directly

ui, _ = loadUiType('main.ui')


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
        self.heat_map_button.clicked.connect(self.open_heat_tab)
        self.line_button.clicked.connect(self.open_line_tab)

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


    # 选项卡的联动
    def open_player_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(0)

    def open_team_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(1)

    def open_games_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(2)

    def open_compare_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(3)

    def open_heat_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(4)

    def open_line_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(5)

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
                        
                          '''
        data_folder_dir = self.dir_input.text()
        sql_import = '''
                    use nba_db
                        
                    BULK INSERT Player_Stats
                        FROM ''' + '\'' + data_folder_dir+r'''\Player_Stats.csv'
                        WITH(
                            FIRSTROW = 2,
                            FIELDTERMINATOR = ',',
                            ROWTERMINATOR = '\n'
                        )
                        
                        BULK INSERT Team_Stats
                        FROM ''' + '\'' + data_folder_dir+r'''\Team_Stats.csv'
                        WITH(
                            FIRSTROW = 2,
                            FIELDTERMINATOR = ',',
                            ROWTERMINATOR = '\n'
                        )
                        
                        BULK INSERT Teams
                        FROM ''' + '\'' + data_folder_dir+r'''\Teams.csv'
                        WITH(
                            FIRSTROW = 2,
                            FIELDTERMINATOR = ',',
                            ROWTERMINATOR = '\n'
                        )
                        
                        BULK INSERT Top_Scorers
                        FROM ''' + '\'' + data_folder_dir+r'''\Top_Scorers.csv'
                        WITH(
                            FIRSTROW = 2,
                            FIELDTERMINATOR = ',',
                            ROWTERMINATOR = '\n'
                        )
                        
                        BULK INSERT Game_Stats
                        FROM ''' + '\'' + data_folder_dir+r'''\final.csv'
                        WITH(
                            FIRSTROW = 2,
                            FIELDTERMINATOR = ',',
                            ROWTERMINATOR = '\n'
                        );
                     '''
        try:
            conn_cur.execute(sql_create_table)
            conn_cur.commit()
            conn_cur.execute(sql_import)
            conn_cur.commit()
            # 消息提示
            self.statusBar().showMessage("所有数据导入成功！")
            conn_cur.close()
        except Exception as e:
            self.statusBar().showMessage("出现异常：", e)

    def show_all_players(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        all_players_data = '''
                             use nba_db
                             SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats;
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

    def show_all_players_from_delete(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        all_players_data = '''
                             use nba_db
                             SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats;
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

        self.player_delete_tableWidget.setRowCount(row)
        self.player_delete_tableWidget.setColumnCount(vol)

        for i in range(row):
            for j in range(vol):
                temp_data = results[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.player_delete_tableWidget.setItem(i, j, data)
        conn_cur.close()

    def add_player_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
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

    def delete_player_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        ipt_id = self.player_delete_id_input.text()
        sql_delete = '''
                        USE nba_db
                        DELETE FROM Player_Stats WHERE PlayerID = ''' + str(ipt_id)+';'
        try:
            conn_cur.execute(sql_delete)
            conn_cur.commit()
            # 消息提示
            self.statusBar().showMessage("删除数据成功！")
            conn_cur.close()
        except Exception as e:
            self.statusBar().showMessage("删除失败：" + str(e))

    def search_player_id(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
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
            self.statusBar().showMessage("搜索失败:" + str(e))

    def search_player_name(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        player_name = self.player_search_name_exact_input.text()
        sql_name_search = "use nba_db SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats WHERE " \
                          "Player = '" + str(player_name) + "';"
        try:
            conn_cur.execute(sql_name_search)
            # 消息提示
            self.statusBar().showMessage("搜索完成！")
        except Exception as e:
            self.statusBar().showMessage("搜索失败:" + str(e))

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

    def search_player_name_fuzzy(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        player_name = self.player_search_name_fuzzy_input.text()
        sql_name_search = "use nba_db SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats WHERE " \
                          "Player LIKE '" + "%" + str(player_name) + "%" + "';"
        try:
            conn_cur.execute(sql_name_search)
            # 消息提示
            self.statusBar().showMessage("搜索完成！")
        except Exception as e:
            self.statusBar().showMessage("搜索失败:" + str(e))

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

    def show_all_teams(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        sql_show_all = 'SELECT * FROM '
        pass

        # 消息提示
        conn_cur.close()

    def change_team_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        sql_show_all = 'SELECT * FROM '
        pass

        # 消息提示
        self.statusBar().showMessage("更改完成！")
        conn_cur.close()

    def search_team(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        sql_show_all = 'SELECT * FROM '
        pass

        # 消息提示
        self.statusBar().showMessage("搜索完成！")
        conn_cur.close()

    def show_all_game_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
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

    def add_game_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur_1 = connect_mssql(user_id, user_pwd)
        conn_cur_2 = connect_mssql(user_id, user_pwd)
        conn_cur_3 = connect_mssql(user_id, user_pwd)

        game_id = self.games_add_game_id_input.text()
        games_add_home_id_input = self.games_add_home_id_input.text()
        games_add_away_id_input = self.games_add_away_id_input.text()
        games_add_home_pts_input = self.games_add_home_pts_input.text()
        games_add_away_pts_input = self.games_add_away_pts_input.text()
        games_add_home_date_input = self.games_add_home_date_input.text()

        conn_cur_1.execute(
            "Use nba_db SELECT TeamName FROM Teams WHERE TeamID = " + str(self.games_add_home_id_input.text()))
        while conn_cur_1.nextset():  # NB: This always skips the first result set
            try:
                games_add_name_home = conn_cur_1.fetchall()[0][0]
                break
            except pyodbc.ProgrammingError:
                continue
        conn_cur_2.execute(
            "use nba_db SELECT TeamName FROM Teams WHERE TeamID = " + str(self.games_add_away_id_input.text()))
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
                        ''' + '(' + game_id+','+games_add_home_id_input+',\''+ games_add_name_home + '\',' + games_add_away_id_input+',\''+games_add_away_name+'\',\''+games_add_home_date_input+'\',\''+games_add_home_winner_input+'\','+games_add_home_pts_input+','+games_add_away_pts_input + ');'

        try:
            conn_cur_3.execute(sql_add_game)
            conn_cur_3.commit()

            # 消息提示
            self.statusBar().showMessage("添加成功！")
        except Exception as e:
            self.statusBar().showMessage("添加数据失败:" + str(e))
        except pyodbc.ProgrammingError:
            self.statusBar().showMessage("添加请求失败，存在语法错误")

        conn_cur_1.close()
        conn_cur_2.close()
        conn_cur_3.close()

    def delete_game(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        ipt_id = self.games_delete_id_input.text()
        sql_delete = '''
                        USE nba_db
                        DELETE FROM Game_Stats WHERE game_id = ''' + str(ipt_id)+';'

        try:
            conn_cur.execute(sql_delete)
            # 消息提示
            self.statusBar().showMessage("删除成功！")
            conn_cur.commit()
            conn_cur.close()
        except Exception as e:
            self.statusBar().showMessage("删除失败！")

    def after_delete_show_all(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
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

    def pts_order(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        all_players_data = '''
                                     use nba_db
                                     SELECT PlayerID, Player, Tm, PTS, TRB, AST, STL, BLK FROM Player_Stats ORDER BY PTS DESC;
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

    def trb_order(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
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

    def ast_order(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
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

    def compare_player_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        sql_show_all = 'SELECT * FROM '
        pass

        # 消息提示
        self.statusBar().showMessage("查询成功！")
        conn_cur.close()

    def heat_map(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        sql_show_all = 'SELECT * FROM '
        pass

        # 消息提示
        conn_cur.close()

    def line_graph(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        sql_show_all = 'SELECT * FROM '
        pass

        # 消息提示
        conn_cur.close()


def main():
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
