import pprint
from maildepoint import MailDePoint
from rwebsearch import RWebSearch

try:
    # Create application list
    apps = []
    apps.append( RWebSearch() )
    apps.append( MailDePoint() )
    ### 最初に各クラスのインスタンスを準備する方法は
    ### Logger もしくは Appdict が singleton のため、
    ### ログ出力などの処理が怪しい（二重出力）になる。
    ### 実行処理本体にも悪影響がでている可能性あり。

    for App in apps:
        App.prepare()
        App.pilot()
        App.tearDown()

except Exception as e:
    App.logger.critical(f'!!{App.exception_message(e)}')
finally:
    # App.pilot_result.sort(key=itemgetter(0))
    result = App.pilot_result
    if result != []:
        App.report(
            pprint.pformat(result, width=40)
        )
