# PyQt5 NBAs数据管理系统 开发
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys

# 实现 ui和Logic的分离
from appdirs import unicode

from connect_mssql import connect_mssql, close_conn

ui, _ = loadUiType('main.ui')


class MainApp(QMainWindow, ui):

    # 定义构造方法
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handle_ui_change()
        self.handle_buttons()

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
        conn_cur = connect_mssql(user_id, user_pwd)
        # 消息提示
        self.statusBar().showMessage("连接成功！")
        conn_cur.close()

    # 导入所有数据
    def load_data(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        sql_create_table = r'''
                        use nba_db
                        CREATE TABLE Teams (
                        TeamID INT NOT NULL,
                        TeamName VARCHAR(100) NOT NULL,
                        TeamAbbr VARCHAR(10),
                        Location VARCHAR(100),
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
                        MP INT,
                        FG INT,
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
                        ORB INT,
                        DRB INT,
                        TRB INT,
                        AST INT,
                        STL INT,
                        BLK INT,
                        TOV INT,
                        PF INT,
                        PTS INT,
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
                        
                        
                        CREATE TABLE Coaches (
                        Name VARCHAR(100),
                        TeamID INT REFERENCES Teams(TeamID),
                        PRIMARY KEY(Name, TeamID));

                        
                        
                          '''

        sql_import = r'''
                    use nba_db
                    BULK INSERT Coaches
                        FROM 'Z:\db_pj\Coaches.csv'
                        WITH(
                            FIRSTROW = 2,
                            FIELDTERMINATOR = ',',
                            ROWTERMINATOR = '\n')
                        
                    BULK INSERT Player_Stats
                        FROM 'Z:\db_pj\Player_Stats.csv'
                        WITH(
                            FIRSTROW = 2,
                            FIELDTERMINATOR = ',',
                            ROWTERMINATOR = '\n'
                        )
                        
                        BULK INSERT Team_Stats
                        FROM 'Z:\db_pj\Team_Stats.csv'
                        WITH(
                            FIRSTROW = 2,
                            FIELDTERMINATOR = ',',
                            ROWTERMINATOR = '\n'
                        )
                        
                        BULK INSERT Teams
                        FROM 'Z:\db_pj\Teams.csv'
                        WITH(
                            FIRSTROW = 2,
                            FIELDTERMINATOR = ',',
                            ROWTERMINATOR = '\n'
                        )
                        
                        BULK INSERT Top_Scorers
                        FROM 'Z:\db_pj\Top_Scorers.csv'
                        WITH(
                            FIRSTROW = 2,
                            FIELDTERMINATOR = ',',
                            ROWTERMINATOR = '\n'
                        );
                     '''

        conn_cur.execute(sql_create_table)
        conn_cur.commit()
        conn_cur.execute(sql_import)
        conn_cur.commit()
        # 消息提示
        self.statusBar().showMessage("所有数据导入成功！")
        conn_cur.close()

    def show_all_players(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn_cur = connect_mssql(user_id, user_pwd)
        sql_show_all = 'SELECT * FROM '
        pass

        # 消息提示
        self.statusBar().showMessage("所有数据导入成功！")
        conn_cur.close()

    def add_player_data(self):
        pass

    def delete_player_data(self):
        pass

    def search_player(self):
        pass

    def show_all_teams(self):
        pass

    def change_team_data(self):
        pass

    def search_team(self):
        pass

    def show_all_game_data(self):
        pass

    def add_game_data(self):
        pass

    def delete_game(self):
        pass

    def compare_player_data(self):
        pass

    def heat_map(self):
        pass

    def line_graph(self):
        pass


def main():
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
