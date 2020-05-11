# __author__ = itsneo1990
from applications.production_manage.models import DataBaseInfo
from libs.hash import decrypt
from libs.mysql_helper import Connection


def catch_most_suit_server_group(grid_id):
    kf_db = DataBaseInfo.objects.get(grid_id=grid_id, db_name="kf")
    conn = Connection(database="kf", host=kf_db.db_address, port=int(kf_db.db_port), password=decrypt(kf_db.db_pwd),
                      user=kf_db.db_username)
    sql = """
    SELECT
        t.t2dserver,
        IFNULL( c.num, 0 ) AS num
    FROM
        t_wdk_sit AS t
        LEFT JOIN (
        SELECT
            t.t2dserver,
            COUNT( c.sessionid ) AS num 
        FROM
            t_wdk_sit AS t
            LEFT JOIN t2d_chatscene AS c ON t.sitid = c.siteid 
        WHERE
            c.starttime >= 1511798400000 
            AND c.starttime <= 1511852729000 
        GROUP BY
            t.t2dmqttserver 
        ) AS c ON t.t2dserver = c.t2dserver 
    GROUP BY
        t.t2dserver;
    """
    result = conn.query(sql)
    print(result)
