import pprint
from operator import itemgetter
from maildepoint import MailDePoint
from rwebsearch import RWebSearch

try:
    # Create application list
    apps = []
    apps.append( 'RWebSearch' )
    apps.append( 'MailDePoint' )
    ### 最初に各クラスのインスタンスを準備する方法は
    ### Logger もしくは Appdict が singleton のため、
    ### ログ出力などの処理が怪しい（二重出力）になる。
    ### 実行処理本体にも悪影響がでている可能性あり。

    for app_class in apps:
        try:
            cls_def = globals()[app_class]
            App = cls_def()
            App.prepare()
            need_report = App.pilot()
            App.tearDown()

        except Exception as e:
            App.logger.critical(f'!!{App.exception_message(e)}')
        finally:
            if need_report:
                result = App.pilot_result.sort(key=itemgetter(0))
                # print(App.pilot_result)
                # print(App.pilot_result.keys())
                # result = list(App.pilot_result)
                # result = [ App.pilot_result ]
                # print(result)
                # for k in sorted(App.pilot_result.keys()):
                #     result.append( {k, App.pilot_result[k]} )
                # result = sorted(App.pilot_result.items(), key=itemgetter(0))
                # result.sort(key=itemgetter(0))
                print(result)
                # result.sort(key=itemgetter(0))
                # if result != []:
                App.report(
                    pprint.pformat(result, width=40)
                )
except Exception as e:
    print(e.args)