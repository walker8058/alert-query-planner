from config import A1_TIME_RANGE, A2_TIME_RANGE
a1=f"""
-查詢完整交易紀錄計劃
    種類：Graylog告警
    說明:透過查詢完整的交易紀錄，確認造成GrayLog的告警原因
    步驟:
        1.根據TXNSEQ:TXNSEQ查詢告警中時(event_timestamp)該筆交易的紀錄，確認詳細錯誤訊息與失敗原因。
        2.根據告警中的發生時間(event_timestamp)查詢Log，以確認是否因其他交易而影響服務。
    計劃需求:
        1.步驟1必須於description欄位中帶入TXNSEQ:"TXNSEQ"的資訊。
        2.time_range設定為{A1_TIME_RANGE}。
        3.查詢時間應訂為"event_timestamp"
"""
b1=f"""
-查詢系統穩定計劃
    種類：確認服務穩定
    說明:透過使用者提供的服務異常時間以及昨日相同時間(預設為服務正常)的ResponseTime，確認目前的系統是否穩定。
    步驟:
        1.根據MSGID:"MSGID"不穩定的時間，查詢MSGID:"MSGID"異常時的平均ResponseTime(單位秒)。
        2.查詢MSGID:"MSGID"於昨日相同時間的ResponseTime，以此取得正常的平均ResponseTime(單位秒)。
        3.查詢MSGID:"MSGID"目前時間(此處必需使用get_current_time工具取得目前時間)的平均ResponseTime(單位秒)。
    計劃需求:
        1.根據以上資訊以及回覆時間是否超過3000(單位秒)，判斷目前的的API服務是否正常且穩定。
        2.在description中須說明查詢時需同時查詢"[GW]COMPLETE[S]"字串，以篩選出攜帶ResponseTime欄位的紀錄。
        3.time_range設定為{A2_TIME_RANGE}。
        4.時間的回覆格式為"YYYY-MM-DD HH:MM:SS"，例如："2023-10-01 12:00:00"。
"""